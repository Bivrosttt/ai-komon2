# AIサービス比較記事 テストレポート

実行日: 2026-07-31

## 自動チェック

| 対象 | SEO/GEO validator | Content quality gate | キーワード scorer |
| --- | --- | --- | --- |
| AI動画生成サービス比較 | PASS / 100点 | 実行済み（下記） | 既存キーワード表を継続利用 |
| AIコーディングサービス比較 | PASS / 100点 | 実行済み（下記） | 既存キーワード表を継続利用 |
| AI議事録ツール比較 | PASS / 100点 | 実行済み（下記） | 既存キーワード表を継続利用 |

比較専用バリデータ（`skills/noimos-comparison-article/scripts/validate_comparison_article.py`）は3記事すべて `PASS`。禁止表現0件、料金・usage・コスパ・強み弱み、初出公式リンク、末尾AI顧問室CTAを検出した。

今回のリライトでは、各記事の料金表直前に代表シナリオ（動画月20本、開発の週10件修正＋月1機能追加、1時間会議月20回）を追加し、単純な月額順ではなくusageに対する判断を先に渡す構成へ更新した。比較スキル本体とエージェントプロンプトも、作業開始時の永続TODOと全項目チェックボックスを必須化した。

サービスレビュー節は、画像・見出し・説明文を一つのカードへまとめ、番号・カテゴリ色・背景色・十分なカード間隔でサービスの上下関係を明示した。3記事すべてに同じデザインルールを適用した。

サービスリンクは、H1・結論・比較表の主リンクを公式ホーム／公式プロダクトホームへ統一した。料金URLは価格ソース欄にのみ残し、比較バリデータの `--home-urls` 検査で課金ページへの誤遷移がないことを確認した。

冒頭の要点ブロックは、記事の構成説明ではなく、用途別の候補、価格・usage、選ばない条件を直接提示する内容へ更新した。比較表のサービス列は内容幅ベースの`nowrap`にし、候補名の最長幅で自動調整されることを確認した。

ホーム画面スクリーンショットも3記事すべてサービス数と一致。各レビュー見出し直前の`figure.service-home-shot`、公式URL、取得日を検出した。Replitだけは公式ホームがCloudflareでブロックされたため、公式Docs掲載のProject Editorホーム画面を代替使用し、captionと台帳に明記した。

## ブラウザ確認

- デスクトップ 1440px: 3ページでタイトル、目次、比較表、CTA、サムネイル、代表シナリオ callout、サービスカード4枚の表示を確認（`/tmp/ai-video-tools-comparison-desktop.png`、`/tmp/ai-coding-tools-comparison-desktop.png`、`/tmp/ai-meeting-notes-comparison-desktop.png`）。
- モバイル 390px: 3ページで横スクロールなし、目次非表示、CTAが記事末尾へ移動、比較表が横スクロール可能、サービスカード間隔、サービス画像4枚の`complete=true`を確認（`/tmp/ai-video-service-review-desktop.png`、`/tmp/ai-video-service-review-mobile.png`）。
- 要点・表QA: 3ページで要点4項目、全候補名、具体的な数値、判断条件、サービス列の改行なしを確認（`/tmp/ai-video-key-points-desktop.png`、`/tmp/ai-video-key-points-mobile.png`、`/tmp/ai-video-strengths-desktop.png`）。
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
