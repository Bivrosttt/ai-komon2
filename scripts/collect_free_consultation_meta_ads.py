#!/usr/bin/env python3
"""Collect diverse Meta Ad Library ads whose CTA/claim leads to free consultation."""

from __future__ import annotations

import csv
import json
import re
import subprocess
import time
from collections import Counter
from pathlib import Path
from urllib.parse import parse_qs, quote_plus, unquote, urlparse, urlunparse


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs/meta-ad-library-research/2026-07-28-free-consultation-20"
RAW = BASE / "raw-candidates.json"
RECORDS_JSON = BASE / "records.json"
RECORDS_CSV = BASE / "records.csv"
SESSION = "free-consult-search"
QUERIES = ["無料相談", "無料カウンセリング", "個別相談", "無料面談", "相談会", "無料体験", "無料診断"]
CONSULT_TERMS = ["無料相談", "無料カウンセリング", "個別相談", "無料面談", "相談無料", "無料でご相談", "まずはご相談", "相談会", "無料体験", "無料診断"]
CTA_TERMS = ["無料相談", "カウンセリング", "個別相談", "無料面談", "相談会", "無料体験", "無料診断", "ご相談", "お問い合わせ", "Book Now", "見積もり", "Learn More", "詳しくはこちら", "資料請求", "申し込む"]
BLOCKED_HOSTS = {
    "line.me",
    "lin.ee",
    "instagram.com",
    "facebook.com",
    "fb.me",
    "tinyurl.com",
    "t.co",
    "outlook.office365.com",
    "calendly.com",
}
BLOCKED_PATH_MARKERS = ("/cms/yoyaku/", "/bookings/", "/calendar/")


def run_browser(*args: str, timeout: int = 75) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["agent-browser", "--session", SESSION, *args], text=True, capture_output=True, timeout=timeout)


def decode_eval(output: str) -> str:
    value = output.strip()
    # agent-browser returns a JSON string on stdout.
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, str) else json.dumps(parsed, ensure_ascii=False)
    except json.JSONDecodeError:
        return value


def clean_url(url: str) -> str:
    url = unquote(url).strip()
    if not url.startswith(("http://", "https://")):
        return ""
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    if any(host == blocked or host.endswith("." + blocked) for blocked in BLOCKED_HOSTS):
        return ""
    if any(marker in parsed.path.lower() for marker in BLOCKED_PATH_MARKERS):
        return ""
    query = []
    for key, value in parse_qs(parsed.query, keep_blank_values=True).items():
        if key.lower() in {"fbclid", "h", "dmai", "ftid", "adcd"} or key.lower().startswith("utm_"):
            continue
        query.extend((key, item) for item in value)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path or "/", "", "&".join(f"{k}={v}" for k, v in query), ""))


def parse_snapshot(snapshot: str, query: str) -> list[dict]:
    records = []
    blocks = re.split(r'(?=  - text: "?アクティブ ライブラリID:)', snapshot)
    for block in blocks:
        id_match = re.search(r"ライブラリID: (\d+).*?掲載開始日: ([^\n\"]+)", block, re.S)
        if not id_match:
            continue
        ad_id, started = id_match.groups()
        links = re.findall(r'- link "([^"]*)"[^\n]*\n\s+- /url: (\S+)', block)
        destination = ""
        link_label = ""
        for label, href in links:
            if "l.facebook.com/l.php?u=" in href:
                try:
                    destination = parse_qs(urlparse(href).query).get("u", [""])[0]
                except Exception:
                    destination = ""
                link_label = label
                break
        lp_url = clean_url(destination)
        if not lp_url:
            continue
        advertiser_match = re.search(r'広告の詳細を見る"[^\n]*\n\s+- link "([^"]+)"', block, re.S)
        advertiser = advertiser_match.group(1).strip() if advertiser_match else ""
        copy_match = re.search(r'スポンサー広告\n\s+- button "([^"]*)"', block)
        ad_copy = copy_match.group(1).strip() if copy_match else ""
        consult_text = f"{ad_copy} {link_label} {block}"
        if not any(term in consult_text for term in CONSULT_TERMS):
            continue
        cta = next((term for term in CTA_TERMS if term.lower() in link_label.lower()), "")
        if not cta:
            cta = next((term for term in CTA_TERMS if term.lower() in ad_copy.lower()), "")
        score = 0
        score += 5 if any(term in link_label for term in ["無料相談", "無料カウンセリング", "個別相談", "無料面談", "相談会"]) else 0
        score += 3 if any(term in ad_copy for term in ["無料相談", "無料カウンセリング", "個別相談", "無料面談", "相談無料"]) else 0
        score += 1 if "無料診断" in consult_text or "無料体験" in consult_text else 0
        score += 1 if len(ad_copy) >= 30 else 0
        records.append({
            "captured_at": "2026-07-28",
            "search_term": query,
            "advertiser": advertiser,
            "ad_library_id": ad_id,
            "started_running": started.strip(),
            "ad_copy": ad_copy,
            "cta": cta,
            "landing_page_url": lp_url,
            "ad_library_url": f"https://www.facebook.com/ads/library/?id={ad_id}",
            "link_label": link_label,
            "score": score,
            "notes": "Meta広告ライブラリUIの掲載中広告から取得。成果指標（CV/CPA）は取得していない。",
        })
    return records


def collect() -> list[dict]:
    all_records = []
    for query in QUERIES:
        url = "https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=JP&q=" + quote_plus(query) + "&search_type=keyword_unordered"
        result = run_browser("open", url, timeout=75)
        time.sleep(2.2)
        snapshot = output_text(run_browser("snapshot", "-c", timeout=60))
        parsed = parse_snapshot(snapshot, query)
        all_records.extend(parsed)
        print(f"{query}: {len(parsed)} candidates", flush=True)
    unique = {}
    for row in all_records:
        key = (row["ad_library_id"], row["landing_page_url"])
        if key not in unique or row["score"] > unique[key]["score"]:
            unique[key] = row
    candidates = list(unique.values())
    candidates.sort(key=lambda r: (-r["score"], r["advertiser"], r["ad_library_id"]))
    return candidates


def output_text(result: subprocess.CompletedProcess[str]) -> str:
    return (result.stdout or "") + "\n" + (result.stderr or "")


def select(records: list[dict]) -> list[dict]:
    selected = []
    used_urls = set()
    advertisers = Counter()
    domains = Counter()
    for max_domain in (2, 3, 5):
        for row in records:
            if len(selected) >= 20:
                break
            url = row["landing_page_url"]
            domain = urlparse(url).netloc.lower()
            if url in used_urls or advertisers[row["advertiser"]] >= 2 or domains[domain] >= max_domain:
                continue
            selected.append(row)
            used_urls.add(url)
            advertisers[row["advertiser"]] += 1
            domains[domain] += 1
        if len(selected) >= 20:
            break
    if len(selected) != 20:
        raise RuntimeError(f"Only selected {len(selected)} LPs from {len(records)} eligible candidates")
    selected.sort(key=lambda r: (-r["score"], r["advertiser"], r["ad_library_id"]))
    return selected


def main() -> None:
    BASE.mkdir(parents=True, exist_ok=True)
    candidates = collect()
    selected = select(candidates)
    RAW.write_text(json.dumps({"captured_at": "2026-07-28", "queries": QUERIES, "candidate_count": len(candidates), "records": candidates}, ensure_ascii=False, indent=2), encoding="utf-8")
    payload = {
        "captured_at": "2026-07-28",
        "country": "JP",
        "active_status": "active",
        "count": len(selected),
        "unique_advertisers": len({r["advertiser"] for r in selected}),
        "unique_landing_pages": len({r["landing_page_url"] for r in selected}),
        "queries": QUERIES,
        "records": selected,
    }
    RECORDS_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    with RECORDS_CSV.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(selected[0].keys()))
        writer.writeheader()
        writer.writerows(selected)
    print(json.dumps({"candidates": len(candidates), "selected": len(selected), "advertisers": payload["unique_advertisers"], "landing_pages": payload["unique_landing_pages"], "records": str(RECORDS_JSON)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
