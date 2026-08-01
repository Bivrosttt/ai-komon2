---
name: noimos-social-conversion-content
description: Turn an evidenced social format into original, brand-aligned X, LinkedIn, Instagram, TikTok, or UGC content designed for one measurable conversion. Use for social post generation, threads, carousels, short-video scripts, UGC scripts, or high-conversion content.
user-invokable: true
argument-hint: "<trend-packet-and-offer>"
license: MIT
---

# Noimos Social Conversion Content

Adapt the mechanics, never the creator's expression. Each asset earns attention,
delivers useful proof, and asks for one proportionate next action.

## Required inputs

- Approved trend packet with evidence.
- Audience, offer, product truth, brand voice, CTA, platform, and available
  proof/assets.

## Checklist

- [ ] State one audience, one pain, one promised outcome, and one CTA.
- [ ] Map the reference to abstract mechanics: hook type, pacing, reveal,
  evidence, objection, CTA.
- [ ] Create a new angle, wording, examples, visuals, and audio plan.
- [ ] Put the audience tension and concrete payoff in the first line or first
  three seconds.
- [ ] Deliver value before the product mention.
- [ ] Use verified first-party proof or sourced market evidence.
- [ ] Label supplied but unverified claims and hypothetical examples.
- [ ] Remove guarantees, unsupported superlatives, artificial urgency, and
  undisclosed imitation.
- [ ] Tailor length, rhythm, captions, safe zones, and CTA to the platform.
- [ ] Produce at least three hook variants while changing one variable at a
  time.
- [ ] Define the metric and decision rule before posting.
- [ ] Run the content scorer and the Noimos quality gate.
- [ ] Require human approval before public posting.

## Platform structures

- X single post: hook, compressed proof, useful takeaway, one CTA.
- X thread: promise, 3-7 evidence/action steps, synthesis, one CTA.
- LinkedIn: specific observation, tension, first-party lesson, transferable
  framework, question or CTA.
- TikTok/Reels/UGC: 0-3s hook, 3-8s problem, 8-25s demonstration/proof,
  25-35s decision rule, CTA. Adjust duration to the actual format.

## Deterministic scorer

```bash
python3 "$SKILL_DIR/scripts/score_social_content.py" \
  --input content-pack.json --out social-content-score.json
```

## Output contract

Return the reference mechanics, originality delta, final variants, shot/card
plan, caption, CTA, claim ledger, risk review, experiment matrix, and approval
state. Do not post or schedule automatically.
