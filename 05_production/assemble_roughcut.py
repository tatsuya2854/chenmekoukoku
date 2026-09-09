# -*- coding: utf-8 -*-
"""
A/B/C 案のラフカット（アニマティクス）を 1080x1920 / 24fps で組む。音なし。
  python3 05_production/assemble_roughcut.py A B C
出力: 05_production/roughcuts/{案}_v01_roughcut.mp4
素材: generated_video/（Veo）、composites/（手×実物ボトル）、assets/ai_sets/（静止画）、assets/product/bottle_front_cutout_level.png
規定: 01_brandbook §5（テロップ）§6（映像）。ボトルは均等スケール＋位置のみ。
"""
import cv2, numpy as np, os, sys, subprocess, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H,FPS=1080,1920,24
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P=lambda *a: os.path.join(ROOT,*a)
FONT_DIR=P("05_production","fonts")
CUT=cv2.imread(P("assets","product","bottle_front_cutout_level.png"),cv2.IMREAD_UNCHANGED)
CHARCOAL=(0x6A,0x66,0x64); ROSE=(0xC1,0x28,0x44); MILK=(0xFF,0xF8,0xF6); BLUSH=(0xFD,0xCB,0xD7); PETAL=(0xFC,0xDD,0xE5)

# ---- 座標（比率）: グリッドで実測して入れる ----
CFG={
 "B2_bottle_bbox": (0.285,0.47,0.08,0.118),   # B2/B8 動画内プレースホルダー x,y,w,h
 "S3V_empty_spot": (0.405,0.395,0.10,0.135),   # 棚の空き（ボトルを置く位置）
}

def font(name,size,wght=None):
    f=ImageFont.truetype(os.path.join(FONT_DIR,name),size)
    if wght:
        try: f.set_variation_by_axes([wght])
        except Exception: pass
    return f
F_BODY=lambda s=64: font("NotoSansJP[wght].ttf",s,700)     # 太字・座布団
F_HEAD=lambda s=92: font("NotoSansJP[wght].ttf",s,800)     # 見出し
F_EN=lambda s=104: font("CormorantGaramond[wght].ttf",s,500)
F_CM=lambda s=80: font("KleeOne-SemiBold.ttf",s)          # CM風・白・手書き（座布団なし）

# ---------- ブランドグレード（全カット共通） ----------
_VIG=None
def grade(f):
    """暖色・シャドウを起こす・軽いフェード・彩度95%・弱いビネット。静止画とAIクリップの色を揃える。"""
    global _VIG
    x=f.astype(np.float32)
    x=x*0.93+14                      # フェード（黒を14へ、白を251へ）
    x[:,:,0]*=0.95; x[:,:,1]*=0.995; x[:,:,2]*=1.035   # B↓ R↑ = 暖色
    g=x.mean(axis=2,keepdims=True); x=g+(x-g)*0.95
    if _VIG is None:
        yy,xx=np.mgrid[0:H,0:W]; r=np.sqrt(((xx-W/2)/(W/2))**2+((yy-H/2)/(H/2))**2); _VIG=(1-0.18*np.clip(r-0.55,0,1)/0.6)[:,:,None]
    return np.clip(x*_VIG,0,255).astype(np.uint8)

def cover(img,zoom=1.0,dx=0.0,dy=0.0,rot=0.0):
    """画像を 1080x1920 にカバーフィット。zoom>1 で寄り、dx/dy は中心のずらし（比率）、rot は度。"""
    h,w=img.shape[:2]; s=max(W/w,H/h)*zoom
    M=cv2.getRotationMatrix2D((w/2,h/2),rot,s)
    M[0,2]+=W/2-w/2 - dx*W; M[1,2]+=H/2-h/2 - dy*H
    return cv2.warpAffine(img,M,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)

def kb(t,dur,z0,z1,d0=(0,0),d1=(0,0)):
    u=t/max(dur,1e-6); u=u*u*(3-2*u)  # smoothstep
    return z0+(z1-z0)*u, d0[0]+(d1[0]-d0[0])*u, d0[1]+(d1[1]-d0[1])*u

def read_clip(path):
    cap=cv2.VideoCapture(path); fr=[]
    while True:
        ok,f=cap.read()
        if not ok: break
        fr.append(f)
    return fr

def paste_bottle(frame,bbox_frac,gain=0.9,shadow=True):
    h,w=frame.shape[:2]; x,y,bw,bh=[int(v*d) for v,d in zip(bbox_frac,(w,h,w,h))]
    s=max(bw*1.04/CUT.shape[1], bh*1.02/CUT.shape[0]); c=cv2.resize(CUT,None,fx=s,fy=s,interpolation=cv2.INTER_AREA if s<1 else cv2.INTER_CUBIC)
    ch,cw=c.shape[:2]; cx=int(x+bw/2-cw/2); cy=int(y+bh-ch)
    out=frame.astype(np.float32)
    if shadow:
        sh=np.zeros((h,w),np.float32); sh[max(y+bh-6,0):min(y+bh+10,h), max(x,0):min(x+bw,w)]=1; sh=cv2.GaussianBlur(sh,(0,0),12)*0.3
        out=out*(1-sh[:,:,None])+np.array([90,90,100],np.float32)*sh[:,:,None]
    x0,y0=max(cx,0),max(cy,0); x1,y1=min(cx+cw,w),min(cy+ch,h)
    cc=c[y0-cy:y1-cy, x0-cx:x1-cx]; a=cc[:,:,3:4].astype(np.float32)/255
    out[y0:y1,x0:x1]=out[y0:y1,x0:x1]*(1-a)+np.clip(cc[:,:,:3].astype(np.float32)*gain,0,255)*a
    return np.clip(out,0,255).astype(np.uint8)

def bgr2pil(f): return Image.fromarray(cv2.cvtColor(f,cv2.COLOR_BGR2RGB))
def pil2bgr(im): return cv2.cvtColor(np.asarray(im),cv2.COLOR_RGB2BGR)

import re
def _segments(text):
    """【...】で囲んだ部分を強調色に。"""
    out=[]
    for part in re.split(r"(【[^】]*】)",text):
        if not part: continue
        if part.startswith("【"): out.append((part[1:-1],True))
        else: out.append((part,False))
    return out

def draw_text(frame,text,fnt,color,y,alpha=1.0,pill=True,pill_color=MILK,emph=ROSE,tracking=0,scale=1.0,x=None,glow=0):
    """y は座布団の中心。pill=True で白い角丸座布団。scale はポップイン用。"""
    im=bgr2pil(frame).convert("RGBA"); layer=Image.new("RGBA",im.size,(0,0,0,0)); d=ImageDraw.Draw(layer)
    lines=text.split("\n"); size=fnt.size; lh=size*1.3
    if scale!=1.0:
        try: fnt=fnt.font_variant(size=max(1,int(size*scale)))
        except Exception: pass
        size=fnt.size; lh=size*1.3
    def width(line):
        return sum(d.textlength(t,font=fnt) for t,_ in _segments(line))+tracking*(len(re.sub(r"[【】]","",line))-1)
    widths=[width(l) for l in lines]; bw=max(widths); total_h=lh*len(lines)
    padx,pady=int(size*0.55),int(size*0.32)
    top=y-total_h/2
    if pill:
        x0=(W-bw)/2-padx if x is None else x-padx
        d.rounded_rectangle((x0,top-pady,x0+bw+2*padx,top+total_h+pady),radius=int(size*0.42),fill=pill_color+(int(235*alpha),))
    if glow:   # 白文字の周りに淡いピンク白の発光（CM風）
        gl=Image.new("RGBA",im.size,(0,0,0,0)); gd=ImageDraw.Draw(gl)
        for i,line in enumerate(lines):
            cx=(W-widths[i])/2 if x is None else x; cy=top+i*lh+lh*0.12
            for seg,_ in _segments(line):
                for ch in seg: gd.text((cx,cy),ch,font=fnt,fill=(255,236,240,int(190*alpha))); cx+=d.textlength(ch,font=fnt)+tracking
        gl=gl.filter(ImageFilter.GaussianBlur(glow)); layer=Image.alpha_composite(layer,gl); d=ImageDraw.Draw(layer)
    for i,line in enumerate(lines):
        cx=(W-widths[i])/2 if x is None else x; cy=top+i*lh+lh*0.12
        for seg,em in _segments(line):
            col=(emph if em else color)
            if tracking:
                for ch in seg:
                    if not pill: d.text((cx+2,cy+3),ch,font=fnt,fill=(60,40,45,int(90*alpha)))   # 影も同じ字送りで
                    d.text((cx,cy),ch,font=fnt,fill=col+(int(255*alpha),)); cx+=d.textlength(ch,font=fnt)+tracking
            else:
                if not pill: d.text((cx+2,cy+3),seg,font=fnt,fill=(60,40,45,int(90*alpha)))
                d.text((cx,cy),seg,font=fnt,fill=col+(int(255*alpha),)); cx+=d.textlength(seg,font=fnt)
    return pil2bgr(Image.alpha_composite(im,layer).convert("RGB"))

def bubble(frame,text,alpha=1.0,y=380):
    im=bgr2pil(frame).convert("RGBA"); layer=Image.new("RGBA",im.size,(0,0,0,0)); d=ImageDraw.Draw(layer)
    fnt=F_BODY(54); tw=d.textlength(text,font=fnt); pad=40; bw=int(tw+pad*2+80); bh=140
    x0=(W-bw)//2
    d.rounded_rectangle((x0,y,x0+bw,y+bh),radius=40,fill=(255,255,255,int(240*alpha)))
    d.ellipse((x0+30,y+38,x0+30+64,y+38+64),fill=BLUSH+(int(255*alpha),))
    d.text((x0+30+64+26,y+(bh-fnt.size)/2-8),text,font=fnt,fill=CHARCOAL+(int(255*alpha),))
    return pil2bgr(Image.alpha_composite(im,layer).convert("RGB"))

def fade_a(t,t0,t1,fin=0.3,fout=0.25):
    if t<t0 or t>t1: return 0.0
    return min(1.0,(t-t0)/fin,(t1-t)/fout,1.0) if (t1-t0)>fin+fout else min(1,(t-t0)/fin)

def find_plain_bottle(frame,region=(0.30,0.30,0.70,0.60)):
    """指定領域内で「白くて低彩度で縦長」の最大ブロブ＝無地ボトルを探し、bbox（比率）を返す。見つからなければ None。"""
    h,w=frame.shape[:2]; x0,y0,x1,y1=[int(v*d) for v,d in zip(region,(w,h,w,h))]
    hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV); m=((hsv[:,:,1]<40)&(hsv[:,:,2]>175)).astype(np.uint8)*255
    mask=np.zeros_like(m); mask[y0:y1,x0:x1]=m[y0:y1,x0:x1]; mask=cv2.morphologyEx(mask,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    n,lab,st,_=cv2.connectedComponentsWithStats(mask); best=None
    for i in range(1,n):
        x,y,bw,bh,a=st[i]
        if bh<bw*1.3 or a<400: continue
        if best is None or a>best[0]: best=(a,(x/w,y/h,bw/w,bh/h))
    return best[1] if best else None

def last_frame(path):
    fr=read_clip(P(path)); return fr[-1]

class Seg:
    def __init__(s,dur,src,kind,**kw): s.dur=dur; s.src=src; s.kind=kind; s.kw=kw
def render(segs,captions,out_path,end_fade=8):
    os.makedirs(os.path.dirname(out_path),exist_ok=True)
    tmp=out_path.replace(".mp4","_raw.mp4"); vw=cv2.VideoWriter(tmp,cv2.VideoWriter_fourcc(*"mp4v"),FPS,(W,H))
    total=sum(s.dur for s in segs); N=int(round(total*FPS)); cache={}
    bounds=[0]
    for sg in segs: bounds.append(bounds[-1]+int(round(sg.dur*FPS)))   # フレーム単位の境界（浮動小数のズレ防止）
    last=None; last_raw=None; last_prev=None
    for n in range(N):
        t=n/FPS
        seg_i=max(i for i in range(len(segs)) if bounds[i]<=n) if n<bounds[-1] else len(segs)-1
        seg_start=bounds[seg_i]/FPS; first=(n==bounds[seg_i])
        s=segs[seg_i]; lt=t-seg_start; kw=s.kw
        if s.kind=="still":
            if s.src not in cache:
                im=cv2.imread(P(s.src),cv2.IMREAD_UNCHANGED)
                if im.ndim==3 and im.shape[2]==4:   # 透過PNG → Blush 背景に乗せる（ラベルマクロ用）
                    hh,ww=im.shape[0]+200,im.shape[1]+400; bg=np.zeros((hh,ww,3),np.float32)
                    for yy_ in range(hh): bg[yy_]=np.array(BLUSH[::-1],np.float32)+(np.array(PETAL[::-1],np.float32)-np.array(BLUSH[::-1],np.float32))*(yy_/hh)
                    a=im[:,:,3:4].astype(np.float32)/255; y0,x0=100,200
                    sh=np.zeros((hh,ww),np.float32); sh[y0+20:y0+im.shape[0]+20, x0+10:x0+im.shape[1]+10]=a[:,:,0]; sh=cv2.GaussianBlur(sh,(0,0),28)*0.35
                    bg=bg*(1-sh[:,:,None])+np.array([100,90,110],np.float32)*sh[:,:,None]; bg=bg.astype(np.uint8)
                    bg[y0:y0+im.shape[0],x0:x0+im.shape[1]]=(bg[y0:y0+im.shape[0],x0:x0+im.shape[1]]*(1-a)+im[:,:,:3]*a).astype(np.uint8); im=bg
                cache[s.src]=im
            img=cache[s.src]
            z,dx,dy=kb(lt,s.dur,kw.get("z0",1.0),kw.get("z1",1.03),kw.get("d0",(0,0)),kw.get("d1",(0,0)))
            rot=kw.get("rot0",0)+(kw.get("rot1",0)-kw.get("rot0",0))*(lt/s.dur)
            if kw.get("bottle"): img=paste_bottle(img,kw["bottle"],gain=kw.get("gain",0.9))
            f=cover(img,z,dx,dy,rot)
        elif s.kind=="clip":
            if s.src not in cache: cache[s.src]=read_clip(P(s.src))
            fr=cache[s.src]
            idx=min(int((kw.get("start",0)+lt*kw.get("speed",1.0))*FPS),len(fr)-1); img=fr[idx]
            if kw.get("hold_last"): img=fr[-1]
            if kw.get("bottle"): img=paste_bottle(img,kw["bottle"],gain=kw.get("gain",0.9))
            if kw.get("reveal"):   # 無地ボトル → 実物ラベルが浮かび上がる（最終フレームの無地ボトル位置に合成し、クロスフェード）
                key=("reveal",s.src)
                if key not in cache:
                    bb=kw.get("reveal_bbox") or find_plain_bottle(fr[-1],kw.get("reveal_region",(0.30,0.30,0.70,0.60))) or CFG["S3V_empty_spot"]; print("reveal bbox",bb)
                    cache[key]=(bb,paste_bottle(fr[-1],bb,gain=kw.get("gain",0.92),shadow=False))
                bb,labeled=cache[key]
                a=min(1.0,max(0.0,(lt-kw.get("reveal_at",0.0))/kw.get("reveal_dur",0.6)))
                img=cv2.addWeighted(fr[-1],1-a,labeled,a,0)
            z,dx,dy=kb(lt,s.dur,kw.get("z0",1.0),kw.get("z1",1.0),kw.get("d0",(0,0)),kw.get("d1",(0,0)))
            f=cover(img,z,dx,dy)
        elif s.kind=="reveal_zoom":
            # src: 動画（最終フレーム）or 静止画。bbox は元画像の比率。ボトル中心へ寄りながらラベルをリビール。
            if s.src not in cache:
                base=last_frame(s.src) if s.src.endswith(".mp4") else cv2.imread(P(s.src)); cache[s.src]=base
            base=cache[s.src]; h,w=base.shape[:2]; bx,by,bw,bh=kw["bbox"]
            cxs,cys=(bx+bw/2)*w,(by+bh*0.55)*h                      # ボトルの中心（少し下寄り）
            u=min(1,lt/s.dur); u=u*u*(3-2*u); z=kw.get("z0",1.0)+(kw.get("z1",2.2)-kw.get("z0",1.0))*u
            sc=max(W/w,H/h)*z
            # 画面中心をボトル中心へ寄せる（u に応じて）
            tx=(w/2-cxs)*sc*kw.get("center",1.0)*u; ty=(h/2-cys)*sc*kw.get("center",1.0)*u
            M=np.float32([[sc,0,W/2-w/2*sc+tx],[0,sc,H/2-h/2*sc+ty]])
            f=cv2.warpAffine(base,M,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
            # 出力座標での bbox
            ox=(bx*w)*sc+M[0,2]; oy=(by*h)*sc+M[1,2]; obw=bw*w*sc; obh=bh*h*sc
            labeled=paste_bottle(f,(ox/W,oy/H,obw/W,obh/H),gain=kw.get("gain",0.9),shadow=False)
            a=min(1.0,max(0.0,(lt-kw.get("reveal_at",0.6))/kw.get("reveal_dur",0.8)))
            f=cv2.addWeighted(f,1-a,labeled,a,0)
        elif s.kind=="solid":
            f=np.zeros((H,W,3),np.uint8); f[:]=s.src
        if "dark" in kw: f=(f.astype(np.float32)*kw["dark"]).astype(np.uint8)
        if "dark_ramp" in kw:  # (a0,a1)
            a0,a1=kw["dark_ramp"]; f=(f.astype(np.float32)*(a0+(a1-a0)*lt/s.dur)).astype(np.uint8)
        f=grade(f)
        if first: last_prev=last_raw if last_raw is not None else f
        if kw.get("xfade_from") is not None and lt<kw.get("xfade",0.5) and last_prev is not None:
            a=lt/kw["xfade"]; f=cv2.addWeighted(last_prev,1-a,f,a,0)
        last_raw=f.copy()
        # captions
        for c in captions:
            a=fade_a(t,c["t0"],c["t1"],c.get("fin",0.25),c.get("fout",0.2))
            if a<=0: continue
            pop=0.94+0.06*min(1,(t-c["t0"])/0.25)   # ポップイン
            if c["style"]=="bubble": f=bubble(f,c["text"],a,y=c.get("y",380))
            else:
                st=c["style"]
                fnt={"body":F_BODY(c.get("size",64)),"head":F_HEAD(c.get("size",92)),"en":F_EN(c.get("size",104)),"en_sub":F_EN(c.get("size",52)),
                     "cm":F_CM(c.get("size",80)),"cm_head":F_CM(c.get("size",100)),"note":F_CM(c.get("size",60))}[st]
                col={"body":CHARCOAL,"head":CHARCOAL,"en":c.get("color",ROSE),"en_sub":c.get("color",CHARCOAL),"cm":(255,255,255),"cm_head":(255,255,255),"note":(255,255,255)}[st]
                yy=c.get("y",{"body":1300,"head":1280,"en":1150,"en_sub":1290,"cm":1250,"cm_head":1240,"note":330}[st])
                pill=c.get("pill", st in ("body","head"))
                is_cm=st in ("cm","cm_head","note")
                f=draw_text(f,re.sub(r"[【】]","",c["text"]) if is_cm else c["text"],fnt,col,yy,a,pill=pill,pill_color=c.get("pill_color",MILK),
                            tracking=c.get("tracking",8 if st in("en","en_sub") else (4 if is_cm else 0)),scale=1.0 if (st=="en" or is_cm) else pop,
                            glow=c.get("glow",16 if is_cm else 0),x=c.get("x"))
        if n>N-end_fade: f=(f.astype(np.float32)*((N-n)/end_fade)).astype(np.uint8)
        vw.write(f); last=f
    vw.release()
    ff=subprocess.run(["python3","-c","import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())"],capture_output=True,text=True).stdout.strip()
    subprocess.run([ff,"-y","-loglevel","error","-i",tmp,"-c:v","libx264","-pix_fmt","yuv420p","-crf","18","-preset","medium","-movflags","+faststart",out_path],check=True); os.remove(tmp)
    print("wrote",out_path,"%.1fs"%total)

def build_A():
    B2=CFG["B2_bottle_bbox"]
    segs=[
     Seg(2.4,"05_production/generated_video/A3_entry_walk.mp4","clip",start=0.0),
     Seg(1.8,"05_production/generated_video/B2_lamp_static.mp4","clip",start=0.0,bottle=B2,z0=1.15,z1=1.15,d0=(-0.02,0.05),d1=(-0.02,0.05)),
     Seg(1.4,"05_production/composites/B3_pump_press.jpg","still",z0=1.0,z1=1.05),
     Seg(3.0,"05_production/generated_video/A6_calf_wrap_v3.mp4","clip",start=1.0,z0=1.6,z1=1.68,d0=(0,0.2),d1=(0,0.22)),
     Seg(2.2,"05_production/generated_video/A7_face_eyes_open_v3.mp4","clip",start=1.4),
     Seg(1.8,"05_production/composites/B7_tea_bottle_bg.jpg","still",z0=1.0,z1=1.04),
     Seg(2.4,"05_production/generated_video/B2_lamp_static.mp4","clip",start=1.4,bottle=B2,z0=1.15,z1=1.2,d0=(-0.02,0.05),d1=(-0.02,0.05)),
    ]
    caps=[
     dict(text="今日、【何時間】立ってた？",style="body",t0=0.6,t1=2.4),
     dict(text="靴、脱いだ。",style="head",t0=2.5,t1=4.2),
     dict(text="今日は、ここまで。",style="body",t0=5.8,t1=8.6),
     dict(text="明日の私に、【ちょっとだけ】。",style="body",t0=8.8,t1=10.8),
     dict(text="Coming back soon",style="en",t0=13.3,t1=15.0,fin=0.4,fout=0.3,y=760),
    ]
    render(segs,caps,P("05_production","roughcuts","A_v01_roughcut.mp4"))

def build_B():
    B2=CFG["B2_bottle_bbox"]
    segs=[
     Seg(0.8,"assets/ai_sets/S4V.png","still",z0=1.0,z1=1.0,dark=0.35),
     Seg(1.6,"05_production/generated_video/B2_lamp_static.mp4","clip",start=0.0,bottle=B2,xfade_from=True,xfade=0.5),
     Seg(2.2,"05_production/composites/B3_pump_press.jpg","still",z0=1.0,z1=1.05),
     Seg(1.8,"05_production/composites/B4_cream_palms.png","still",z0=1.0,z1=1.04),
     Seg(3.2,"05_production/generated_video/B5_calf_closeup_v3.mp4","clip",start=0.8,z0=1.6,z1=1.68,d0=(0,0.2),d1=(0,0.22)),
     Seg(1.8,"05_production/generated_video/B5_calf_closeup_v3.mp4","clip",start=4.0,z0=1.68,z1=1.68,d0=(0,0.22),d1=(0,0.22)),
     Seg(1.4,"05_production/composites/B7_tea_bottle_bg.jpg","still",z0=1.0,z1=1.03),
     Seg(1.0,"05_production/generated_video/B8_lamp_off.mp4","clip",start=1.2,bottle=B2,dark_ramp=(1.0,0.6)),
     Seg(1.2,"05_production/generated_video/B8_lamp_off.mp4","clip",start=3.0,bottle=B2,gain=0.55,dark=0.35),
    ]
    caps=[
     dict(text="夜の【3分】。",style="head",t0=3.0,t1=4.5,y=330),
     dict(text="うるおうのに、【べたつかない】。",style="body",t0=4.8,t1=6.4,y=1380),
     dict(text="【ホワイトシトロン】の香り。",style="body",t0=7.2,t1=9.5,y=330),
     dict(text="今日より、明日。",style="head",t0=10.0,t1=11.4,y=330),
     dict(text="Stay tuned",style="en",t0=13.9,t1=15.0,color=MILK,y=960,size=100,fin=0.5,fout=0.3),
    ]
    render(segs,caps,P("05_production","roughcuts","B_v01_roughcut.mp4"))

def build_C():
    E=CFG["S3V_empty_spot"]
    segs=[
     Seg(1.6,"05_production/composites/C1_hold_front.jpg","still",z0=1.0,z1=1.02),
     Seg(1.8,"05_production/composites/C1_hold_front.jpg","still",z0=1.02,z1=1.06,rot0=0,rot1=3),
     Seg(2.2,"assets/product/bottle_front_cutout_level.png","still",z0=1.6,z1=1.9,d0=(0,-0.08),d1=(0,0.02)),   # ラベルマクロ（背景は cover の反射で白）
     Seg(2.2,"05_production/composites/C4_place_table.jpg","still",z0=1.0,z1=1.03),
     Seg(2.4,"assets/ai_sets/S3V.png","still",z0=1.1,z1=1.1,d0=(-0.04,0),d1=(0.04,0)),
     Seg(1.8,"assets/ai_sets/S3V.png","still",z0=1.1,z1=1.1,d0=(0.04,0),d1=(0.04,0),bottle=E,gain=0.95),
     Seg(1.6,"assets/ai_sets/S3V.png","still",z0=1.1,z1=1.14,d0=(0.04,0),d1=(0.04,0),bottle=E,gain=0.95),
     Seg(1.4,"assets/ai_sets/S3V.png","still",z0=1.14,z1=1.16,d0=(0.04,0),d1=(0.04,0),bottle=E,gain=0.95),
    ]
    caps=[
     dict(text="もう買えないですか？",style="bubble",t0=0.0,t1=3.4,fin=0.25,fout=0.2),
     dict(text="ごめんね、、、",style="note",t0=1.6,t1=2.6,fin=0.2,fout=0.15,y=280,x=90),
     dict(text="うん、いま在庫切れ",style="cm",t0=2.6,t1=3.4,fin=0.15,fout=0.1,y=1250),
     dict(text="ラベルの子、かわいいでしょ",style="cm",t0=3.5,t1=5.6,y=300),
     dict(text="いま、ちょっとお休み中。",style="cm",t0=5.7,t1=7.8,y=1250),
     dict(text="でも、準備してるから。",style="cm",t0=7.9,t1=9.0,fout=0.1,y=320),
     dict(text="戻ってくるから",style="cm_head",t0=9.0,t1=10.2,fin=0.15,y=320),
     dict(text="戻ってくる日が決まったら、\nいちばんに。",style="cm",t0=10.4,t1=12.0,y=300),
     dict(text="Coming back soon",style="en",t0=12.1,t1=15.0,fin=0.4,fout=0.3,y=480),
     dict(text="Get notified",style="en_sub",t0=13.7,t1=15.0,fin=0.4,fout=0.3,y=640,color=(255,255,255)),
     dict(text="再販のお知らせはプロフィールから",style="cm",size=40,y=740,t0=13.8,t1=15.0,fin=0.4,fout=0.3,glow=8),
    ]
    render(segs,caps,P("05_production","roughcuts","C_v01_roughcut.mp4"))

def build_C2():
    """C v02：動きあり。無地ボトルの Veo クリップ 4 本 → 最後だけ実物ラベルが浮かび上がる。"""
    segs=[
     Seg(1.6,"05_production/generated_video/C1_hold_tilt.mp4","clip",start=0.0),
     Seg(1.8,"05_production/generated_video/C1_hold_tilt.mp4","clip",start=1.6),
     Seg(2.2,"05_production/generated_video/C3_pump_press.mp4","clip",start=0.4),
     Seg(2.2,"05_production/generated_video/C4_place.mp4","clip",start=0.6),
     Seg(3.6,"05_production/generated_video/C5_shelf_place.mp4","clip",start=0.6),
     Seg(1.4,"05_production/generated_video/C5_shelf_place.mp4","clip",hold_last=True,reveal=True,reveal_at=0.2,reveal_dur=0.8,reveal_bbox=(0.405,0.15,0.115,0.19),z0=1.0,z1=1.03),
     Seg(2.2,"05_production/generated_video/C5_shelf_place.mp4","clip",hold_last=True,reveal=True,reveal_at=-9,reveal_dur=0.1,reveal_bbox=(0.405,0.15,0.115,0.19),z0=1.03,z1=1.07),
    ]
    caps=[
     dict(text="もう買えないですか？",style="bubble",t0=0.0,t1=3.4,fin=0.25,fout=0.2),
     dict(text="ごめんね、、、",style="note",t0=1.6,t1=2.6,fin=0.2,fout=0.15,y=280,x=90),
     dict(text="うん、いま在庫切れ",style="cm",t0=2.6,t1=3.4,fin=0.15,fout=0.1,y=1250),
     dict(text="いつもの、1プッシュ。",style="cm",t0=3.6,t1=5.6,y=300),
     dict(text="いま、ちょっとお休み中。",style="cm",t0=5.8,t1=7.8,y=1250),
     dict(text="でも、準備してるから。",style="cm",t0=8.0,t1=9.4,fout=0.1,y=1250),
     dict(text="戻ってくるから",style="cm_head",t0=9.4,t1=11.2,fin=0.15,y=1250),
     dict(text="Coming back soon",style="en",t0=12.2,t1=15.0,fin=0.4,fout=0.3,y=1180),
     dict(text="Get notified",style="en_sub",t0=13.6,t1=15.0,fin=0.4,fout=0.3,y=1330,color=(255,255,255)),
     dict(text="再販のお知らせはプロフィールから",style="cm",size=40,y=1420,t0=13.7,t1=15.0,fin=0.4,fout=0.3,glow=8),
    ]
    render(segs,caps,P("05_production","roughcuts","C_v02_roughcut.mp4"))

def build_C3():
    """C v03：パジャマの AI 出演者が演じる版。無地ボトル → 最後に実物ラベルがリビール。"""
    RB=(0.32,0.385,0.087,0.11)   # P4 最終フレームの無地ボトル位置（棚の上）
    segs=[
     Seg(3.4,"05_production/generated_video/P1_hold.mp4","clip",start=0.0),
     Seg(2.3,"05_production/generated_video/P2_pump.mp4","clip",start=0.0),
     Seg(2.5,"05_production/generated_video/B5_calf_closeup_v3.mp4","clip",start=1.0,z0=1.25,z1=1.3,d0=(0,0.12),d1=(0,0.14)),
     Seg(3.4,"05_production/generated_video/P4_shelf.mp4","clip",start=0.4),
     Seg(1.4,"05_production/generated_video/P4_shelf.mp4","clip",hold_last=True,reveal=True,reveal_at=0.2,reveal_dur=0.8,reveal_bbox=RB,z0=1.0,z1=1.06,d0=(-0.06,0.0),d1=(-0.08,-0.02)),
     Seg(2.0,"05_production/generated_video/P4_shelf.mp4","clip",hold_last=True,reveal=True,reveal_at=-9,reveal_dur=0.1,reveal_bbox=RB,z0=1.06,z1=1.16,d0=(-0.08,-0.02),d1=(-0.12,-0.04)),
    ]
    caps=[
     dict(text="もう買えないですか？",style="bubble",t0=0.0,t1=3.4,fin=0.25,fout=0.2,y=1290),
     dict(text="ごめんね、、、",style="note",t0=1.4,t1=2.4,fin=0.2,fout=0.15,y=280,x=90),
     dict(text="うん、いま在庫切れ",style="cm",t0=2.4,t1=3.4,fin=0.15,fout=0.1,y=1150),
     dict(text="いつもの、1プッシュ。",style="cm",t0=3.6,t1=5.7,y=1250),
     dict(text="今日も、おつかれ。",style="cm",t0=5.9,t1=8.2,y=300),
     dict(text="でも、準備してるから。",style="cm",t0=8.4,t1=9.8,fout=0.1,y=1250),
     dict(text="戻ってくるから",style="cm_head",t0=9.8,t1=11.6,fin=0.15,y=1250),
     dict(text="Coming back soon",style="en",t0=12.4,t1=15.0,fin=0.4,fout=0.3,y=1180),
     dict(text="Get notified",style="en_sub",t0=13.6,t1=15.0,fin=0.4,fout=0.3,y=1330,color=(255,255,255)),
     dict(text="再販のお知らせはプロフィールから",style="cm",size=40,y=1420,t0=13.7,t1=15.0,fin=0.4,fout=0.3,glow=8),
    ]
    render(segs,caps,P("05_production","roughcuts","C_v03_roughcut.mp4"))

def build_C4():
    """C v04：人物版＋最後は人が消えて商品だけをズーム。18 秒。"""
    segs=[
     Seg(3.4,"05_production/generated_video/P1_hold.mp4","clip",start=0.0),
     Seg(0.9,"05_production/generated_video/P2_pump.mp4","clip",start=0.0,z0=1.15,z1=1.18,d0=(0,0.08),d1=(0,0.09)),   # 指がポンプを押す（出る瞬間の直前で切る）
     Seg(1.4,"05_production/generated_video/P2_pump.mp4","clip",start=1.5,speed=0.65,z0=1.7,z1=1.78,d0=(0.02,0.20),d1=(0.02,0.21)),   # 手のひらにクリーム（同クリップ後半・スロー・寄り）。出る瞬間(0.9-1.5s)は飛ばす
     Seg(2.5,"05_production/generated_video/B5_calf_closeup_v3.mp4","clip",start=1.0,z0=1.3,z1=1.36,d0=(0,0.16),d1=(0,0.18)),
     Seg(3.8,"05_production/generated_video/P4_shelf.mp4","clip",start=0.6),
     Seg(6.0,"05_production/generated_video/C5_shelf_place.mp4","reveal_zoom",bbox=(0.405,0.15,0.115,0.19),z0=1.0,z1=2.3,reveal_at=0.7,reveal_dur=0.9,gain=0.92,xfade_from=True,xfade=0.5),
    ]
    caps=[
     dict(text="もう買えないですか？",style="bubble",t0=0.0,t1=3.4,fin=0.25,fout=0.2,y=1290),
     dict(text="ごめんね、、、",style="note",t0=1.4,t1=2.4,fin=0.2,fout=0.15,y=280,x=90),
     dict(text="うん、いま在庫切れ",style="cm",t0=2.4,t1=3.4,fin=0.15,fout=0.1,y=1150),
     dict(text="いつもの、1プッシュ。",style="cm",t0=3.6,t1=5.7,y=300),
     dict(text="今日も、おつかれ。",style="cm",t0=5.9,t1=8.2,y=300),
     dict(text="でも、準備してるから。",style="cm",t0=8.4,t1=10.0,fout=0.1,y=1250),
     dict(text="戻ってくるから",style="cm_head",t0=10.0,t1=12.0,fin=0.15,y=1250),
     dict(text="Coming back soon",style="en",t0=14.2,t1=18.0,fin=0.5,fout=0.3,y=360),
     dict(text="Get notified",style="en_sub",t0=15.6,t1=18.0,fin=0.4,fout=0.3,y=500,color=(255,255,255)),
     dict(text="再販のお知らせはプロフィールから",style="cm",size=40,y=590,t0=15.7,t1=18.0,fin=0.4,fout=0.3,glow=8),
    ]
    render(segs,caps,P("05_production","roughcuts","C_v04_roughcut.mp4"),end_fade=12)

def build_C5():
    """C v05：ラグジュアリー版（v3_luxe モデル）。18 秒。人物→人が消えて商品ズーム→ラベルが灯る。"""
    segs=[
     Seg(3.4,"05_production/generated_video/L1_hold.mp4","clip",start=0.0),
     Seg(0.9,"05_production/generated_video/L2_pump.mp4","clip",start=0.0,z0=1.15,z1=1.18,d0=(0,0.06),d1=(0,0.07)),
     Seg(1.4,"05_production/generated_video/L2_pump.mp4","clip",start=1.3,speed=0.6,z0=1.7,z1=1.78,d0=(-0.02,0.16),d1=(-0.02,0.17)),
     Seg(2.5,"05_production/generated_video/L3_leg.mp4","clip",start=1.0,z0=1.15,z1=1.2,d0=(0,0.08),d1=(0,0.1)),
     Seg(3.8,"05_production/generated_video/L4_table.mp4","clip",start=0.6),
     Seg(6.0,"assets/ai_sets/L5_table_empty.png","reveal_zoom",bbox=(0.335,0.685,0.135,0.18),z0=1.0,z1=2.2,reveal_at=0.7,reveal_dur=0.9,gain=0.92,xfade_from=True,xfade=0.5),
    ]
    caps=[
     dict(text="もう買えないですか？",style="bubble",t0=0.0,t1=3.4,fin=0.25,fout=0.2,y=1290),
     dict(text="ごめんね、、、",style="note",t0=1.4,t1=2.4,fin=0.2,fout=0.15,y=280,x=90),
     dict(text="うん、いま在庫切れ",style="cm",t0=2.4,t1=3.4,fin=0.15,fout=0.1,y=1150),
     dict(text="いつもの、1プッシュ。",style="cm",t0=3.6,t1=5.7,y=300),
     dict(text="自分を好きになる時間を、\n脚元から。",style="cm",size=72,t0=5.9,t1=8.2,y=300),
     dict(text="でも、準備してるから。",style="cm",t0=8.4,t1=10.0,fout=0.1,y=1250),
     dict(text="戻ってくるから",style="cm_head",t0=10.0,t1=12.0,fin=0.15,y=1250),
     dict(text="Coming back soon",style="en",t0=14.2,t1=18.0,fin=0.5,fout=0.3,y=360),
     dict(text="Get notified",style="en_sub",t0=15.6,t1=18.0,fin=0.4,fout=0.3,y=500,color=(255,255,255)),
     dict(text="再販のお知らせはプロフィールから",style="cm",size=40,y=590,t0=15.7,t1=18.0,fin=0.4,fout=0.3,glow=8),
    ]
    render(segs,caps,P("05_production","roughcuts","C_v05_luxe_roughcut.mp4"),end_fade=12)

if __name__=="__main__":
    for k in (sys.argv[1:] or ["A","B","C"]): {"A":build_A,"B":build_B,"C":build_C,"C2":build_C2,"C3":build_C3,"C4":build_C4,"C5":build_C5}[k]()
