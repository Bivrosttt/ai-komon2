#!/usr/bin/env python3
"""Run the daily research + audit loop and write one reviewable brief."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run(command: list[str], cwd: Path) -> None:
    print("$", " ".join(command))
    subprocess.run(command, cwd=cwd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--config", default="seo/config.json")
    parser.add_argument("--seeds", default="seo/seeds.json")
    parser.add_argument("--date", help="YYYY-MM-DD; defaults to local today")
    parser.add_argument("--max-candidates", type=int, default=10)
    parser.add_argument("--skip-research", action="store_true")
    parser.add_argument("--skip-audit", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    config = json.loads((root / args.config).read_text(encoding="utf-8"))
    day = args.date or datetime.now().astimezone().strftime("%Y-%m-%d")
    run_dir = root / config["paths"]["run_dir"] / day
    run_dir.mkdir(parents=True, exist_ok=True)
    python = sys.executable
    scripts = root / "seo/scripts"
    raw = run_dir / "keyword-observations.json"
    candidates = run_dir / "candidates.json"
    candidates_csv = run_dir / "candidates.csv"
    spec_stubs = run_dir / "spec-stubs"
    audit = run_dir / "site-audit.json"
    audit_md = run_dir / "site-audit.md"
    gsc_json = run_dir / "gsc-opportunities.json"
    gsc_md = run_dir / "gsc-opportunities.md"

    if not args.skip_research:
        run([python, str(scripts / "research_sources.py"), "--seeds", str(root / args.seeds), "--config", str(root / args.config), "--manual-dir", str(root / config["paths"].get("manual_sources_dir", "seo/data/manual")), "--out", str(raw)], root)
    if raw.exists():
        run([python, str(scripts / "score_candidates.py"), "--input", str(raw), "--json-out", str(candidates), "--csv-out", str(candidates_csv), "--limit", str(args.max_candidates)], root)
        run([python, str(scripts / "generate_spec_stubs.py"), "--candidates", str(candidates), "--config", str(root / args.config), "--out-dir", str(spec_stubs), "--limit", "5"], root)
    if not args.skip_audit:
        run([python, str(scripts / "site_audit.py"), "--root", str(root), "--json-out", str(audit), "--md-out", str(audit_md)], root)
    gsc_csv = root / config["paths"].get("gsc_csv", "seo/data/gsc/latest.csv")
    if gsc_csv.exists():
        run([python, str(scripts / "import_gsc.py"), "--input", str(gsc_csv), "--json-out", str(gsc_json), "--md-out", str(gsc_md)], root)

    candidate_rows = json.loads(candidates.read_text(encoding="utf-8")).get("candidates", []) if candidates.exists() else []
    audit_payload = json.loads(audit.read_text(encoding="utf-8")) if audit.exists() else {"issue_counts": {}, "pages": []}
    gsc_rows = json.loads(gsc_json.read_text(encoding="utf-8")).get("rows", []) if gsc_json.exists() else []
    lines = [f"# AI顧問室 SEO daily brief — {day}", "", "## 今日の結論", "", "未レビューのページは公開せず、下の候補から1件を選んで仕様確認・実装・検証する。", "", "## 次に作る無料ツール候補", "", "| 優先度 | キーワード | 意図 | ツール仮説 | 根拠ソース | 次の作業 |", "|---:|---|---|---|---|---|"]
    for row in candidate_rows:
        lines.append(f"| {row['priority']} | {row['keyword']} | {row['intent']} | {row['tool_hypothesis']} | {', '.join(row['sources'])} | {row['next_action']} |")
    lines += ["", "## 仕様スタブ", "", f"上位5候補のレビュー用JSONを `{spec_stubs.relative_to(root)}/` に作成済み。`status: draft` のまま実装・公開しない。", "", "## 既存サイトの改善", "", f"監査ページ数: {audit_payload.get('page_count', 0)}", ""]
    for issue, count in sorted(audit_payload.get("issue_counts", {}).items(), key=lambda item: -item[1]):
        lines.append(f"- `{issue}`: {count}ページ")
    lines += ["", "## Search Consoleの改善候補", ""]
    if gsc_rows:
        lines += [f"- `{row['query']}` — 掲載順位 {row['position']}, 表示 {row['impressions']}, CTR {row['ctr']:.1%}" for row in gsc_rows[:10]]
    else:
        lines.append("- `seo/data/gsc/latest.csv` が未配置。Search Consoleの検索結果CSVを置くと実績ベースの候補が追加される。")
    lines += ["", "## 公開前チェック", "", "- 既存ページと検索意図が重複していない", "- 本当に使えるUIと空/エラー状態がある", "- title / description / canonical / H1 / OGPを確認した", "- 関連ツールと文脈に合うサービスCTAを追加した", "- モバイルで操作し、表示速度とプライバシー説明を確認した", ""]
    (run_dir / "daily-brief.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"daily brief: {run_dir / 'daily-brief.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
