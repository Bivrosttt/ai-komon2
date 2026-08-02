# AI画像生成サービス比較：実行TODO

## 0. ゴール

- [x] 検索意図「AI画像生成 比較」を軸に、価格・利用量・コスパ・口コミ・用途を一記事で判断できる状態にする。
- [x] 対象をMidjourney / Adobe Firefly / Ideogram / Canvaに固定する。

## 1. キーワード・SERP

- [x] 商用・比較意図の候補をCSV化: `ai-image-generation-comparison-keywords.csv`
- [x] スコアリングを実行: `keyword-ranking.json`
- [x] 採用KWをタイトル・H1・要点・見出しへ反映。

## 2. 公式・レビュー調査

- [x] 各サービスの公式ホーム・料金・ヘルプを調査: `ai-image-generation-comparison-research.md`
- [x] 国内外の独立レビュー/G2/Capterra/Reddit/TechRadarの傾向を公式情報と分離して記録。
- [x] 数値と出典をclaims台帳へ登録: `ai-image-generation-comparison-claims.json`
- [x] 価格・usage・単位コストをCSV化: `ai-image-generation-comparison-pricing.csv`

## 3. 公式ホーム画面

- [x] Midjourney: `articles/ai-image-generation-comparison/home-screens/midjourney-home.png`
- [x] Adobe Firefly: `articles/ai-image-generation-comparison/home-screens/firefly-home.png`
- [x] Ideogram: `articles/ai-image-generation-comparison/home-screens/ideogram-home.png`
- [x] Canva: `articles/ai-image-generation-comparison/home-screens/canva-home.png`
- [x] 各画像をサービス見出しの直前に配置し、取得日と公式リンクをfigcaptionへ記載。

## 4. 本文・UI

- [x] `answer` と `key-points` にサービス名・価格・usage・第一候補・向かない条件を明記。
- [x] 価格・usage・コスパ表を作成。換算不能は算定不能と記載。
- [x] 強み・弱み・向く人・向かない人の比較表を作成。
- [x] サービス名の初出を公式ホームリンクにし、価格リンクをサービスリンクと分離。
- [x] 左TOC / 中央本文 / 右CTA、スマホではTOC非表示・CTAを本文下へ配置。
- [x] CTAを「自社に合うAIを / 最短経路で導入」「無料でコンサル一回分をプレゼント」に統一。
- [x] 構造化データ（Article/Breadcrumb/FAQ）と関連リンクを追加。
- [x] サムネイルを `scripts/generate_article_thumbnail.py` で生成。

## 5. 検証

- [x] 比較記事バリデータ: `ai-image-generation-comparison-validation.json`（PASS）
- [x] SEO/GEOバリデータ: `ai-image-generation-comparison-seo-validation.json`（score 100 / pass）
- [x] AI-only品質ゲート: `ai-image-generation-comparison-quality-report.json`（PASS）
- [x] 1440px / 768px / 390pxで表示・横スクロール・画像欠落・CTAリンクを確認（scrollWidth=clientWidth、画像はscrollintoview後に全件読込）。
- [x] `git diff --check` と禁止表現検索を実行。
