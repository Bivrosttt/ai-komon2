#!/usr/bin/env python3
"""Turn a Search Console CSV export into prioritized SEO opportunities."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ALIASES = {
    "query": ("query", "検索キーワード", "クエリ"),
    "page": ("page", "ページ"),
    "clicks": ("clicks", "クリック数"),
    "impressions": ("impressions", "表示回数"),
    "ctr": ("ctr", "クリック率"),
    "position": ("position", "平均掲載順位", "掲載順位"),
}


def find_key(headers: list[str], names: tuple[str, ...]) -> str | None:
    lower = {header.strip().lower(): header for header in headers}
    for name in names:
        if name.lower() in lower:
            return lower[name.lower()]
    return None


def number(value: str) -> float:
    value = (value or "").strip().replace(",", "")
    if value.endswith("%"):
        return float(value[:-1]) / 100
    return float(value or 0)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--json-out", required=True)
    parser.add_argument("--md-out", required=True)
    parser.add_argument("--limit", type=int, default=30)
    args = parser.parse_args()
    with Path(args.input).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        keys = {name: find_key(headers, aliases) for name, aliases in ALIASES.items()}
        if not keys["query"]:
            raise SystemExit("Search Console CSV needs a query/検索キーワード column")
        rows = []
        for raw in reader:
            query = (raw.get(keys["query"] or "") or "").strip()
            if not query:
                continue
            impressions = number(raw.get(keys["impressions"] or "", "0"))
            clicks = number(raw.get(keys["clicks"] or "", "0"))
            ctr = number(raw.get(keys["ctr"] or "", "0"))
            position = number(raw.get(keys["position"] or "", "99"))
            # Queries in positions 8-30 with impressions are often the fastest wins.
            opportunity = round(impressions * (1.0 if 8 <= position <= 30 else 0.35) * (1.0 if ctr < 0.05 else 0.4), 2)
            rows.append({"query": query, "page": raw.get(keys["page"] or "", ""), "clicks": clicks, "impressions": impressions, "ctr": ctr, "position": position, "opportunity": opportunity})
    rows.sort(key=lambda row: (-row["opportunity"], -row["impressions"]))
    rows = rows[: args.limit]
    payload = {"source": args.input, "rows": rows}
    json_path = Path(args.json_out)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Search Console opportunities", "", "| Opportunity | Query | Position | Impressions | CTR | Page |", "|---:|---|---:|---:|---:|---|"]
    lines += [f"| {row['opportunity']} | {row['query']} | {row['position']} | {row['impressions']} | {row['ctr']:.1%} | {row['page']} |" for row in rows]
    md_path = Path(args.md_out)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {len(rows)} Search Console opportunities")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
