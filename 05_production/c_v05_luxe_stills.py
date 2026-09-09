# -*- coding: utf-8 -*-
"""C v05（ラグジュアリー版）：新モデル × 無地ボトルの開始フレームを Gemini(Vertex) で生成。顔は L_face_primary に固定。"""
import os, sys, json, base64, urllib.request, time
T=os.environ["GOOGLE_OAUTH_TOKEN"]; P=os.environ["GOOGLE_CLOUD_PROJECT"]; MODEL="gemini-2.5-flash-image"
OUT="05_production/generated_c5"; os.makedirs(OUT,exist_ok=True)
FACE="assets/ai_talent/v3_luxe/L_face_primary.jpg"; LEG="assets/ai_talent/v3_luxe/L_pose_legcare.jpg"
LOCK=("Photorealistic, luxury hotel bedroom at night, warm golden lamp light, city lights bokeh through the window, marble side table with gold trim, "
      "shallow depth of field, natural skin texture, vertical 9:16. Keep the woman's face and long wavy dark-brown hair identical to the first reference image (same person, mid twenties). "
      "She wears a rose-pink satin slip dress like the second reference image. "
      "The bottle is a plain matte white RECTANGULAR pump bottle with rounded corners, flat blank front, white pump head, about 2.3 times taller than wide, NO label, NO text, NO logo. "
      "Exactly five fingers per hand, short nude-pink nails. No text or logos anywhere.")
SHOTS={
 "L1_hold":  ("Medium shot: she sits on the edge of the hotel bed holding the plain white rectangular pump bottle with both hands at chest height, "
              "looking down at it with a soft, slightly apologetic smile, bottle front facing the camera. ",[FACE,LEG]),
 "L2_pump":  ("Medium close-up from the front: she holds the plain white rectangular pump bottle in her left hand and rests her right index finger on the pump head, "
              "right palm cupped directly under the nozzle, looking down at her hands, sitting on the bed. ",[FACE,LEG]),
 "L3_leg":   ("Medium shot like the second reference image: she sits on the bed edge, leaning forward, both hands gently smoothing cream on her lower leg, eyes down, calm smile, "
              "bare feet on a soft carpet, no bottle in frame. ",[FACE,LEG]),
 "L4_table": ("Medium-wide shot: she stands beside the marble side table in the hotel bedroom, reaching out to place the plain white rectangular pump bottle on the table "
              "next to a small vase of pale pink roses and a candle, seen from the side, gentle smile, city lights in the window. ",[FACE,LEG]),
}
def call(prompt, refs):
    parts=[{"inline_data":{"mime_type":"image/jpeg","data":base64.b64encode(open(r,"rb").read()).decode()}} for r in refs]+[{"text":prompt}]
    body={"contents":[{"role":"user","parts":parts}],"generationConfig":{"responseModalities":["IMAGE"],"imageConfig":{"aspectRatio":"9:16"}}}
    req=urllib.request.Request(f"https://aiplatform.googleapis.com/v1/projects/{P}/locations/global/publishers/google/models/{MODEL}:generateContent",
        data=json.dumps(body).encode(),headers={"Authorization":f"Bearer {T}","Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=180) as f: j=json.load(f)
    for c in j.get("candidates",[]):
        for p in c.get("content",{}).get("parts",[]):
            if "inlineData" in p: return base64.b64decode(p["inlineData"]["data"])
    raise RuntimeError(json.dumps(j)[:300])
ids=sys.argv[1:] or list(SHOTS); n=int(os.environ.get("N",2))
for sid in ids:
    prompt,refs=SHOTS[sid]
    for k in range(1,n+1):
        path=f"{OUT}/{sid}_{k}.png"
        if os.path.exists(path): continue
        for a in range(4):
            try: open(path,"wb").write(call("Use the first reference image for the woman's face and hair. "+prompt+LOCK,refs)); print("ok",path); break
            except Exception as e: print("retry",sid,k,str(e)[:100]); time.sleep(15*(a+1))
        time.sleep(10)
