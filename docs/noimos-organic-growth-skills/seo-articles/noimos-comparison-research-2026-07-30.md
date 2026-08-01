# Noimos比較記事の再調査メモ（2026-07-30）

## 結論

今回確認した4本は、精密な図解を中心にした記事ではなく、検索者が比較・選定できる情報構造を中心にした記事だった。画像は記事テーマを伝えるサムネイルとして機能し、SEO/GEO上の主な価値は、検索意図に合う見出し、評価軸、比較表、FAQ、更新情報、内部・外部リンクにある。

## 対象ページ

- [Best Dental Marketing Tools in 2026](https://noimosai.com/en/blog/best-dental-marketing-tools-in-2026-the-ultimate-guide-to-practice-growth-and-automation)
- [10 Best AI Agents for Lead Generation in 2026](https://noimosai.com/en/blog/10-best-ai-agents-for-lead-generation-in-2026)
- [Top 7 AI Agents for Content Strategy in 2026](https://noimosai.com/en/blog/top-7-ai-agents-for-content-strategy-in-2026-the-shift-to-autonomous-content-engines)
- [Best AI CMO for Solopreneur in 2026](https://noimosai.com/en/blog/best-ai-cmo-for-solopreneur-top-5-autonomous-marketing-platforms-in-2026)

## 抽出した共通パターン

1. **商用比較クエリをタイトルで明示:** `Best/Top + 対象 + 2026` の形で、比較・購入検討の意図と鮮度を同時に伝える。
2. **冒頭でKey Takeaways:** 4点前後の要約を置き、読者が本文を読む価値と結論を先に判断できる。
3. **比較軸を先に定義:** 自律性、統合、データ品質、セキュリティ、GEO、価格モデルなど、後段の各サービス評価に使う物差しを先に提示する。
4. **候補ごとの同じフォーマット:** `Best For / Core Features / Pricing / Pros / Cons / Verdict` のように、各候補の説明順をそろえる。
5. **比較表で横並びにする:** 本文の長い説明を、用途、強み、価格、特徴、公式リンクの表へ圧縮する。
6. **選び方の手順を置く:** ボトルネック特定、既存システム互換性、社内運用能力など、比較後の意思決定を3段階程度にする。
7. **FAQでロングテールを回収:** 定義、違い、セキュリティ、連携、導入条件を質問形式で明示する。
8. **更新日・著者・CTA:** 記事の鮮度と責任主体を表示し、FAQ後とフッター付近に無料導線を置く。
9. **サムネイルはシンプル:** 大きな画像はテーマとブランドを伝える役割で、本文の比較ロジックを図解していない。コード生成SVG/CSSで十分に代替できる。
10. **サイドレール:** 左側に目次、中央に本文、右側に短いCTAを配置し、長文でも「現在地」と「次の行動」を固定する。

## どこがSEO/GEOに効くか

| 要素 | SEOに効く理由 | GEO/読者体験への効果 | 実装判断 |
|---|---|---|---|
| タイトルの対象・比較・年 | クエリと検索意図の一致を明示 | 回答エンジンがページ主題を要約しやすい | 年は実際の更新日と整合させる |
| Key Takeaways | 冒頭の情報密度と主要語の明示 | 引用候補となる短い結論を作る | 記事固有の3〜5点にする |
| 評価軸 | 関連語・エンティティ・判断条件を網羅 | 「なぜその順位か」を説明できる | 先に軸を定義し全候補へ適用 |
| 同じ候補フォーマット | 見出し階層と反復語で比較意図を補強 | 各候補を同じ粒度で要約できる | Best For等の見出しを固定 |
| 比較表 | 構造化された比較情報を提供 | 抽出・引用・意思決定が速い | モバイルは横スクロール対応 |
| FAQ | 質問型ロングテールを自然に含める | 回答エンジンがQ&A単位で理解しやすい | FAQPageは表示保証と誤解しない |
| 更新日・出典 | 鮮度と主張の根拠を示す | 主張と出典を分けて評価できる | 価格・仕様は公式確認を促す |
| 内部リンク・CTA | 関連ページと次の行動を接続 | 読者のタスク完了を助ける | 比較→診断→相談の順で設計 |
| サムネイル | 画像検索・SNS共有・第一印象を補助 | ページテーマを視覚的に示す | 詳細図解は必要な記事だけ |
| 左目次・右CTA | 直接の順位要因ではないが離脱と回遊を支援 | 長文の現在地と行動を固定 | 1180px以上で3カラム、モバイルは1カラム |

## 比較記事の量が多い理由

4本とも `best/top` と複数候補の選定を中心にしており、Noimosのブログは比較・購入検討フェーズを強く狙っていると判断できる。ただし、比較記事だけでは検索意図が偏るため、比較の前後に「費用」「導入手順」「リスク」「個別業務」の記事を内部リンクでつなぐ必要がある。

## 今回の実装

- 新規記事: `/articles/ai-marketing-tools-comparison/`
- CSS生成SVGサムネイル: `ai-marketing-tools-comparison-thumbnail.svg`
- 比較対象は製品の断定的なランキングではなく、オールインワン、CRM連携、SEO/GEO、ブランド運用、業務自動化の5タイプに整理。
- 料金は変動しやすいため、固定価格ランキングを避け、初期費用・従量費・社内工数・追加改修まで含む比較軸にした。
- サイドバーは共通CSSで、デスクトップは左目次・中央本文・右CTA、モバイルは1カラムへ切り替える。

## 注意点

- 参照記事内の市場データ・価格・機能説明は、公開日時点の主張であり、当社の検証済み事実とは分けて扱う。
- 比較表に記載する製品仕様や価格は、公開前に各社公式ページと対象プランを再確認する。
- 比較記事で自社を推奨する場合も、向かないケース、確認点、停止条件を併記して信頼性を保つ。

## 実画像の確認と量産ツール

参照4ページのOG画像をダウンロードして目視確認した。いずれも900×506のPNGで、文字や長い説明はなく、背景の形状・色・中央の白いアイコンだけが違っていた。

- 保存先（ローカル確認用）: `tmp/noimos-reference-thumbnails/`
- `dental.png`: 水色の斜線背景 + 白い地球アイコン
- `lead-generation.png`: 深い緑の曲線背景 + 白い地球アイコン
- `content-strategy.png`: 青い曲線背景 + 白い棒グラフアイコン
- `ai-cmo.png`: 紫の斜線背景 + 白い雲アイコン

当社では、参照画像をそのまま再配布せず、同じ設計原則をオリジナルSVGとして量産する。

```bash
python3 scripts/generate_article_thumbnail.py \
  --output articles/<slug>/<slug>-thumbnail.svg \
  --icon sparkles --palette purple --shape diagonal --seed <slug>
```

利用可能なアイコンは `globe / cloud / bars / sparkles / bot / heart / megaphone`、背景は `diagonal / arcs / waves / rays / blobs`。slugをseedにすることで、記事ごとに背景形状を変えながら再現可能なサムネイルを生成できる。

今回の比較記事は、参照したAI CMO画像に寄せて `cloud + purple + diagonal` で生成し、アイコン上部を白、下部を淡い紫へ落とすグラデーションにした。
