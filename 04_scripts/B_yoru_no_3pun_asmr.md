# 案B「夜の3分 ASMR」— 制作パッケージ
### 型：ナイトルーティン手元ASMR　／　9:16　1080×1920　24fps（素材 60fps）　15.0秒　／　音が主役。音OFFでも質感で成立
規定：`01_brandbook/`　薬機：`02_research/compliance_yakkiho.md`　ボトル：`05_production/bottle_placement_workflow.md`

> **実物基準（2026-09-08）**：#2 の開始フレームは `01_bottle_bedroom_pink.jpg`（レンダー）ではなく、**実物を同構図で撮った静止画**を優先。レンダーはラベルの彩度が低く実物と差が出る。合成は `bottle_front_cutout_level.png`。

---

## 1. コンセプト
真っ暗な部屋で、ランプの「カチッ」だけが鳴る。ボトルが照らされ、ポンプの「しゅ」、クリームの「とろ」、手のなでる音。
人物の顔は出さない。**音と質感と灯りだけで、ChenMe の夜を"体験"させる**。K-beauty で最も強い"手元ASMR"の文法をそのまま使う。
締め：`Stay tuned`。

## 2. 秒単位台本
| # | IN–OUT | 尺 | 映像 | 音 | テロップ | 備考 |
|---|---|---|---|---|---|---|
| 1 | 0.0–0.8 | 0.8 | **黒**。かすかに部屋の輪郭。手がランプに伸びる | 無音 → 衣擦れ | なし | 完全な黒ではなく Charcoal 5%。SNS で「壊れた？」と思われない程度 |
| 2 | 0.8–2.4 | 1.6 | **ランプ点灯「カチッ」**。サイドテーブルの**ボトル**が暖色に浮かぶ。ハーブティーのカップ、小さなキャンドル（`01_bottle_bedroom_pink` の構図を踏襲） | SE：カチッ（大きめ、−6dB） | なし | **ボトル初出 0.8秒**。この案だけ早出し（質感型のため） |
| 3 | 2.4–4.6 | 2.2 | **ポンプを押す手元**、60fps→24 スロー 40%。クリームが手のひらに「とろ」と乗る | SE：ポンプ「しゅ」→「とろ」。BGM IN（極小 −26dB） | 「夜の3分。」（Zen Maru Gothic 84px） | テロップは 3.0 秒 IN、1.4 秒表示 |
| 4 | 4.6–6.4 | 1.8 | **手のひらでクリームを合わせる**マクロ。指の間に伸びる | SE：手と手の「くちゅ」（小さく） | 「うるおうのに、べたつかない。」（Noto Sans JP 52px） | 白さが飛ばないよう −0.3EV。**2026-09-08 追加**（事実確認済みの質感） |
| 5 | 6.4–9.6 | 3.2 | **ふくらはぎ**、膝→足首→膝。両手で包み、親指でゆっくり。60fps→24 スロー 60% | SE：肌をなでる音。BGM −22dB | 「ホワイトシトロンの香り。」（Noto Sans JP 52px、7.2 秒 IN） | 1 往復。手の動きは"円"を描く。**強く押さない**。**2026-09-08 追加**（香りは事実） |
| 6 | 9.6–11.4 | 1.8 | **足首→足の甲**、指先まで。最後に手を離す | SE 続く | 「今日より明日。」（Zen Maru Gothic 84px） | 10.0 秒 IN。ラベルのサブコピーと同じ言葉 |
| 7 | 11.4–12.8 | 1.4 | **ハーブティーを持ち上げる手**。湯気。背景にボトル（ボケ） | SE：カップの「コッ」 | なし | ボトルはボケでも**形は正しく**。合成なら実写プレート |
| 8 | 12.8–13.8 | 1.0 | **ランプを消す手**。「カチッ」で暗転 | SE：カチッ。BGM −30dB | なし | 暗転後も 0.2 秒は輪郭を残す |
| 9 | 13.8–15.0 | 1.2 | **暗い画面に英語1行**。下に小さくボトルのシルエット（実写の暗部を残す） | 無音に近い。最後にピアノ 1 音 | **Stay tuned**（Cormorant Garamond Medium 92px, Milk White `#FFF8F6`, 字間+8%） | 暗い背景なので白系。Rose は使わない |

テロップ 5 枚（日本語 4、英語 1）。質感・香りの 2 枚は `B_v01_pure`（テロップ 3 枚版）とのA/Bで効果を測る。

## 3. 絵コンテ（構図）
※ 図版：`storyboards/B_storyboard.svg`
| # | 構図 | ライト | レンズ |
|---|---|---|---|
| 1 | 画面右上にランプの輪郭、下 1/3 に手のシルエット | 環境光のみ −3EV | 35mm F2 |
| 2 | **`01_bottle_bedroom_pink.jpg` を再現**：ボトル中央やや左、後ろにランプ、左に小さなキャンドルとフォトフレーム、右にピンクのクッション。ラベル正面 | ランプ 3200K、キャンドル | 50mm F2 |
| 3 | ポンプ頭部が画面上 1/3、手のひらが下 2/3。クリームの落下が中央 | ランプ横から、白い面でバウンス | 85mm マクロ F2.8 |
| 4 | 両手のひらが画面いっぱい。背景は Blush の布 | 同上 | 85mm F2.8 |
| 5 | ふくらはぎが対角線。手は下から上へ。背景に丸ボケ | ランプ＋弱いリム | 50mm F2 |
| 6 | 足首〜甲、指先。シーツの上 | 同上 | 50mm F2 |
| 7 | カップが中央、湯気が上へ。右奥にボトルのボケ | ランプ逆光で湯気を出す | 85mm F2 |
| 8 | #2 と同構図、手がランプへ | 点灯→消灯 | 50mm F2 |
| 9 | 黒に近い画面、中央に英語、下 1/4 にボトルの影 | なし | — |

## 4. カメラワーク
- **三脚固定が基本**。#5・#6 だけ手持ちの微揺れを許可（"人がいる"感）。
- **速度**：#3 40%、#5 60%、#4 は 100%。他は実速。スローは 60fps 素材から。
- 動き：push-in は使わない（ASMR は静止の方が"音"に集中できる）。
- **禁止**：ボトルを持ち上げる、回す、ラベルを手で隠す。ポンプは置いたまま押す。

## 5. 出演者（**AI**：`05_production/ai_talent_and_set.md`。手のカットは実写）
- **顔を出さない**。手・脚・足のみ。20 代前半に見える手（ネイル：ミルキーピンク、短め）。
- 服：サテンのキャミワンピ（KV と同じピンク系）。脚はルームウェアのショートパンツでも可。
- 手の動き：**「触れる」より「包む」**。指を立てない。爪でひっかかない。

## 6. BGM／SE
| 要素 | 指定 |
|---|---|
| BGM | ほぼ聞こえないピアノのパッド。BPM 70、ルート音のみが 4 秒に 1 回。−26 → −22 → −30dB。「BGMがある」と気づかれない程度 |
| SE（すべて実録） | カチッ（ランプ）×2、衣擦れ、ポンプ「しゅ」、クリーム「とろ」、手のひら「くちゅ」、肌をなでる音、カップ「コッ」、湯気は無音。**録音**：ラベリアかショットガンを 15cm、ローカット 80Hz、ノイズは −60dB 以下の部屋で |
| ミックス | SE −10〜−6dB（ASMR 主役）。統合 −16 LUFS。**ピークは −1dBTP を厳守**（カチッが割れやすい） |

## 7. 動画生成AI用プロンプト
> 方針：**この案はボトル露出が多い（#2・#7・#8・#9）ため、基本は実写を推奨**。実写できない場合、#2・#8 のプレートは「白い無地の直方体ボトルのプレースホルダー」で生成し、正式画像を合成。#3〜#6 の手元は AI 生成可（ボトルのポンプ頭部が映る #3 は**実写必須**：ポンプ形状を AI が崩す）。
> 共通ロック：`single warm bedside lamp 3200K, near-dark room, soft shadows, shallow depth of field, macro realism, natural skin texture, pastel pink bedding and milk white surfaces, vertical 9:16, 24fps, ASMR-style stillness`
> 共通ネガティブ：`no text, no logo, no labeled product, no face, no fluorescent light, no blue tint, no glossy CGI skin, no extra fingers, no fast motion`

| # | ツール | プロンプト |
|---|---|---|
| 1 | Veo 3.1（ネイティブ音声はOFF、SEは実録） | `Near-black bedroom at night, faint outline of a bedside lamp on the right, a young woman's hand slowly reaches toward the lamp switch, subtle fabric rustle, extremely low light, 1 second, static camera` + ロック |
| 2（プレート） | Kling 3.0 image-to-video（開始フレーム：正式画像 `01_bottle_bedroom_pink.jpg` を**そのまま**。カメラ動きのみ） | `The bedside lamp switches on, the scene brightens smoothly from dark to warm lamp light within 0.5 seconds, everything else stays perfectly still, no object moves, no camera movement, 1.6 seconds` + ロック。**生成後、ボトル領域をフレーム差分で検証**（`05_production` §4）。歪みがあれば実写に切替 |
| 4 | Runway Gen-4（手のリファレンス 2 枚） | `Macro shot of two palms gently pressing together and spreading a pearl-white cream between the fingers, slow, warm lamp light from the side, pastel pink cloth background, 1.8 seconds` + ロック |
| 5 | Runway Gen-4 | `Close-up of a young woman's hands slowly wrapping around her calf and gliding from knee to ankle in one unhurried stroke, thumbs drawing gentle circles, sitting on pastel pink bedding at night, warm lamp bokeh behind, 3 seconds, 60fps-like smoothness` + ロック |
| 6 | Runway Gen-4 | `Hands gliding from the ankle over the top of the foot to the toes and gently lifting away, pastel pink sheets, warm low light, 1.8 seconds` + ロック |
| 7（背景のみ） | Kling 3.0 | `A hand lifts a clear glass cup of herbal tea from a white side table, thin steam rises in warm backlight, background is a soft blur of a pink bedroom, 1.4 seconds` + ロック + `no bottle in frame`（ボトルは実写プレートで奥に合成、またはボケ用に正式画像をガウス 12px で合成） |

## 8. Premiere 編集指示
1. シーケンス `B_yoru3_v01`：1080×1920、24fps、48kHz。
2. **素材**：60fps 撮影クリップは「クリップを解釈」で 24fps にせず、**速度/デュレーション**で 40%／60% に（音は別トラックのため映像のみ）。補間：オプティカルフロー。
3. トラック：V1 実写／V2 AIプレート／V3 合成ボトル／V4 テロップ／V5 ガイド。A1 SE／A2 BGM。
4. **#1→#2 の点灯**：「露光」を調整レイヤーでキーフレーム。−3EV → 0EV を 12 フレーム。実写で撮れていればそのまま。
5. **#8→#9 の消灯**：同様に 0 → −3EV を 8 フレーム。完全黒にしない（不透明度 92% の黒ソリッドを上に置き、ボトルの影を 8% 残す）。
6. テロップ：Zen Maru Gothic Medium 84px、Charcoal、Y=1150。IN 8 フレームフェード＋Y +8px。英語：Cormorant Garamond Medium 92px、Milk White、Y=980、IN 12 フレーム。
7. Lumetri：ブランド規定値。**#3・#4 のみ「白」を −8**（クリームの白飛び防止）。
8. 音：SE を最初に置き、波形のピークを −6dB に正規化。カチッは**リミッター**（−1dBTP）を必ず。BGM は −26 → −22（6.4秒）→ −30（12.8秒）。エッセンシャルサウンド「SFX」に割り当て。
9. **音OFF検証**：ミュートで 1 回通し、質感とテロップだけで意味が通るか確認。通らなければ #3 のテロップ表示を 0.4 秒延長。
10. 書き出し：H.264 12Mbps VBR 2 パス、AAC 320kbps。`B_yoru3_v01_TT.mp4`。サムネ：2.4 秒フレーム。
11. バリエーション：`B_v01_comingback`（英語差替）、`B_v01_30s`（#5・#6 を 2 往復、#3 の前に「靴を脱ぐ」1 カット追加）。

## 9. 薬機・規定チェック
- 効能語：なし（「夜の3分」「今日より明日」）✅
- 「ほぐす」系の効果表現：なし（動作のみ）✅
- ボトル：置き＋ポンプ押し。#2 の AI 点灯は**検証必須**、NG なら実写 ✅
- 質感表現（ひんやり等）：未使用 ✅
- 購入CTA：なし ✅
