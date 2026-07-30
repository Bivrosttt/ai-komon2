# Noimos SEO記事リファレンス整理TODO

開始日: 2026-07-30

- [x] 対象範囲を `articles/*/index.html` の27本に固定する
- [x] title / description / canonical / 公開日 / 更新日を抽出する
- [x] H1/H2/H3、文字数、表、FAQ、JSON-LD、CTA、内部/外部リンクを抽出する
- [x] CSSクラスとinline CSS / 外部stylesheetを装飾台帳として保存する
- [x] 記事内の図解・画像29点をローカルコピーし、alt・caption・寸法・SHA-256を保存する
- [x] 全文を可読Markdownへ転記する
- [x] 記事一覧、リサーチメモ、デザインシステム、画像マニフェスト、inventory.jsonを作成する
- [x] Markdown内の画像リンク、コピー画像、元HTMLのSHA-256を検証する
- [x] 再実行可能な生成スクリプトを保存する
- [x] 参照コーパスをPushする（既存WIPはステージしない）

## 再調査トリガー

- 記事を追加・削除したとき
- title / H1 / CTA / JSON-LD / 画像を変更したとき
- 90日または180日のコンテンツレビュー時
- GSCで表示・クリック・クエリ・CTR・掲載順位の変化が確認できたとき
