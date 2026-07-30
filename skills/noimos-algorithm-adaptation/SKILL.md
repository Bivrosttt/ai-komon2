---
name: noimos-algorithm-adaptation
description: Monitor SEO, AI-search, conversion, and social time series; detect material changes; diagnose likely causes; and prepare reversible response plans. Use for Advisor Agent instructions, ranking drops, algorithm updates, content decay, anomaly detection, or automatic repair proposals.
user-invokable: true
argument-hint: "<performance-export-or-monitoring-goal>"
license: MIT
---

# Noimos Algorithm Adaptation

Detect meaningful changes quickly without rewriting content because of normal
daily noise. This skill proposes reversible actions; it does not autonomously
publish repairs.

## Required inputs

- Daily page/query/channel metrics with timezone and data-source freshness.
- Comparable baseline and recent windows.
- Release, tracking, site-change, and campaign annotations.
- Minimum sample sizes and business thresholds.

## Checklist

- [ ] Validate data completeness, timezone, attribution, property, and delayed
  reporting before detecting anomalies.
- [ ] Compare rolling recent and baseline windows; exclude partial current day.
- [ ] Enforce minimum impressions, views, clicks, or conversions.
- [ ] Track position, impressions, CTR, clicks, conversions, AI citations when
  observed, reach, engagement, and qualified actions.
- [ ] Separate sitewide, page, query, device, country, and platform effects.
- [ ] Check tracking/deployment changes, seasonality, SERP feature changes,
  competitor movement, content drift, and policy changes.
- [ ] Rank incidents by business impact, confidence, and reversibility.
- [ ] Propose the smallest testable repair plus success and rollback rules.
- [ ] Preserve the original page and baseline.
- [ ] Require human approval before rewrite, republish, redirect, delete,
  noindex, or public cross-post.

## Change detector

```bash
python3 "$SKILL_DIR/scripts/detect_changes.py" \
  --input performance.csv --baseline-days 14 --recent-days 7 \
  --out incidents.json
```

The detector flags loss, gain, and insufficient-data states. It is not evidence
of a search engine update by itself.

## Advisor Agent instruction

Run daily:

1. Validate yesterday's complete data.
2. Detect material changes with sample thresholds.
3. Join release/tracking annotations.
4. Produce incident cards with facts, hypotheses, confidence, and impact.
5. Recommend a reversible action or continued observation.
6. Await human approval for content or external changes.
7. Re-measure on the declared review date and learn from the result.

## Output contract

Return incident cards, segmentation, likely-cause tree, recommended experiment,
approval requirement, review date, success metric, and rollback condition.
