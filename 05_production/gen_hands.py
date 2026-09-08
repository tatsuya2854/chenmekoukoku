# -*- coding: utf-8 -*-
"""手＋プレースホルダーボトルの静止画を Gemini 画像モデル(Vertex)で生成。R4(手)を参照。9:16。
   その後 composite_hands.py でプレースホルダーを実物切り抜きで覆う。"""
import os, sys, json, base64, urllib.request, time
T=os.environ["GOOGLE_OAUTH_TOKEN"]; P=os.environ["GOOGLE_CLOUD_PROJECT"]; MODEL="gemini-2.5-flash-image"
OUT="05_production/generated_hands"; os.makedirs(OUT,exist_ok=True)
LOCK=("Photorealistic, 85mm macro lens, warm bedside lamp light 3200K, soft shadows, shallow depth of field, natural skin texture, "
      "pastel pink bedding and milk white surfaces, vertical 9:16. The bottle is a plain matte white rounded-rectangle pump bottle with a white pump head, "
      "about 2.3 times taller than wide, with a completely blank white front and NO label, NO text, NO logo. "
      "Hands hold it only from the sides and bottom so the entire front face of the bottle is fully visible and unobstructed. "
      "Exactly five fingers per hand, short milky-pink nails like the reference hands.")
SHOTS={
 "C1_hold_front": "A young woman's two hands gently hold the blank white pump bottle upright at chest height in front of pastel pink bedding, "
                  "fingers wrapped around the lower sides, thumbs at the sides, bottle facing the camera straight on, centered. ",
 "C4_place_table": "A young woman's right hand places the blank white pump bottle onto a white wooden side table next to a small warm lamp, "
                   "fingers releasing from the sides, bottle upright and facing camera, pink bedroom background. ",
 "B3_pump_press": "Close-up: a young woman's index finger rests on top of the pump head of the blank white pump bottle standing on a white side table, "
                  "other hand cupped below the nozzle waiting for cream, bottle front fully visible, warm lamp light. ",
 "B4_cream_palms": "Extreme close-up of two palms held together with a small pearl-white dollop of cream spreading between the fingers, "
                   "no bottle in frame, pastel pink cloth background, warm lamp light. ",
 "B7_tea_bottle_bg": "A young woman's hand lifts a clear glass cup of herbal tea from a white side table, thin steam, "
                     "in the background the blank white pump bottle stands upright slightly out of focus, warm lamp glow. ",
}
def call(prompt, refs):
    parts=[]
    for r in refs:
        parts.append({"inline_data":{"mime_type":"image/png","data":base64.b64encode(open(r,"rb").read()).decode()}})
    parts.append({"text":prompt})
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
    for k in range(1,n+1):
        path=f"{OUT}/{sid}_{k}.png"
        if os.path.exists(path): continue
        for a in range(4):
            try:
                open(path,"wb").write(call("Use the reference image for the hands' skin tone and nails. "+SHOTS[sid]+LOCK,["assets/ai_talent/R4.png"])); print("ok",path); break
            except Exception as e: print("retry",sid,k,str(e)[:120]); time.sleep(15*(a+1))
        time.sleep(8)
