# -*- coding: utf-8 -*-
"""キューシート通りに音を並べてミックスし、動画に乗せる。無いファイルはスキップ。
   python3 05_production/audio/mux_audio.py [入力mp4] [出力mp4]"""
import os, sys, subprocess, shlex
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
A=os.environ.get("AUDIO_DIR") or os.path.join(ROOT,"05_production","audio")
SRC=sys.argv[1] if len(sys.argv)>1 else os.path.join(ROOT,"05_production","roughcuts","C_v04_roughcut.mp4")
DST=sys.argv[2] if len(sys.argv)>2 else os.path.join(ROOT,"05_production","roughcuts","C_v04_with_audio.mp4")
DUR=18.0
CUES=[  # (file, in_sec, gain_dB)
 ("bgm",0.0,-22),("se_cloth",0.0,-18),("vo_01",1.4,-14),("vo_02",2.4,-14),("vo_03",3.6,-14),("se_pump",3.9,-8),("se_cream",4.3,-14),
 ("vo_04",5.9,-14),("se_stroke",6.0,-16),("vo_05",8.4,-14),("se_place",8.6,-10),("vo_06",10.0,-14),("se_reveal",12.7,-12),
]
def find(name):
    for ext in (".wav",".mp3",".m4a",".aac",".flac"):
        p=os.path.join(A,name+ext)
        if os.path.exists(p): return p
ff=subprocess.run([sys.executable,"-c","import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())"],capture_output=True,text=True).stdout.strip() or "ffmpeg"
inputs=["-i",SRC]; filters=[]; labels=[]; idx=1
for name,t,g in CUES:
    p=find(name)
    if not p: continue
    inputs+=["-i",p]
    extra=""
    if name=="bgm": extra=",afade=t=in:st=0:d=0.5,afade=t=out:st=17.4:d=0.6"
    filters.append(f"[{idx}:a]volume={g}dB,adelay={int(t*1000)}|{int(t*1000)}{extra}[a{idx}]"); labels.append(f"[a{idx}]"); idx+=1
if not labels: sys.exit("audio/ に音ファイルがありません")
mix="".join(labels)+f"amix=inputs={len(labels)}:normalize=0,atrim=0:{DUR},loudnorm=I=-16:TP=-1:LRA=9[aout]"
cmd=[ff,"-y","-loglevel","error"]+inputs+["-filter_complex",";".join(filters+[mix]),"-map","0:v","-map","[aout]","-c:v","copy","-c:a","aac","-b:a","256k","-shortest",DST]
print(" ".join(shlex.quote(c) for c in cmd)); subprocess.run(cmd,check=True); print("wrote",DST)
