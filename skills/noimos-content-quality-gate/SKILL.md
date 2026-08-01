---
name: noimos-content-quality-gate
description: Block AI slop by validating source coverage, first-party evidence, brand voice, specificity, originality, factual claims, risk, and a documented approval policy for articles and social content. Use for AI content QA, hallucination checks, brand checks, pre-publication review, or AI-only publication gates.
user-invokable: true
argument-hint: "<content-file-and-claim-register>"
license: MIT
---

# Noimos Content Quality Gate

Scale quality, not output count. Missing evidence and incomplete approval policy
checks are blocking states, not warnings to ignore. The default policy supports
human approval; an explicit `ai_only` policy can approve publication only after
all automated checks are recorded as true.

## Required inputs

- Content file.
- Claim register containing claim ID, exact claim, source URL, publisher,
  retrieval date, evidence type, and verification state.
- Brand memory containing audience, promise, tone, prohibited claims, preferred
  vocabulary, real proof, and CTA.
- Approval policy containing `mode: human` or `mode: ai_only`. AI-only mode must
  include named pipeline identity, timestamp, and every required automated check.

## Checklist

### Evidence

- [ ] Tag factual and numeric claims with claim IDs.
- [ ] Verify public claims against primary or authoritative sources.
- [ ] Mark first-party metrics with owner, period, definition, and evidence
  location.
- [ ] Mark scenarios as examples and never present them as customer results.
- [ ] Remove claims that cannot be verified.

### Usefulness and originality

- [ ] Answer a specific audience decision or job.
- [ ] Include concrete steps, examples, thresholds, limitations, or a decision
  rule.
- [ ] Add first-party learning or a novel synthesis that competitors do not
  already provide.
- [ ] Remove repeated paragraphs, template filler, generic conclusions, and
  unsupported certainty.
- [ ] Ensure the CTA is proportionate to the delivered value.

### Brand and risk

- [ ] Match the approved audience, promise, vocabulary, and tone.
- [ ] Check privacy, copyright, platform, legal, safety, and reputation risks.
- [ ] Avoid copying a source's distinctive expression.
- [ ] Record approval mode, pipeline or reviewer identity, approval time,
  corrections, and final status.

## Deterministic gate

```bash
python3 "$SKILL_DIR/scripts/quality_gate.py" \
  --content content.md --claims claims.json --brand brand.json \
  --approval approval.json --out quality-report.json
```

Blocking failures include unregistered numeric claims, invalid or unverified
claim records, prohibited claims, missing audience/CTA, excessive generic
phrases, placeholders, and incomplete approval policy checks. `ai_only` mode
is valid only when claim evidence, brand alignment, specificity, risk screening,
and render QA are all explicitly true.

## Output contract

Return `PASS`, `BLOCK`, or `PASS_WITH_WARNINGS`, followed by evidence coverage,
specificity, originality, brand alignment, risk, and approval sections. Provide
exact fixes for every blocker. The checker does not deploy by itself; a caller
may publish only after a `PASS` result and the configured approval policy.
