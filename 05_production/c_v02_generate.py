# -*- coding: utf-8 -*-
"""
C v02：無地の白ボトルで動く 4 クリップを Veo で生成（開始フレーム＝AI の手＋無地ボトルの静止画）。
最後の Coming back soon だけ実物ラベル（切り抜き）を合成する → ラベルは一切改変しない。
  export GOOGLE_OAUTH_TOKEN=ya29... GOOGLE_CLOUD_PROJECT=gen-lang-client-0924303510
  python3 05_production/c_v02_generate.py          # 投入→ポーリング→保存
"""
import subprocess, os, sys, time
LOCK=("Photorealistic, warm bedside lamp light 3200K, soft shadows, shallow depth of field, natural skin texture, 24fps cinematic, vertical 9:16. "
      "The bottle is a plain matte white rounded-rectangle pump bottle with a completely blank front, NO label, NO text, NO logo; keep the bottle exactly as in the first frame. "
      "Camera completely static. Slow, calm, one single gentle motion. No new objects, no people entering.")
SHOTS=[
 ("C1_hold_tilt",  "05_production/generated_hands/C1_hold_front_2.png",
  "The two hands holding the blank white pump bottle tilt it very slightly toward the camera by about 5 degrees and back, as if gently showing it, fingers stay on the sides. ",4),
 ("C3_pump_press", "05_production/generated_hands/B3_pump_press_2.png",
  "The index finger slowly presses the pump head down once; a small pearl-white dollop of cream comes out onto the cupped palm below, then the finger lifts. ",4),
 ("C4_place",      "05_production/generated_hands/C4_place_table_1.png",
  "The hand gently sets the blank white pump bottle down on the white side table and slowly withdraws out of frame to the right, the bottle stays upright. ",4),
 ("C5_shelf_place","assets/ai_sets/S3V.png",
  "A young woman's hand with short milky-pink nails enters from the right holding a plain matte white rounded-rectangle pump bottle with a blank front, places it upright in the empty center spot of the upper shelf compartment between the two jars, and slowly withdraws out of frame. The bottle stays perfectly still after being placed. ",6),
]
env=dict(os.environ)
for sid,img,prompt,sec in SHOTS:
    subprocess.run([sys.executable,"05_production/veo_gen.py","submit",sid,img,prompt+LOCK,str(sec)],check=True,env=env)
    time.sleep(3)
subprocess.run([sys.executable,"05_production/veo_gen.py","poll"],check=True,env=env)
