# SEO記事 次バッチ納品メモ

実施日: 2026-07-13

## 追加した5本

| URL | 主キーワード | 本文文字数 | 図解 |
|---|---|---:|---|
| `/articles/contract-ai/` | 契約書 AI | 約2,800字 | 契約条件整理→下書き→人の確認→台帳・更新 |
| `/articles/invoice-efficiency/` | 請求書 作成 効率化 | 約2,800字 | 取引データ→請求書作成→承認・確認→送付・記録 |
| `/articles/internal-ai-training/` | 社内研修 AI | 約2,800字 | 課題→教材→演習→理解度→更新の循環 |
| `/articles/chatgpt-work-guide/` | ChatGPT 仕事 使い方 | 約2,800字 | 目的→材料→条件→出力確認→業務反映 |
| `/articles/ai-agent-business/` | AIエージェント 企業 | 約2,900字 | 定型業務→参照データ→承認→記録・監視 |

## 実施内容

- 各記事に結論ボックス、要点ボックス、目次、手順・比較表、FAQ、CTA、関連記事を配置。
- 各記事に記事固有のテキスト入りPNG図解を配置。画像は1672×941、`alt`、`figcaption`、lazy-loadを確認。
- 競合候補10ページのモバイルファーストビュー・全体スクリーンショットを `seo/evidence/competitors/next-batch-2026-07-13/` に保存。
- `tools/index.html` の関連記事導線と `sitemap.xml` に5本を追加。
- 一次情報として経済産業省、IPA、個人情報保護委員会、中小企業大学校、OpenAIの公開資料を参照。

## 検証

- 5本とも H1は1個、図解は1点、figcaptionあり、altあり。
- 主要内部リンクのローカル存在確認: missing 0件。
- 390px幅のブラウザ確認: `bodyScrollWidth=390`、画像のnaturalWidth=1672、画像読み込み完了。
- `git diff --check`: pass。
- `site_audit.py`: サイト全体では既存LP・デモ由来の課題が147件。今回の5記事は個別チェックでtitle、description、canonical、OG、H1、画像要件を満たす。

検索数や順位は推定していない。サジェストと公開SERPは検索意図の観測として扱い、公開後はSearch Consoleで表示回数、CTR、検索語、問い合わせ導線を確認する。
