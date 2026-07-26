# AI仕事道具箱

広告・LINE流入から、登録なしで実務の最初の一歩を体験してもらうためのリードマグネットです。

## 入口

- `/lead-magnets/ai-work-kit/`: 10個のプレゼントを束ねるハブ
- `/lead-magnets/ai-work-kit/prompts/`: 説明とプロンプトを検索・絞り込みできる100選ライブラリ

## 広告クリエイティブ

- `creative.html`: 日本語の見出し・10個の特典内容・CTAを正確に重ねるための制作元HTML
- `../../assets/meta-ads-creatives/current/lead-magnet-10-gifts/00-background.png`: 画像生成したAI仕事道具箱の背景
- `../../assets/meta-ads-creatives/current/lead-magnet-10-gifts/01-ai-work-kit-4x5.png`: Metaフィード向け4:5クリエイティブ
- `../../assets/meta-ads-creatives/current/lead-magnet-10-gifts/02-ai-work-kit-square.png`: LINE・正方形配置向けクリエイティブ

訴求の主見出しは「AI活用の10大特典プレゼント」。画像上には10個すべての内容を短く掲載し、詳細説明と実際に使えるページはAI仕事道具箱とプロンプト100選に集約しています。

## 10個のプレゼント

1. 実務で使えるパターン別プロンプト集100選
2. AI活用レベル診断
3. AI導入リスク・社内ルール診断
4. 議事録テンプレート・ToDo整理
5. 営業・見積もり工数シミュレーター
6. AI導入回収期間シミュレーター
7. 見積書かんたん作成
8. 請求書かんたん作成
9. 業務効率化アイデア50選
10. AI導入の7つの失敗チェック

## プロンプトの作成方針

100件の日本語プロンプトは、このリポジトリの利用者向けに新規作成したものです。特定の海外リポジトリの文面を転載せず、用途別の分類、目的・入力・条件・出力の構造、確認質問と人のレビューを重視しています。

設計の参考にした公開資料:

- [DAIR.AI Prompt Engineering Guide](https://github.com/dair-ai/Prompt-Engineering-Guide): instruction、context、input、outputの要素整理と反復改善の考え方。
- [Awesome ChatGPT Prompts](https://github.com/f/awesome-chatgpt-prompts): 用途別にプロンプトを探すライブラリ構成。リポジトリの現在のライセンス表示を確認して、文面の転載はしていません。
- [RISE-UNIBAS Prompt Library](https://github.com/RISE-UNIBAS/prompt-library): 検索可能なライブラリ、メタデータ、用途の記述方法。各プロンプトの権利表示を持つ設計を参考にしています。
- [useful-ai-prompts](https://github.com/aj-geddes/useful-ai-prompts): カテゴリ、全文検索、コピーUI、実例を備えたMIT Licenseのライブラリ。操作体験の参考にしています。

## 計測とプライバシー

- 入力されたプロンプト本文をサーバーへ送信する機能はありません。
- コピー、プレゼント遷移、相談CTAは既存の `measurement.js` が本番ホスト上でのみ計測します。
- 広告・LINE流入は `from`、UTM、`fbclid` など既存のfirst-touch attributionを引き継ぎます。
- 外部AIへ入力する情報は、このページの外で処理されます。顧客情報、個人情報、機密情報は必要最小限にしてください。
