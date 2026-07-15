#!/usr/bin/env python3
"""Normalize, deduplicate, classify, and score keyword observations."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any


TOOL_TERMS = ("計算", "シミュレーター", "シミュレーション", "生成", "変換", "作成", "チェック", "診断", "テンプレート", "一覧", "比較", "無料", "自動")
SERVICE_TERMS = ("AI", "業務改善", "業務効率化", "自動化", "導入", "DX", "議事録", "営業", "採用", "コスト", "ROI", "顧問")
QUESTION_TERMS = ("方法", "やり方", "とは", "なぜ", "できる", "どう", "必要", "おすすめ")


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "")
    return re.sub(r"\s+", " ", value).strip().lower()


def intent(keyword: str) -> str:
    if any(term in keyword for term in ("無料", "ツール", "計算", "生成", "変換", "作成", "自動", "チェック", "診断", "シミュレーター", "テンプレート")):
        return "utility"
    if any(term in keyword for term in ("料金", "費用", "導入", "比較", "おすすめ")):
        return "commercial"
    if any(term in keyword for term in QUESTION_TERMS):
        return "informational"
    return "exploratory"


def score(keyword: str, rows: list[dict[str, Any]]) -> tuple[int, dict[str, int]]:
    source_count = len({row.get("source") for row in rows})
    tool_fit = min(5, sum(term in keyword for term in TOOL_TERMS) + (1 if source_count >= 2 else 0))
    service_fit = min(5, sum(term.lower() in keyword.lower() for term in SERVICE_TERMS))
    longtail = 2 if 8 <= len(keyword) <= 30 else 1 if len(keyword) > 30 else 0
    repeat_use = 2 if any(term in keyword for term in ("計算", "チェック", "変換", "生成", "テンプレート")) else 0
    total = min(100, 30 + tool_fit * 8 + service_fit * 7 + longtail * 5 + repeat_use * 4 + min(10, source_count * 2))
    return total, {"tool_fit": tool_fit, "service_fit": service_fit, "source_count": source_count, "longtail": longtail, "repeat_use": repeat_use}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--json-out", required=True)
    parser.add_argument("--csv-out", required=True)
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in payload.get("rows", []):
        value = normalize(str(row.get("keyword", "")))
        if value:
            grouped[value].append(row)

    candidates: list[dict[str, Any]] = []
    for keyword, rows in grouped.items():
        priority, factors = score(keyword, rows)
        seed = max(rows, key=lambda row: int(row.get("seed_service_fit") or 0)).get("seed", "")
        slug = "tool-" + hashlib.sha1(keyword.encode("utf-8")).hexdigest()[:10]
        candidates.append(
            {
                "keyword": keyword,
                "seed": seed,
                "slug": slug,
                "intent": intent(keyword),
                "priority": priority,
                "factors": factors,
                "sources": sorted({row.get("source") for row in rows}),
                "observed_at": sorted({row.get("retrieved_at") for row in rows})[-1],
                "tool_hypothesis": f"{keyword}をブラウザで完結できる無料ツール",
                "next_action": "SERPと既存ページの重複を確認してから仕様化",
            }
        )
    candidates.sort(key=lambda row: (-row["priority"], row["keyword"]))
    candidates = candidates[: args.limit]

    output = {"source": args.input, "candidate_count": len(candidates), "candidates": candidates}
    json_path = Path(args.json_out)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    csv_path = Path(args.csv_out)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=["priority", "keyword", "seed", "intent", "slug", "sources", "tool_fit", "service_fit", "next_action"])
        writer.writeheader()
        for row in candidates:
            writer.writerow({**{key: row[key] for key in ("priority", "keyword", "seed", "intent", "slug", "next_action")}, "sources": ",".join(row["sources"]), "tool_fit": row["factors"]["tool_fit"], "service_fit": row["factors"]["service_fit"]})
    print(f"wrote {len(candidates)} candidates to {json_path} and {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
