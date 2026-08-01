#!/usr/bin/env python3
"""Validate an always-on agent spec and simulate scheduled runs without writes."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


REQUIRED_STAGES = [
    "collect",
    "normalize",
    "analyze",
    "prioritize",
    "draft",
    "quality_gate",
    "approval_policy",
    "publish_handoff",
    "learn",
]
EXTERNAL_ACTIONS = {"publish", "post", "send_email", "delete", "redirect", "activate_ads"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True)
    parser.add_argument("--start", required=True)
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    start = date.fromisoformat(args.start)
    stages = spec.get("stages", [])
    stage_names = [stage.get("name") for stage in stages]
    missing = [name for name in REQUIRED_STAGES if name not in stage_names]
    violations = []
    if missing:
        violations.append(f"missing_stages:{','.join(missing)}")
    if not spec.get("timezone"):
        violations.append("missing_timezone")
    approval_policy = spec.get("approval_policy", {})
    approval_mode = approval_policy.get("mode", "human")
    if approval_mode not in {"human", "ai_only"}:
        violations.append("invalid_approval_mode")
    if approval_mode == "human" and not spec.get("reviewers"):
        violations.append("missing_reviewers")
    if approval_mode == "ai_only" and not approval_policy.get("pipeline"):
        violations.append("missing_ai_pipeline")
    if int(spec.get("max_retries", 0)) > 3:
        violations.append("retry_limit_above_3")
    if not spec.get("idempotency_key_fields"):
        violations.append("missing_idempotency_key_fields")

    ledger = []
    seen_keys = set()
    for offset in range(args.days):
        run_date = start + timedelta(days=offset)
        for job in spec.get("jobs", []):
            weekdays = job.get("weekdays", list(range(7)))
            if run_date.weekday() not in weekdays:
                continue
            raw_key = "|".join(
                [
                    str(spec.get("name")),
                    str(job.get("name")),
                    run_date.isoformat(),
                    str(job.get("channel", "")),
                ]
            )
            idem = hashlib.sha256(raw_key.encode()).hexdigest()[:16]
            if idem in seen_keys:
                status = "deduplicated"
            else:
                seen_keys.add(idem)
                requested = set(job.get("actions", []))
                external = sorted(requested.intersection(EXTERNAL_ACTIONS))
                if external and approval_mode == "ai_only":
                    status = "ai_approved_for_publish"
                elif external:
                    status = "awaiting_human_approval"
                else:
                    status = "dry_run_complete"
            ledger.append(
                {
                    "run_date": run_date.isoformat(),
                    "job": job.get("name"),
                    "channel": job.get("channel"),
                    "idempotency_key": idem,
                    "status": status,
                    "external_actions": sorted(set(job.get("actions", [])).intersection(EXTERNAL_ACTIONS)),
                }
            )

    approval_jobs = [row for row in ledger if row["external_actions"]]
    expected_external_status = (
        "ai_approved_for_publish" if approval_mode == "ai_only" else "awaiting_human_approval"
    )
    if any(row["status"] != expected_external_status for row in approval_jobs):
        violations.append("external_action_not_held_for_approval_policy")
    overall = "pass" if not violations and ledger else "block"
    report = {
        "tool": "noimos-always-on-agent",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "agent": spec.get("name"),
        "overall": overall,
        "violations": violations,
        "summary": {
            "scheduled_runs": len(ledger),
            "approval_handoffs": len(approval_jobs),
            "approval_mode": approval_mode,
            "ai_approved_runs": sum(row["status"] == "ai_approved_for_publish" for row in ledger),
            "external_actions_executed": 0,
        },
        "ledger": ledger,
    }
    Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"overall": overall, **report["summary"]}, ensure_ascii=False))
    return 0 if overall == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
