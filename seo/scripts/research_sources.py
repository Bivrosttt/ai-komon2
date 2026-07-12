#!/usr/bin/env python3
"""Collect keyword ideas from low-cost/public sources with polite pacing.

The collector intentionally uses only public suggestion endpoints and the
official Rakkokeyword API when an API key is present. It does not bypass
authentication, robots rules, rate limits, or paid features.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


USER_AGENT = "ai-komon-seo-research/1.0 (+https://ai-komon.bivrost.co.jp)"


def get_json(url: str, timeout: float = 20.0) -> Any:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        # Google sometimes labels the Japanese suggestion response Shift_JIS
        # even though the payload is JSON. Respect the advertised charset.
        raw = response.read().decode(charset, errors="replace").strip()
        # The YouTube suggestion variant is JSONP even when no callback was
        # requested; unwrap its stable callback wrapper before parsing.
        if raw.startswith("window.google.ac") and "(" in raw:
            raw = raw[raw.find("(") + 1 :]
            if raw.endswith(");"):
                raw = raw[:-2]
            elif raw.endswith(")"):
                raw = raw[:-1]
        return json.loads(raw)


def post_json(url: str, body: dict[str, Any], api_key: str, timeout: float = 30.0) -> Any:
    request = urllib.request.Request(
        url,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        method="POST",
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-API-Key": api_key,
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def strings_from_payload(payload: Any) -> Iterable[str]:
    if isinstance(payload, str):
        value = payload.strip()
        if value:
            yield value
        return
    if isinstance(payload, list):
        for item in payload:
            yield from strings_from_payload(item)
        return
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key.lower() in {"keyword", "keywords", "suggestion", "suggestions", "query", "queries", "text"}:
                yield from strings_from_payload(value)
            elif isinstance(value, (dict, list)):
                yield from strings_from_payload(value)


def google_suggest(seed: str, mode: str = "google") -> list[str]:
    params = {"client": "firefox", "hl": "ja", "q": seed}
    if mode == "youtube":
        params.update({"client": "youtube", "ds": "yt"})
    url = "https://suggestqueries.google.com/complete/search?" + urllib.parse.urlencode(params)
    payload = get_json(url)
    if isinstance(payload, list) and len(payload) > 1 and isinstance(payload[1], list):
        values: list[str] = []
        for item in payload[1]:
            candidate = item[0] if isinstance(item, list) and item and isinstance(item[0], str) else item
            if isinstance(candidate, str) and candidate.strip():
                values.append(candidate.strip())
        return values
    return []


def bing_suggest(seed: str) -> list[str]:
    url = "https://api.bing.com/osjson.aspx?" + urllib.parse.urlencode({"query": seed, "market": "ja-JP"})
    payload = get_json(url)
    if isinstance(payload, list) and len(payload) > 1 and isinstance(payload[1], list):
        return [str(item).strip() for item in payload[1] if str(item).strip()]
    return []


def rakko_suggest(seed: str, api_key: str) -> list[str]:
    payload = post_json(
        "https://api.rakkokeyword.com/v1/suggest-keywords",
        {"keyword": seed, "modes": ["google"], "increaseKeyword": False, "limit": 200},
        api_key,
    )
    values = []
    for value in strings_from_payload(payload):
        if value not in values:
            values.append(value)
    return values


def load_seeds(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Seed file must contain a JSON array")
    return data


def load_manual_rows(directory: Path, retrieved_at: str) -> list[dict[str, Any]]:
    """Ingest exports from Trends, Keyword Planner, aramakijake, etc."""
    rows: list[dict[str, Any]] = []
    if not directory.exists():
        return rows
    aliases = {"keyword", "query", "term", "キーワード", "検索キーワード", "クエリ"}
    for path in sorted(directory.glob("*.csv")):
        try:
            with path.open(encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                headers = reader.fieldnames or []
                key = next((header for header in headers if header.strip().lower() in aliases), None)
                if not key:
                    print(f"warning: manual CSV has no keyword column: {path}", file=sys.stderr)
                    continue
                for record in reader:
                    keyword = (record.get(key) or "").strip()
                    if keyword:
                        rows.append({"keyword": keyword, "seed": keyword, "source": f"manual:{path.stem}", "retrieved_at": retrieved_at, "metrics": {k: v for k, v in record.items() if k != key and v}})
        except (OSError, UnicodeError) as exc:
            print(f"warning: manual CSV failed: {path}: {exc}", file=sys.stderr)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect keyword ideas from public/free sources.")
    parser.add_argument("--seeds", default="seo/seeds.json")
    parser.add_argument("--out", required=True)
    parser.add_argument("--config", default="seo/config.json")
    parser.add_argument("--sleep", type=float)
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--manual-dir", default="seo/data/manual")
    args = parser.parse_args()

    seeds = load_seeds(Path(args.seeds))
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    research = config.get("research", {})
    delay = research.get("request_delay_seconds", 0.35) if args.sleep is None else args.sleep
    retrieved_at = datetime.now(timezone.utc).isoformat()
    rows: list[dict[str, Any]] = []
    api_key = os.environ.get("RAKKO_KEYWORD_API_KEY")

    for seed_info in seeds:
        seed = str(seed_info.get("seed", "")).strip()
        if not seed:
            continue
        sources: list[tuple[str, list[str]]] = []
        for source, enabled in (
            ("google_suggest", research.get("google_suggest", True)),
            ("bing_suggest", research.get("bing_suggest", True)),
            ("youtube_suggest", research.get("youtube_suggest", True)),
        ):
            if not enabled:
                continue
            try:
                values = google_suggest(seed, "youtube") if source == "youtube_suggest" else bing_suggest(seed) if source == "bing_suggest" else google_suggest(seed)
                sources.append((source, values))
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                print(f"warning: {source} failed for {seed}: {exc}", file=sys.stderr)
            time.sleep(max(0.0, delay))
        if api_key and research.get("rakkokeyword_api", "optional") != "disabled":
            try:
                sources.append(("rakkokeyword_api", rakko_suggest(seed, api_key)))
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                print(f"warning: rakkokeyword_api failed for {seed}: {exc}", file=sys.stderr)
            time.sleep(max(0.0, delay))

        seen_for_seed: set[str] = set()
        for source, values in sources:
            for keyword in values:
                normalized = " ".join(keyword.split())
                if not normalized or normalized in seen_for_seed or normalized == seed:
                    continue
                seen_for_seed.add(normalized)
                rows.append(
                    {
                        "keyword": normalized,
                        "seed": seed,
                        "source": source,
                        "retrieved_at": retrieved_at,
                        "seed_intent": seed_info.get("intent"),
                        "seed_service_fit": seed_info.get("service_fit", 0),
                    }
                )

    rows.extend(load_manual_rows(Path(args.manual_dir), retrieved_at))
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"retrieved_at": retrieved_at, "rows": rows}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(rows)} keyword observations to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
