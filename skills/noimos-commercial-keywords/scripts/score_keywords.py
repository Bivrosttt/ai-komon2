#!/usr/bin/env python3
"""Rank commercial keyword candidates without inventing missing metrics."""

from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path


ELIGIBLE_INTENTS = {"purchase", "comparison", "commercial"}
INTENT_SCORE = {
    "purchase": 1.0,
    "comparison": 0.95,
    "commercial": 0.8,
    "utility": 0.45,
    "informational": 0.2,
    "navigational": 0.1,
}


def number(value: str) -> float | None:
    value = (value or "").strip().replace(",", "")
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return min(high, max(low, value))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    rows = list(csv.DictReader(Path(args.input).open(encoding="utf-8-sig", newline="")))
    volumes = [number(row.get("search_volume", "")) for row in rows]
    known_volumes = [value for value in volumes if value is not None and value >= 0]
    max_log = max((math.log1p(value) for value in known_volumes), default=1.0)

    ranked: list[dict] = []
    for row in rows:
        keyword = (row.get("keyword") or "").strip()
        intent = (row.get("intent") or "unknown").strip().lower()
        volume = number(row.get("search_volume", ""))
        difficulty = number(row.get("difficulty", ""))
        product_fit = number(row.get("product_fit", "")) or 0
        evidence_confidence = number(row.get("evidence_confidence", "")) or 0
        maintenance_cost = number(row.get("maintenance_cost", "")) or 3
        demand_proxy = number(row.get("demand_proxy", ""))

        if volume is not None:
            demand = math.log1p(max(volume, 0)) / max_log
            demand_basis = "observed_volume"
        elif demand_proxy is not None:
            demand = clamp(demand_proxy / 5)
            demand_basis = "proxy"
        else:
            demand = 0.35
            demand_basis = "unknown_neutral"

        ease = clamp(1 - difficulty / 100) if difficulty is not None else 0.5
        intent_value = INTENT_SCORE.get(intent, 0.0)
        fit = clamp(product_fit / 5)
        confidence = clamp(evidence_confidence / 5)
        maintainability = 1 - clamp((maintenance_cost - 1) / 4)

        score = 100 * (
            0.25 * demand
            + 0.20 * ease
            + 0.25 * intent_value
            + 0.15 * fit
            + 0.10 * confidence
            + 0.05 * maintainability
        )
        eligible = intent in ELIGIBLE_INTENTS
        reasons = []
        if not eligible:
            reasons.append("intent_not_commercial")
        if volume is None:
            reasons.append("volume_not_observed")
        if difficulty is None:
            reasons.append("difficulty_not_observed")
        if (row.get("cannibalization_risk") or "").strip().lower() in {"high", "yes", "true"}:
            score -= 12
            reasons.append("cannibalization_risk")

        ranked.append(
            {
                "keyword": keyword,
                "intent": intent,
                "eligible": eligible,
                "score": round(max(score, 0), 1),
                "search_volume": volume,
                "difficulty": difficulty,
                "demand_basis": demand_basis,
                "source": row.get("source", ""),
                "retrieved_at": row.get("retrieved_at", ""),
                "reasons": reasons,
            }
        )

    ranked.sort(key=lambda item: (item["eligible"], item["score"]), reverse=True)
    report = {
        "tool": "noimos-commercial-keywords",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "method": "planning heuristic; not a ranking or revenue prediction",
        "eligible_count": sum(1 for row in ranked if row["eligible"]),
        "candidates": ranked,
    }
    Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"candidates": len(ranked), "eligible": report["eligible_count"], "top": ranked[0]["keyword"] if ranked else None}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
