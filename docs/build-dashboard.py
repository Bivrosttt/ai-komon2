#!/usr/bin/env python3
"""運用ダッシュボード生成。リポジトリルートで実行: python3 docs/build-dashboard.py → docs/dashboard.html"""
import glob, re, html, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://ai-komon.bivrost.co.jp"


def title_of(f):
    s = open(f, encoding="utf-8").read()
    m = re.search(r"<title>([^<]+)</title>", s)
    t = m.group(1) if m else f
    return re.sub(r"｜AI顧問室.*$", "", t).strip()


def rows(files, note_map=None):
    out = []
    for f in sorted(files):
        name = pathlib.Path(f).name
        url = f"{BASE}/{name}"
        note = (note_map or {}).get(name, "")
        out.append(
            f'<tr><td><a href="{url}" target="_blank">{name}</a></td>'
            f"<td>{html.escape(title_of(f))}</td><td>{note}</td></tr>"
        )
    return "\n".join(out)


LP_NOTES = {  # 訴求軸メモ（?from= はファイル名と同じ）
    "lp-ai-diagnosis.html": "広告専用・AI活用診断",
    "lp-cost.html": "コスト訴求", "lp-fear.html": "危機感", "lp-story.html": "ストーリー",
    "lp-simple.html": "シンプル", "lp-demo-first.html": "デモ先出し", "lp-anti.html": "アンチコンサル",
    "lp-speed.html": "スピード", "lp-boss.html": "経営者目線", "lp-hojokin.html": "補助金",
    "lp-jiso.html": "自走・内製化", "lp-level.html": "レベル診断軸", "lp-question.html": "問いかけ",
    "lp-risk.html": "リスク回避", "lp-time.html": "時間創出", "lp-hitode.html": "人手不足",
    "lp-kantan.html": "かんたん", "lp-hikaku.html": "比較", "lp-genba.html": "現場（建設）",
    "lp-roi.html": "ROI試算", "lp-chatgpt.html": "ChatGPT止まり", "lp-lv2.html": "レベル2向け",
    "lp-lv3.html": "レベル3向け", "lp-lv4.html": "レベル4向け", "lp-fudosan.html": "不動産向け",
}

lps = glob.glob(str(ROOT / "lp-*.html"))
works = [f for f in glob.glob(str(ROOT / "works*.html")) if "slides-deck" not in f]
works += [str(ROOT / "service-movie.html"), str(ROOT / "floorplan-walkthrough.html"), str(ROOT / "creative-flyer.html")]
demos = glob.glob(str(ROOT / "demo-*.html"))
core = [str(ROOT / f) for f in [
    "index.html", "data.html", "diagnosis.html", "bivrost.html", "tokushoho.html", "privacy.html"] if (ROOT / f).exists()]
pdfs = sorted(glob.glob(str(ROOT / "materials" / "*.pdf"))) + sorted(glob.glob(str(ROOT / "works" / "*.pdf")))
pdf_rows = "\n".join(
    f'<tr><td><a href="{BASE}/{pathlib.Path(f).relative_to(ROOT)}" target="_blank">{pathlib.Path(f).name}</a></td>'
    f"<td>{round(pathlib.Path(f).stat().st_size/1e6,1)}MB</td></tr>" for f in pdfs)

now = datetime.date.today().isoformat()

TPL = open(ROOT / "docs" / "dashboard-template.html", encoding="utf-8").read()
out = (TPL
    .replace("{{DATE}}", now)
    .replace("{{LP_COUNT}}", str(len(lps)))
    .replace("{{LP_ROWS}}", rows(lps, LP_NOTES))
    .replace("{{WORKS_COUNT}}", str(len(works)))
    .replace("{{WORKS_ROWS}}", rows(works))
    .replace("{{DEMO_COUNT}}", str(len(demos)))
    .replace("{{DEMO_ROWS}}", rows(demos))
    .replace("{{CORE_ROWS}}", rows(core))
    .replace("{{PDF_ROWS}}", pdf_rows))
open(ROOT / "docs" / "dashboard.html", "w", encoding="utf-8").write(out)
print(f"docs/dashboard.html generated: LP={len(lps)} works={len(works)} demos={len(demos)} pdfs={len(pdfs)}")
