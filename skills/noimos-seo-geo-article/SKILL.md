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
- [ ] Add a real article-specific diagram with `img`, descriptive `alt`, and
  `figcaption`. Visually verify all image labels.
- [ ] Include Article and Breadcrumb JSON-LD that matches visible content.
- [ ] Treat FAQ as reader content; never promise a rich result.

### 4. Delivery gates

- [ ] Run the deterministic validator.
- [ ] Render at mobile, tablet, and desktop widths.
- [ ] Check images, links, console, JSON-LD, overflow, and CTA destination.
- [ ] Run the Noimos content quality gate.
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
