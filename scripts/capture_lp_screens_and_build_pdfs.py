#!/usr/bin/env python3
"""Capture every unique research LP screen-by-screen and build LP PDFs."""

from __future__ import annotations

import csv
import json
import math
import re
import subprocess
import time
import unicodedata
from pathlib import Path
from urllib.parse import urlparse

from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs/meta-ad-library-research/2026-07-28-ai-komon-40"
RECORDS_JSON = BASE / "records.json"
RECORDS_CSV = BASE / "records.csv"
SCREEN_ROOT = BASE / "output/lp-screens"
PDF_ROOT = BASE / "output/lp-pdfs"
INDEX_JSON = BASE / "output/lp-capture-index.json"
INDEX_CSV = BASE / "output/lp-capture-index.csv"
SESSION = "lp-capture"
VIEWPORT_W = 1440
VIEWPORT_H = 900
STEP = 900
MAX_SCREENS = 40


def run_browser(*args: str, timeout: int = 75) -> subprocess.CompletedProcess[str]:
    cmd = ["agent-browser", "--session", SESSION, *args]
    return subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)


def output_text(result: subprocess.CompletedProcess[str]) -> str:
    return (result.stdout or "") + "\n" + (result.stderr or "")


def eval_json(expression: str) -> dict:
    result = run_browser("eval", expression, timeout=45)
    text = output_text(result)
    matches = re.findall(r"\{.*\}", text)
    if not matches:
        raise RuntimeError(text[-500:])
    value = matches[-1]
    # agent-browser can return JSON as a quoted JSON string.
    try:
        data = json.loads(value.replace('\\"', '"'))
        if isinstance(data, str):
            data = json.loads(data)
        return data
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Could not parse browser eval: {value}") from exc


def slug_for(index: int, url: str, ad_id: str) -> str:
    host = urlparse(url).netloc.replace("www.", "")
    host = re.sub(r"[^A-Za-z0-9]+", "-", host).strip("-") or "site"
    return f"lp-{index:02d}-{host}-{ad_id}"


def capture_one(index: int, url: str, ad_id: str, advertiser: str) -> dict:
    slug = slug_for(index, url, ad_id)
    screen_dir = SCREEN_ROOT / slug
    pdf_path = PDF_ROOT / f"{slug}.pdf"
    screen_dir.mkdir(parents=True, exist_ok=True)
    PDF_ROOT.mkdir(parents=True, exist_ok=True)
    result = {
        "capture_index": index,
        "landing_page_url": url,
        "advertiser": advertiser,
        "representative_ad_library_id": ad_id,
        "slug": slug,
        "viewport_width": VIEWPORT_W,
        "viewport_height": VIEWPORT_H,
        "page_title": "",
        "page_height_px": None,
        "screen_count": 0,
        "capture_status": "failed",
        "screenshots_dir": f"output/lp-screens/{slug}",
        "pdf_path": f"output/lp-pdfs/{slug}.pdf",
        "error": "",
    }
    try:
        opened = run_browser("open", url, timeout=75)
        # Some external sites keep a never-ending analytics/resource request
        # and agent-browser reports a navigation timeout even though the page
        # is already usable. Validate the actual URL after navigation before
        # deciding that the capture failed.
        run_browser("set", "viewport", str(VIEWPORT_W), str(VIEWPORT_H), timeout=30)
        run_browser("wait", "1800", timeout=30)
        info = eval_json("JSON.stringify({height:Math.max(document.body.scrollHeight,document.documentElement.scrollHeight),title:document.title,url:location.href})")
        expected_host = urlparse(url).netloc
        actual_host = urlparse(info.get("url", "")).netloc
        if expected_host and actual_host and expected_host != actual_host:
            raise RuntimeError(output_text(opened)[-800:])
        result["page_title"] = info.get("title", "")
        result["page_height_px"] = int(info.get("height", VIEWPORT_H) or VIEWPORT_H)

        y = 0
        screen_paths = []
        screen_no = 1
        while y < result["page_height_px"] and screen_no <= MAX_SCREENS:
            run_browser("eval", f"window.scrollTo(0,{y})", timeout=30)
            run_browser("wait", "300", timeout=30)
            shot = screen_dir / f"screen-{screen_no:03d}.png"
            captured = run_browser("screenshot", str(shot), timeout=60)
            if captured.returncode != 0 or not shot.exists():
                raise RuntimeError(output_text(captured)[-800:])
            screen_paths.append(shot)
            screen_no += 1
            y += STEP
            # Lazy-loaded sections can extend the page while scrolling.
            try:
                refreshed = eval_json("JSON.stringify({height:Math.max(document.body.scrollHeight,document.documentElement.scrollHeight)})")
                result["page_height_px"] = max(result["page_height_px"], int(refreshed.get("height", 0) or 0))
            except RuntimeError:
                pass

        result["screen_count"] = len(screen_paths)
        result["capture_status"] = "complete" if y >= result["page_height_px"] else "truncated_max_screens"

        # The PDF page is the screenshot itself at 0.75pt per CSS pixel.
        pdf = canvas.Canvas(str(pdf_path), pagesize=(VIEWPORT_W * 0.75, VIEWPORT_H * 0.75))
        pdf.setTitle(f"{advertiser} LP screen capture")
        for shot in screen_paths:
            pdf.drawImage(ImageReader(str(shot)), 0, 0, width=VIEWPORT_W * 0.75, height=VIEWPORT_H * 0.75, preserveAspectRatio=False, mask="auto")
            pdf.showPage()
        pdf.save()
    except Exception as exc:  # keep the batch moving and record failures in DB
        result["error"] = str(exc)[:1000]
    return result


def unique_lps(records: list[dict]) -> list[tuple[str, str, str]]:
    seen = {}
    for row in records:
        url = row["landing_page_url"]
        if url and url not in seen:
            seen[url] = (row["ad_library_id"], row["advertiser"])
    return [(url, ad_id, advertiser) for url, (ad_id, advertiser) in seen.items()]


def write_indexes(captures: list[dict]) -> None:
    INDEX_JSON.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "captured_at": "2026-07-28",
        "viewport": {"width": VIEWPORT_W, "height": VIEWPORT_H},
        "unique_lp_count": len(captures),
        "completed": sum(c["capture_status"] == "complete" for c in captures),
        "captures": captures,
    }
    INDEX_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    fields = list(captures[0].keys()) if captures else []
    with INDEX_CSV.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(captures)


def attach_to_db(records: list[dict], captures: list[dict]) -> None:
    by_url = {c["landing_page_url"]: c for c in captures}
    fields = list(records[0].keys())
    extra = ["lp_capture_status", "lp_page_title", "lp_page_height_px", "lp_screen_count", "lp_screenshots_dir", "lp_pdf_path", "lp_capture_error"]
    for field in extra:
        if field not in fields:
            fields.append(field)
    for row in records:
        capture = by_url.get(row["landing_page_url"], {})
        row["lp_capture_status"] = capture.get("capture_status", "not_captured")
        row["lp_page_title"] = capture.get("page_title", "")
        row["lp_page_height_px"] = capture.get("page_height_px", "")
        row["lp_screen_count"] = capture.get("screen_count", "")
        row["lp_screenshots_dir"] = capture.get("screenshots_dir", "")
        row["lp_pdf_path"] = capture.get("pdf_path", "")
        row["lp_capture_error"] = capture.get("error", "")
    payload = json.loads(RECORDS_JSON.read_text(encoding="utf-8"))
    payload["lp_capture"] = {
        "captured_at": "2026-07-28",
        "viewport_width": VIEWPORT_W,
        "viewport_height": VIEWPORT_H,
        "unique_lp_count": len(captures),
        "completed": sum(c["capture_status"] == "complete" for c in captures),
        "index_json": "output/lp-capture-index.json",
        "index_csv": "output/lp-capture-index.csv",
    }
    payload["records"] = records
    RECORDS_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    with RECORDS_CSV.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)


def main() -> None:
    records_payload = json.loads(RECORDS_JSON.read_text(encoding="utf-8"))
    records = records_payload["records"]
    targets = unique_lps(records)
    print(f"Capturing {len(targets)} unique LPs at {VIEWPORT_W}x{VIEWPORT_H}")
    captures = []
    for index, (url, ad_id, advertiser) in enumerate(targets, 1):
        print(f"[{index}/{len(targets)}] {advertiser} {url}", flush=True)
        capture = capture_one(index, url, ad_id, advertiser)
        captures.append(capture)
        print(f"  -> {capture['capture_status']} screens={capture['screen_count']} pdf={capture['pdf_path']}", flush=True)
        # Give the browser a moment to settle between external domains.
        time.sleep(0.2)
    write_indexes(captures)
    attach_to_db(records, captures)
    print(json.dumps({
        "unique_lps": len(captures),
        "completed": sum(c["capture_status"] == "complete" for c in captures),
        "truncated": sum(c["capture_status"] == "truncated_max_screens" for c in captures),
        "failed": sum(c["capture_status"] == "failed" for c in captures),
        "screens": sum(c["screen_count"] for c in captures),
        "index": str(INDEX_JSON),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
