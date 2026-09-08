# ChenMe ほぐほぐクリーム｜広告プロジェクト

足用マッサージクリーム「ChenMe ほぐほぐクリーム」の SNS 動画広告（TikTok / Instagram Reels）制作パッケージ。
**在庫切れ期**のため、購入ではなく「再販待ちの期待感」を作る。締めは `Coming back soon` / `Stay tuned` で統一。

## 読む順番
| # | フォルダ／ファイル | 中身 |
|---|---|---|
| 0 | `assets/product/` | **正式ビジュアル 4 点＋実物写真 2 点（改変禁止）**、合成用の切り抜き PNG、使用ルール |
| 1 | `01_brandbook/ChenMe_BrandBook.md` | 世界観、トンマナ、使う言葉／避ける言葉、カラーパレット（実測）、フォント、映像トーン、禁止事項 |
| 2 | `02_research/ad_pattern_analysis.md` | 美容・セルフケア・K-beauty 系ショート広告のパターン分析（型 100 エントリ）。**実視聴ではなく公開レポートからの再構成**、実視聴の手順も同梱 |
|   | `02_research/ad_database.csv` | 100 行の型データベース（`build_ad_database.py` で生成） |
|   | `02_research/compliance_yakkiho.md` | 薬機法・景表法チェックリスト |
|   | `02_research/product_facts.md` | 商品ファクトシート（香り・テクスチャ・成分・無添加・競合・Amazon ページ表現の判定） |
| 3 | `03_concepts/10_concepts.md` | 15 秒動画の企画 **13 本**＋採点＋配信設計 |
| 4 | `04_scripts/A_kutsu_nuida.md` | **案A「靴、脱いだ。」** 秒単位台本／絵コンテ／カメラ／出演者／BGM・SE／AIプロンプト／Premiere |
|   | `04_scripts/B_yoru_no_3pun_asmr.md` | **案B「夜の3分 ASMR」** 同上 |
|   | `04_scripts/C_urikireteta.md` | **案C「もう買えないですか？」** 同上（実在コメント使用） |
|   | `04_scripts/storyboards/*.svg` | 3 案の絵コンテ（構図ラフ、セーフゾーン表示） |
| 5 | `05_production/bottle_placement_workflow.md` | ボトルを改変ゼロで動画に置く方法（実写／合成／image-to-video）と検証コマンド |
|   | `05_production/premiere_common_setup.md` | Premiere の共通セットアップ、.mogrt 仕様、書き出し |
|   | `05_production/ai_talent_and_set.md` | **AI 出演者・AI セットの制作ガイド**（キャラシート、セット・バイブル、ショット別 AI/実写、法務・開示） |
|   | `02_research/community_comments.md` | 実在コメント（匿名化）とその使い方、許諾 DM テンプレ |
| 6 | `06_qa/quality_review_log.md` | 自己レビューと改善の記録。次に必要なもの |
| — | `inbox/` | なるねの動画・正式ボトル画像の受け口と、受領後の処理手順 |

## 3 本の本命
| 案 | 一言 | 型 | 締め |
|---|---|---|---|
| A | ヒールを脱ぐ「カッ、、、ふう」から始まる、脚の1日の終わり | 解放POV | Coming back soon |
| B | 真っ暗な部屋で、ランプの音とポンプの音だけ | 手元ASMR | Stay tuned |
| C | 実在コメント「もう買えないですか？」に動画で返す | コメント返し×ティザー | Coming back soon → Get notified |

## 絶対ルール（全成果物共通）
1. ボトル・ラベル・ロゴは改変しない（変形・色変更・再タイプ・アニメ化 禁止）。AI に描かせない。
2. 効能を断定しない（むくみ・血行・痩せ・疲労回復 禁止）。気分・習慣・ご褒美のみ。
3. 在庫切れは隠さず、煽らず、「待ち」を演出する。購入CTAは出さない。
