---
name: noimos-seo-geo-article
description: Research, outline, write, validate, and prepare commercial-intent articles for Google search and AI citation surfaces without copying competitors or inventing evidence. Use for SEO/GEO articles, comparison content, buying guides, AI-search optimization, or article publication preparation.
user-invokable: true
argument-hint: "<keyword-or-brief>"
license: MIT
---

# Noimos SEO/GEO Article

Create the best decision aid for the reader, not a longer paraphrase of the
SERP. Publication is a separate action gated by the configured approval policy.
The default is human review; an explicit `ai_only` policy is valid only when
the deterministic quality gate and render checks are all recorded as true.

## Required inputs

- Approved keyword cluster and page brief.
- Audience, product, CTA, brand rules, author, and publication format.
- Existing pages and first-party evidence.

## Checklist

### 1. SERP evidence

- [ ] Search the primary query and record retrieval date, country, language, and
  device.
- [ ] Review 2-5 public top-result candidates.
- [ ] Record intent, content type, decision criteria, structure, sources,
  recency, visuals, trust signals, and CTA placement.
- [ ] Save reusable information architecture only. Do not copy wording,
  screenshots, logos, imagery, HTML, CSS, or exact visual treatment.
- [ ] List gaps, contradictions, and questions competitors leave unanswered.

### 2. Evidence and originality

- [ ] Build a claim ledger: `claim | source | date | scope | confidence`.
- [ ] Prefer first-party data and primary sources.
- [ ] Mark company experience as verified first-party, supplied-but-unverified,
  or hypothetical.
- [ ] Remove unsupported numbers and superlatives.
- [ ] Define at least two information-gain elements: original data, tested
  workflow, decision matrix, failure conditions, or practitioner observation.

### 3. Outline and draft

- [ ] Match the actual intent: comparison, purchase guide, procedure, or
  decision page.
- [ ] Put the answer and decision rule before background explanation.
- [ ] Use a clear H1, 4-7 H2 sections, comparison/decision table, limitations,
  next action, visible FAQ, sources, and update date.
- [ ] Add 3-8 contextual internal links and 2-5 authoritative external links.
- [ ] Keep one focused CTA after value delivery.
- [ ] Add an article-specific visual cover with `img`, descriptive `alt`, and
  `figcaption`. A detailed diagram is optional; for comparison or guide pages,
  a code-generated SVG/CSS thumbnail is sufficient when it communicates the
  topic without fabricated data.
- [ ] Include Article and Breadcrumb JSON-LD that matches visible content.
- [ ] Treat FAQ as reader content; never promise a rich result.

### 4. Noimos構造チェック（今回の既存記事改善で得た標準）

- [ ] 既存記事を先に棚卸しし、URL・canonical・リダイレクト・公開日を変更せずに不足要素だけを補う。
- [ ] 記事冒頭に、読者が最初に判断できる結論（`.answer`）を置く。
- [ ] 結論の直後に、記事固有の3点要約（`.key-points`）を置く。一般論の使い回しではなく、本文の判断材料を要約する。
- [ ] H2にIDを付けた目次（`.toc`）を置き、目次のリンク先が実在することを確認する。
- [ ] 記事固有の図解または画像を1点以上置く。写真・図解のヒーローが既にある場合は、同じ視覚要素を重複追加しない。
- [ ] 手順記事には、前・中・後または入力・処理・確認の3ステップ（`.steps`）を置く。
- [ ] 表はモバイルで横溢れしないよう `.table-scroll` で包み、`role="region"`、`aria-label`、`tabindex="0"` を付ける。
- [ ] CTAは価値提供後に1つ置き、関連記事（`.related`）で次の比較・診断・相談行動へ接続する。
- [ ] FAQ、一次情報の出典、更新日、著者、Article/Breadcrumb JSON-LDの内容を画面表示と一致させる。
- [ ] 薄い記事を無理に量産せず、実務表・失敗条件・確認手順など独自の意思決定材料を追加してから公開する。

### 5. 自動化・更新チェック

- [ ] 変更前にベースライン（文字量、要素の有無、リンク切れ）を保存し、変更理由・仮説・対象指標・レビュー日をTODOに記録する。
- [ ] 過去記事の改善は削除・一括リダイレクトで済ませず、記事単位の変更とロールバック方法を残す。
- [ ] 繰り返し適用する構造は、再実行しても二重挿入しないマーカー付きスクリプトにする。
- [ ] 変更後に、記事ディレクトリ全体の要素充足率を再計測し、対象外にした要素（既存画像ヒーローなど）を明記する。
- [ ] 派生する参照Markdown、インベントリ、画像ハッシュを再生成し、HTMLとの差分を同期する。
- [ ] 公開後28日を目安にGSCの表示回数・クリック数・CTR・平均掲載順位、記事CTAクリック、相談CVをURL単位で比較する。
- [ ] 効果が出ない記事は、検索意図・SERP・競合の変化を個別に再調査する。全記事を一括で再改変しない。
- [ ] 比較記事では、タイトルで対象・比較意図・更新年を明示し、評価軸、候補ごとの同じ項目、比較表、選び方、FAQを揃える。
- [ ] 1180px以上では左に目次、中央に本文、右に短いCTAを配置し、モバイルでは1カラムへ戻す。

### 6. Delivery gates

- [ ] Run the deterministic validator.
- [ ] Render at mobile, tablet, and desktop widths.
- [ ] Check images, links, console, JSON-LD, overflow, and CTA destination.
- [ ] Run the Noimos content quality gate.
- [ ] Record a representative browser QA result: `overflow=false`, all images complete, and `.answer`/`.key-points`/`.toc`/`.related` present.
- [ ] For an explicit `ai_only` workflow, attach the validator, quality-gate, and render evidence to the article TODO; do not claim ranking or CV impact before post-publication data exists.
- [ ] Require the configured approval policy (`human` or explicit `ai_only`) before publish.

```bash
python3 "$SKILL_DIR/scripts/validate_article.py" \
  --input <article.html> --site-root <project-root> --out article-validation.json
```

## Output contract

Return the research memo, claim ledger, approved outline, canonical draft,
validation report, screenshots, remaining blockers, and post-publication
measurement plan. Do not present a draft as publish-ready when any P0 gate
fails or the configured approval policy is incomplete.
