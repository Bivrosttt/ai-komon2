---
name: noimos-social-trend-mining
description: Research recent public social posts across platforms, preserve evidence, and extract repeatable hooks and format patterns with product-fit scoring. Use for viral trend research, hook analysis, format mining, social content research, or cross-platform opportunity discovery.
user-invokable: true
argument-hint: "<industry-or-niche>"
license: MIT
---

# Noimos Social Trend Mining

Find repeatable audience behavior, not one famous account's outlier. A format
is considered a strong candidate only when its evidence is recent, attributable,
and transferable to the product.

## Required inputs

- Niche, audience, product, allowed platforms, geography/language, and desired
  conversion.
- Seven-day research window by default.

## Checklist

- [ ] Search at least two relevant platforms and save public URLs.
- [ ] Record platform, author, publication time, retrieval time, account age or
  first observable activity, post count, followers, views, likes, comments, and
  shares when visible.
- [ ] Mark every unavailable metric as unknown.
- [ ] Capture the first line/first three seconds, format, narrative arc, proof,
  CTA, comments signal, and product fit.
- [ ] Cluster by format mechanics, not topic words alone.
- [ ] Prefer formats repeated by at least two independent creators within seven
  days.
- [ ] Raise the signal when a new/small account substantially outperforms its
  visible baseline, but do not infer account age without evidence.
- [ ] Distinguish `observed viral`, `promising`, `weak evidence`, and `not
  transferable`.
- [ ] Check brand, platform, copyright, privacy, and claim risk.
- [ ] Extract the structural pattern only. Do not copy wording, footage, music,
  identity, or a creator's distinctive execution.

## Scoring

```bash
python3 "$SKILL_DIR/scripts/score_trends.py" \
  --input observed-posts.json --as-of YYYY-MM-DD --out trend-patterns.json
```

Recency, cross-creator repetition, normalized engagement, emerging-account
signal, evidence completeness, and product fit contribute to the score.

## Output contract

Return:

- Evidence table with direct URLs and timestamps.
- Pattern clusters and their independent creator count.
- Hook anatomy, format sequence, proof device, CTA, and why it works.
- Transfer plan for the product plus risks.
- Three patterns to test, three to avoid, and the next measurement window.

If public metrics or dates cannot be verified, say so and lower confidence.
