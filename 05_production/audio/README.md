# audio — C v04（18.0s）の音キューシート
> **仮音（2026-09-09）**：フリー音源サイトがこの環境から届かないため、`make_placeholder_audio.py` で BGM（BPM85、C→G→Am→F のピアノ風＋ローファイノイズ）と SE 6 種を合成し、`placeholder/` に置いた。`AUDIO_DIR=05_production/audio/placeholder python3 05_production/audio/mux_audio.py` で `roughcuts/C_v04_placeholder_audio.mp4`（−17.4 LUFS、ピーク −0.9 dB）。**本物の音源をこのフォルダ直下に同名で置けば、同じコマンド（AUDIO_DIR なし）で差し替わる。**
音ファイルをこのフォルダに置いて `python3 05_production/audio/mux_audio.py` を実行すると、`roughcuts/C_v04_roughcut.mp4` に音を乗せた `C_v04_with_audio.mp4` ができる。
ラウドネス：統合 −16 LUFS、ピーク −1 dBTP。VO 基準 −14 dB、BGM は VO の −12 dB 下、SE −10〜−6 dB。

## 1. キューシート（IN は動画の秒）
| IN | 種類 | 内容 | ファイル名（この名前で置く） | 音量目安 |
|---|---|---|---|---|
| 0.0 | BGM | アコースティックギター or ソフトなローファイ、BPM 85、歌なし。フェードイン 0.5s、17.4s からフェードアウト | `bgm.wav` / `.mp3` | −22 dB（VO 中はダッキング −10 dB） |
| 0.0 | SE | 衣擦れ（小さく） | `se_cloth.wav` | −18 dB |
| 1.4 | VO | 「ごめんね、、、」（小声、困った笑い） | `vo_01.wav` | −14 dB |
| 2.4 | VO | 「うん、いま在庫切れ」 | `vo_02.wav` | −14 dB |
| 3.9 | SE | ポンプ「しゅっ」（指が押す瞬間 3.4+0.5s） | `se_pump.wav` | −8 dB |
| 4.3 | SE | クリーム「とろ」（カット直後、小さく） | `se_cream.wav` | −14 dB |
| 3.6 | VO | 「いつもの、1プッシュ」 | `vo_03.wav` | −14 dB |
| 5.9 | VO | 「今日も、おつかれ」 | `vo_04.wav` | −14 dB |
| 6.0 | SE | 手が肌をなでる音（2.0s） | `se_stroke.wav` | −16 dB |
| 8.4 | VO | 「でも、準備してるから」 | `vo_05.wav` | −14 dB |
| 8.6 | SE | ボトルを棚に置く「コト」 | `se_place.wav` | −10 dB |
| 10.0 | VO | 「戻ってくるから」（少し明るく） | `vo_06.wav` | −14 dB |
| 12.7 | SE | ラベルが灯る瞬間：小さなグラス系「チン」 or 柔らかいキラ音 | `se_reveal.wav` | −12 dB |
| 14.2 | — | Coming back soon（音は BGM のみ。ここから BGM を −18 dB に少し上げる） | — | — |
| 17.4 | — | 全体フェードアウト 0.6s | — | — |

## 2. 入手先の目安
- BGM：Artlist / Epidemic Sound で `lo-fi piano intimate` `acoustic guitar warm bedroom` を検索。無料なら DOVA-SYNDROME（商用可・要クレジット確認）。
- SE：効果音ラボ（無料・商用可）「ポンプ」「布」「置く」、Artlist SFX。**ポンプ・とろ は実録が最良**（スマホで十分）。
- VO：中の人のスマホ録音で OK（静かな部屋、口から 15cm、ボイスメモ）。無理なら ElevenLabs 等の AI 音声（若い女性・ささやき手前）。

## 3. 置き方
```
05_production/audio/
  bgm.wav  se_cloth.wav  se_pump.wav  se_cream.wav  se_stroke.wav  se_place.wav  se_reveal.wav
  vo_01.wav ... vo_06.wav
```
無いファイルは自動でスキップ（BGM だけでも動く）。
