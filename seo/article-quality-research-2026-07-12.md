# SEO記事の量・構成・図解に関する調査記録

調査日: 2026-07-12

## 結論

文字数だけで順位は決まらない。Googleは固定の最低文字数・最適文字数を否定しており、検索意図を満たす十分な網羅性、独自性、信頼性を重視している。

ただし、今回のAI顧問室の主題は「AI導入」「業務効率化」「営業効率化」のように検索意図が広い。現在の新規10記事は本文約1,448〜1,898字で、短い疑問への回答としては成立するが、導入判断や比較を支える本命記事としては不足しやすい。今後は4,000〜6,000字を制作目安にし、競合と検索意図に応じて上下する。

## 現在の記事の計測

| 対象 | 本文文字数 | 図解画像 | 評価 |
|---|---:|---:|---|
| 新規10本 | 1,448〜1,898字 | 0点 | 入口記事としては可。本命記事としては薄い |
| 既存2本 | 2,035〜2,845字 | 各2点 | 新規10本より厚いが、追加改善余地あり |

## 文字数の判断

1. **狭い疑問・用語解説**: 2,000〜3,500字
2. **手順・比較・導入判断**: 4,000〜6,000字
3. **広いテーマの基幹記事**: 6,000〜9,000字

これはGoogleの評価基準ではなく、読者が再検索しなくて済む情報量を確保するための制作基準である。上位10ページの平均値は、論点の抜けを発見するためにだけ使い、平均文字数への機械的な追従はしない。

## 推奨構成

`検索意図の明示 → 結論 → 判断基準 → 手順/比較 → 具体例 → 図解 → 失敗・限界 → ツール/CTA → FAQ → まとめ・出典`

業務改善系では、単なる一般論より以下を優先する。

- どの業務から始めるか
- 何を入力してよいか
- 誰が確認するか
- 失敗したときに何を戻すか
- どの数字で効果を測るか
- AIに任せない範囲はどこか

## 図解の判断

Googleは、画像を関連する本文の近くに置き、標準の`img`要素、説明的なファイル名、altテキストを使うことを推奨している。図解そのものが順位を保証するわけではないが、業務フロー・比較・判断基準を一目で理解させるため、AI顧問室の記事では1記事1点以上を必須にする。

画像生成AIには構図や図の土台を作らせ、正確な日本語ラベル・数値・条件はHTML/SVG・表・本文で保持する。画像内の誤字が意味を変える記事では、生成画像だけを唯一の説明にしない。

## FAQ・AI検索

FAQは読者の追加疑問を解決する本文として有効だが、Googleは2026年5月7日以降FAQリッチリザルトの表示を終了している。FAQPage JSON-LDを入れること自体を主要なSEO施策にしない。結論・定義・手順・出典を、HTMLのテキストとして明確にする。

GoogleのAI Overviews / AI Modeにも追加の特別な最適化はなく、通常のSEO基礎、クロール可能性、内部リンク、重要情報のテキスト化、関連する高品質画像、可視本文と一致する構造化データが基本となる。

## 参照ソース

- Google Search Central, [Creating Helpful, Reliable, People-First Content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content), retrieved 2026-07-12
- Google Search Central, [SEO Starter Guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide), retrieved 2026-07-12
- Google Search Central, [Google Images SEO Best Practices](https://developers.google.com/search/docs/appearance/google-images), retrieved 2026-07-12
- Google Search Central, [AI features and your website](https://developers.google.com/search/docs/appearance/ai-features), retrieved 2026-07-12
- Google Search Central, [Article structured data](https://developers.google.com/search/docs/appearance/structured-data/article), retrieved 2026-07-12
- Google Search Central, [Structured data markup supported in Search](https://developers.google.com/search/docs/appearance/structured-data/search-gallery), retrieved 2026-07-12
- Orbit Media, [Guest Blogging Guidelines](https://www.orbitmedia.com/guidelines/), retrieved 2026-07-12
- MarketingProfs, [Blogging Benchmarks for 2025](https://www.marketingprofs.com/charts/2025/53736/blogging-benchmarks-2025-word-count-frequency-study-orbit-media), retrieved 2026-07-12
- 株式会社プリンシプル, [SEO記事の最適な文字数](https://www.principle-c.com/column/seo-content-length-guide/), retrieved 2026-07-12
