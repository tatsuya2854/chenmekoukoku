# -*- coding: utf-8 -*-
"""C v03：パジャマの AI 出演者 × 無地ボトルの開始フレーム（9:16）を Gemini(Vertex) で生成。R1 を顔参照、必要に応じて S3V を部屋参照。"""
import os, sys, json, base64, urllib.request, time
T=os.environ["GOOGLE_OAUTH_TOKEN"]; P=os.environ["GOOGLE_CLOUD_PROJECT"]; MODEL="gemini-2.5-flash-image"
OUT="05_production/generated_c3"; os.makedirs(OUT,exist_ok=True)
LOCK=("Photorealistic, warm bedside lamp light 3200K, soft shadows, shallow depth of field, natural skin texture, pastel pink bedroom, vertical 9:16. "
      "Keep the woman's face, hair and pastel pink short-sleeve pajama set identical to the reference image (same person, early twenties). "
      "The bottle is a plain matte white RECTANGULAR pump bottle with rounded corners, flat blank front, white pump head, about 2.3 times taller than wide, NO label, NO text, NO logo. "
      "Exactly five fingers per hand, short milky-pink nails. No text or logos anywhere in the image.")
SHOTS={
 "P1_hold": ("Medium shot: the woman sits on the edge of her bed holding the plain white rectangular pump bottle with both hands at chest height, "
             "looking down at it with a soft, slightly apologetic smile, bottle front facing the camera. ", ["assets/ai_talent/R1.png"]),
 "P2_pump": ("Medium close-up from the front: the woman holds the plain white rectangular pump bottle in her left hand and rests her right index finger on the pump head, "
             "right palm cupped below the nozzle, looking down at her hands, sitting on the bed. ", ["assets/ai_talent/R1.png"]),
 "P4_shelf": ("Medium-wide shot: the woman stands beside a small white two-tier cube shelf in her pink bedroom, reaching out to place the plain white rectangular pump bottle "
              "on top of the shelf next to a small vase of baby's breath and two frosted jars, seen from the side, gentle smile, warm lamp light. Use the second reference image for the shelf and room. ",
              ["assets/ai_talent/R1.png","assets/ai_sets/S3V.png"]),
}
def call(prompt, refs):
    parts=[{"inline_data":{"mime_type":"image/png","data":base64.b64encode(open(r,"rb").read()).decode()}} for r in refs]+[{"text":prompt}]
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
            try: open(path,"wb").write(call("Use the first reference image for the woman's identity. "+prompt+LOCK,refs)); print("ok",path); break
            except Exception as e: print("retry",sid,k,str(e)[:100]); time.sleep(15*(a+1))
        time.sleep(10)
