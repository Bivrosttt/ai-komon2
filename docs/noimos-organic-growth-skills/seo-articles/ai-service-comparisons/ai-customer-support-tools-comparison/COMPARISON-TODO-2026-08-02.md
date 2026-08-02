# AIカスタマーサポート比較：実行TODO

## 0. ゴール

- [x] 検索意図「AIカスタマーサポート 比較」を軸に、席数・解決件数・セッション・コスパ・用途を一記事で判断できる状態にする。
- [x] 対象をIntercom Fin / Zendesk AI / Gorgias AI Agent / Freshdesk Freddy AIに固定する。

## 1. キーワード・SERP

- [x] 商用・比較意図の候補をCSV化: `ai-customer-support-tools-comparison-keywords.csv`
- [x] スコアリングを実行: `keyword-ranking.json`
- [x] 採用KWをタイトル・H1・要点・見出しへ反映。

## 2. 公式・レビュー調査

- [x] 各サービスの公式ホーム・料金・ヘルプを調査: `ai-customer-support-tools-comparison-research.md`
- [x] 国内外の独立レビュー/G2/Capterra/Reddit/TechRadarの傾向を公式情報と分離して記録。
- [x] 数値と出典をclaims台帳へ登録: `ai-customer-support-tools-comparison-claims.json`
- [x] 価格・usage・単位コストをCSV化: `ai-customer-support-tools-comparison-pricing.csv`

## 3. 公式ホーム画面

- [x] Intercom: `articles/ai-customer-support-tools-comparison/home-screens/intercom-home.png`
- [x] Zendesk: `articles/ai-customer-support-tools-comparison/home-screens/zendesk-home.png`
- [x] Gorgias: `articles/ai-customer-support-tools-comparison/home-screens/gorgias-home.png`
- [x] Freshdesk: `articles/ai-customer-support-tools-comparison/home-screens/freshdesk-home.png`
- [x] 各画像をサービス見出しの直前に配置し、取得日と公式リンクをfigcaptionへ記載。

## 4. 本文・UI

- [x] `answer` と `key-points` にサービス名・価格・課金単位・第一候補・向かない条件を明記。
- [x] 席数・解決件数・セッション・コスパ表を作成。契約条件に依存する部分は公開情報の範囲を明記。
- [x] 強み・弱み・向く人・向かない人の比較表を作成。
- [x] サービス名の初出を公式ホームリンクにし、価格リンクをサービスリンクと分離。
- [x] 左TOC / 中央本文 / 右CTA、スマホではTOC非表示・CTAを本文下へ配置。
- [x] CTAを「自社に合うAIを / 最短経路で導入」「無料でコンサル一回分をプレゼント」に統一。
- [x] 構造化データ（Article/Breadcrumb/FAQ）と関連リンクを追加。
- [x] サムネイルを `scripts/generate_article_thumbnail.py` で生成。

## 5. 検証

- [x] 比較記事バリデータ: `ai-customer-support-tools-comparison-validation.json`（PASS）
- [x] SEO/GEOバリデータ: `ai-customer-support-tools-comparison-seo-validation.json`（score 100 / pass）
- [x] AI-only品質ゲート: `ai-customer-support-tools-comparison-quality-report.json`（PASS）
- [x] 1440px / 768px / 390pxで表示・横スクロール・画像欠落・CTAリンクを確認（scrollWidth=clientWidth、画像はscrollintoview後に全件読込）。
- [x] `git diff --check` と禁止表現検索を実行。
