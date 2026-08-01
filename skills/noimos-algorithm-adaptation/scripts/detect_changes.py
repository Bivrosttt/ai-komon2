#!/usr/bin/env python3
"""Detect material recent-vs-baseline changes in page/query performance."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


def aggregate(rows: list[dict]) -> dict:
    impressions = sum(float(row.get("impressions") or 0) for row in rows)
    clicks = sum(float(row.get("clicks") or 0) for row in rows)
    conversions = sum(float(row.get("conversions") or 0) for row in rows)
    weighted_position_numerator = sum(
        float(row.get("position") or 0) * float(row.get("impressions") or 0)
        for row in rows
    )
    position = weighted_position_numerator / impressions if impressions else None
    return {
        "impressions": impressions,
        "clicks": clicks,
        "ctr": clicks / impressions if impressions else None,
        "position": position,
        "conversions": conversions,
    }


def pct(recent: float, baseline: float) -> float | None:
    return (recent - baseline) / baseline if baseline else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--baseline-days", type=int, default=14)
    parser.add_argument("--recent-days", type=int, default=7)
    parser.add_argument("--min-impressions", type=float, default=100)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    rows = list(csv.DictReader(Path(args.input).open(encoding="utf-8-sig", newline="")))
    if not rows:
        raise SystemExit("No rows")
    parsed = []
    for row in rows:
        copy = dict(row)
        copy["_date"] = date.fromisoformat(row["date"])
        parsed.append(copy)
    max_date = max(row["_date"] for row in parsed)
    recent_start = max_date - timedelta(days=args.recent_days - 1)
    baseline_end = recent_start - timedelta(days=1)
    baseline_start = baseline_end - timedelta(days=args.baseline_days - 1)
    by_entity: defaultdict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in parsed:
        by_entity[(row.get("page", ""), row.get("query", ""))].append(row)

    incidents = []
    for (page, query), entity_rows in by_entity.items():
        baseline_rows = [row for row in entity_rows if baseline_start <= row["_date"] <= baseline_end]
        recent_rows = [row for row in entity_rows if recent_start <= row["_date"] <= max_date]
        baseline = aggregate(baseline_rows)
        recent = aggregate(recent_rows)
        notes = []
        if not baseline_rows or not recent_rows:
            classification = "insufficient_data"
            notes.append("missing_window")
        elif baseline["impressions"] < args.min_impressions or recent["impressions"] < args.min_impressions:
            classification = "insufficient_data"
            notes.append("below_minimum_impressions")
        else:
            click_change = pct(recent["clicks"] / args.recent_days, baseline["clicks"] / args.baseline_days)
            impression_change = pct(recent["impressions"] / args.recent_days, baseline["impressions"] / args.baseline_days)
            conversion_change = pct(recent["conversions"] / args.recent_days, baseline["conversions"] / args.baseline_days)
            position_change = (
                recent["position"] - baseline["position"]
                if recent["position"] is not None and baseline["position"] is not None
                else None
            )
            if (
                (click_change is not None and click_change <= -0.30)
                and (
                    (position_change is not None and position_change >= 1.5)
                    or (impression_change is not None and impression_change <= -0.25)
                )
            ):
                classification = "material_loss"
            elif (
                click_change is not None and click_change >= 0.30
                and (position_change is None or position_change <= -1.0 or impression_change >= 0.25)
            ):
                classification = "material_gain"
            else:
                classification = "stable_or_noise"
            if conversion_change is not None and conversion_change <= -0.4:
                notes.append("conversion_loss")
        click_change = pct(recent["clicks"] / max(args.recent_days, 1), baseline["clicks"] / max(args.baseline_days, 1))
        impression_change = pct(recent["impressions"] / max(args.recent_days, 1), baseline["impressions"] / max(args.baseline_days, 1))
        position_change = (
            recent["position"] - baseline["position"]
            if recent["position"] is not None and baseline["position"] is not None
            else None
        )
        incidents.append(
            {
                "page": page,
                "query": query,
                "classification": classification,
                "baseline": baseline,
                "recent": recent,
                "changes": {
                    "clicks_per_day": round(click_change, 4) if click_change is not None else None,
                    "impressions_per_day": round(impression_change, 4) if impression_change is not None else None,
                    "position": round(position_change, 3) if position_change is not None else None,
                },
                "notes": notes,
                "requires_human_approval_for_change": classification in {"material_loss", "material_gain"},
            }
        )
    order = {"material_loss": 0, "material_gain": 1, "stable_or_noise": 2, "insufficient_data": 3}
    incidents.sort(key=lambda item: order[item["classification"]])
    counts = {key: sum(item["classification"] == key for item in incidents) for key in order}
    report = {
        "tool": "noimos-algorithm-adaptation",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "windows": {
            "baseline": [baseline_start.isoformat(), baseline_end.isoformat()],
            "recent": [recent_start.isoformat(), max_date.isoformat()],
        },
        "counts": counts,
        "incidents": incidents,
        "warning": "A detected change does not prove an algorithm update.",
    }
    Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(counts, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
