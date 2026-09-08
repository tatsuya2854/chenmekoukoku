# inbox — 追加素材の受け口

「なるね」の動画、追加のボトル画像、既存投稿などはここに入れる。

## 入れ方
```
inbox/
  narune/            ← なるねの動画（mp4/mov）＋あれば投稿URLをurls.txtに
  bottle_official/   ← 正式ボトル画像（PNG推奨、背景透過があれば最良）
  past_posts/        ← 過去の自社投稿・広告があれば
```

## 受け取ったら何をするか（処理手順）
1. **なるねの動画**：`02_research/ad_database.csv` に1本ずつ行を追加（同じ列で記録）。冒頭3秒・構成・色味・テロップ・テンポ・音を書き出し、`02_research/ad_pattern_analysis.md` の「§8 なるね分析」を埋める。台本A/B/Cのトーン・テンポを、なるねの実測値に寄せて改訂する。
2. **正式ボトル画像**：`assets/product/` に移し、READMEの表を更新。`05_production/bottle_placement_workflow.md` の切り抜き手順に沿ってPNGを作成し、3案の合成プレートを差し替える。
3. 変更点は `06_qa/quality_review_log.md` に「ラウンドN」として追記する。
