# 実在AIサービス比較記事リライト TODO

更新日: 2026年7月31日  
対象: 既存のAI動画・AIコーディング・AI議事録比較記事  
運用: 各項目は証跡（ファイル、URL、コマンド、画面確認）がそろった時点でのみ `[x]` にする。

## 全体チェックリスト

- [x] 対象記事を3本に固定した
- [x] 最新の `noimos-comparison-article` スキル全文を読み、現行記事の不足を確認した
- [x] スキルの全工程をチェックリスト形式へ統一し、TODO必須運用を明文化する
- [x] 公式ホーム画面のスクリーンショットを各サービスのレビュー直前へ配置した
- [x] 価格・usage・コスパ・強み・弱み・公式リンク・最終AI顧問室CTAを各記事で確認した
- [x] 3記事を最新チェックリストに沿ってブラッシュアップし、差分を検証する
- [x] デスクトップ・スマホの実ブラウザ表示を3記事で確認する
- [x] 比較バリデータ、SEO/GEOバリデータ、品質ゲートを再実行する
- [x] TODOの未完了項目を解消し、証跡ファイルをリンクする

## AI動画サービス比較

- [x] ブリーフ・候補・代表シナリオ・決定ルールを確認: `ai-video-tools-comparison-brief.md`
- [x] 公式料金・usage・口コミの調査証跡を確認: `ai-video-tools-comparison-research.md`
- [x] claim ledgerと価格入力を確認: `ai-video-tools-comparison-claims.json`, `ai-video-tools-comparison-pricing.csv`
- [x] 公式ホーム画面4枚と取得元台帳を確認: `ai-video-tools-comparison/home-screens/`, `ai-video-tools-comparison-screenshots.json`
- [x] 本文・価格表・強み弱み表・CTAを確認: `articles/ai-video-tools-comparison/index.html`
- [x] 最新チェックリストでDOM、禁止語、リンク、画像、レスポンシブ表示を再検証する
- [x] リライト後の品質レポートを保存する

## AIコーディングサービス比較

- [x] ブリーフ・候補・代表シナリオ・決定ルールを確認: `ai-coding-tools-comparison-brief.md`
- [x] 公式料金・usage・口コミの調査証跡を確認: `ai-coding-tools-comparison-research.md`
- [x] claim ledgerと価格入力を確認: `ai-coding-tools-comparison-claims.json`, `ai-coding-tools-comparison-pricing.csv`
- [x] 公式ホーム画面4枚と取得元台帳を確認: `ai-coding-tools-comparison/home-screens/`, `ai-coding-tools-comparison-screenshots.json`
- [x] 本文・価格表・強み弱み表・CTAを確認: `articles/ai-coding-tools-comparison/index.html`
- [x] 最新チェックリストでDOM、禁止語、リンク、画像、レスポンシブ表示を再検証する
- [x] リライト後の品質レポートを保存する

## AI議事録サービス比較

- [x] ブリーフ・候補・代表シナリオ・決定ルールを確認: `ai-meeting-notes-comparison-brief.md`
- [x] 公式料金・usage・口コミの調査証跡を確認: `ai-meeting-notes-comparison-research.md`
- [x] claim ledgerと価格入力を確認: `ai-meeting-notes-comparison-claims.json`, `ai-meeting-notes-comparison-pricing.csv`
- [x] 公式ホーム画面4枚と取得元台帳を確認: `ai-meeting-notes-comparison/home-screens/`, `ai-meeting-notes-comparison-screenshots.json`
- [x] 本文・価格表・強み弱み表・CTAを確認: `articles/ai-meeting-notes-comparison/index.html`
- [x] 最新チェックリストでDOM、禁止語、リンク、画像、レスポンシブ表示を再検証する
- [x] リライト後の品質レポートを保存する

## 完了条件

- [x] 3記事すべてで比較バリデータが `PASS`（blockers 0、warnings 0）になる
- [x] 3記事すべてでSEO/GEOバリデータとAI-only品質ゲートが成功する
- [x] 3記事すべてでサービス数とホーム画面数が一致し、各レビュー見出し直前に画像がある
- [x] 3記事すべてでスマホ時に目次が非表示、CTAが記事下に移動し、比較表が横スクロール可能である
- [x] 対象記事内の禁止語検索が0件になる
- [x] 変更したスキル、記事、証跡、画像だけをコミットする

## 実行証跡

- 比較バリデータ出力: `ai-video-tools-comparison-comparison-validation.json` / `ai-coding-tools-comparison-comparison-validation.json` / `ai-meeting-notes-comparison-comparison-validation.json`
- SEO/GEO出力: `ai-video-tools-comparison-validation.json` / `ai-coding-tools-comparison-validation.json` / `ai-meeting-notes-comparison-validation.json`
- AI-only品質出力: 各 `*-quality-report.json`（3件とも `PASS`）
- 公式ホーム画面台帳: 各 `*-screenshots.json` と各記事の `home-screens/`
- 実ブラウザ画面: `/tmp/ai-video-tools-comparison-desktop.png`、`/tmp/ai-coding-tools-comparison-desktop.png`、`/tmp/ai-meeting-notes-comparison-desktop.png`
