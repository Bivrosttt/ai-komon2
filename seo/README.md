# AI顧問室 SEO factory

無料ツールSEOを、調査・候補化・監査・改善のループとして運用するための土台。
未レビューのページを自動公開しないことを前提に、毎日「次に作るべきもの」と「直すべきもの」を出力する。

## ローカル実行

```bash
python3 seo/scripts/run_daily.py --root .
```

実行結果は `seo/data/runs/YYYY-MM-DD/` に出る。候補、CSV、サイト監査、Search Console取り込み結果、当日の作業ブリーフを確認する。

ラッコキーワードAPIを使う場合だけ環境変数を設定する。未設定でもGoogle/Bing/YouTubeの無料サジェストで動く。

```bash
export RAKKO_KEYWORD_API_KEY='...'
python3 seo/scripts/run_daily.py --root .
```

## 日次ループ

1. `research_sources.py` が複数ソースの候補語を取得する。
2. `score_candidates.py` が正規化・重複除去・検索意図推定・ツール適性/サービス適合度を付ける。
3. `site_audit.py` が既存HTMLのtitle、description、canonical、H1、OGP、内部リンクを検査する。
4. Search ConsoleのCSVが `seo/data/gsc/latest.csv` にあれば `import_gsc.py` が実績ベースの改善候補を追加する。
5. `run_daily.py` が上位候補と改善タスクを `daily-brief.md` にまとめる。
6. 人が候補をレビューしてから、ページ実装・テスト・PR・デプロイを行う。

## データソースの扱い

- サジェストは意図の発見用で、検索数ではない。
- Google Trendsは相対的な傾向確認用。
- Googleキーワードプランナー/aramakijake等の検索数は、取得日と推定値であることを記録する。
- Search Consoleは自社サイトに実際に表示された検索語なので、公開後の改善では最優先する。
- APIキー、OAuthトークン、個人情報をリポジトリに保存しない。

Google Trends、Googleキーワードプランナー、aramakijake等に公式APIがない/制限がある場合は、CSVを `seo/data/manual/` に置く。`keyword` / `query` / `term` / `キーワード` のいずれかの列を読み込み、ファイル名をデータソース名として候補に残す。これでブラウザで無料調査した結果も同じスコアリングに合流できる。

## 手動運用の境界

日次実行は手動で行う。`python3 seo/scripts/run_daily.py --root .` を実行してから、候補の検索意図・ツールとしての実用性・既存ページとの重複を確認する。自動生成ページを即時公開せず、人がレビューしてから実装・テスト・デプロイする。
