#!/usr/bin/env python3
"""Validate structural publication gates for an HTML SEO/GEO article."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


def clean_html(value: str) -> str:
    value = re.sub(r"<script\b[\s\S]*?</script>", " ", value, flags=re.I)
    value = re.sub(r"<style\b[\s\S]*?</style>", " ", value, flags=re.I)
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def check(results: list[dict], name: str, passed: bool, evidence: str, priority: str = "P1") -> None:
    results.append(
        {"check": name, "status": "pass" if passed else "fail", "evidence": evidence, "priority": priority}
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--site-root", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    path = Path(args.input).resolve()
    site_root = Path(args.site_root).resolve()
    html = path.read_text(encoding="utf-8", errors="replace")
    text = clean_html(html)
    results: list[dict] = []

    title = re.findall(r"<title\b[^>]*>(.*?)</title>", html, re.I | re.S)
    h1s = re.findall(r"<h1\b[^>]*>(.*?)</h1>", html, re.I | re.S)
    h2s = re.findall(r"<h2\b[^>]*>(.*?)</h2>", html, re.I | re.S)
    check(results, "title", len(title) == 1 and 15 <= len(clean_html(title[0])) <= 90,
          clean_html(title[0]) if title else "missing", "P0")
    check(results, "single_h1", len(h1s) == 1,
          f"{len(h1s)} H1 elements", "P0")
    check(results, "h2_depth", 4 <= len(h2s) <= 12,
          f"{len(h2s)} H2 elements")

    canonical_match = re.search(
        r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)', html, re.I
    )
    canonical = canonical_match.group(1) if canonical_match else ""
    check(results, "canonical", canonical.startswith("https://"), canonical or "missing", "P0")

    meta_desc = re.search(
        r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)', html, re.I
    )
    desc = meta_desc.group(1) if meta_desc else ""
    check(results, "meta_description", 60 <= len(desc) <= 180,
          f"{len(desc)} chars" if desc else "missing")

    schema_blocks = re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html, re.I | re.S
    )
    schema_types: set[str] = set()
    schema_valid = True
    for raw in schema_blocks:
        try:
            payload = json.loads(raw)
            nodes = [payload] + payload.get("@graph", []) if isinstance(payload, dict) else payload
            for node in nodes:
                if isinstance(node, dict):
                    types = node.get("@type", [])
                    schema_types.update(types if isinstance(types, list) else [types] if types else [])
        except json.JSONDecodeError:
            schema_valid = False
    article_schema = bool(schema_types.intersection({"Article", "BlogPosting"}))
    check(results, "article_schema", schema_valid and article_schema,
          f"valid={schema_valid}, types={sorted(schema_types)}", "P0")

    answer_first = bool(re.search(r'class=["\'][^"\']*(?:answer|summary|key-points|tldr)', html, re.I))
    check(results, "answer_first", answer_first, "answer/summary block detected" if answer_first else "missing")

    faq = bool(re.search(r"(よくある質問|FAQ|Frequently Asked)", text, re.I))
    check(results, "visible_faq", faq, "present" if faq else "missing")

    images = re.findall(r"<img\b([^>]+)>", html, re.I)
    good_images = sum(
        1 for attrs in images
        if re.search(r'\balt=["\'][^"\']{8,}["\']', attrs, re.I)
        and re.search(r'\bsrc=["\'][^"\']+', attrs, re.I)
    )
    figcaptions = len(re.findall(r"<figcaption\b", html, re.I))
    check(results, "article_diagram", good_images >= 1 and figcaptions >= 1,
          f"images_with_alt={good_images}, figcaptions={figcaptions}", "P0")

    hrefs = re.findall(r'<a\b[^>]+href=["\']([^"\']+)', html, re.I)
    external = [h for h in hrefs if h.startswith("http")]
    canonical_host = urlparse(canonical).netloc
    internal = [
        h for h in hrefs
        if h.startswith(("/", "./", "../")) or (canonical_host and canonical_host in h)
    ]
    check(results, "internal_links", len(set(internal)) >= 3,
          f"{len(set(internal))} unique")
    check(results, "external_sources", len(set(external)) >= 2,
          f"{len(set(external))} unique")

    cta = bool(re.search(r'class=["\'][^"\']*(?:tool-cta|service-cta|cta)', html, re.I))
    check(results, "cta", cta, "present" if cta else "missing")
    author_date = bool(re.search(r'"author"\s*:', html)) and bool(
        re.search(r'"dateModified"\s*:', html)
    )
    check(results, "author_and_date", author_date, "present" if author_date else "missing", "P0")

    japanese_chars = len(re.findall(r"[\u3040-\u30ff\u3400-\u9fff]", text))
    check(results, "substantive_length", japanese_chars >= 2000,
          f"{japanese_chars} Japanese characters")

    placeholders = re.findall(r"\[(?:TODO|TBD|INTERNAL-LINK|STAT|IMAGE|CLAIM)[^\]]*\]", text, re.I)
    check(results, "no_placeholders", not placeholders,
          "none" if not placeholders else f"{len(placeholders)} placeholders", "P0")

    local_missing = []
    for src in re.findall(r'<img\b[^>]+src=["\']([^"\']+)', html, re.I):
        if src.startswith(("http://", "https://", "data:")):
            continue
        resolved = (path.parent / src).resolve()
        if site_root not in resolved.parents and resolved != site_root:
            local_missing.append(f"outside-root:{src}")
        elif not resolved.exists():
            local_missing.append(src)
    check(results, "local_assets", not local_missing,
          "all present" if not local_missing else f"missing={local_missing}", "P0")

    failures = [item for item in results if item["status"] == "fail"]
    p0 = [item for item in failures if item["priority"] == "P0"]
    overall = "block" if p0 else "needs_work" if failures else "pass"
    report = {
        "tool": "noimos-seo-geo-article",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input": str(path),
        "overall": overall,
        "score": round(100 * (len(results) - len(failures)) / len(results)),
        "checks": results,
        "human_approval_required": True,
    }
    Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"overall": overall, "score": report["score"], "failures": len(failures), "p0": len(p0)}, ensure_ascii=False))
    return 1 if overall != "pass" else 0


if __name__ == "__main__":
    raise SystemExit(main())
