# AI仕事道具箱

広告・LINE流入から「無料顧問1回分」の面談につなぎ、面談後に実務資料・ツールを送付するためのリードマグネットです。ここでいう無料顧問1回分は、今回の面談1回分を顧問サービス1回分として提供する意味です。

## 入口

- `/lead-magnets/ai-work-kit/`: 相談後送付する10個の特典を紹介する案内ハブ
- `/lead-magnets/ai-work-kit/prompts/`: 相談後に送付するプロンプト100選の案内ページ
- `/lead-magnets/ai-work-kit/agent-implementation-guide/`: AIエージェント導入ガイドのプレビュー
- `/lead-magnets/ai-work-kit/state-of-ai-report/`: 中小企業のAI活用レポートのプレビュー
- `/lead-magnets/ai-work-kit/ai-presentation-guide/`: AIスライド実務ガイドのプレビュー

## 今回の正式版教材

- `../../materials/ai-komon-prompt-100-field-guide.pptx`: 100件を1件1枚で整理した編集用PowerPoint
- `../../materials/ai-komon-prompt-100-field-guide.pdf`: 100件を配布用に書き出したPDF
- `../../materials/ai-komon-presentation-quality-playbook.pptx`: 構成、根拠、図解、AI指示、レビュー、出力確認をまとめた32枚のPowerPoint
- `../../materials/ai-komon-presentation-quality-playbook.pdf`: 上記の配布用PDF

## 広告クリエイティブ

- `creative.html`: 旧版のレイアウト検証用。配信用の本命は、後加工なしで完成させた `03-ai-work-kit-book-launch.png`
- `../../assets/meta-ads-creatives/current/lead-magnet-10-gifts/00-background.png`: 画像生成したAI仕事道具箱の背景
- `../../assets/meta-ads-creatives/current/lead-magnet-10-gifts/01-ai-work-kit-4x5.png`: Metaフィード向け4:5クリエイティブ
- `../../assets/meta-ads-creatives/current/lead-magnet-10-gifts/02-ai-work-kit-square.png`: LINE・正方形配置向けクリエイティブ
- `../../assets/meta-ads-creatives/current/lead-magnet-10-gifts/03-ai-work-kit-book-launch.png`: テキスト・10商品モックアップ・CTAまで画像生成だけで完結したブックローンチ型の本命クリエイティブ
- `../../assets/meta-ads-creatives/current/lead-magnet-10-gifts/04-ai-work-kit-three-guides.png`: 相談後に届く3つの実務教材を、テキスト込みで1発生成した教材カバー
- `../../assets/meta-ads-creatives/current/lead-magnet-10-gifts/05-free-advisor-session-4x5.png`: 「無料顧問1回分」を主見出しにした4:5広告クリエイティブ。文字も画像生成時に描画
- `../../assets/meta-ads-creatives/current/lead-magnet-10-gifts/06-free-advisor-plus-10-gifts-4x5.png`: 「無料顧問1回分」と「AI活用10大特典プレゼント」を組み合わせた4:5広告クリエイティブ。文字も画像生成時に描画

本命クリエイティブの主見出しは「AI活用 10大特典」。画像生成時に、見出し・10個の特典名・各商品の説明・CTAまで直接描画しています。詳細説明と実際に使えるページはAI仕事道具箱とプロンプト100選に集約しています。

追加した3教材は、海外のAIコンサル企業に多い診断・成熟度・ロードマップ型の構成と、AIスライド関連サービスの実務フローを参考にしたAI顧問室オリジナルです。公開ページは本編のプレビューとして扱い、相談後に業務内容に合わせて送付します。

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

## 送付方針

100件の日本語プロンプトは、相談後に送付する実務資料として管理します。公開ページでは本文を表示せず、相談で伺った業務・社内ルールに合わせて使うジャンルと最初のプロンプトを案内します。

1. 相談予約フォームでメールアドレスと相談内容を受け取る。
2. 無料顧問1回分の面談を実施し、送付対象と送付先アドレスを確認する。
3. 相談後、担当者がプロンプト100選・必要な資料・ツール案内をメール送付する。
4. 送付済みかどうかを社内のリード管理表へ記録する。

現時点のサイトは静的配布のため、相談者だけに限定する認証機能や自動メール送信は未実装です。公開ページは `noindex, nofollow` とし、特典本文・直接リンクを表示しない運用に変更しています。自動化する場合は、次段でメール配信基盤または認証付き配布URLを追加してください。

## 計測とプライバシー

- 入力されたプロンプト本文をサーバーへ送信する機能はありません。
- コピー、プレゼント遷移、相談CTAは既存の `measurement.js` が本番ホスト上でのみ計測します。
- 広告・LINE流入は `from`、UTM、`fbclid` など既存のfirst-touch attributionを引き継ぎます。
- 外部AIへ入力する情報は、このページの外で処理されます。顧客情報、個人情報、機密情報は必要最小限にしてください。
