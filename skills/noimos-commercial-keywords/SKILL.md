---
name: noimos-commercial-keywords
description: Find, evidence, cluster, and prioritize commercial or purchase-intent SEO/GEO keywords using first-party data, public discovery sources, and clearly labeled proxies. Use for high-volume low-difficulty keyword research, comparison queries, buying queries, or content opportunity selection.
user-invokable: true
argument-hint: "<industry-or-seed>"
license: MIT
---

# Noimos Commercial Keywords

This skill chooses the smallest defensible cluster that can generate qualified
demand. A keyword with large volume but weak commercial intent does not win.
Unknown volume or difficulty stays unknown.

## Required inputs

- Audience, offer, country/language, seed problems, and desired conversion.
- Existing site inventory and Search Console export when available.
- Authorized provider exports such as Semrush or another keyword database.

## Source ladder

1. GSC query/page exports: first-party performance and existing opportunity.
2. Authorized keyword-provider exports: dated volume, difficulty, CPC.
3. Search suggestions, People Also Ask, related searches, forums, and SERP
   composition: discovery proxies only.
4. Sales calls, CRM, support tickets, and site search: first-party language.

Do not use result counts as search volume. Do not invent difficulty. Store the
provider, market, retrieval date, and whether each metric is observed or proxy.

## Checklist

- [ ] Define one job to be done and one conversion for the research run.
- [ ] Gather raw candidates without prematurely merging variants.
- [ ] Label intent: `purchase`, `comparison`, `commercial`, `utility`,
  `informational`, or `navigational`.
- [ ] Block informational-only candidates from the acquisition shortlist unless
  they support an approved cluster.
- [ ] Record volume, difficulty, CPC, GSC impressions, or proxy evidence in
  separate fields.
- [ ] Normalize spelling, cluster by intent, and identify the canonical query.
- [ ] Compare title/H1/intent with existing pages and flag cannibalization.
- [ ] Inspect current SERP types and determine whether an article, comparison,
  landing page, directory, tool, or video is the right format.
- [ ] Score demand, attainable difficulty, conversion proximity, product fit,
  evidence confidence, and maintenance cost.
- [ ] Select one primary cluster plus 2-4 supporting queries.

## Scoring rules

Use the bundled scorer for comparable candidate data:

```bash
python3 "$SKILL_DIR/scripts/score_keywords.py" \
  --input candidates.csv --out keyword-ranking.json
```

The score is a planning heuristic. Missing volume is not zero and does not
become an estimated number. Candidates without commercial intent are marked
ineligible even when their raw score is high.

## Output contract

Return:

- A raw evidence table with dates and source types.
- A normalized cluster table with intent and cannibalization risk.
- Ranked eligible candidates with a score explanation.
- Rejected candidates and rejection reasons.
- One chosen cluster and a page brief containing audience, decision, format,
  primary query, supporting questions, evidence needs, CTA, and success metric.

Never state that a score predicts traffic, ranking, revenue, or conversion.
