#!/usr/bin/env python3
"""Score observed public social posts and aggregate repeatable format patterns."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return min(high, max(low, value))


def numeric(record: dict, key: str) -> float | None:
    value = record.get(key)
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    as_of = date.fromisoformat(args.as_of)
    posts = json.loads(Path(args.input).read_text(encoding="utf-8"))
    if isinstance(posts, dict):
        posts = posts.get("posts", [])
    grouped: defaultdict[str, list[dict]] = defaultdict(list)

    for post in posts:
        published = date.fromisoformat(str(post["published_at"])[:10])
        age = (as_of - published).days
        followers = numeric(post, "followers")
        views = numeric(post, "views")
        likes = numeric(post, "likes") or 0
        comments = numeric(post, "comments") or 0
        shares = numeric(post, "shares") or 0
        posts_count = numeric(post, "posts_count")
        account_age_days = numeric(post, "account_age_days")
        product_fit = numeric(post, "product_fit") or 0
        evidence_fields = ["url", "published_at", "platform", "creator", "hook", "format"]
        completeness = sum(bool(post.get(key)) for key in evidence_fields) / len(evidence_fields)
        recency = 1.0 if 0 <= age <= 7 else 0.5 if age <= 14 else 0.1
        if views and views > 0:
            engagement = clamp((likes + 2 * comments + 3 * shares) / views / 0.08)
        else:
            engagement = 0.25 if any([likes, comments, shares]) else 0
        emerging = 0
        if account_age_days is not None and account_age_days <= 14:
            emerging += 0.5
        if posts_count is not None and posts_count <= 5:
            emerging += 0.25
        if followers is not None and views is not None and followers > 0 and views / followers >= 5:
            emerging += 0.25
        score = 100 * (
            0.25 * recency
            + 0.25 * engagement
            + 0.15 * clamp(emerging)
            + 0.20 * clamp(product_fit / 5)
            + 0.15 * completeness
        )
        post_out = {
            **post,
            "age_days": age,
            "post_score": round(score, 1),
            "evidence_completeness": round(completeness, 2),
            "metrics_observed": views is not None,
        }
        grouped[str(post.get("format") or "unknown")].append(post_out)

    patterns: list[dict] = []
    for format_name, items in grouped.items():
        creators = {str(item.get("creator")) for item in items if item.get("creator")}
        platforms = {str(item.get("platform")) for item in items if item.get("platform")}
        recent_items = [item for item in items if 0 <= item["age_days"] <= 7]
        repetition = clamp(len({item.get("creator") for item in recent_items}) / 3)
        base = sum(item["post_score"] for item in items) / len(items)
        pattern_score = 0.75 * base + 25 * repetition
        confidence = (
            "high" if len(creators) >= 3 and len(recent_items) >= 3
            else "medium" if len(creators) >= 2 and len(recent_items) >= 2
            else "low"
        )
        patterns.append(
            {
                "format": format_name,
                "score": round(min(pattern_score, 100), 1),
                "confidence": confidence,
                "independent_creators": len(creators),
                "platforms": sorted(platforms),
                "recent_posts": len(recent_items),
                "posts": sorted(items, key=lambda item: item["post_score"], reverse=True),
            }
        )
    patterns.sort(key=lambda item: item["score"], reverse=True)
    report = {
        "tool": "noimos-social-trend-mining",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "as_of": args.as_of,
        "patterns": patterns,
        "rule": "A high score is a test priority, not a guarantee of virality.",
    }
    Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"patterns": len(patterns), "top": patterns[0]["format"] if patterns else None, "confidence": patterns[0]["confidence"] if patterns else None}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
