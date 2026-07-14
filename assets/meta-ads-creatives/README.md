# AI顧問室 Meta広告クリエイティブ

AI顧問室のMeta広告用クリエイティブを、レビュー・選定・入稿準備のために集約するフォルダです。

## 構成

- `current/json-first-5/`：2026-07-13生成の最新5案
- `current/meta-ads-basic-4/`：基本訴求4案
- `current/lp-top5-5/`：LPトップ5連動5案
- `current/design-exploration-6/`：デザイン方向探索6案
- `current/news-tv/`：テレビニュースをスマホ撮影したような意外性訴求
- `current/reaction-first-10/`：既存案を消化して作った停止力・クリック意欲重視の10案
- `current/additional-5-2026-07-14/`：構成を分けた追加バリエーション5案
- `archive/complete-a-to-c-9/`：過去のA1〜C3完成版9案
- `archive/initial-six-6/`：過去の初回6案
- `contact-sheets/`：各セットの一覧確認用コンタクトシート
- `ideas/ai-komon-meta-creative-ideas-30.md`：次回以降の意外性クリエイティブ案30個
- `ideas/reaction-first-creative-strategy-v2.md`：反応重視の戦略、視点別30案、初回テスト優先順位
- `ideas/reaction-first-creative-strategy-v3.md`：停止力・クリック欲を最優先にした昇華案、残す案、降格案、初回6本

広告フォーマットをさらに広げるため、25種類の広告ファミリーから作った [Ads Explorerのプロンプトウォール](</Users/koki/Desktop/ai-komon2/outputs/imagegen/ai-komon-meta-ads-explorer-25/prompts-manifest.json>) も用意しています。まだ画像生成はしていないため、まずはこの中から反応検証する型を選びます。

## 現在の枚数

- 現行・探索セット：20枚
- 今回追加したニュース番組型：1枚
- Reaction First 10：10案＋追加比較差分8枚
- 追加構成バリエーション：5枚
- 過去アーカイブ：15枚
- 合計：59枚

コンタクトシートや生成途中のサムネイルは広告枚数に含めていません。元データはリポジトリ内の既存 `outputs/` とDownloads側に残しています。

## 運用ルール

1. 新しく生成した本命候補は `current/` に追加する。
2. 配信終了・比較用の案は削除せず `archive/` に移す。
3. 画像単体だけでなく、訴求軸と遷移先LPを企画メモに残す。
4. 初期の停止力テストでは価格を入れず、CTA・LP側の表現が一致しているか確認する。価格訴求は高意向層向けの後段テストに分ける。
