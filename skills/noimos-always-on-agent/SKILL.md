---
name: noimos-always-on-agent
description: Design and dry-run an always-on organic marketing agent that collects evidence, creates drafts, enforces quality policies, prevents duplicate work, and learns from performance. Use for Turn into an Agent, content automation, scheduled marketing agents, or continuous content operations.
user-invokable: true
argument-hint: "<workflow-or-agent-goal>"
license: MIT
---

# Noimos Always-On Agent

Replace reliance on willpower with a visible queue, durable state, explicit
service levels, and approval gates. External publication requires a configured
approval policy: `human` by default, or `ai_only` when every automated quality
check is recorded as passing.

## Required inputs

- Goal, channels, cadence, audience, data sources, brand memory, approval
  policy, allowed tools, and explicit prohibited actions.

## Checklist

- [ ] Decompose the loop into `collect`, `normalize`, `analyze`, `prioritize`,
  `draft`, `quality_gate`, `approval_policy`, `publish_handoff`, and `learn`.
- [ ] Define schedule, timezone, SLA, retry limit, timeout, and quiet hours.
- [ ] Store immutable input snapshots, run IDs, output hashes, lineage, and
  status transitions.
- [ ] Use idempotency keys to prevent duplicate drafts or sends.
- [ ] Define `no_data`, `partial_data`, `source_changed`, `rate_limited`,
  `quality_failed`, and `approval_expired` behavior.
- [ ] Keep credentials out of prompts, logs, and generated files.
- [ ] Route all public posting, email sends, destructive edits, and spend
  changes to the configured approval policy.
- [ ] Cap retry loops and create a dead-letter queue.
- [ ] Track production SLA separately from business outcomes.
- [ ] Feed performance and reviewer corrections into versioned brand memory.
- [ ] Dry-run at least one week without external writes.

## Agent spec and dry run

Use JSON so the spec can be validated without third-party packages:

```bash
python3 "$SKILL_DIR/scripts/dry_run_agent.py" \
  --spec agent-spec.json --start YYYY-MM-DD --days 7 --out agent-dry-run.json
```

The dry run must show that external actions are not executed. In `ai_only`
mode, a passing quality gate produces `ai_approved_for_publish`; in `human`
mode it produces `awaiting_human_approval`.

## Output contract

Return the agent charter, data contract, schedule, state machine, approval
matrix, failure policy, run ledger, dry-run result, and operational dashboard
spec. Never claim that creating a schedule guarantees consistency or growth.
