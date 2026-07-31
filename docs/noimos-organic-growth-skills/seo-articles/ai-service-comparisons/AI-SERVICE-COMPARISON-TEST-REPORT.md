# AIサービス比較記事 テストレポート

実行日: 2026-07-31

## 自動チェック

| 対象 | SEO/GEO validator | Content quality gate | キーワード scorer |
| --- | --- | --- | --- |
| AI動画生成サービス比較 | PASS / 100点 | PASS / blocker 0 | 5候補・5件eligible |
| AIコーディングサービス比較 | PASS / 100点 | PASS / blocker 0 | 5候補・5件eligible |
| AI議事録ツール比較 | PASS / 100点 | PASS / blocker 0 | 5候補・5件eligible |

## ブラウザ確認

- デスクトップ 1440px: 3ページでタイトル、目次、比較表、CTA、サムネイルの表示を確認。
- モバイル 390px: 横スクロールなし、目次非表示、記事末尾CTA表示を確認。
- SVGサムネイル: 3ページとも `complete=true` かつ自然幅を取得。
- アイコン位置: SVGの変形後バウンディングボックスをブラウザで測定し、3枚ともキャンバス中心（1600×900の中心）に一致することを確認。
- 代表スクリーンショット: `/tmp/ai-komon-service-articles/video-desktop.png`、`coding-desktop.png`、`meeting-desktop.png`、`meeting-mobile.png`

## 公式URLの疎通

Runway、HeyGen、Synthesia、GitHub Copilot、Cursor、Claude Code、Replit、Notta、Otter、Fireflies、Zoomの公式URLはHTTP 200を確認した。Adobe Fireflyは同じURLへの応答がタイムアウトしたため、ブラウザでの再確認対象として残した。記事ではAdobeの機能・料金を固定値として断定していない。

## 判定

記事公開前のAI専用品質ゲートは通過。価格・機能・ライセンス・保存条件は更新されるため、公開後は月次で公式ページを再確認し、検索順位・クリック・相談遷移・相談内容を記録する。
