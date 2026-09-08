# -*- coding: utf-8 -*-
"""
Vertex AI Veo 3.1 (fast) で image-to-video を生成する。
  export GOOGLE_OAUTH_TOKEN=ya29...  GOOGLE_CLOUD_PROJECT=gen-lang-client-xxxx
  python3 05_production/veo_gen.py submit <shot_id> <image_path> "<prompt>" [seconds=4]
  python3 05_production/veo_gen.py poll                 # 未完了の全オペレーションを確認し、完了分を mp4 保存
出力: 05_production/generated_video/<shot_id>.mp4 、状態は generated_video/ops.json
ルール: ボトルは生成させない（合成）。9:16、音なし、4〜8秒、1ショット1動作。
"""
import os, sys, json, base64, time, urllib.request
T=os.environ["GOOGLE_OAUTH_TOKEN"]; P=os.environ["GOOGLE_CLOUD_PROJECT"]
LOC="us-central1"; MODEL=os.environ.get("VEO_MODEL","veo-3.1-fast-generate-001")
OUT="05_production/generated_video"; os.makedirs(OUT,exist_ok=True); OPS=f"{OUT}/ops.json"
BASE=f"https://{LOC}-aiplatform.googleapis.com/v1/projects/{P}/locations/{LOC}/publishers/google/models/{MODEL}"
def req(url,body):
    r=urllib.request.Request(url,data=json.dumps(body).encode(),headers={"Authorization":f"Bearer {T}","Content-Type":"application/json"})
    with urllib.request.urlopen(r,timeout=120) as f: return json.load(f)
def load(): return json.load(open(OPS)) if os.path.exists(OPS) else {}
def save(d): json.dump(d,open(OPS,"w"),ensure_ascii=False,indent=1)
def submit(shot,img,prompt,sec=4):
    mime="image/png" if img.lower().endswith(".png") else "image/jpeg"
    body={"instances":[{"prompt":prompt,"image":{"bytesBase64Encoded":base64.b64encode(open(img,"rb").read()).decode(),"mimeType":mime}}],
          "parameters":{"aspectRatio":"9:16","durationSeconds":int(sec),"sampleCount":1,"generateAudio":False,"personGeneration":"allow_adult","resolution":"720p"}}
    j=req(BASE+":predictLongRunning",body); d=load(); d[shot]={"op":j["name"],"image":img,"prompt":prompt,"sec":sec,"done":False}; save(d); print("submitted",shot,j["name"].split("/")[-1])
def poll():
    d=load(); pending=[k for k,v in d.items() if not v.get("done")]
    for k in pending:
        j=req(BASE+":fetchPredictOperation",{"operationName":d[k]["op"]})
        if not j.get("done"): print("running",k); continue
        if "error" in j: d[k]["done"]=True; d[k]["error"]=j["error"]; print("ERROR",k,str(j["error"])[:200]); continue
        vids=j.get("response",{}).get("videos",[])
        if not vids: d[k]["done"]=True; d[k]["error"]=str(j.get("response"))[:300]; print("no video",k,d[k]["error"]); continue
        v=vids[0]; path=f"{OUT}/{k}.mp4"
        if "bytesBase64Encoded" in v: open(path,"wb").write(base64.b64decode(v["bytesBase64Encoded"]))
        else: d[k]["gcs"]=v.get("gcsUri")
        d[k]["done"]=True; d[k]["file"]=path; print("saved",path)
    save(d); return [k for k,v in d.items() if not v.get("done")]
if __name__=="__main__":
    if sys.argv[1]=="submit": submit(sys.argv[2],sys.argv[3],sys.argv[4],int(sys.argv[5]) if len(sys.argv)>5 else 4)
    else:
        while True:
            left=poll()
            if not left or "--once" in sys.argv: break
            time.sleep(20)
