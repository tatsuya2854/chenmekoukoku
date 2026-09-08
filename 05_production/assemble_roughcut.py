# -*- coding: utf-8 -*-
"""
A/B/C 案のラフカット（アニマティクス）を 1080x1920 / 24fps で組む。音なし。
  python3 05_production/assemble_roughcut.py A B C
出力: 05_production/roughcuts/{案}_v01_roughcut.mp4
素材: generated_video/（Veo）、composites/（手×実物ボトル）、assets/ai_sets/（静止画）、assets/product/bottle_front_cutout_level.png
規定: 01_brandbook §5（テロップ）§6（映像）。ボトルは均等スケール＋位置のみ。
"""
import cv2, numpy as np, os, sys, subprocess, math
from PIL import Image, ImageDraw, ImageFont
W,H,FPS=1080,1920,24
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P=lambda *a: os.path.join(ROOT,*a)
FONT_DIR=P("05_production","fonts")
CUT=cv2.imread(P("assets","product","bottle_front_cutout_level.png"),cv2.IMREAD_UNCHANGED)
CHARCOAL=(0x6A,0x66,0x64); ROSE=(0xC1,0x28,0x44); MILK=(0xFF,0xF8,0xF6); BLUSH=(0xFD,0xCB,0xD7); PETAL=(0xFC,0xDD,0xE5)

# ---- 座標（比率）: グリッドで実測して入れる ----
CFG={
 "B2_bottle_bbox": (0.285,0.47,0.08,0.118),   # B2/B8 動画内プレースホルダー x,y,w,h
 "S3V_empty_spot": (0.605,0.535,0.06,0.13),   # 棚の空き（ボトルを置く位置）
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

def draw_text(frame,text,fnt,color,y,alpha=1.0,pill=True,pill_color=MILK,emph=ROSE,tracking=0,scale=1.0,x=None):
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

class Seg:
    def __init__(s,dur,src,kind,**kw): s.dur=dur; s.src=src; s.kind=kind; s.kw=kw
def render(segs,captions,out_path,end_fade=8):
    os.makedirs(os.path.dirname(out_path),exist_ok=True)
    tmp=out_path.replace(".mp4","_raw.mp4"); vw=cv2.VideoWriter(tmp,cv2.VideoWriter_fourcc(*"mp4v"),FPS,(W,H))
    total=sum(s.dur for s in segs); N=int(round(total*FPS)); cache={}
    t_acc=0.0; seg_i=0; seg_start=0.0; last=None
    for n in range(N):
        t=n/FPS
        while seg_i<len(segs)-1 and t>=seg_start+segs[seg_i].dur: seg_start+=segs[seg_i].dur; seg_i+=1
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
            if kw.get("bottle"): img=paste_bottle(img,kw["bottle"],gain=kw.get("gain",0.9))
            z,dx,dy=kb(lt,s.dur,kw.get("z0",1.0),kw.get("z1",1.0),kw.get("d0",(0,0)),kw.get("d1",(0,0)))
            f=cover(img,z,dx,dy)
        elif s.kind=="solid":
            f=np.zeros((H,W,3),np.uint8); f[:]=s.src
        if "dark" in kw: f=(f.astype(np.float32)*kw["dark"]).astype(np.uint8)
        if "dark_ramp" in kw:  # (a0,a1)
            a0,a1=kw["dark_ramp"]; f=(f.astype(np.float32)*(a0+(a1-a0)*lt/s.dur)).astype(np.uint8)
        f=grade(f)
        if kw.get("xfade_from") is not None and lt<kw.get("xfade",0.5) and last is not None:
            a=lt/kw["xfade"]; f=cv2.addWeighted(last_prev,1-a,f,a,0)
        if lt<1/FPS: last_prev=last if last is not None else f
        # captions
        for c in captions:
            a=fade_a(t,c["t0"],c["t1"],c.get("fin",0.25),c.get("fout",0.2))
            if a<=0: continue
            pop=0.94+0.06*min(1,(t-c["t0"])/0.25)   # ポップイン
            if c["style"]=="bubble": f=bubble(f,c["text"],a)
            else:
                st=c["style"]
                fnt={"body":F_BODY(c.get("size",64)),"head":F_HEAD(c.get("size",92)),"en":F_EN(c.get("size",104)),"en_sub":F_EN(c.get("size",52))}[st]
                col={"body":CHARCOAL,"head":CHARCOAL,"en":c.get("color",ROSE),"en_sub":c.get("color",CHARCOAL)}[st]
                yy=c.get("y",{"body":1300,"head":1280,"en":1150,"en_sub":1290}[st])
                pill=c.get("pill", st in ("body","head"))
                f=draw_text(f,c["text"],fnt,col,yy,a,pill=pill,pill_color=c.get("pill_color",MILK),tracking=c.get("tracking",8 if st in("en","en_sub") else 0),scale=pop if st!="en" else 1.0)
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
     Seg(3.0,"05_production/generated_video/A6_calf_wrap_v2.mp4","clip",start=1.0,z0=1.6,z1=1.68,d0=(0,0.2),d1=(0,0.22)),
     Seg(2.2,"05_production/generated_video/A7_face_eyes_open_v2.mp4","clip",start=1.4),
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
     Seg(3.2,"05_production/generated_video/A6_calf_wrap_v2.mp4","clip",start=1.0,z0=1.6,z1=1.68,d0=(0,0.2),d1=(0,0.22)),
     Seg(1.8,"05_production/generated_video/A6_calf_wrap_v2.mp4","clip",start=4.2,z0=1.68,z1=1.68,d0=(0,0.22),d1=(0,0.22)),
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
     dict(text="ごめんね、、、",style="body",t0=1.6,t1=2.5,fin=0.15,fout=0.1,y=300),
     dict(text="うん、いま【在庫切れ】",style="body",t0=2.5,t1=3.4,fin=0.15,fout=0.1,y=300),
     dict(text="ラベルの子、かわいいでしょ",style="body",t0=3.5,t1=5.6,y=300),
     dict(text="いま、ちょっと【お休み中】。",style="body",t0=5.7,t1=7.8),
     dict(text="でも、準備してるから。",style="body",t0=7.9,t1=9.0,fout=0.1,y=300),
     dict(text="【戻ってくる】から",style="head",t0=9.0,t1=10.2,fin=0.15,y=300),
     dict(text="戻ってくる日が決まったら、\nいちばんに。",style="body",t0=10.4,t1=12.0,y=300),
     dict(text="Coming back soon",style="en",t0=12.1,t1=15.0,fin=0.4,fout=0.3,y=480),
     dict(text="Get notified",style="en_sub",t0=13.7,t1=15.0,fin=0.4,fout=0.3,y=640),
     dict(text="再販のお知らせはプロフィールから",style="body",size=40,y=740,t0=13.8,t1=15.0,fin=0.4,fout=0.3,pill=False),
    ]
    render(segs,caps,P("05_production","roughcuts","C_v01_roughcut.mp4"))

if __name__=="__main__":
    for k in (sys.argv[1:] or ["A","B","C"]): {"A":build_A,"B":build_B,"C":build_C}[k]()
