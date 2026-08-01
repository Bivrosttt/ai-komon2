# 無料相談導線LPリサーチ 6件

取得日: 2026-07-28（JST）  
対象: Meta Ad Library の日本・掲載中広告  
目的: 「無料相談」「無料カウンセリング」「個別相談」「無料面談」など、相談・体験・診断へ誘導するLPの構成を比較する。

## 取得範囲

以下の検索語でMeta Ad Libraryを検索した後、HPや予約ページではなく、広告から相談・体験・診断へ誘導するLPと判断した6件だけを残した。

- 無料相談
- 無料カウンセリング
- 個別相談
- 無料面談
- 相談会
- 無料体験
- 無料診断

残したのは、採用、人材、スクール、住宅・建設、歯科、金融、診断型サブスクの6パターン。その他14件はLPではなくHP・予約ページと判断したため、DB・PDF・画面キャプチャから削除した。LINE・Instagram・Facebookなどへの直行リンク、予約カレンダー直行リンクも対象外とした。

## ファイル構成

```text
records.json                  # 広告・広告文・CTA・Meta広告ID・LP URLの構造化DB
records.csv                   # スプレッドシート等で開ける一覧
raw-candidates.json           # 7検索語から得たうち、採用した6件の記録
output/
  lp-capture-index.json       # LPごとのキャプチャ結果・画面数・PDFパス
  lp-capture-index.csv        # 同上の表形式
  lp-screens/<LP slug>/       # 1440x900の画面単位PNG
  lp-pdfs/<LP slug>.pdf       # 各LPを画面単位でまとめたPDF
```

## キャプチャ仕様

- ビューポート: 1440 x 900px
- 1画面ずつ縦方向にスクロールしてPNG保存
- 各LPの全画面をLP別PDFに格納
- 6LP、合計135画面、6PDFを保持
- `records.json` の `lp_capture_status` が全件 `complete` であることを確認済み
- PDFページ数とPNG画面数が全6件で一致することを確認済み

保持している参考LP:

- 求人Booster: 強い数字・図解を最初に出す採用LP
- Sakiyomiスクール: 2問診断から始めるクイズ型LP
- ハウプロ: 実績・権威・高単価の信頼形成型LP
- こう歯科矯正歯科: 明るいビジュアルとサービス理解を両立した長尺LP
- ABCash: キャンペーン・特典を前面に出すオファー型LP
- Coloria: 診断を主役にした診断完結型LP

## DB項目

広告由来の項目:

- `captured_at`: 取得日
- `search_term`: ヒットした検索語
- `advertiser`: 広告主名
- `ad_library_id`: Meta広告ライブラリID
- `started_running`: 掲載開始日の表示
- `ad_copy`: 広告本文
- `cta`: 広告から抽出した相談・体験系CTA
- `landing_page_url`: 追跡用パラメータを整理したLP URL
- `ad_library_url`: Meta広告ライブラリの広告詳細URL
- `link_label`: 広告リンク周辺の表示文
- `score`: 相談導線の強さと広告文量による選定用スコア

保存後に追加したLP項目:

- `lp_capture_status`
- `lp_page_title`
- `lp_page_height_px`
- `lp_screen_count`
- `lp_screenshots_dir`
- `lp_pdf_path`
- `lp_capture_error`

## 読み方・注意点

これはMeta Ad Library上の掲載事例を保存したリサーチDBであり、成果の良い順のランキングではない。Meta Ad Libraryからは通常、他社広告のCV数、CPA、予算、実際のLPコンバージョン率は取得できないため、PDFは「無料相談へ誘導するファーストビュー、コピー、CTA、信頼要素、フォーム構成」の比較用に使う。

外部サイトは取得時点の表示を保存している。後日LPが変更・終了・リダイレクトされても、保存済みPNG/PDFは取得時点の観察記録として残る。

## 再取得

候補収集:

```bash
/Users/koki/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  scripts/collect_free_consultation_meta_ads.py
```

LPキャプチャ:

```bash
/Users/koki/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  scripts/capture_free_consultation_lp_screens.py
```

外部LPのナビゲーションがタイムアウトしても、ブラウザ上で実際のURLに到達していればキャプチャを継続する。取得後は `output/lp-capture-index.json` と `records.json` の `lp_capture` を確認する。
