# 新規SEO記事5本 納品記録

実施日: 2026-07-13

## 作成した記事

| 記事 | 主キーワード | 本文文字数 | 図解 | CTA |
|---|---|---:|---:|---|
| [業務マニュアルの作り方](../articles/business-manual-howto/) | 業務マニュアル 作り方 | 2,418 | 1 | 業務効率化のアイデア |
| [社内FAQの作り方](../articles/internal-faq-howto/) | 社内FAQ 作り方 | 2,368 | 1 | AI活用事例 |
| [提案書をAIで作成する方法](../articles/proposal-ai/) | 提案書 作成 AI | 2,526 | 1 | 営業効率化の方法 |
| [カスタマーサポートのAI活用](../articles/customer-support-ai/) | カスタマーサポート AI | 2,548 | 1 | AI活用事例 |
| [業務引き継ぎの方法](../articles/work-handover-manual/) | 引き継ぎ 方法 | 2,359 | 1 | 業務効率化のアイデア |

## 実装内容

- キーワード調査記録: [article-research-2026-07-13.md](article-research-2026-07-13.md)
- 各記事にtitle、description、canonical、OGP、Article JSON-LD、FAQ JSON-LDを追加
- 各記事に結論ボックス、目次、手順・比較表、注意点、可視FAQ、関連記事を追加
- 各記事へ記事固有のAI生成図解を配置。短い日本語ラベルを画像内に含むPNG、1672×941、`alt`、`figcaption`あり
- [無料ツール一覧](../tools/)の読みもの導線と[sitemap.xml](../sitemap.xml)を更新

## 検証結果

- 新規5記事のHTML監査エラー: 0件
- 新規5記事のローカルリンク切れ: 0件
- ローカルHTTP確認: 5記事すべてHTTP 200
- 画像サイズ: 5点すべて1672×941
- H1: 5記事すべて1つ
- 可視FAQ: 5記事すべて3問
- `python3 -m py_compile seo/scripts/site_audit.py`: pass
- `git diff --check`: pass

サイト全体の監査では130 HTMLページ中129件の既存課題が残っている。内容は主に記事外のLP・デモ等のcanonical、OGP、meta description不足であり、新規5記事の課題ではない。

## 運用メモ

初稿は手順と判断材料を優先した約2,300〜2,600字。広い検索意図で表示データが集まった記事は、Search Consoleの検索語・CTR・問い合わせ導線を見て、比較表や事例を追加する。検索数や順位は今回推測していない。
