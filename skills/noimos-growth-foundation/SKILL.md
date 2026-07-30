---
name: noimos-growth-foundation
description: Audit and prioritize the website, conversion, analytics, SEO/GEO, social-profile, and cross-channel foundations required before organic content production. Use for website readiness, launch foundation, SEO/GEO setup, CTA, tracking, or mobile first-view audits.
user-invokable: true
argument-hint: "<site-url-or-project-root>"
license: MIT
---

# Noimos Growth Foundation

Organic growth starts only after the site can explain, persuade, measure, and
route demand. This skill produces an evidence-backed implementation queue. It
does not reward decorative complexity and never treats a tag found in source as
proof that conversions are visible in an analytics product.

## Required inputs

- Site URL or local project root.
- Primary audience, their urgent job, offer, and desired conversion.
- Primary CTA destination.
- Known analytics and social profiles. Missing credentials are acceptable.

## Checklist

### A. Positioning and conversion

- [ ] State the audience, urgent problem, promised outcome, and distinctive
  mechanism in one line.
- [ ] Verify that the mobile first view shows the offer and a concrete CTA
  without requiring a long scroll.
- [ ] Verify one primary CTA per decision state and a working destination.
- [ ] Inspect trust, price/next-step clarity, objections, proof, and risk
  reversal.
- [ ] Separate observable evidence from proposed copy.

### B. Technical SEO/GEO

- [ ] Check HTTPS, status code, title, description, canonical, viewport, one H1,
  crawlability, robots.txt, sitemap, llms.txt, Open Graph, and Twitter card.
- [ ] Parse JSON-LD and verify that visible content matches it.
- [ ] Check Organization/WebSite on the site and Article/Breadcrumb on articles.
- [ ] Confirm important content exists in rendered HTML and is not JS-gated.
- [ ] Record AI crawler policy as a deliberate business choice, not a universal
  requirement.

### C. Measurement

- [ ] Inventory page-view, CTA, form, lead, booking, and purchase events.
- [ ] Verify source code, live network firing, analytics receipt, and
  conversion configuration as four separate states.
- [ ] Preserve UTM parameters through the CTA destination.
- [ ] Document consent, privacy, cross-domain, referral exclusion, and test
  traffic handling.
- [ ] Label login-dependent verification explicitly.

### D. Cross-channel continuity

- [ ] Check consistent brand name, one-line, avatar, CTA, and canonical link on
  each active profile.
- [ ] Check that website, newsletter, social bios, and lead destinations link
  to the intended canonical pages.
- [ ] Record broken, conflicting, or untracked paths.

### E. Visual verification

- [ ] Use `agent-browser open -> snapshot -i -> interact -> re-snapshot`.
- [ ] Capture 390x844 mobile and 1280x800 desktop screenshots.
- [ ] Check horizontal overflow, clipped copy, tap targets, CTA visibility,
  contrast, and layout shift.

## Prioritization

Classify every finding:

- `P0`: blocks crawling, conversion, safety, or measurement.
- `P1`: materially weakens message, trust, or attribution.
- `P2`: optimization after baseline data exists.
- `P3`: cosmetic preference without demonstrated conversion impact.

Also assign an execution bucket:

- `implement now`: reversible and supported by evidence.
- `measure first`: needs an A/B test or baseline.
- `login/deploy required`: cannot be verified from source alone.

## Deterministic local audit

```bash
python3 "$SKILL_DIR/scripts/audit_foundation.py" \
  --root <project-root> --html index.html --out foundation-audit.json
```

The script is a baseline, not the full audit. Always add rendered mobile
evidence and live tracking evidence when accessible.

## Output contract

Return:

1. One-line positioning diagnosis.
2. Evidence table with `fact | evidence | status | confidence`.
3. P0-P3 action queue with exact implementation steps.
4. Measurement matrix separating source/live/receipt/conversion states.
5. Screenshot paths and viewport findings.
6. Open questions and login/deployment dependencies.

Never claim that design, SEO tags, or a tag manager alone caused conversion.
