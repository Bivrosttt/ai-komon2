#!/usr/bin/env python3
"""Build the 40-ad Meta Ad Library research DB and a compact PDF report."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import quote

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs/meta-ad-library-research/2026-07-28-ai-komon-40"
RAW = BASE / "raw-selected-ads.json"
LEGACY = ROOT / "docs/meta-ad-library-research/records.csv"
OUT_JSON = BASE / "records.json"
OUT_CSV = BASE / "records.csv"
OUT_PDF = BASE / "output/pdf/ai-komon-competitive-lp-research-2026-07-28.pdf"

EXCLUDED_ADVERTISERS = {
    "パソコン工房",
    "ケア・オール",
    "P-Tips",
    "株式会社バリューアップコンサルティング",
    "中小企業診断士",
}

# These were captured in the same research run and add useful AI consulting,
# training, or implementation LPs that were not in the current six-query set.
ADDITIONAL_IDS = {
    "1328135136168969",
    "1329589688664626",
    "2020193342231942",
    "1450044673482974",
    "848897063757936",
    "1346352280971244",
    "1478298100973786",
}

SAMPLE_FIRST_VIEW = {
    "2288547545231743": {
        "first_view_status": "rendered_sample",
        "first_view_h1": "eラーニングで終わらない、現場で使えるAI研修／開発スピードが変わる、Claude Code研修",
        "first_view_cta": "まずは無料相談する／とりあえず無料相談",
        "first_view_proof": "導入実績1,200社、業務効率80%アップ、助成金最大75%",
        "notes": "広告ライブラリからLPへ遷移し、DOMでファーストビューを確認したサンプル。",
    }
}


def canonical_url(url: str) -> str:
    """Remove tracking-only parameters while retaining the useful LP path."""
    if not url:
        return ""
    url = re.sub(r"[?&](?:fbclid|dmai)=[^&#]*", "", url)
    url = re.sub(r"[?&]$", "", url)
    url = re.sub(r"&(?=#|$)", "", url)
    return url


def ad_library_url(ad_id: str) -> str:
    return f"https://www.facebook.com/ads/library/?id={quote(ad_id)}"


def load_legacy() -> dict[str, dict]:
    result = {}
    if not LEGACY.exists():
        return result
    with LEGACY.open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            ad_id = (row.get("ad_library_id") or "").strip()
            if ad_id:
                result[ad_id] = row
    return result


def normalize(raw: dict, legacy: dict[str, dict]) -> dict:
    ad_id = raw["ad_library_id"]
    sample = SAMPLE_FIRST_VIEW.get(ad_id, {})
    return {
        "captured_at": raw.get("captured_at", "2026-07-28"),
        "search_term": raw.get("query", ""),
        "advertiser": raw.get("advertiser", ""),
        "ad_library_id": ad_id,
        "started_running": raw.get("started_running", ""),
        "ad_copy": raw.get("copy", ""),
        "cta": raw.get("cta", ""),
        "landing_page_url": canonical_url(raw.get("landing_page_url", "")),
        "ad_library_url": ad_library_url(ad_id),
        "score": raw.get("score", ""),
        "first_view_status": sample.get("first_view_status", "not_rendered_batch"),
        "first_view_h1": sample.get("first_view_h1", ""),
        "first_view_cta": sample.get("first_view_cta", ""),
        "first_view_proof": sample.get("first_view_proof", ""),
        "notes": sample.get(
            "notes",
            "Meta Ad Libraryの広告情報。成果指標（CV/CPA）は広告ライブラリから取得不可。",
        ),
    }


def normalize_legacy(row: dict) -> dict:
    return {
        "captured_at": row.get("captured_at", "2026-07-28"),
        "search_term": row.get("search_term", ""),
        "advertiser": row.get("advertiser", ""),
        "ad_library_id": row["ad_library_id"],
        "started_running": row.get("started_running", ""),
        "ad_copy": row.get("creative_claim_summary", ""),
        "cta": row.get("cta", ""),
        "landing_page_url": canonical_url(row.get("landing_page_url", "")),
        "ad_library_url": ad_library_url(row["ad_library_id"]),
        "score": "legacy_capture",
        "first_view_status": "not_rendered_batch",
        "first_view_h1": "",
        "first_view_cta": "",
        "first_view_proof": "",
        "notes": "同日取得済みの補充レコード。広告コピー要約と遷移先を保存。成果指標は未取得。",
    }


def build_records() -> list[dict]:
    payload = json.loads(RAW.read_text(encoding="utf-8"))
    legacy = load_legacy()
    records = []
    seen = set()
    for raw in payload["records"]:
        ad_id = raw.get("ad_library_id", "")
        if not ad_id or raw.get("advertiser") in EXCLUDED_ADVERTISERS:
            continue
        records.append(normalize(raw, legacy))
        seen.add(ad_id)
    for ad_id in ADDITIONAL_IDS:
        if ad_id in seen or ad_id not in legacy:
            continue
        records.append(normalize_legacy(legacy[ad_id]))
        seen.add(ad_id)
    if len(records) != 40:
        raise RuntimeError(f"expected 40 records, got {len(records)}")
    records.sort(key=lambda r: (-int(r["score"]) if str(r["score"]).isdigit() else 999, r["advertiser"], r["ad_library_id"]))
    return records


def write_db(records: list[dict]) -> None:
    BASE.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fields = list(records[0].keys())
    OUT_JSON.write_text(
        json.dumps(
            {
                "captured_at": "2026-07-28",
                "country": "JP",
                "active_status": "active",
                "count": len(records),
                "unique_advertisers": len({r["advertiser"] for r in records}),
                "unique_landing_pages": len({r["landing_page_url"] for r in records}),
                "queries": [
                    "AI 顧問",
                    "AI コンサル",
                    "AI 導入 支援",
                    "生成AI 業務改善",
                    "AI 活用 診断",
                    "生成AI 中小企業",
                ],
                "records": records,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    with OUT_CSV.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)


def p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph((text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>"), style)


def build_pdf(records: list[dict]) -> None:
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    # STHeiti is a TrueType collection available on macOS and renders Japanese
    # correctly in Preview/pdftoppm, unlike the unembedded Adobe-Japan1 CID font
    # which can appear blank when a local CMap language pack is absent.
    pdfmetrics.registerFont(TTFont("STHeiti", "/System/Library/Fonts/STHeiti Medium.ttc"))
    styles = getSampleStyleSheet()
    title = ParagraphStyle("title", parent=styles["Title"], fontName="STHeiti", fontSize=19, leading=25, alignment=TA_CENTER, spaceAfter=8)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontName="STHeiti", fontSize=12, leading=16, textColor=colors.HexColor("#0B3157"), spaceBefore=6, spaceAfter=5)
    body = ParagraphStyle("body", parent=styles["BodyText"], fontName="STHeiti", fontSize=8.2, leading=11, spaceAfter=3)
    small = ParagraphStyle("small", parent=body, fontSize=6.6, leading=8.5)
    tiny = ParagraphStyle("tiny", parent=body, fontSize=5.8, leading=7.4)
    meta = ParagraphStyle("meta", parent=body, fontSize=7.4, leading=9.5, textColor=colors.HexColor("#555555"))

    doc = SimpleDocTemplate(str(OUT_PDF), pagesize=landscape(A4), rightMargin=10 * mm, leftMargin=10 * mm, topMargin=10 * mm, bottomMargin=10 * mm)
    story = [
        p("AI顧問室 Meta広告・競合LPリサーチ", title),
        p("取得日：2026-07-28｜日本向け・掲載中広告｜40広告／32ユニークLP／28広告主", meta),
        Spacer(1, 4 * mm),
        p("目的", h2),
        p("AI顧問・AIコンサル・AI導入支援・生成AI業務改善・AI活用診断・中小企業向け生成AIの検索語で、Meta広告ライブラリ上の広告と遷移先を収集しました。広告の勝ち負けを断定する資料ではなく、ファーストビュー、課題の切り取り方、オファー、証拠、CTAの型を比較するためのDBです。", body),
        p("重要な制約", h2),
        p("Meta広告ライブラリからCV数・CPA・予算・インプレッションなどの成果指標は取得できません。掲載中であることは確認できますが、広告の成果を意味しません。また、LPのファーストビューは全40件を同一条件で自動レンダリングしたものではなく、代表サンプルを確認し、残りは遷移先URLと広告コピーを保存しています。", body),
        p("検索語", h2),
        p("AI 顧問／AI コンサル／AI 導入 支援／生成AI 業務改善／AI 活用 診断／生成AI 中小企業", body),
        Spacer(1, 2 * mm),
        p("代表LPのファーストビュー確認サンプル", h2),
    ]
    sample = next(r for r in records if r["ad_library_id"] == "2288547545231743")
    sample_data = [
        [p("広告主", small), p(sample["advertiser"], small), p("広告ID", small), p(sample["ad_library_id"], small)],
        [p("H1", small), p(sample["first_view_h1"], small), p("CTA", small), p(sample["first_view_cta"], small)],
        [p("証拠・数字", small), p(sample["first_view_proof"], small), p("示唆", small), p("数字＋助成金＋無料相談で導入ハードルを下げる", small)],
    ]
    t = Table(sample_data, colWidths=[23 * mm, 105 * mm, 23 * mm, 105 * mm])
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#B8C6D1")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EAF2F8")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#EAF2F8")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.extend([t, Spacer(1, 4 * mm), p("このサンプルは実際にLPへ遷移し、DOM上の見出し・CTA・数字を確認したものです。全件の確認を進める場合は records.csv の landing_page_url を優先順位順に開いてください。", meta), PageBreak()])

    story.append(p("広告・LP DB（40件）", h2))
    headers = ["#", "広告主", "広告ID", "開始", "広告コピー／訴求", "CTA", "LP（正規化URL）", "FV"]
    rows = [[p(h, tiny) for h in headers]]
    for i, r in enumerate(records, 1):
        copy = re.sub(r"\s+", " ", r["ad_copy"]).strip()
        if len(copy) > 145:
            copy = copy[:142] + "…"
        lp = r["landing_page_url"]
        if len(lp) > 75:
            lp = lp[:72] + "…"
        rows.append([
            p(str(i), tiny),
            p(r["advertiser"], tiny),
            p(r["ad_library_id"], tiny),
            p(r["started_running"], tiny),
            p(copy, tiny),
            p(r["cta"], tiny),
            p(lp, tiny),
            p("確認済み" if r["first_view_status"] == "rendered_sample" else "URL保存", tiny),
        ])
    table = Table(rows, repeatRows=1, colWidths=[8 * mm, 35 * mm, 26 * mm, 20 * mm, 72 * mm, 25 * mm, 82 * mm, 20 * mm])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.18, colors.HexColor("#CBD5DE")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B3157")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F8FA")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 2.2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2),
    ]))
    story.extend([table, Spacer(1, 4 * mm), p("活用順：①広告コピーとLPの約束が一致しているか ②課題が1つに絞られているか ③数字・実績・対象者限定などの証拠があるか ④CTAが無料診断・無料相談・資料DLなど低摩擦か ⑤AI顧問室の診断LPへ転用できる要素か。", meta)])

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("STHeiti", 6.5)
        canvas.setFillColor(colors.HexColor("#66727C"))
        canvas.drawString(10 * mm, 5 * mm, "Internal research only · Meta Ad Library capture · 2026-07-28")
        canvas.drawRightString(287 * mm, 5 * mm, f"{doc.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def main() -> None:
    records = build_records()
    write_db(records)
    build_pdf(records)
    print(json.dumps({
        "records": len(records),
        "advertisers": len({r["advertiser"] for r in records}),
        "landing_pages": len({r["landing_page_url"] for r in records}),
        "csv": str(OUT_CSV),
        "json": str(OUT_JSON),
        "pdf": str(OUT_PDF),
        "first_view_samples": sum(r["first_view_status"] == "rendered_sample" for r in records),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
