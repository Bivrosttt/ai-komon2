# AI業務自動化ツール比較｜制作TODO（2026-08-03）

## 企画・検索意図

- [x] 既存記事とのカニバリ確認：既存の業務効率化記事は個別業務の手順で、汎用自動化サービス比較は未作成
- [x] 主キーワードを「AI業務自動化ツール 比較」に設定
- [x] 検索意図を比較・購入意図と判定
- [x] 読者を中小企業の経営者・業務改善担当・情シスに設定
- [x] CTAを「無料でコンサル一回分をプレゼント」に限定

## リサーチ

- [x] 日本語SERPの上位比較記事を4件確認
- [x] Zapier、n8n、Activepieces、Relevance AIの公式ホームを取得し、目視確認
- [x] 公式料金・usage・権限・セルフホスト可否を確認
- [x] G2、Capterra、TechRadar、Redditの傾向をサービス別に分離
- [x] 取得日・URL・主張をclaim ledgerへ記録
- [x] 検索ボリューム・難易度は未取得のため、数値を捏造せずプロキシと明記

## 執筆・実装

- [x] 結論と固有の要点を本文冒頭へ配置
- [x] 料金・usage・コスパ比較表を作成
- [x] 強み・弱み・向く人・向かない人の表を作成
- [x] 各サービスの最初の名称を公式ホームへリンク
- [x] 各サービスのホーム画面スクリーンショットと取得日を掲載
- [x] 1180px以上は左目次・中央本文・右CTA、モバイルは1カラム
- [x] Article / Breadcrumb / FAQ JSON-LDを可視情報と一致させる
- [x] 記事計測スタックと`data-analytics-content-type="article"`を追加

## 品質・公開ゲート

- [x] `validate_article.py`を実行（`ai-automation-tools-comparison-seo-validation.json`: score 100）
- [x] 比較記事バリデーターを実行（`ai-automation-tools-comparison-validation.json`: PASS）
- [x] 390px / 768px / 1280pxで表示確認（`ai-automation-tools-comparison-render-qa.json`）
- [x] 横スクロール・画像読込・リンク・CTA遷移・コンソールを確認（overflow false、全画像complete、TimeRex直リンク）
- [x] AI-only品質ゲートの結果を保存（`ai-automation-tools-comparison-quality-report.json`: PASS）
- [ ] 公開後28日でGSC・記事CTA・相談CVをURL単位で確認

## 判断メモ

主役はサービス名ではなく「誰が保守するか」「1回の実行で何を課金するか」「AI出力をどこで人が確認するか」。ツール単体の導入を勧めず、最初の1業務を決めてから組み込む導線にする。

## 証跡・未完了

- 公式ホーム画像4枚は `home-screens/` に保存し、`ai-automation-tools-comparison-screenshots.json` の全件を `visual_check: pass` とした。
- 検索ボリューム・難易度の数値は取得できなかったため、キーワードCSVでは空欄にし、SERP商用性・比較記事の存在・一次情報量を需要プロキシとして記録した。
- 公開後28日のGSC・記事CTA・相談CV確認は公開後に実施するため未完了。

## note変換・公開

- [x] note-article-converterでタイトルと本文を分離し、サイト用メタ情報・関連記事・独自CSSを除去
- [x] HTML表4つをサービス別の`h3`＋`blockquote`比較カードへ変換
- [x] 公式ホーム画像4枚とサムネイルをnote画像へアップロードし、本文順を維持
- [x] note内部APIで下書き保存後、明示承認に基づきフルpayloadで公開
- [x] note APIで`status=published`、`is_published=true`、画像5枚、タグ4件を確認
- [x] 公開HTMLをHTTP 200で取得し、ブラウザでタイトル・画像・本文・CTAを確認
- [x] 変換本文に`table`、`div`、`section`、`details`、関連記事、サイト専用ラベルを残していない

証跡：`note-article-converted.html`、`note-publication.json`、公開URL [note記事](https://note.com/try_aikomon/n/n2f59eb6f7c15)。
