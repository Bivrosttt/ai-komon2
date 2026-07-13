#!/usr/bin/env python3
"""Static SEO audit for the repository's HTML pages."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse


TAG_RE = re.compile(r"<(?P<tag>title|h1|meta|link)\b(?P<attrs>[^>]*)>(?P<body>.*?)</\1>|<(?P<single>meta|link)\b(?P<single_attrs>[^>]*)/?>", re.I | re.S)
ATTR_RE = re.compile(r"([:\w-]+)\s*=\s*([\"'])(.*?)\2", re.S)


def attrs(value: str) -> dict[str, str]:
    return {match.group(1).lower(): re.sub(r"\s+", " ", match.group(3).strip()) for match in ATTR_RE.finditer(value)}


def text_content(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value).strip()


def audit_file(path: Path, root: Path) -> dict:
    source = path.read_text(encoding="utf-8", errors="ignore")
    title_match = re.search(r"<title[^>]*>(.*?)</title>", source, re.I | re.S)
    description = ""
    canonical = ""
    og_title = ""
    og_description = ""
    for match in re.finditer(r"<(?:meta|link)\b([^>]*)/?>", source, re.I | re.S):
        item = attrs(match.group(1))
        if item.get("name", "").lower() == "description":
            description = item.get("content", "")
        if item.get("property", "").lower() == "og:title":
            og_title = item.get("content", "")
        if item.get("property", "").lower() == "og:description":
            og_description = item.get("content", "")
        if item.get("rel", "").lower() == "canonical":
            canonical = item.get("href", "")
    h1s = [text_content(match.group(1)) for match in re.finditer(r"<h1\b[^>]*>(.*?)</h1>", source, re.I | re.S)]
    issues: list[str] = []
    title = text_content(title_match.group(1)) if title_match else ""
    if not title:
        issues.append("missing_title")
    elif len(title) > 60:
        issues.append("title_over_60_chars")
    if not description:
        issues.append("missing_meta_description")
    elif len(description) > 160:
        issues.append("meta_description_over_160_chars")
    if not canonical:
        issues.append("missing_canonical")
    if len(h1s) != 1:
        issues.append("h1_count_not_one")
    if not og_title:
        issues.append("missing_og_title")
    if not og_description:
        issues.append("missing_og_description")

    # SEO articles require at least one real, crawlable image. CSS-only hero
    # visuals are not sufficient for the article production rule.
    if str(path.relative_to(root)).startswith("articles/"):
        if not re.search(r"<img\b[^>]+src=", source, re.I):
            issues.append("article_missing_diagram")
        if re.search(r"<img\b", source, re.I) and not re.search(r"<figcaption\b", source, re.I):
            issues.append("article_missing_figcaption")

    broken_links: list[str] = []
    for match in re.finditer(r"href\s*=\s*[\"']([^\"']+)", source, re.I):
        href = match.group(1).split("#", 1)[0]
        if not href or href.startswith(("http://", "https://", "mailto:", "tel:", "javascript:", "data:")):
            continue
        parsed = urlparse(href)
        candidate = (root / parsed.path.lstrip("/")) if parsed.path.startswith("/") else (path.parent / parsed.path)
        if parsed.path and candidate.suffix in {".html", ".css", ".js", ".pdf"} and not candidate.exists():
            broken_links.append(href)
    return {"path": str(path.relative_to(root)), "title": title, "description": description, "canonical": canonical, "h1": h1s, "issues": issues, "broken_local_links": sorted(set(broken_links))}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--json-out", required=True)
    parser.add_argument("--md-out", required=True)
    args = parser.parse_args()
    root = Path(args.root).resolve()
    pages = [audit_file(path, root) for path in sorted(root.rglob("*.html")) if ".git" not in path.parts and "node_modules" not in path.parts]
    title_counts = Counter(page["title"] for page in pages if page["title"])
    for page in pages:
        if title_counts[page["title"]] > 1:
            page["issues"].append("duplicate_title")
    issue_counts = Counter(issue for page in pages for issue in page["issues"])
    payload = {"page_count": len(pages), "issue_counts": dict(issue_counts), "pages": pages}
    json_path = Path(args.json_out)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Site SEO audit", "", f"- pages: {len(pages)}", "- issues: {sum(issue_counts.values())}", "", "## Issue counts", ""]
    lines += [f"- `{key}`: {value}" for key, value in issue_counts.most_common()]
    lines += ["", "## Pages requiring attention", ""]
    for page in pages:
        if page["issues"] or page["broken_local_links"]:
            lines.append(f"- `{page['path']}`: {', '.join(sorted(set(page['issues'] + ([f'broken:{href}' for href in page['broken_local_links']]))))}")
    md_path = Path(args.md_out)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"audited {len(pages)} HTML pages; {sum(issue_counts.values())} issues")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
