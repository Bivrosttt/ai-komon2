# SEO記事運用インデックス

## 比較記事

実在サービスの比較記事は、ルールとチェックリストを分けずに次のスキルで実行します。

- [比較記事スキル（唯一の正本）](../../../skills/noimos-comparison-article/SKILL.md)
- [比較記事スキルの補足README](../../../skills/noimos-comparison-article/README.md)
- [比較記事の案件TODO・調査証跡](ai-service-comparisons/)
- [3記事の公開・検証README](ai-service-comparisons/README.md)
- [リライトTODOの実例](ai-service-comparisons/COMPARISON-REWRITE-TODO-2026-07-31.md)

`ai-service-comparisons/`には、AI動画、AIコーディング、AI議事録の各記事について、ブリーフ、リサーチ、価格/usage入力、claim ledger、公式ホーム画面台帳、本文スナップショット、バリデーション、品質レポートをまとめています。

## 一般SEO/GEO記事

- [一般SEO/GEO記事スキル](../../../skills/noimos-seo-geo-article/SKILL.md)
- 一般記事の案件別TODO・検証結果はこのディレクトリ直下と`refresh-validation/`にあります。

## ファイルの見分け方

- `skills/.../SKILL.md`: 全案件で共有するルール。ここが唯一の正本
- `*-TODO-YYYY-MM-DD.md`: その案件の作業チェックリスト
- `*-brief.md` / `*-research.md` / `*-claims.json` / `*-pricing.csv`: 調査入力と根拠
- `*-screenshots.json` と`home-screens/`: 公式ホーム画面の取得台帳と画像
- `*-validation.json` / `*-quality-report.json`: 自動検証の出力
- `archive/`: 過去の参照メモ。新規記事の作業対象ではない
