#!/usr/bin/env python3
"""Create review-first tool-spec drafts from scored keyword candidates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def choose_cta(candidate: dict, config: dict) -> dict:
    keyword = candidate.get("keyword", "").lower()
    for cta in config.get("service_ctas", []):
        if any(term.lower() in keyword for term in cta.get("fit_terms", [])):
            return {"label": cta["label"], "url": cta["url"]}
    return {"label": "AI導入診断を受ける", "url": "/diagnosis.html"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", required=True)
    parser.add_argument("--config", default="seo/config.json")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()
    candidates = json.loads(Path(args.candidates).read_text(encoding="utf-8")).get("candidates", [])
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for candidate in candidates[: args.limit]:
        keyword = candidate["keyword"]
        spec = {
            "status": "draft",
            "keyword": keyword,
            "slug": candidate["slug"],
            "title": f"{keyword} 無料ツール",
            "description": f"{keyword}に関する作業をブラウザで簡単に進める無料ツールです。",
            "base_url": config.get("base_url", ""),
            "tool_type": "shell",
            "fields": [],
            "result": {},
            "explanations": [
                f"{keyword}で困っている人が、最初に確認したい用途と使い方を記載する。",
                "入力・出力・制限・プライバシーを、実装に合わせて具体化する。",
            ],
            "related_tools": [],
            "cta": choose_cta(candidate, config),
            "research": {"intent": candidate["intent"], "priority": candidate["priority"], "sources": candidate["sources"], "observed_at": candidate["observed_at"]},
        }
        (out_dir / f"{candidate['slug']}.json").write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote up to {min(len(candidates), args.limit)} review-first spec stubs to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
