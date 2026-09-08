# AI 出演者＆セット制作ガイド（決定：人物・部屋は AI、手とボトルは実写）
最終更新：2026-09-08　　規定：`01_brandbook/`　ボトル：`bottle_placement_workflow.md`

---

## 0. 結論
| 要素 | 作り方 | 理由 |
|---|---|---|
| 出演者（顔・体・脚） | **AI**。1 人のキャラを 3 面リファレンスで固定し、全ショット同じ参照で生成 | 顔出しは A#7 の 2 秒だけ。脚・足元は AI で十分 |
| 部屋（玄関・ベッドルーム・棚） | **AI**。静止画で「セット」を先に確定 → image-to-video | 世界観を数値で固定できる。撮影場所を探す工数ゼロ |
| 手＋ボトル（ポンプ押し、握り、ラベルマクロ） | **実写**（iPhone、ランプ 1 灯、1 時間） | AI の手は崩れる。ボトルは改変ゼロ規定。この 2 つが同時に映るカットは実写が最速で最安 |
| 声（C の VO） | **中の人の実声**を推奨。無理なら AI 音声（ElevenLabs 等）＋ AI 開示 | 本物の声が一番安く一番信頼される |
| 音（SE） | 実録（ポンプ・とろ・カチッ） | AI 動画に音は付けない（Veo のネイティブ音声は OFF） |

> **静止画（R1〜R4・S1〜S4）は、この環境から Google Gemini の画像モデルで生成できる**（エンドポイント到達を確認済み）。必要なのは Gemini API キー 1 つ。`generate_refs.py` が各 4 候補を生成してコンタクトシートを作り、`--adopt` で採用画像を `assets/` に置く。動画は Runway Gen-4 References／Kling 3.0 Elements／Veo 3.1 で（こちらは各ツールの UI から）。
>
> ```bash
> export GEMINI_API_KEY=...            # https://aistudio.google.com/apikey
> python3 05_production/generate_refs.py R1 S1 S2 S3   # 参照不要のものから
> python3 05_production/generate_refs.py --adopt R1=2 S2=1  # シートを見て採用
> python3 05_production/generate_refs.py R2 R3 R4 S4   # 採用画像を参照して生成
> ```

---

## 0b. 進捗（2026-09-08 夜）
- **R1〜R4、S1〜S4 は生成・採用済み** → `assets/ai_talent/`、`assets/ai_sets/`。候補のコンタクトシートは `05_production/generated/*_sheet.jpg`。
- 生成経路：Google AI Studio の API キーは無料枠／前払い残高 0 で画像モデルが通らなかったため、**Vertex AI（OAuth トークン＋課金有効プロジェクト）**で生成。手順は `generate_refs.py` 冒頭。
- 実証：`samples/composite_S2_realbottle.jpg` ＝ AI セット S2 のプレースホルダーを実物ボトルの切り抜きで覆った合成。違和感なし。
- 学び：①参照画像付きの生成は 1 分あたりのレート制限に当たりやすい → **直列・20 秒間隔**で回す。②デフォルト出力は正方形 → `imageConfig.aspectRatio` で 9:16 / 4:5 を指定（スクリプト対応済み）。③プレースホルダーは「実物より少し小さめ」と書く。

## 0c. 動画生成（Veo 3.1 Fast／Vertex AI）— 2026-09-08 夜 実行結果
`veo_gen.py` で image-to-video。9:16、720p、24fps、音なし、4〜6 秒。1 本あたり約 1 分で上がる。

| クリップ | 開始フレーム | 結果 | 判定 |
|---|---|---|---|
| `A7_face_eyes_open` | R2（正方形） | 目を閉じ→息→開けて微笑む。顔同一 | ◎ 内容合格、**黒帯**（入力が正方形）→ R2V で v2 |
| `A6_calf_wrap` | R3（正方形） | 前傾して両手でふくらはぎを包む | ○ 同上 → R3V で v2 |
| `B2_lamp_static` | S2V | 静止、キャンドルのみ揺れる。**ボトル領域 SSIM 0.971** | ◎ 採用 |
| `A3_entry_walk` | S1V | 玄関からランプの部屋へ手持ちで進む。ヒールが下を通る | ◎ 採用 |
| `B8_lamp_off` | S2V | 2 秒後にランプが消え、キャンドルだけ残る | ○ 採用（暗部は Premiere でもう一段落とす） |
| `C5_shelf_slide`／`_v2` | S3V | スライド中に**手前の黒い柱が横切る**（2 回とも） | ❌ Veo でカメラ移動を頼まない。**Premiere で静止画を 3% パン** |
| `A8_pushin` | S2V | push-in の途中で**人影が通過**（禁止指示を無視） | ❌ `B2_lamp_static` に Premiere で 3% スケールを付けて代用 |

### 学び（Veo の癖）
1. **カメラを動かすと嘘をつく。** 空の部屋で「スライド」「push-in」を頼むと遮蔽物や人を足してくる。→ Veo では **camera completely static**、カメラワークは Premiere のスケール／位置キーフレームで。
2. **入力画像の比率がそのまま出る。** 正方形を入れると 9:16 に黒帯。→ 開始フレームは必ず 9:16（`generate_refs.py` の `*V` で作る）。
3. 人物の 1 動作（目を開ける、脚を包む）は非常に安定。表情の芝居は Veo が得意。
4. 光の変化（消灯）は成立する。点灯も同じ書き方で可。
5. 4 秒で十分。6 秒以上は崩れる余地が増える。

### 実写に残すもの（変わらず）
手＋ボトル（A#1・A#5、B#2 実物版・B#3・B#4・B#7、C#1〜#4）。Veo にボトルを出させない方針は維持。

## 0d. 現物ボトルなしで「手＋ボトル」を作る（2026-09-08 夜、実装済み）
実写予定だった 10 カットのうち、ボトルが映る 4 カット（C#1/2、B#3、C#4、B#7）と B#4 を **AI の手 × 実物切り抜き** で代替した。
1. `gen_hands.py`：手が**無地の白いプレースホルダー**を「側面と底だけで持つ」画を 9:16 で生成（R4 参照、正面を隠さない指示）。
2. `composite_hands.py`：プレースホルダー位置に実物切り抜きを均等スケールで重ねる（幅・高さの大きい方で完全に覆う）→ 肌マスク（YCrCb ＋ 彩度>45・明度<215）で指をラベルの前に戻す → 接地影。
3. 結果は `composites/`。ボトルは変形ゼロ、色相・彩度変更ゼロ、露出ゲインのみ。
学び：①肌マスクは「白いプレースホルダーを肌と誤判定」しやすい → 明度・彩度で締める。②プレースホルダーの自動検出は不安定 → グリッド画像で座標を読んで手指定。③ポンプ押し・クリームが出る瞬間など「ボトルが変形する動き」はこの方法では作れない → ポンプ音（SE）＋手のひらのクリーム（B#4）でカットを繋いで"押した"ことを伝える。

## 1. AI 出演者「ChenMe の子」キャラクターシート

### 1.1 仕様（ブランドブック §6.4 準拠）
| 項目 | 指定 |
|---|---|
| 見た目の年齢 | 23〜25 歳。10 代に見せない、30 代にも寄せない |
| 顔 | 日本人。柔らかい輪郭、目は大きすぎない、**KV のモデル（`03_keyvisual`）を"雰囲気の参考"に**。実在人物に似せない |
| 髪 | ダークブラウン、鎖骨下のミディアム〜ロング。A では下ろし、B ではゆるいお団子 |
| 肌 | ナチュラル。毛穴・産毛が少し残る。美肌フィルター感 NG |
| メイク | ノーメイク風メイク。ピンクベージュのリップ、チーク薄め |
| ネイル | ミルキーピンク、短め |
| 服（A） | 仕事帰り：白のブラウス＋グレージュのスカート。ヒール（5〜7cm、ストラップ、ベージュ） |
| 服（B） | サテンのキャミワンピ、KV と同じピンク系 |
| 服（C） | 手だけ実写のため不要 |
| 体型 | 指定しない。**脚の形を評価軸にしない**（映すのは動作と表情） |
| 表情の基本 | 目を閉じて「ふう」→ 開けて小さく笑う。口角は 2mm |

### 1.2 リファレンス画像を作る（3 面＋手）
静止画生成。**同一シードで 3 枚**を作り、以降すべての動画生成にこの 3 枚を参照させる。

共通ロック文字列（全プロンプト末尾に付ける）：
```
photorealistic, 85mm portrait lens, natural skin texture with visible pores, no beauty filter, soft warm tungsten light 3200K, shallow depth of field, pastel pink and milk white palette, editorial Korean beauty campaign look, vertical 4:5
```
共通ネガティブ：
```
--no text, logo, watermark, extra fingers, deformed hands, plastic skin, oversaturated, blue tint, fluorescent light, heavy makeup, revealing pose, child-like features
```

| # | 用途 | プロンプト |
|---|---|---|
| R1 | 顔・正面 | `Portrait of a Japanese woman in her mid twenties, dark brown medium-long hair worn down, gentle relaxed expression with a small closed-mouth smile, no-makeup makeup with pink-beige lips, sitting on the edge of a bed in a small pink bedroom at night, looking slightly off camera` ＋ロック |
| R2 | 顔・横 45° | `Same woman as reference, three-quarter profile turned 45 degrees, eyes closed as if exhaling after a long day, warm bedside lamp bokeh behind her` ＋ロック（R1 を画像参照 `--cref` / Character Reference に指定） |
| R3 | 全身 | `Same woman as reference, full body, sitting on the bed edge with bare feet on a wooden floor, white blouse and greige skirt, beige strappy heels placed beside her on the floor, small cozy Japanese apartment bedroom` ＋ロック |
| R4 | 手（参考用） | `Close-up of a Japanese woman's hands with short milky-pink nails resting on pastel pink bedding, natural skin, warm lamp light` ＋ロック（手は実写にするが、AI ショットの手の質感合わせ用） |

**採用基準**：①3 枚で同一人物に見える ②実在の有名人に似ていない（逆画像検索で確認） ③指が 5 本 ④肌に質感がある。**4 セット生成して 1 セット選ぶ**（打数）。採用したら `assets/ai_talent/R1〜R4.png` に保存し、README に「AI 生成・実在しない人物」と明記。

---

## 2. セット・バイブル（部屋は先に"静止画"で確定する）

各セットの静止画を 1 枚ずつ確定し、**同じ画像を開始フレーム**にして動画化する。これで A/B/C の部屋が同じ部屋になる。

共通ロック（セット用）：
```
photorealistic interior, small Japanese apartment, night, single warm bedside lamp 3200K, soft shadows, pastel pink bedding and milk white walls, shallow depth of field, 24fps cinematic still, vertical 9:16, no people, no text, no branded products
```

| セット | 使うショット | プロンプト |
|---|---|---|
| S1 玄関（暗） | A#1・A#2・A#3 冒頭 | `Dim entryway of a small Japanese apartment at night, wooden floor, a sliver of warm light spilling from a door on the left, a pair of beige strappy heels on the floor, mostly in shadow, quiet and intimate` ＋ロック |
| S2 ベッドルーム（ランプ） | A#3〜#9、B#1〜#9 | `Cozy bedroom corner, bed with pastel pink sheets and a soft pink knit blanket, white wooden side table with a small warm lamp, a small candle in a glass, a framed photo, a clear glass cup of herbal tea, the lamp is the only light source` ＋ロック。**サイドテーブルの上に「a plain matte white rounded-rectangle pump bottle without any label, about 2.3 times taller than wide」を置く**（合成用プレースホルダー） |
| S3 棚（明るめ） | C#5・C#6 | `Small white three-tier shelf in a pastel pink bedroom, soft window daylight mixed with warm lamp, unlabeled frosted glass jars, a small vase of baby's breath, a folded pink towel, a few books, one clearly empty spot at the center of the middle shelf` ＋ロック |
| S4 ベッドルーム（消灯） | B#1・B#8・B#9 | S2 と同じ構図で `lamp switched off, near-black, faint outline of the lamp and the bottle silhouette only` |

**採用基準**：①S2 と S4 が同じ部屋に見える ②ラベル付き製品・文字が映っていない ③壁が青白くない ④プレースホルダーのボトルが直立している。各 4 枚生成 → 1 枚採用 → `assets/ai_sets/S1〜S4.png`。

---

## 3. ショット別：何を AI で作り、何を実写するか

| 案#ショット | 内容 | 方式 | 生成ツール／参照 |
|---|---|---|---|
| A#1 | ストラップを外す手元 POV | **実写**（手＋ヒール。床は暗いので自宅で可） | — |
| A#2 | 素足が床に | AI | Kling 3.0 i2v、開始フレーム S1 ＋ R3 の足元 |
| A#3 | 歩いてランプを点ける | AI | Runway Gen-4 References（R1〜R3）＋ S1→S2 |
| A#4 | 座る、膝下＋ボトル | AI（人物・部屋）＋ **合成ボトル** | Runway、S2 開始。ボトルは `bottle_front_cutout_level.png` |
| A#5 | ポンプを押す手元マクロ | **実写** | — |
| A#6 | ふくらはぎを包む | AI | Runway References（R3・R4） |
| A#7 | 顔（目を閉じ→笑う） | AI | Runway References（R1・R2）、S2 |
| A#8–9 | ボトル静止＋英語 | AI 背景（S2）＋ **合成ボトル** | Kling i2v（光のゆらぎのみ） |
| B#1・#8・#9 | 暗転／点灯／消灯 | AI 背景（S4↔S2）＋ **合成ボトル** | Kling i2v、SSIM 検証必須 |
| B#2 | 点灯後のボトル | **実写推奨**（実物を同構図で） or AI 背景＋合成 | — |
| B#3 | ポンプ→とろ | **実写** | — |
| B#4 | 手のひらのクリーム | **実写**（手なので） | — |
| B#5・#6 | ふくらはぎ／足首→甲 | AI | Runway References（R3・R4） |
| B#7 | ハーブティーを持つ手＋奥にボトル | **実写**（手）。無理なら AI 手＋合成ボトル（ボケ） | — |
| C#1・#2 | ボトルを両手で持つ | **実写** | — |
| C#3 | ラベルマクロ | **実写** | — |
| C#4 | 置く | **実写** | — |
| C#5 | 棚パン | AI | Kling i2v、S3 開始、スライドのみ |
| C#6〜#8 | 棚にボトル | AI 背景（S3 最終フレーム）＋ **合成ボトル** | — |

**実写リスト（1 時間で撮る）**：A#1、A#5、B#2、B#3、B#4、B#7、C#1〜#4。必要なもの：実物ボトル、ランプ 1 灯、ピンクのシーツか布、白いサイドテーブル（白い箱でも可）、ハーブティーのカップ、ヒール、iPhone（4K 24fps／スロー用 60fps）、誰かの手。

---

## 4. 動画生成の共通ルール
1. **必ず image-to-video**。text-to-video は使わない（部屋も人も変わる）。
2. **1 ショット 4 本生成**、最良を 1 本採用。尺は 2〜4 秒、それ以上は崩れる。
3. カメラ指示は 1 つだけ（`slow push-in 3%` か `static` か `subtle handheld sway`）。
4. 人物ショットは R1〜R3 を**毎回**参照に付ける（Runway：References、Kling：Elements、Veo：Ingredients）。
5. 動きは「ゆっくり 1 動作」だけ頼む（`one slow stroke from knee to ankle`）。複数動作を書かない。
6. ネガティブに常に `no bottle, no label, no text, no logo`（ボトルは合成するため）。ただし S2 のプレースホルダーは例外。
7. 生成物の命名：`{案}{#}_{ツール}_{seed}_v{n}.mp4`。採用は `06_qa/quality_review_log.md` に記録。

---

## 5. QA チェック（AI ショット 1 本ごと）
- [ ] 顔が R1 と同一人物に見える（A#7）
- [ ] 指 5 本、関節の数が正しい（映る場合）
- [ ] 脚の長さ・関節が不自然に曲がっていない
- [ ] 部屋が S2 と同じ（ランプ位置、シーツの色）
- [ ] 文字・ロゴ・他社製品が生成されていない
- [ ] 肌が青白くない、ハイライトが飛んでいない
- [ ] 実写カットと並べて色温度が揃う（Lumetri で調整可能な範囲）
- [ ] 合成ボトル：等倍以下・変形なし・接地影あり

---

## 6. 法務・開示（AI 出演者を使うときの約束）
| 項目 | 対応 |
|---|---|
| 実在人物の肖像 | 似せない。採用前に逆画像検索。有名人の名前をプロンプトに入れない |
| プラットフォームの AI 表示 | TikTok・Instagram は「リアルに見える AI 生成コンテンツ」にラベル付けを求めている。投稿時に **AI 生成ラベルを ON**。広告管理画面でも該当項目にチェック |
| 景表法（なりすまし口コミ） | AI 出演者を「実際の購入者」「お客様の声」として見せない。C の吹き出しは**実在コメント**（`02_research/community_comments.md`）のみ。AI の人物にそのコメントを"言わせない" |
| 声 | AI 音声を使う場合、実在の人の声を模倣しない。中の人の実声を推奨 |
| 未成年に見える表現 | 禁止（仕様 23〜25 歳を守る） |
| 露出 | キャミワンピは KV と同程度まで。脚は「ケアの動作」としてのみ |

---

## 7. 工数とコストの目安
| 工程 | 所要 | 備考 |
|---|---|---|
| キャラ R1〜R4 確定 | 1〜2 時間 | 4 セット生成→選定 |
| セット S1〜S4 確定 | 1〜2 時間 | 各 4 枚 |
| 動画生成（AI ショット 12 本 × 4 テイク） | 3〜4 時間 | 生成待ちが主。並列で回す |
| 実写（手＋ボトル、10 カット） | 1 時間 | 自宅・iPhone |
| 合成（ボトル 6 カット） | 2 時間 | AE または Premiere |
| 編集 3 本＋バリエーション | 1 日 | `premiere_common_setup.md` |
| 合計 | **約 2 日** | 生成ツールのクレジットは月額プラン内で収まる本数 |
