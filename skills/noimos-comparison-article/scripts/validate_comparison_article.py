#!/usr/bin/env python3
"""Validate comparison-article requirements that generic SEO checks miss."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup


BANNED_PHRASES = [
    "同じ台本",
    "同じ素材",
    "同じ尺",
    "生成時間",
    "修正回数",
    "権利確認",
    "公開までの工数",
    "誰が止める",
    "社内で",
    "確認してください",
    "公式ページを再確認",
    "対象プランを確認",
    "契約前",
    "初回は",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--services", required=True, help="JSON array of service names")
    parser.add_argument("--out", required=True)
    parser.add_argument("--screenshot-dir", help="Directory containing official service home screenshots")
    parser.add_argument("--screenshot-ledger", help="JSON ledger containing source URLs and manual visual checks")
    parser.add_argument("--home-urls", help="JSON object mapping service names to canonical official home URLs")
    args = parser.parse_args()

    path = Path(args.input)
    html = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    services = json.loads(args.services)
    home_urls = json.loads(args.home_urls) if args.home_urls else {}
    text = soup.get_text(" ", strip=True)
    blockers: list[dict] = []
    warnings: list[dict] = []

    for phrase in BANNED_PHRASES:
        if phrase in text:
            blockers.append({"code": "banned_reader_burden", "phrase": phrase})

    required_markers = {
        "price": ["価格", "料金", "月額", "年額"],
        "usage": ["usage", "クレジット", "分数", "生成数", "席数", "文字数", "利用量"],
        "cost_effectiveness": ["コスパ", "実効コスト", "単位あたり", "費用対効果"],
        "strengths_weaknesses": ["強み", "弱み", "向く", "向かない"],
    }
    for name, markers in required_markers.items():
        if not any(marker.lower() in text.lower() for marker in markers):
            blockers.append({"code": "required_comparison_section_missing", "section": name})

    key_points = soup.select_one(".key-points")
    if not key_points:
        blockers.append({"code": "key_points_missing"})
    else:
        key_point_text = key_points.get_text(" ", strip=True)
        missing_services = [service for service in services if service not in key_point_text]
        if missing_services:
            blockers.append({"code": "key_points_service_missing", "services": missing_services})
        key_point_markers = ["月", "分", "選", "向き", "不向き", "第一候補", "credits", "$", "価格"]
        marker_count = sum(1 for marker in key_point_markers if marker.lower() in key_point_text.lower())
        if marker_count < 4 or not re.search(r"\d", key_point_text):
            blockers.append({"code": "key_points_not_decision_ready", "marker_count": marker_count})

    first_link_failures = []
    for service in services:
        # Locate the first text occurrence in DOM order and require an ancestor link.
        found = False
        linked = False
        for node in soup.find_all(string=re.compile(re.escape(service))):
            # JSON-LD and metadata repeat service names before the visible article.
            # The requirement concerns the first reader-visible occurrence.
            if node.parent and node.parent.name in {"script", "style", "title"}:
                continue
            found = True
            parent = node.parent
            linked = parent.name == "a" or parent.find_parent("a") is not None
            break
        if not found:
            first_link_failures.append({"service": service, "reason": "service_name_missing"})
        elif not linked:
            first_link_failures.append({"service": service, "reason": "first_occurrence_not_linked"})
        elif service in home_urls:
            link = parent if parent.name == "a" else parent.find_parent("a")
            href = (link.get("href") or "").split("#", 1)[0].rstrip("/")
            expected = str(home_urls[service]).split("#", 1)[0].rstrip("/")
            if href != expected:
                first_link_failures.append(
                    {
                        "service": service,
                        "reason": "first_occurrence_not_home_url",
                        "href": link.get("href"),
                        "expected": home_urls[service],
                    }
                )
    if first_link_failures:
        blockers.append({"code": "first_service_link_missing", "detail": first_link_failures})

    # Every review service must begin with an official home/product screenshot.
    reviews_heading = soup.select_one("#reviews")
    screenshot_failures = []
    if reviews_heading:
        review_h3s = []
        for node in reviews_heading.find_all_next():
            if node.name == "h2":
                break
            if node.name == "h3":
                review_h3s.append(node)
        if len(review_h3s) < len(services):
            screenshot_failures.append({"reason": "review_heading_count_less_than_services", "review_h3_count": len(review_h3s)})
        for heading in review_h3s[:len(services)]:
            previous = heading.find_previous_sibling()
            classes = previous.get("class", []) if previous else []
            if not previous or "service-home-shot" not in classes or not previous.find("img"):
                screenshot_failures.append({"service_heading": heading.get_text(" ", strip=True), "reason": "screenshot_not_immediately_before_heading"})
    if args.screenshot_dir:
        screenshot_dir = Path(args.screenshot_dir)
        image_files = sorted([*screenshot_dir.glob("*.png"), *screenshot_dir.glob("*.webp"), *screenshot_dir.glob("*.jpg"), *screenshot_dir.glob("*.jpeg")])
        if len(image_files) < len(services):
            screenshot_failures.append({"reason": "screenshot_file_count_less_than_services", "file_count": len(image_files), "screenshot_dir": str(screenshot_dir)})
    if args.screenshot_ledger:
        ledger_path = Path(args.screenshot_ledger)
        try:
            ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
            entries = ledger.get("services") or ledger.get("screenshots") or []
            if ledger.get("manual_visual_review", {}).get("status") != "pass":
                screenshot_failures.append({"reason": "manual_visual_review_not_pass", "ledger": str(ledger_path)})
            if len(entries) < len(services):
                screenshot_failures.append({"reason": "screenshot_ledger_entry_count_less_than_services", "entry_count": len(entries), "ledger": str(ledger_path)})
            entries_by_service = {entry.get("service") or entry.get("name"): entry for entry in entries}
            missing_visual_services = [
                service for service in services
                if entries_by_service.get(service, {}).get("visual_check", {}).get("status") != "pass"
            ]
            if missing_visual_services:
                screenshot_failures.append({"reason": "expected_service_visual_check_missing_or_not_pass", "services": missing_visual_services, "ledger": str(ledger_path)})
            for entry in entries:
                if entry.get("visual_check", {}).get("status") != "pass":
                    screenshot_failures.append({"reason": "screenshot_visual_check_not_pass", "service": entry.get("service") or entry.get("name"), "ledger": str(ledger_path)})
        except (OSError, json.JSONDecodeError) as exc:
            screenshot_failures.append({"reason": "screenshot_ledger_unreadable", "ledger": str(ledger_path), "error": str(exc)})
    if screenshot_failures:
        blockers.append({"code": "home_screenshot_missing", "detail": screenshot_failures})

    service_cta = soup.select_one(".service-cta")
    if not service_cta:
        blockers.append({"code": "cta_missing"})
    else:
        cta_text = service_cta.get_text(" ", strip=True)
        if "AI顧問室" not in text or "最短経路" not in cta_text:
            blockers.append({"code": "final_ai_advisor_cta_missing"})
        if "無料でコンサル一回分をプレゼント" not in cta_text:
            blockers.append({"code": "gift_cta_missing"})
        cta_heading = service_cta.find("h2")
        headings = soup.find_all("h2")
        if cta_heading is not None and headings and headings[-1] is not cta_heading:
            warnings.append({"code": "cta_not_last_h2", "detail": "CTA should be the final value-delivery block."})

    report = {
        "tool": "noimos-comparison-article",
        "input": str(path),
        "status": "BLOCK" if blockers else ("PASS_WITH_WARNINGS" if warnings else "PASS"),
        "blockers": blockers,
        "warnings": warnings,
        "services": services,
        "home_urls": home_urls,
    }
    Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "blockers": len(blockers), "warnings": len(warnings)}, ensure_ascii=False))
    return 0 if not blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
