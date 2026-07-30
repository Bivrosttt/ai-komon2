---
name: noimos-content-refresh
description: Build an evidence-based content refresh and gap queue from Search Console, page freshness, SERP changes, internal links, cannibalization, and factual drift. Use for SEO content refreshes, declining rankings, stale posts, content pruning, or competitor keyword gaps.
user-invokable: true
argument-hint: "<site-root-or-gsc-export>"
license: MIT
---

# Noimos Content Refresh

Age is a review trigger, not proof that a rewrite is needed. Prioritize pages
where performance, intent, facts, links, or conversion paths materially changed.

## Required inputs

- Site inventory with canonical URL and last modified date.
- GSC query/page export for a recent period and a comparable baseline when
  available.
- Conversion data and current SERP observations when available.

## Checklist

- [ ] Inventory every article, canonical, title/H1, dateModified, author, word
  count, internal inlinks/outlinks, and CTA.
- [ ] Flag age bands at 90 and 180 days, while preserving actual last review
  evidence.
- [ ] Compare clicks, impressions, CTR, position, queries, and conversions
  between comparable windows.
- [ ] Separate page loss, query loss, sitewide shift, seasonality, and tracking
  change.
- [ ] Re-check current SERP intent and top-result structure for affected
  queries.
- [ ] Detect broken links, orphans, dead ends, title overlap, duplicate intent,
  and potential cannibalization.
- [ ] Classify factual drift, offer drift, screenshot drift, and policy/pricing
  drift.
- [ ] Choose `keep`, `light refresh`, `substantial rewrite`, `differentiate`,
  `merge/redirect proposal`, or `new page`.
- [ ] Preserve the pre-change baseline, hypothesis, exact change list, success
  metric, review date, and rollback condition.
- [ ] Require explicit approval before redirects, deletion, noindex, or
  canonical changes.

## Deterministic inventory

```bash
python3 "$SKILL_DIR/scripts/analyze_content.py" \
  --root <project-root> --articles articles --as-of YYYY-MM-DD \
  --out content-refresh-queue.json
```

The script detects local structural signals. GSC loss and current SERP intent
must be added when available.

## Output contract

Return a prioritized table with evidence, diagnosis, confidence, action, effort,
expected metric, and approval requirement. Separate facts, proxies, hypotheses,
and unknowns. Never delete or redirect content from this skill automatically.
