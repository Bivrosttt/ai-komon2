# AIサービス比較記事 テストレポート

実行日: 2026-07-31

## 自動チェック

| 対象 | SEO/GEO validator | Content quality gate | キーワード scorer |
| --- | --- | --- | --- |
| AI動画生成サービス比較 | PASS / 100点 | 実行済み（下記） | 既存キーワード表を継続利用 |
| AIコーディングサービス比較 | PASS / 100点 | 実行済み（下記） | 既存キーワード表を継続利用 |
| AI議事録ツール比較 | PASS / 100点 | 実行済み（下記） | 既存キーワード表を継続利用 |

比較専用バリデータ（`skills/noimos-comparison-article/scripts/validate_comparison_article.py`）は3記事すべて `PASS`。禁止表現0件、料金・usage・コスパ・強み弱み、初出公式リンク、末尾AI顧問室CTAを検出した。

ホーム画面スクリーンショットも3記事すべてサービス数と一致。各レビュー見出し直前の`figure.service-home-shot`、公式URL、取得日を検出した。Replitだけは公式ホームがCloudflareでブロックされたため、公式Docs掲載のProject Editorホーム画面を代替使用し、captionと台帳に明記した。

## ブラウザ確認

- デスクトップ 1440px: 3ページでタイトル、目次、比較表、CTA、サムネイルの表示を確認。
- モバイル 390px: 横スクロールなし、目次非表示、記事末尾CTA表示を確認。
- SVGサムネイル: 3ページとも `complete=true` かつ自然幅を取得。
- アイコン位置: SVGの変形後バウンディングボックスをブラウザで測定し、3枚ともキャンバス中心（1600×900の中心）に一致することを確認。
- 代表スクリーンショット: `/tmp/ai-komon-service-articles/video-desktop.png`、`coding-desktop.png`、`meeting-desktop.png`、`meeting-mobile.png`

## 調査カバレッジ

- AI動画: Runway、HeyGen、Synthesia、Adobe Fireflyの公式価格・機能、G2/Capterra/TechRadar/Redditのレビュー傾向を記録。
- AIコーディング: GitHub Copilot、Cursor、Claude Code、Replitの公式価格・usage、G2/Capterra/TechRadar/ITPro/Tom's Hardwareのレビュー傾向を記録。
- AI議事録: Notta、Otter、Fireflies、Zoom AI Companionの公式価格・usage、G2/Capterra/海外独立レビューの傾向を記録。

## 公式URLの疎通

Runway、HeyGen、Synthesia、GitHub Copilot、Cursor、Claude Code、Replit、Notta、Otter、Fireflies、Zoomの公式URLはHTTP 200を確認した。Adobe Fireflyは同じURLへの応答がタイムアウトしたため、ブラウザでの再確認対象として残した。記事ではAdobeの機能・料金を固定値として断定していない。

## 判定

記事公開前のAI専用品質ゲートは通過。価格・機能・ライセンス・保存条件は取得日付きの調査表と記事内へ反映し、次回更新時は同じ比較スキルのTODOを再実行する。
