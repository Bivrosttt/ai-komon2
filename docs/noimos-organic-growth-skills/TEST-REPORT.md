# Noimos Organic Growth Skills — 実装・検証レポート

実施日: 2026-07-30

対象: `/Users/koki/Desktop/ai-komon2`

結論: 9スキルを実装し、成功・失敗・AI-only承認待ちを含む再現可能な試験を完了した。外部公開、SNS投稿、広告・予算変更は実行していない。

## 実装したスキル

| # | スキル | 主な責務 | 試験結果 |
|---|---|---|---|
| 1 | `noimos-growth-foundation` | SEO/GEO、計測、訴求、CTA、モバイルFVの監査 | 実サイトで9件PASS、2件FAIL。canonicalとJSON-LD不足を検出 |
| 2 | `noimos-commercial-keywords` | 商用意図、需要、難易度、カニバリを分離して優先順位化 | 合成データ試験PASS。ライブ候補では「AI顧問 比較」を第1候補化 |
| 3 | `noimos-seo-geo-article` | SERP差分、回答先出し、出典、FAQ、構造化データを持つ記事制作 | 4,052字の記事を試作。構造チェッカー100点、品質ゲートPASS |
| 4 | `noimos-content-refresh` | GSC・鮮度・構造・競合差分から更新キューを作る | 実記事25本を走査。薄い意思決定情報の候補2本を検出 |
| 5 | `noimos-social-trend-mining` | 直近性、独立投稿者、反復フォーマット、商品適合を評価 | LinkedInの4投稿で手順型フォーマットの反復を確認。合成マルチSNS試験PASS |
| 6 | `noimos-social-conversion-content` | X、LinkedIn、短尺UGC向けのCV投稿を生成・検査 | 3形式の構造試験は全て100点。実績主張入り案は品質ゲートでBLOCK |
| 7 | `noimos-always-on-agent` | 収集からAI-only品質承認・学習までを継続ジョブ化 | 7日間ドライランで6実行、AI公開許可1件、外部実行0件 |
| 8 | `noimos-algorithm-adaptation` | 基準期間と直近期間を比較し、下落・上昇・ノイズを分類 | 合成時系列で下落1、上昇1、ノイズ1を正しく分類 |
| 9 | `noimos-content-quality-gate` | 出典、ブランド、具体性、重複、AI-only承認ポリシーを公開前に検査 | 高品質例PASS、低品質例BLOCK、未検証ARR投稿BLOCK |

各スキルは `skills/noimos-*/SKILL.md` にあり、`~/.codex/skills/` へシンボリックリンクを作成した。次回以降はスキル名で呼び出せる。

## 1. 成長基盤構築

実ファイル `AI顧問/index.html` とローカル表示を監査した。

- PASS: title、description、viewport、単一H1、OGP、CTA、robots.txt、sitemap.xml、llms.txt
- P0 FAIL: canonical未設定、JSON-LD未設定
- 390×844、1280×800で目視し、横スクロールは0px。モバイルFV内に主要CTAが表示された
- 計測タグはソース上の存在のみを確認した。GA/Meta側での受信やイベント到達はログインなしでは未確認

証跡:

- `test-runs/foundation-audit.json`
- `test-runs/site-evidence/mobile-390x844.png`
- `test-runs/site-evidence/desktop-1280x800.png`

次の修正候補は、トップページのcanonicalと `Organization` / `WebSite` JSON-LD追加。今回はスキル作成と試験が対象のため、本番ファイル自体は変更していない。

## 2. 商用キーワード選定

順位付けは、商用意図を先にゲートし、検索需要・難易度・事業適合・カニバリを別々に扱う。

ライブ候補:

1. `AI顧問 比較` — 81.3
2. `AI顧問 費用` — 80.5
3. `AI導入支援会社 比較` — 79.0

公開SERPの構成と競合密度を代理指標にした。Semrush等の検索ボリュームと難易度は接続されていないため `null` のまま保存し、推測値は入れていない。採用クラスタは `AI顧問 比較`。

証跡:

- `test-runs/live-keywords.csv`
- `test-runs/live-keyword-ranking.json`
- `test-runs/keyword-ranking.json`

## 3. SEO/GEO記事

「AI顧問 比較」を対象に、競合の情報構造を確認してから独自記事を作った。37Design、SHIFT AI、GXOの比較記事を調査し、費用・種類・選び方に加えて、Human-in-the-Loop、責任分界、向く企業・向かない企業を独自の意思決定論点として追加した。

成果物:

- `test-runs/article/ai-advisor-comparison.md`
- `test-runs/article/ai-advisor-comparison.html`
- `test-runs/article/ai-advisor-comparison.pdf`
- `test-runs/article/ai-advisor-comparison-diagram.png`

検証結果:

- 4,052字
- Article + BreadcrumbList、canonical、OGP、著者、更新日、FAQ、比較表、内部リンク、外部出典、CTAを検出
- 記事チェッカー100点
- 品質ゲートPASS
- 390px、768px、1280pxで横オーバーフロー0
- 初回の長いURLによる横崩れを検出し、折返しと表の内部スクロールを追加して再検証
- 固有図解の文字と内容を目視確認

記事の著者表示は組織著者「AI顧問室 編集部」としている。AI-only運用では実名レビュアーを公開条件にしないが、公開後の信頼性向上施策として著者プロフィールを追加する余地はある。

## 4. 記事更新

既存記事25本を走査し、構造、更新日、内容量、リンク、重複を確認した。

- 優先候補: `articles/gijiroku-template/index.html`
- 優先候補: `articles/internal-faq-howto/index.html`
- 理由: 意思決定を助ける具体情報が薄い
- 実記事は新しく、経年だけを理由に全改稿する対象はなかった
- 180日経過記事を含む合成試験では、古さと下落の組み合わせを正しく高優先度化

証跡: `test-runs/content-refresh-queue.json`

## 5. SNSトレンド

2026-07-30時点で直近7日境界のLinkedIn公開投稿4件を確認し、`step_by_step_playbook` が複数投稿者で反復していることを検出した。公開画面では閲覧・いいね・シェアを十分取得できなかったため、これは「フォーマット反復」の証拠であり、「バズ」の実証ではない。

TikTokは公開検索のrobots制約、YouTube Shortsは対象期間内の十分な比較標本不足を記録した。LinkedIn、X、Instagramを含む合成データでは、複数プラットフォームのクラスタリングと順位を検証した。

証跡:

- `test-runs/live-social-observations.json`
- `test-runs/live-trend-score.json`
- `test-runs/trend-synthetic-score.json`

## 6. SNS投稿

NoimosAIの9手順を題材に、LinkedIn、X、TikTok/UGCの3案を作成した。構成チェッカーは全て100点。

ただし、LinkedIn案に含めた「30日以下で$1M ARR」「広告費0円」の主張は、今回の入力以外に確認可能な出典URLがない。品質ゲートは次の2理由で公開をBLOCKした。

1. 実績主張の `source_url` と検証状態が不足
2. 人の最終承認が未記録

これは期待どおりの安全動作。出典が確認できるまでは、数値を使わないX案か、検証過程を見せるUGC案を採用する。

証跡:

- `test-runs/social-content-live.json`
- `test-runs/social-content-live-score.json`
- `test-runs/social-quality-block.json`

## 7. 継続運用エージェント

収集、分析、下書き、品質検査、承認、公開後学習を別ジョブとして定義した。2026-08-03開始の1週間をドライランした結果:

- スケジュール実行: 6
- 人への承認ハンドオフ: 1
- 外部公開・送信: 0
- 重複防止キー、再試行、入力スナップショット、成果物保存を確認

証跡: `test-runs/agent-dry-run.json`

## 8. アルゴリズム変化への適応

14日基準期間と7日直近期間を比較する合成データで検証した。

- material loss: 1件
- material gain: 1件
- stable/noise: 1件
- insufficient data: 0件

下落例では日次クリック -66.67%、日次表示回数 -40%、平均順位 +3悪化、CV減少を同時検出した。これは更新やアルゴリズム変更との相関候補であり、原因の証明ではない。修正案はAI-only品質ゲートとロールバック条件を通過してから実行する。

証跡: `test-runs/algorithm-incidents.json`

## 9. AI Slop品質ゲート

3原則を機械検査と承認記録に落とし込んだ。

1. 自社データと市場データ: 主張台帳の出典・取得日・検証状態を確認
2. Brand Memory: 対象読者、禁止表現、承認済みCTA、トーンを確認
3. Human-in-the-Loop: 承認状態、レビュアー、確認時刻を確認

試験結果:

- 高品質記事: PASS
- 低品質例: 7 blocker + 1 warningでBLOCK
- Noimos実績入りSNS案: 2 blockerでBLOCK

検出項目には、未出典数値、一般論の水増し、プレースホルダー、対象読者の欠落、未承認CTA、具体性不足、承認欠落が含まれる。

証跡:

- `test-runs/quality/pass-report.json`
- `test-runs/quality/block-report.json`
- `test-runs/article/article-quality-report.json`

## 統合試験と自動テスト

制作ループ `1 → 2 → 3 → 5 → 6 → 7` と、改善ループ `4 → 8 → 3/6` を成果物とJSON契約で接続した。全ての公開候補は最終的に9の品質ゲートとAI-only承認ポリシーへ入る。

実行コマンド:

```bash
python3 -m unittest discover -s tests -p 'test_noimos_skills.py' -v
python3 -m py_compile skills/noimos-*/scripts/*.py
git diff --check -- skills docs/noimos-organic-growth-skills tests/test_noimos_skills.py tests/fixtures/noimos
```

自動テストは9件で、各スキルの成功・失敗・境界条件を1件以上含む。

## 現時点の判断

実装と安全なドライランは完了。運用開始前に必要なのは次の4点。

1. トップページへcanonicalとJSON-LDを追加（完了）
2. GSCとSemrush等を接続し、代理指標を実測値へ置換
3. NoimosAIのARR・広告費実績について確認可能な一次証拠URLを登録
4. AI-only承認レコードをCI/CDへ接続し、公開後のGSC監視を自動化

2〜4が未接続でも、今回のローカルAI-onlyゲートは完了している。公開後の計測と一次証拠の追加は、品質を継続的に高める運用タスクとして残る。
