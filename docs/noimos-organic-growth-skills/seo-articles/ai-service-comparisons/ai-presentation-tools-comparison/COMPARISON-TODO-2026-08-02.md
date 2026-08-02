# AIプレゼン作成サービス比較：実行TODO

## 0. ゴール

- [x] 検索意図「AIプレゼン作成 比較」を軸に、価格・AIクレジット・スライド上限・コスパ・用途を一記事で判断できる状態にする。
- [x] 対象をGamma / Beautiful.ai / Canva / Microsoft 365 Copilotに固定する。

## 1. キーワード・SERP

- [x] 商用・比較意図の候補をCSV化: `ai-presentation-tools-comparison-keywords.csv`
- [x] スコアリングを実行: `keyword-ranking.json`
- [x] 採用KWをタイトル・H1・要点・見出しへ反映。

## 2. 公式・レビュー調査

- [x] 各サービスの公式ホーム・料金・ヘルプを調査: `ai-presentation-tools-comparison-research.md`
- [x] 国内外の独立レビュー/G2/Capterra/Reddit/TechRadarの傾向を公式情報と分離して記録。
- [x] 数値と出典をclaims台帳へ登録: `ai-presentation-tools-comparison-claims.json`
- [x] 価格・usage・単位コストをCSV化: `ai-presentation-tools-comparison-pricing.csv`

## 3. 公式ホーム画面

- [x] Gamma: `articles/ai-presentation-tools-comparison/home-screens/gamma-home.png`
- [x] Beautiful.ai: `articles/ai-presentation-tools-comparison/home-screens/beautiful-ai-home.png`
- [x] Canva: `articles/ai-presentation-tools-comparison/home-screens/canva-home.png`
- [x] Microsoft PowerPoint: `articles/ai-presentation-tools-comparison/home-screens/microsoft-powerpoint-home.png`
- [x] 各画像をサービス見出しの直前に配置し、取得日と公式リンクをfigcaptionへ記載。
- [x] 全4枚を `view_image` で1枚ずつ目視確認し、Cloudflare検証・ログイン後ワークスペース・主要領域のCookie遮蔽がないことを確認。代替画面は理由をfigcaption/台帳へ記載: `ai-presentation-tools-comparison-screenshots.json` の `manual_visual_review` / `visual_check`。

## 4. 本文・UI

- [x] `answer` と `key-points` にサービス名・価格・usage・第一候補・向かない条件を明記。
- [x] 料金・AIクレジット・スライド上限・コスパ表を作成。換算不能は算定不能と記載。
- [x] 強み・弱み・向く人・向かない人の比較表を作成。
- [x] サービス名の初出を公式ホームリンクにし、価格リンクをサービスリンクと分離。
- [x] 左TOC / 中央本文 / 右CTA、スマホではTOC非表示・CTAを本文下へ配置。
- [x] CTAを「自社に合うAIを / 最短経路で導入」「無料でコンサル一回分をプレゼント」に統一。
- [x] 構造化データ（Article/Breadcrumb/FAQ）と関連リンクを追加。
- [x] サムネイルを `scripts/generate_article_thumbnail.py` で生成。

## 5. 検証

- [x] 比較記事バリデータ: `ai-presentation-tools-comparison-validation.json`（PASS）
- [x] SEO/GEOバリデータ: `ai-presentation-tools-comparison-seo-validation.json`（score 100 / pass）
- [x] AI-only品質ゲート: `ai-presentation-tools-comparison-quality-report.json`（PASS）
- [x] 1440px / 768px / 390pxで表示・横スクロール・画像欠落・CTAリンクを確認（scrollWidth=clientWidth、画像はscrollintoview後に全件読込）。
- [x] 画像の存在確認だけで完了にせず、目視確認の全サービス判定が `pass` であることを確認。
- [x] `git diff --check` と禁止表現検索を実行。
