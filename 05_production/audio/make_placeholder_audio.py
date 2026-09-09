# -*- coding: utf-8 -*-
"""仮音（プレースホルダー）を合成する。本物の音源に差し替えるまでのタイミング確認用。
   出力: 05_production/audio/placeholder/{bgm,se_cloth,se_pump,se_cream,se_stroke,se_place,se_reveal}.wav"""
import numpy as np, wave, os, math
SR=48000; OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"placeholder"); os.makedirs(OUT,exist_ok=True)
def save(name,x):
    x=np.clip(x,-1,1); w=wave.open(os.path.join(OUT,name+".wav"),"wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x*32767).astype(np.int16).tobytes()); w.close(); print("wrote",name, "%.2fs"%(len(x)/SR))
def tone(f,dur,amp=0.3,harm=(1,0.4,0.2,0.1),decay=2.5):
    t=np.arange(int(SR*dur))/SR; env=np.exp(-t*decay)*(1-np.exp(-t*200)); y=sum(a*np.sin(2*np.pi*f*(i+1)*t) for i,a in enumerate(harm)); return amp*env*y
def lowpass(x,cut=3000):
    a=math.exp(-2*math.pi*cut/SR); y=np.zeros_like(x); z=0.0
    for i in range(len(x)): z=a*z+(1-a)*x[i]; y[i]=z
    return y
def noise(dur): return np.random.default_rng(7).standard_normal(int(SR*dur))
# ---- BGM: 85 BPM, C G Am F, soft piano-like plucks + pad, 18 s ----
bpm=85; beat=60/bpm; total=18.0; y=np.zeros(int(SR*total))
chords=[[261.63,329.63,392.00],[196.00,246.94,293.66],[220.00,261.63,329.63],[174.61,220.00,261.63]]  # C G Am F
pattern=[0,0.5,1,1.5,2,2.5,3,3.5]  # 8ths
bar=0; t0=0.0
while t0<total:
    ch=chords[bar%4]
    for k,off in enumerate(pattern):
        st=t0+off*beat
        if st>=total: break
        f=ch[k%3]*(2 if k in (1,5) else 1)*(0.5 if k==0 else 1)
        n=tone(f,1.2,amp=0.11 if k%2==0 else 0.07,decay=3.0); i=int(st*SR); y[i:i+len(n)]+=n[:len(y)-i]
    # pad
    tt=np.arange(int(SR*4*beat))/SR; pad=sum(0.03*np.sin(2*np.pi*f/2*tt) for f in ch)*np.sin(np.pi*tt/(4*beat)); i=int(t0*SR); y[i:i+len(pad)]+=pad[:len(y)-i]
    t0+=4*beat; bar+=1
y=lowpass(y,2600); y+=0.004*lowpass(noise(total),1200)   # ローファイ感（薄いノイズ）
t=np.arange(len(y))/SR; y*=np.minimum(1,t/0.5)*np.minimum(1,np.maximum(0,(total-t)/0.8))
save("bgm",y/np.max(np.abs(y))*0.8)
# ---- SE ----
n=noise(0.35); t=np.arange(len(n))/SR; save("se_cloth",lowpass(n,1500)*np.exp(-t*12)*0.35)
n=noise(0.18); t=np.arange(len(n))/SR; pump=lowpass(n,5000)*np.exp(-t*30)*0.9+tone(900,0.18,amp=0.15,decay=40); save("se_pump",pump)
t=np.arange(int(SR*0.3))/SR; save("se_cream",(0.25*np.sin(2*np.pi*(180-120*t)*t))*np.exp(-t*10))
n=noise(2.0); t=np.arange(len(n))/SR; env=np.sin(np.pi*t/2.0)**2; save("se_stroke",lowpass(n,900)*env*0.25)
t=np.arange(int(SR*0.25))/SR; save("se_place",(0.6*np.sin(2*np.pi*140*t)+0.2*lowpass(noise(0.25),2000))*np.exp(-t*28))
save("se_reveal",tone(1318.5,1.6,amp=0.22,harm=(1,0.3,0.1),decay=2.2)+tone(1975.5,1.6,amp=0.10,harm=(1,0.2),decay=2.6))
