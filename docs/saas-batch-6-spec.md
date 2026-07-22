<!-- 2026-07-22: SaaS候補6本の生成仕様（Composer向け・トークン節約用） -->
# SaaS級デモ 6本バッチ仕様

既存参照（必ず型として読む・JSパターンを踏襲）:
- `works-contract.html`（KAWASU）
- `works-invoice.html`（SOROBAN）
- `works-support.html`（MIMIYORI）

共通必須:
- 先頭コメント、github.io redirect、gtag `G-RSS02GXVRJ`
- `demo-frame-bar` → index.html
- `#view-login` → `doLogin()` → `#view-app`、hash routing `go()`
- sidebar + mobile drawer、toast、settings
- CTA `index.html?from=<file>#contact`
- 末尾: analytics-config.js / analytics.js / ga4-events.js / meta-pixel-config.js / meta-pixel.js
- 日本語UI、サンプル日付は2026-07前後
- ID・関数名は既存に合わせる（loginBtn, sidebar, toastHost 等）
- 触らない: 実API。全部クライアントデモ
- 各ファイル完了後: `assets/thumbs/works-<slug>.jpg` 900×562 をPILで簡易生成可
- `systems.html` / `works.html` へのカード追加は全6本できてから一括でOK

---

## 1. GENBA（ゲンバ）`works-genba.html`
- 領域: 建設・現場OS
- 印象: 安全黄 × charcoal × concrete。角小さめ工業UI
- 色: `#EAB308` / `#1C1917` / `#F5F5F4` / hazard `#F97316`
- 書体: IBM Plex Sans JP + Mono
- 画面: Dashboard / 現場一覧 / 現場詳細（写真ボード+AI是正・日報下書き）/ 出来高突合 / 設定
- AI演出: 「AIで写真を点検」→スキャン→finding順出→日報・是正下書きタイピング。「人が確認」バッジ
- データ: 工務店、現場6〜8件（港区改修・相模原新築など）

## 2. HANKYO（ハンキョウ）`works-hankyo.html`
- 領域: 不動産・反響CRM
- 印象: ネイビー×金の不動産営業デスク。タイムライン追客が主役
- 色: `#0B2447` / `#C9A227` / `#EEF3F9`
- 書体: Noto Sans JP + Noto Serif JP（物件名・SLA）
- 画面: Dashboard（SLA KPI）/ 反響受信箱 / 反響詳細（SLAタイマー+返信下書き+Day3/7/14追客）/ 物件メモ / 設定
- AI演出: 反響選択→一次返信下書き生成→追客シーケンス3通をタブ切替
- データ: 反響8〜10件（内見・査定・賃貸）

## 3. BRIEF（ブリーフ）`works-brief.html`
- 領域: BtoB営業ワークスペース
- 印象: ダークエディトリアル。提案スライド感
- 色: `#0F172A` / `#38BDF8` / `#F8FAFC`
- 書体: Noto Serif JP見出し + Sans UI
- 画面: Dashboard / 案件一覧 / 案件詳細（リサーチブリーフ1枚+提案アウトライン+議事録下書き）/ テンプレ庫 / 設定
- AI演出: 「商談ブリーフ生成」→企業要点カード→論点リスト→提案章立て出現
- データ: IT商材営業、案件6〜8件

## 4. KITEI（キテイ）`works-kitei.html`
- 領域: 規程・稟議
- 印象: 官公庁寄りクリア。グレー×藍。出典リンクが主役
- 色: `#1E3A5F` / `#64748B` / `#F1F5F9` / accent `#2563EB`
- 書体: Noto Serif JP（条文）+ Sans
- 画面: Dashboard / 規程検索 / 検索結果詳細（出典ハイライト+回答）/ 稟議下書き / 設定
- AI演出: 質問入力（サンプルチップ）→出典付き回答→稟議書下書き生成
- データ: 就業規則・稟議規程・出張規程の擬似条文

## 5. SAIYO（サイヨウ）`works-saiyo.html`
- 領域: 採用デスク
- 印象: 明るめヒューマン。ラベンダー×白。カード中心
- 色: `#7C3AED` / `#F5F3FF` / `#FFFFFF` / ink `#1F1635`
- 書体: M PLUS Rounded 1c
- 画面: Dashboard / 求人一覧 / 候補者詳細（面接メモ→評価表AI）/ 求人下書き / 設定
- AI演出: 面接メモから評価表・不採用/通過メール下書き生成
- データ: 候補者6〜8名・求人3本

## 6. SHAIN（シャイン）`works-shain.html`
- 領域: 社内FAQ / オンボーディング
- 印象: ソフトグリーン×白。Wiki/ヘルプセンター
- 色: `#059669` / `#ECFDF5` / `#FFFFFF` / ink `#064E3B`
- 書体: Noto Sans JP（丸みは控えめ）
- 画面: Dashboard / 質問受信箱 / スレッド（社内FAQ回答+出典）/ ナレッジ記事リスト / 設定
- AI演出: 新人質問→規程/マニュアル出典→回答下書き→ナレッジ追加カード
- データ: 社内質問8件、記事6本（休暇・経費・PC・入館など）

---

## 差別化ルール
既存3本とシェルを被せない:
- KAWASU=象牙×朱印 Legal
- SOROBAN=ledger green 帳票
- MIMIYORI=coral チャット
- GENBA=安全黄 industrial
- HANKYO=紺金 CRM
- BRIEF=ダーク編集
- KITEI=藍グレー 条文
- SAIYO=紫ラウンド 採用
- SHAIN=緑 Wiki

## 完了定義（各ファイル）
- ログインできる
- 主要画面をhashで切替できる
- AI演出が1本以上動く
- モバイルでsidebar開閉できる
- コミットメッセージ例: `🏗️ feat: GENBA現場OSのSaaS級デモを追加`
