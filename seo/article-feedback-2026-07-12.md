# SEO記事フィードバックループ記録

実施日: 2026-07-12

## 今回の実施内容

既存のSEO記事12本を、`seo/article-rules.md` と調査記録に照らして1周レビューした。

- 10本の新規記事に、記事固有のAI生成図解を1点ずつ追加
- 各図解を結論ボックス直後に配置し、`img`、説明的な`alt`、`figcaption`を付与
- 各記事に、導入条件、確認者、例外時の戻し方、効果測定、運用チェックの説明を追加
- FAQ、CTA、出典、関連記事の導線を確認
- サイト監査、ローカルリンク、Python構文を再確認

## 改善後の計測

本文文字数はHTMLの`main`内から`script`、`style`、`noscript`を除いて計測した。文字数は順位を保証する基準ではなく、検索意図を満たす量を判断するための制作目安である。

| 記事 | 本文文字数 | H2 | 図解 | 内部リンク |
|---|---:|---:|---:|---:|
| AI活用事例 | 2,697 | 13 | 1 | 18 |
| AI導入のメリット | 2,690 | 12 | 1 | 19 |
| AI導入のリスク | 2,963 | 11 | 1 | 12 |
| AI導入の進め方 | 2,671 | 12 | 1 | 16 |
| 採用業務のAI効率化 | 2,712 | 12 | 1 | 15 |
| AI導入の費用対効果 | 2,700 | 12 | 1 | 15 |
| 業務効率化のアイデア | 2,682 | 11 | 1 | 12 |
| 見積書作成の時間削減 | 2,568 | 12 | 1 | 13 |
| 生成AIの社内利用ルール | 2,974 | 12 | 1 | 10 |
| 議事録をAIで効率化 | 2,928 | 9 | 2 | 13 |
| 議事録の書き方 | 2,094 | 8 | 2 | 12 |
| 営業効率化の方法 | 2,624 | 12 | 1 | 15 |

## 判定

- 記事ページ: 12本
- 図解あり: 12本
- `alt` / `figcaption`: 12本
- 記事ページの監査エラー: 0件
- 記事ページのローカルリンク切れ: 0件
- `site_audit.py` の構文チェック: pass
- `git diff --check`: pass

サイト全体の監査は115 HTMLページを対象に129件の既存課題を検出した。主に記事以外のLP・デモ等にあるcanonical、OGP、meta descriptionの不足であり、今回の12記事には該当しない。

## 次の改善ループ

今回の1周で、入口記事としての情報量と実務判断材料は増えた。ただし、`AI導入の進め方`、`営業効率化`、`業務効率化`のような広い検索意図の記事は、現在2,600〜3,000字前後であり、制作目安の4,000〜6,000字にはまだ届いていない。

次周では水増しを避け、以下を追加する。

1. 読者が迷うケース別の比較表
2. 想定例と実測値を分けた具体例
3. 導入前後の測定テンプレート
4. 失敗した場合の切り戻し手順
5. 関連記事を束ねるハブ記事と検索意図別の内部リンク

## 参照した基準

- [AI顧問室 SEO記事 制作ルール](article-rules.md)
- [SEO記事の量・構成・図解に関する調査記録](article-quality-research-2026-07-12.md)
- [Google Search Central: Creating helpful, reliable, people-first content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)
- [Google Search Central: SEO Starter Guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide)
- [Google Search Central: Google Images SEO best practices](https://developers.google.com/search/docs/appearance/google-images)
