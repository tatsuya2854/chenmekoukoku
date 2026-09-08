# -*- coding: utf-8 -*-
"""
R1〜R4（AI出演者）・S1〜S4（セット）の候補を Gemini 画像モデルで生成し、コンタクトシートを作る。
使い方:
  export GEMINI_API_KEY=...   # Google AI Studio で発行（https://aistudio.google.com/apikey）
  # または Vertex AI 経由（AI Studio の前払い残高に依存しない。プロジェクトの請求先に後払い）:
  export GOOGLE_OAUTH_TOKEN=ya29...  GOOGLE_CLOUD_PROJECT=gen-lang-client-xxxx
  python3 05_production/generate_refs.py            # 全部（各4候補）
  python3 05_production/generate_refs.py R1 S2      # 指定だけ
  python3 05_production/generate_refs.py --adopt R1=2 S2=1   # 候補番号を採用して assets/ にコピー
出力: 05_production/generated/{ID}_{n}.png と {ID}_sheet.jpg
人物の一貫性: R2/R3/R4 は採用済み R1（assets/ai_talent/R1.png）があればそれを参照画像として渡す。
"""
import os, sys, json, base64, time, urllib.request, glob, shutil
from PIL import Image, ImageDraw

MODEL = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")
KEY = os.environ.get("GEMINI_API_KEY")
OAUTH = os.environ.get("GOOGLE_OAUTH_TOKEN")          # Vertex AI 経由（OAuth アクセストークン、cloud-platform スコープ）
PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT")      # Vertex 使用時のプロジェクト ID
OUT = "05_production/generated"; os.makedirs(OUT, exist_ok=True)
N = int(os.environ.get("N_CANDIDATES", "4"))

LOCK_P = ("photorealistic, 85mm portrait lens, natural skin texture with visible pores, no beauty filter, "
          "soft warm tungsten light 3200K, shallow depth of field, pastel pink and milk white palette, "
          "editorial Korean beauty campaign look, vertical 4:5 composition. "
          "Do not include any text, logo, watermark, product bottle or brand packaging. No heavy makeup, no revealing pose, "
          "the woman must clearly look like an adult in her mid twenties.")
LOCK_S = ("photorealistic interior, small Japanese apartment, night, single warm bedside lamp 3200K, soft shadows, "
          "pastel pink bedding and milk white walls, shallow depth of field, cinematic still, vertical 9:16 composition, "
          "no people, no text, no logos, no branded products.")

PROMPTS = {
 "R1": ("Portrait of a Japanese woman in her mid twenties, dark brown medium-long hair worn down, gentle relaxed expression "
        "with a small closed-mouth smile, no-makeup makeup with pink-beige lips, sitting on the edge of a bed in a small pink "
        "bedroom at night, looking slightly off camera. " + LOCK_P),
 "R2": ("The same woman as in the reference image, three-quarter profile turned 45 degrees, eyes closed as if exhaling after a "
        "long day, warm bedside lamp bokeh behind her. Keep her face, hair and skin identical to the reference. " + LOCK_P),
 "R3": ("The same woman as in the reference image, full body, sitting on the bed edge with bare feet on a wooden floor, white "
        "blouse and greige skirt, beige strappy heels placed beside her on the floor, small cozy Japanese apartment bedroom. "
        "Keep her face and hair identical to the reference. " + LOCK_P),
 "R4": ("Close-up of the same woman's hands with short milky-pink nails resting on pastel pink bedding, natural skin, warm lamp "
        "light, exactly five fingers on each hand. " + LOCK_P),
 "S1": ("Dim entryway of a small Japanese apartment at night, wooden floor, a sliver of warm light spilling from a door on the "
        "left, a pair of beige strappy heels on the floor, mostly in shadow, quiet and intimate. " + LOCK_S),
 "S2": ("Cozy bedroom corner, bed with pastel pink sheets and a soft pink knit blanket, white wooden side table with a small warm "
        "lamp, a small candle in a glass, a framed photo, a clear glass cup of herbal tea, the lamp is the only light source. "
        "On the side table stands a plain matte white rounded-rectangle pump bottle without any label, about 2.3 times taller "
        "than wide, slightly smaller than a typical hand-soap bottle, as a placeholder. " + LOCK_S),
 "S3": ("Small white three-tier shelf in a pastel pink bedroom, soft window daylight mixed with warm lamp light, unlabeled frosted "
        "glass jars, a small vase of baby's breath, a folded pink towel, a few books, one clearly empty spot at the center of the "
        "middle shelf. " + LOCK_S),
 "S4": ("The same bedroom corner as the reference image but with the lamp switched off, near-black, only a faint outline of the "
        "lamp and the placeholder bottle silhouette visible. " + LOCK_S),
}
for _k in ("S1","S2","S3","S4"):
    PROMPTS[_k+"V"] = ("Recreate exactly the same scene as the reference image, same room, same furniture, same objects, same lighting and colors, "
                       "but reframed as a vertical 9:16 composition with more ceiling/wall above and floor below, nothing added or removed. " + LOCK_S)
REF_FOR = {"S1V": "assets/ai_sets/S1.png", "S2V": "assets/ai_sets/S2.png", "S3V": "assets/ai_sets/S3.png", "S4V": "assets/ai_sets/S4.png",
"R2": "assets/ai_talent/R1.png", "R3": "assets/ai_talent/R1.png", "R4": "assets/ai_talent/R1.png", "S4": "assets/ai_sets/S2.png"}
ADOPT_DIR = {"R": "assets/ai_talent", "S": "assets/ai_sets"}

ASPECT = {"R": "4:5", "S": "9:16"}

def call(prompt, ref=None, pid="S"):
    parts = [{"text": prompt}]
    if ref and os.path.exists(ref):
        with open(ref, "rb") as f:
            parts.insert(0, {"inline_data": {"mime_type": "image/png", "data": base64.b64encode(f.read()).decode()}})
    if OAUTH and PROJECT:
        body = {"contents": [{"role": "user", "parts": parts}], "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": ASPECT[pid[0]]}}}
        url = f"https://aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/global/publishers/google/models/{MODEL}:generateContent"
        headers = {"Authorization": f"Bearer {OAUTH}", "Content-Type": "application/json"}
    else:
        body = {"contents": [{"parts": parts}], "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": ASPECT[pid[0]]}}}
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
        headers = {"x-goog-api-key": KEY, "Content-Type": "application/json"}
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers)
    with urllib.request.urlopen(req, timeout=180) as r:
        j = json.load(r)
    for c in j.get("candidates", []):
        for p in c.get("content", {}).get("parts", []):
            if "inlineData" in p:
                return base64.b64decode(p["inlineData"]["data"])
    raise RuntimeError("no image in response: " + json.dumps(j)[:400])

def sheet(pid):
    files = sorted(glob.glob(f"{OUT}/{pid}_[0-9].png"))
    if not files: return
    ims = [Image.open(f).convert("RGB") for f in files]
    h = 720; ims = [im.resize((int(im.width * h / im.height), h)) for im in ims]
    W = sum(im.width for im in ims) + 20 * (len(ims) + 1)
    sh = Image.new("RGB", (W, h + 60), (255, 248, 246)); d = ImageDraw.Draw(sh); x = 20
    for i, im in enumerate(ims, 1):
        sh.paste(im, (x, 40)); d.text((x, 12), f"{pid} #{i}", fill=(106, 102, 100)); x += im.width + 20
    sh.save(f"{OUT}/{pid}_sheet.jpg", quality=88); print("sheet", f"{OUT}/{pid}_sheet.jpg")

def generate(ids):
    if not KEY and not (OAUTH and PROJECT): sys.exit("GEMINI_API_KEY か、GOOGLE_OAUTH_TOKEN + GOOGLE_CLOUD_PROJECT を設定して実行。")
    for pid in ids:
        ref = REF_FOR.get(pid)
        if ref and not os.path.exists(ref): print(f"[{pid}] 参照 {ref} が未採用。先に採用するか、参照なしで生成する"); 
        for n in range(1, N + 1):
            path = f"{OUT}/{pid}_{n}.png"
            if os.path.exists(path): continue
            for attempt in range(3):
                try:
                    png = call(PROMPTS[pid], ref, pid); open(path, "wb").write(png); print("ok", path); break
                except Exception as e:
                    print("retry", pid, n, attempt, str(e)[:160]); time.sleep(3 * (attempt + 1))
        sheet(pid)

def adopt(pairs):
    for pr in pairs:
        pid, n = pr.split("="); src = f"{OUT}/{pid}_{n}.png"; dst_dir = ADOPT_DIR[pid[0]]
        os.makedirs(dst_dir, exist_ok=True); shutil.copy(src, f"{dst_dir}/{pid}.png"); print("adopted", src, "->", f"{dst_dir}/{pid}.png")

if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--adopt": adopt(args[1:])
    else: generate(args or list(PROMPTS))
