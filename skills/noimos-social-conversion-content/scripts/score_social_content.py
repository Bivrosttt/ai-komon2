#!/usr/bin/env python3
"""Score structured social content packs before the stricter quality gate."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


PLATFORM_LIMITS = {
    "x": 280,
    "linkedin": 3000,
    "instagram": 2200,
    "tiktok": 2200,
}
RISK_PATTERNS = [
    r"必ず(?:成功|伸び|稼げ)",
    r"絶対に",
    r"100\s*%",
    r"誰でも",
    r" guaranteed? ",
    r" overnight ",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    assets = payload.get("assets", payload if isinstance(payload, list) else [])
    scored = []
    for asset in assets:
        platform = str(asset.get("platform", "")).lower()
        content = str(asset.get("content", "")).strip()
        hook = str(asset.get("hook", "")).strip()
        cta = str(asset.get("cta", "")).strip()
        claim_ids = asset.get("claim_ids", [])
        proof = str(asset.get("proof", "")).strip()
        reference_mechanics = asset.get("reference_mechanics", [])
        originality_delta = asset.get("originality_delta", [])
        issues = []
        points = 0
        if len(hook) >= 10 and hook in content[: max(120, len(hook) + 10)]:
            points += 20
        else:
            issues.append("weak_or_missing_hook")
        if proof and (claim_ids or re.search(r"(実測|データ|検証|手順|例)", proof)):
            points += 20
        else:
            issues.append("proof_not_grounded")
        if cta and cta in content:
            points += 15
        else:
            issues.append("missing_single_cta")
        if asset.get("audience") and asset.get("problem") and asset.get("outcome"):
            points += 15
        else:
            issues.append("audience_problem_outcome_incomplete")
        if reference_mechanics and originality_delta:
            points += 15
        else:
            issues.append("reference_or_originality_not_documented")
        limit = PLATFORM_LIMITS.get(platform)
        if limit and len(content) <= limit:
            points += 10
        else:
            issues.append("platform_length")
        risks = [pattern for pattern in RISK_PATTERNS if re.search(pattern, f" {content} ", re.I)]
        if not risks:
            points += 5
        else:
            issues.append("unsupported_or_guaranteed_claim")
        status = "pass" if points >= 85 and not risks else "needs_work" if points >= 65 and not risks else "block"
        scored.append(
            {
                "id": asset.get("id"),
                "platform": platform,
                "score": points,
                "status": status,
                "issues": issues,
            }
        )
    overall = "pass" if scored and all(item["status"] == "pass" for item in scored) else "block"
    report = {
        "tool": "noimos-social-conversion-content",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "overall": overall,
        "assets": scored,
        "human_approval_required": True,
    }
    Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"overall": overall, "assets": len(scored), "passing": sum(item["status"] == "pass" for item in scored)}, ensure_ascii=False))
    return 0 if overall == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
