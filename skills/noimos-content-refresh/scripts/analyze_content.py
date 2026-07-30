#!/usr/bin/env python3
"""Inventory local HTML articles and build a structural refresh queue."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path


def strip_html(value: str) -> str:
    value = re.sub(r"<script\b[\s\S]*?</script>", " ", value, flags=re.I)
    value = re.sub(r"<style\b[\s\S]*?</style>", " ", value, flags=re.I)
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def extract(pattern: str, html: str) -> str:
    match = re.search(pattern, html, re.I | re.S)
    return strip_html(match.group(1)) if match else ""


def parse_iso(value: str) -> date | None:
    try:
        return date.fromisoformat(value[:10])
    except (ValueError, TypeError):
        return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--articles", default="articles")
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    article_root = (root / args.articles).resolve()
    as_of = date.fromisoformat(args.as_of)
    files = sorted(article_root.glob("**/*.html"))
    records: list[dict] = []
    titles: defaultdict[str, list[str]] = defaultdict(list)

    for path in files:
        html = path.read_text(encoding="utf-8", errors="replace")
        title = extract(r"<title\b[^>]*>(.*?)</title>", html)
        h1 = extract(r"<h1\b[^>]*>(.*?)</h1>", html)
        canonical_match = re.search(
            r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)', html, re.I
        )
        canonical = canonical_match.group(1) if canonical_match else ""
        modified_match = re.search(r'"dateModified"\s*:\s*"([^"]+)"', html)
        modified = modified_match.group(1) if modified_match else ""
        modified_date = parse_iso(modified)
        age_days = (as_of - modified_date).days if modified_date else None
        text = strip_html(html)
        jp_chars = len(re.findall(r"[\u3040-\u30ff\u3400-\u9fff]", text))
        is_collection = (
            '"@type": "CollectionPage"' in html
            or '"@type":"CollectionPage"' in html
            or path.resolve() == (article_root / "index.html").resolve()
        )
        content_type = "collection" if is_collection else "article"
        hrefs = re.findall(r'<a\b[^>]+href=["\']([^"\']+)', html, re.I)
        internal = [href for href in hrefs if href.startswith(("/", "./", "../"))]
        broken = []
        for href in internal:
            clean = href.split("#", 1)[0].split("?", 1)[0]
            if not clean or clean == "/":
                continue
            if clean.startswith("/"):
                target = root / clean.lstrip("/")
            else:
                target = path.parent / clean
            if target.suffix:
                exists = target.resolve().exists()
            else:
                exists = (target / "index.html").resolve().exists() or target.resolve().exists()
            if not exists:
                broken.append(href)
        slug = str(path.relative_to(root))
        title_key = re.sub(r"\s*[|｜].*$", "", title).strip().lower()
        titles[title_key].append(slug)
        issues = []
        if not canonical:
            issues.append("missing_canonical")
        if not modified_date:
            issues.append("missing_date_modified")
        elif age_days is not None and age_days >= 180:
            issues.append("stale_180")
        elif age_days is not None and age_days >= 90:
            issues.append("review_90")
        if not is_collection and jp_chars < 2000:
            issues.append("thin_for_decision_content")
        if len(set(internal)) < 3:
            issues.append("few_internal_links")
        if broken:
            issues.append("broken_internal_links")
        records.append(
            {
                "path": slug,
                "title": title,
                "h1": h1,
                "canonical": canonical,
                "date_modified": modified,
                "age_days": age_days,
                "content_type": content_type,
                "japanese_characters": jp_chars,
                "internal_links": len(set(internal)),
                "broken_links": sorted(set(broken)),
                "issues": issues,
            }
        )

    duplicates = {title: paths for title, paths in titles.items() if title and len(paths) > 1}
    for record in records:
        key = re.sub(r"\s*[|｜].*$", "", record["title"]).strip().lower()
        if key in duplicates:
            record["issues"].append("duplicate_title")
        severity = sum(
            {
                "missing_canonical": 30,
                "missing_date_modified": 15,
                "stale_180": 20,
                "review_90": 10,
                "thin_for_decision_content": 15,
                "few_internal_links": 10,
                "broken_internal_links": 25,
                "duplicate_title": 20,
            }.get(issue, 5)
            for issue in record["issues"]
        )
        record["priority_score"] = severity
        record["recommended_action"] = (
            "substantial_review" if severity >= 40
            else "light_refresh" if severity >= 15
            else "keep"
        )

    records.sort(key=lambda item: item["priority_score"], reverse=True)
    issue_counts = Counter(issue for record in records for issue in record["issues"])
    report = {
        "tool": "noimos-content-refresh",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "as_of": args.as_of,
        "article_count": len(records),
        "issue_counts": dict(issue_counts),
        "duplicate_titles": duplicates,
        "queue": records,
        "limitations": [
            "No GSC, conversion, backlink, or live SERP data was used.",
            "Thin-content flags are review prompts, not automatic rewrite decisions.",
            "No redirect, deletion, noindex, or content mutation was performed.",
        ],
    }
    Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"articles": len(records), "flagged": sum(bool(r["issues"]) for r in records), "top": records[0]["path"] if records else None}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
