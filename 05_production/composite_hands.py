# -*- coding: utf-8 -*-
"""AI生成の手＋プレースホルダー画像に、実物ボトルの切り抜きを等倍スケールで重ね、指が前に来る部分は肌マスクで手を上に戻す。
   使い方: python3 05_production/composite_hands.py <in.png> <out.jpg> [--no-hand-restore]
   ボトル本体は変形しない（均等スケール＋位置のみ）。"""
import cv2, numpy as np, sys
CUT="assets/product/bottle_front_cutout_level.png"
def placeholder_bbox(img):
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV); H,W=img.shape[:2]
    m=((hsv[:,:,1]<45)&(hsv[:,:,2]>165)).astype(np.uint8)*255
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((9,9),np.uint8))
    n,lab,st,_=cv2.connectedComponentsWithStats(m)
    best=None
    for i in range(1,n):
        x,y,w,h,a=st[i]
        if a<0.01*H*W or h<w*1.2 or h>W*3: continue          # tall-ish blob
        cx=x+w/2
        if not (0.15*W<cx<0.85*W): continue
        score=a
        if best is None or score>best[0]: best=(score,(x,y,w,h))
    return best[1] if best else None
def skin_mask(img):
    ycc=cv2.cvtColor(img,cv2.COLOR_BGR2YCrCb); hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    m=cv2.inRange(ycc,(0,135,85),(255,180,135))
    # 白いプレースホルダー（高明度・低彩度）を肌と誤判定しないよう締める
    m=cv2.bitwise_and(m, ((hsv[:,:,1]>45)&(hsv[:,:,2]<215)).astype(np.uint8)*255)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8)); m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
    return cv2.GaussianBlur(m,(5,5),0).astype(np.float32)/255
def composite(src,dst,restore=True,bbox_frac=None):
    img=cv2.imread(src); H,W=img.shape[:2]
    bb=tuple(int(v*d) for v,d in zip(bbox_frac,(W,H,W,H))) if bbox_frac else placeholder_bbox(img)
    if bb is None: print("placeholder not found",src); return
    x,y,w,h=bb; cut=cv2.imread(CUT,cv2.IMREAD_UNCHANGED)
    s=max((w*1.04)/cut.shape[1], (h*1.02)/cut.shape[0])   # 幅・高さの大きい方に合わせて完全に覆う（均等スケール）
    if s>1.0: print("warning: upscaling %.2f"%s)
    c=cv2.resize(cut,None,fx=s,fy=s,interpolation=cv2.INTER_AREA if s<1 else cv2.INTER_CUBIC)
    ch,cw=c.shape[:2]; cx=int(x+w/2-cw/2); cy=int(y+h-ch)+int(0.01*h)   # align base
    # paste with bounds
    x0,y0=max(cx,0),max(cy,0); x1,y1=min(cx+cw,W),min(cy+ch,H)
    cc=c[y0-cy:y1-cy, x0-cx:x1-cx]; a=cc[:,:,3:4].astype(np.float32)/255
    # exposure-only match: mean luminance of placeholder vs cutout
    ph=cv2.cvtColor(img[y:y+h,x:x+w],cv2.COLOR_BGR2GRAY).mean(); cl=cv2.cvtColor(cc[:,:,:3],cv2.COLOR_BGR2GRAY)[cc[:,:,3]>200].mean()
    gain=float(np.clip(ph/cl,0.85,1.15))
    out=img.copy().astype(np.float32); reg=out[y0:y1,x0:x1]
    # contact shadow under bottle
    sh=np.zeros((H,W),np.float32); sh[y+h-6:y+h+10, x:x+w]=1; sh=cv2.GaussianBlur(sh,(0,0),14)*0.35
    out=out*(1-sh[:,:,None])+np.array([90,90,100],np.float32)*sh[:,:,None]; reg=out[y0:y1,x0:x1]
    reg[:]=reg*(1-a)+np.clip(cc[:,:,:3].astype(np.float32)*gain,0,255)*a
    if restore:
        sk=skin_mask(img)[y0:y1,x0:x1][:,:,None]; reg[:]=reg*(1-sk)+img[y0:y1,x0:x1].astype(np.float32)*sk
    cv2.imwrite(dst,np.clip(out,0,255).astype(np.uint8),[cv2.IMWRITE_JPEG_QUALITY,93]); print("ok",dst,"bbox",bb,"scale %.2f gain %.2f"%(s,gain))
if __name__=="__main__":
    bf=None
    for a in sys.argv:
        if a.startswith("--bbox="): bf=[float(v) for v in a[7:].split(",")]   # x,y,w,h を画像サイズに対する比率で
    composite(sys.argv[1],sys.argv[2],"--no-hand-restore" not in sys.argv,bf)
