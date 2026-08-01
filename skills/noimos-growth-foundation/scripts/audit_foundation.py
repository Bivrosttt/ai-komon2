#!/usr/bin/env python3
"""Deterministic local baseline for the Noimos growth-foundation skill."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def add(findings: list[dict], check: str, status: str, evidence: str, priority: str) -> None:
    findings.append(
        {"check": check, "status": status, "evidence": evidence, "priority": priority}
    )


def first(pattern: str, text: str, flags: int = re.I | re.S) -> str:
    match = re.search(pattern, text, flags)
    return re.sub(r"\s+", " ", match.group(1)).strip() if match else ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--html", default="index.html")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    html_path = (root / args.html).resolve()
    if not html_path.is_file() or root not in html_path.parents:
        raise SystemExit(f"HTML file not found inside root: {html_path}")
    html = html_path.read_text(encoding="utf-8", errors="replace")
    findings: list[dict] = []

    title = first(r"<title[^>]*>(.*?)</title>", html)
    add(findings, "title", "pass" if 10 <= len(title) <= 70 else "warn",
        title or "missing", "P1")

    description = first(
        r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']', html
    ) or first(
        r'<meta[^>]+content=["\'](.*?)["\'][^>]+name=["\']description["\']', html
    )
    add(findings, "meta_description", "pass" if 60 <= len(description) <= 180 else "warn",
        f"{len(description)} chars" if description else "missing", "P1")

    canonical = first(
        r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\'](.*?)["\']', html
    ) or first(
        r'<link[^>]+href=["\'](.*?)["\'][^>]+rel=["\']canonical["\']', html
    )
    add(findings, "canonical", "pass" if canonical.startswith("http") else "fail",
        canonical or "missing", "P0")

    viewport = bool(re.search(r'<meta[^>]+name=["\']viewport["\']', html, re.I))
    add(findings, "viewport", "pass" if viewport else "fail",
        "present" if viewport else "missing", "P0")

    h1s = re.findall(r"<h1\b[^>]*>(.*?)</h1>", html, re.I | re.S)
    add(findings, "single_h1", "pass" if len(h1s) == 1 else "warn",
        f"{len(h1s)} H1 elements", "P1")

    scripts = re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html, re.I | re.S
    )
    valid_schema = 0
    schema_types: list[str] = []
    for raw in scripts:
        try:
            payload = json.loads(raw)
            valid_schema += 1
            nodes = payload.get("@graph", []) if isinstance(payload, dict) else []
            candidates = [payload] + nodes if isinstance(payload, dict) else payload
            for node in candidates:
                if isinstance(node, dict) and node.get("@type"):
                    value = node["@type"]
                    schema_types.extend(value if isinstance(value, list) else [value])
        except json.JSONDecodeError:
            pass
    add(findings, "json_ld", "pass" if valid_schema else "fail",
        f"{valid_schema}/{len(scripts)} valid; types={sorted(set(schema_types))}", "P0")

    og_required = ["og:title", "og:description", "og:url", "og:image"]
    missing_og = [
        key for key in og_required
        if not re.search(
            rf'<meta[^>]+property=["\']{re.escape(key)}["\'][^>]+content=', html, re.I
        )
    ]
    add(findings, "open_graph", "pass" if not missing_og else "warn",
        "complete" if not missing_og else f"missing {', '.join(missing_og)}", "P1")

    flattened_ctas = []
    for anchor_tag in re.findall(r"<a\b[^>]*>", html, re.I):
        class_match = re.search(r'class=["\']([^"\']*)["\']', anchor_tag, re.I)
        href_match = re.search(r'href=["\']([^"\']*)["\']', anchor_tag, re.I)
        if (
            class_match
            and href_match
            and re.search(r"(?:^|\s)(?:btn|cta|button)(?:[-_\s]|$)", class_match.group(1), re.I)
        ):
            flattened_ctas.append(href_match.group(1))
    flattened_ctas = sorted(set(flattened_ctas))
    add(findings, "cta_links", "pass" if flattened_ctas else "fail",
        f"{len(flattened_ctas)} unique CTA destinations: {flattened_ctas[:5]}", "P0")

    analytics_tokens = []
    for token, pattern in {
        "gtag": r"\bgtag\s*\(",
        "dataLayer": r"\bdataLayer\b",
        "meta_pixel": r"\bfbq\s*\(",
        "lead_event": r"generate_lead|lead_submit|timerex_click",
    }.items():
        if re.search(pattern, html, re.I):
            analytics_tokens.append(token)
    add(findings, "analytics_source", "pass" if analytics_tokens else "warn",
        f"source markers: {analytics_tokens}; live receipt not verified", "P1")

    robots_path = root / "robots.txt"
    robots = robots_path.read_text(encoding="utf-8", errors="replace") if robots_path.exists() else ""
    has_sitemap = bool(re.search(r"^\s*Sitemap:\s*https?://", robots, re.I | re.M))
    disallow_all = bool(re.search(r"User-agent:\s*\*[\s\S]{0,200}Disallow:\s*/\s*$", robots, re.I | re.M))
    robot_status = "pass" if robots and has_sitemap and not disallow_all else "fail"
    add(findings, "robots_and_sitemap", robot_status,
        f"robots={robots_path.exists()}, sitemap={has_sitemap}, disallow_all={disallow_all}", "P0")

    llms_path = root / "llms.txt"
    llms = llms_path.read_text(encoding="utf-8", errors="replace") if llms_path.exists() else ""
    add(findings, "llms_txt", "pass" if len(llms.strip()) >= 80 else "warn",
        f"{len(llms)} chars" if llms else "missing", "P2")

    status_counts = {
        key: sum(1 for item in findings if item["status"] == key)
        for key in ("pass", "warn", "fail")
    }
    overall = "fail" if status_counts["fail"] else "warn" if status_counts["warn"] else "pass"
    report = {
        "tool": "noimos-growth-foundation",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "html": str(html_path),
        "overall": overall,
        "summary": status_counts,
        "findings": findings,
        "limitations": [
            "Source inspection does not verify live network firing or analytics receipt.",
            "Rendered mobile/desktop visual checks are required separately.",
            "Positioning quality and trust proof require human review.",
        ],
    }
    Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"overall": overall, **status_counts}, ensure_ascii=False))
    return 1 if status_counts["fail"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
