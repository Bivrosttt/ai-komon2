from __future__ import annotations

import csv
import json
import subprocess
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "noimos"


def run_script(relative: str, *args: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["python3", str(ROOT / relative), *map(str, args)],
        text=True,
        capture_output=True,
        cwd=ROOT,
        check=False,
    )
    if result.returncode != expected:
        raise AssertionError(
            f"{relative} returned {result.returncode}, expected {expected}\n"
            f"stdout={result.stdout}\nstderr={result.stderr}"
        )
    return result


class NoimosSkillTests(unittest.TestCase):
    def test_01_growth_foundation_pass_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "index.html").write_text(
                """<!doctype html><html><head>
                <title>中小企業のAI導入を業務実装まで支援するAI顧問室</title>
                <meta name="description" content="中小企業のAI導入を、対象業務の選定、試作、社内ルール、現場定着まで一気通貫で支援します。無料相談で最初の一業務を整理できます。">
                <meta name="viewport" content="width=device-width">
                <link rel="canonical" href="https://example.com/">
                <meta property="og:title" content="AI顧問室"><meta property="og:description" content="説明">
                <meta property="og:url" content="https://example.com/"><meta property="og:image" content="https://example.com/og.png">
                <script type="application/ld+json">{"@context":"https://schema.org","@type":"Organization","name":"AI顧問室"}</script>
                </head><body><h1>AIを御社で使える仕事に変える</h1>
                <a class="btn cta" href="/consultation">無料相談</a>
                <script>window.dataLayer=[]; function gtag(){}; gtag("event","generate_lead");</script>
                </body></html>""",
                encoding="utf-8",
            )
            (root / "robots.txt").write_text(
                "User-agent: *\nAllow: /\nSitemap: https://example.com/sitemap.xml\n",
                encoding="utf-8",
            )
            (root / "llms.txt").write_text(
                "# AI顧問室\n中小企業のAI導入を対象業務の選定から実装、確認、定着まで支援します。\n"
                "主要ページと問い合わせ方法をここに記載しています。料金、導入支援、研修、"
                "運営会社、プライバシーポリシーへの正規リンクも案内します。\n",
                encoding="utf-8",
            )
            out = root / "out.json"
            run_script(
                "skills/noimos-growth-foundation/scripts/audit_foundation.py",
                "--root", root, "--out", out,
            )
            self.assertEqual(json.loads(out.read_text())["overall"], "pass")

    def test_02_commercial_keyword_ranking(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "out.json"
            run_script(
                "skills/noimos-commercial-keywords/scripts/score_keywords.py",
                "--input", FIXTURES / "keywords.csv", "--out", out,
            )
            report = json.loads(out.read_text())
            self.assertEqual(report["candidates"][0]["keyword"], "AI顧問 比較")
            informational = next(item for item in report["candidates"] if item["keyword"] == "生成AI とは")
            self.assertFalse(informational["eligible"])

    def test_03_article_validator_pass_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            article_dir = root / "articles" / "test"
            article_dir.mkdir(parents=True)
            (article_dir / "diagram.png").write_bytes(b"PNG")
            body = "中小企業の経営者が比較するときは、対象業務、確認方法、費用、契約条件、失敗時の戻し方を順に判断します。" * 120
            html = f"""<!doctype html><html><head>
            <title>AI顧問を比較する判断基準と導入手順 | AI顧問室</title>
            <meta name="description" content="中小企業がAI顧問を比較するときの判断基準を、対象業務、費用、実装範囲、人の確認、契約条件、失敗時の戻し方まで具体的に整理します。">
            <link rel="canonical" href="https://example.com/articles/test/">
            <script type="application/ld+json">{{"@context":"https://schema.org","@type":"Article","headline":"AI顧問比較","author":{{"@type":"Person","name":"著者"}},"dateModified":"2026-07-30"}}</script>
            </head><body><article><h1>AI顧問を比較する判断基準</h1>
            <div class="answer">先に結論を示します。</div>
            <figure><img src="diagram.png" alt="AI顧問を比較する五つの判断基準を示す図"><figcaption>比較の順序</figcaption></figure>
            <h2>対象業務</h2><p>{body}</p><h2>費用</h2><p>判断条件を比較します。</p>
            <h2>人の確認</h2><p>注意点と失敗条件を確認します。</p>
            <h2>よくある質問</h2><p>FAQへの回答です。</p>
            <a href="/a">内部A</a><a href="/b">内部B</a><a href="/c">内部C</a>
            <a href="https://www.meti.go.jp/">経済産業省</a><a href="https://www.smrj.go.jp/">中小機構</a>
            <div class="service-cta">無料相談</div></article></body></html>"""
            article = article_dir / "index.html"
            article.write_text(html, encoding="utf-8")
            out = root / "out.json"
            run_script(
                "skills/noimos-seo-geo-article/scripts/validate_article.py",
                "--input", article, "--site-root", root, "--out", out,
            )
            self.assertEqual(json.loads(out.read_text())["overall"], "pass")

    def test_04_content_refresh_queue(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for slug, modified, body in [
                ("old", "2025-01-01", "短い本文"),
                ("new", "2026-07-20", "具体的な判断手順と注意点。" * 300),
            ]:
                folder = root / "articles" / slug
                folder.mkdir(parents=True)
                (folder / "index.html").write_text(
                    f"""<html><head><title>{slug} | Site</title>
                    <link rel="canonical" href="https://example.com/articles/{slug}/">
                    <script>{{"dateModified":"{modified}"}}</script></head>
                    <body><h1>{slug}</h1><p>{body}</p>
                    <a href="/">home</a><a href="/articles/new/">new</a><a href="/articles/old/">old</a></body></html>""",
                    encoding="utf-8",
                )
            (root / "articles" / "index.html").write_text(
                """<html><head><title>記事一覧 | Site</title>
                <link rel="canonical" href="https://example.com/articles/">
                <script type="application/ld+json">
                {"@context":"https://schema.org","@type":"CollectionPage","dateModified":"2026-07-30"}
                </script></head><body><h1>記事一覧</h1>
                <a href="/">home</a><a href="/articles/new/">new</a><a href="/articles/old/">old</a>
                </body></html>""",
                encoding="utf-8",
            )
            out = root / "out.json"
            run_script(
                "skills/noimos-content-refresh/scripts/analyze_content.py",
                "--root", root, "--as-of", "2026-07-30", "--out", out,
            )
            report = json.loads(out.read_text())
            self.assertEqual(report["queue"][0]["path"], "articles/old/index.html")
            self.assertIn("stale_180", report["queue"][0]["issues"])
            collection = next(
                item for item in report["queue"] if item["path"] == "articles/index.html"
            )
            self.assertEqual(collection["content_type"], "collection")
            self.assertNotIn("thin_for_decision_content", collection["issues"])

    def test_05_trend_pattern_scoring(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "out.json"
            run_script(
                "skills/noimos-social-trend-mining/scripts/score_trends.py",
                "--input", FIXTURES / "trends.json", "--as-of", "2026-07-30", "--out", out,
            )
            top = json.loads(out.read_text())["patterns"][0]
            self.assertEqual(top["format"], "milestone_playbook")
            self.assertEqual(top["confidence"], "high")

    def test_06_social_content_pass_and_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "pass.json"
            run_script(
                "skills/noimos-social-conversion-content/scripts/score_social_content.py",
                "--input", FIXTURES / "social-content-pass.json", "--out", out,
            )
            self.assertEqual(json.loads(out.read_text())["overall"], "pass")
            fail_out = Path(temp) / "fail.json"
            run_script(
                "skills/noimos-social-conversion-content/scripts/score_social_content.py",
                "--input", FIXTURES / "social-content-fail.json", "--out", fail_out,
                expected=1,
            )
            self.assertEqual(json.loads(fail_out.read_text())["overall"], "block")

    def test_07_agent_dry_run_holds_publication(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "out.json"
            run_script(
                "skills/noimos-always-on-agent/scripts/dry_run_agent.py",
                "--spec", FIXTURES / "agent-spec.json", "--start", "2026-08-03",
                "--days", "7", "--out", out,
            )
            report = json.loads(out.read_text())
            self.assertEqual(report["overall"], "pass")
            self.assertEqual(report["summary"]["external_actions_executed"], 0)
            self.assertGreater(report["summary"]["approval_handoffs"], 0)
            self.assertEqual(report["summary"]["approval_mode"], "ai_only")
            self.assertGreater(report["summary"]["ai_approved_runs"], 0)

    def test_08_change_detector_loss_gain_noise(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            csv_path = root / "performance.csv"
            start = date(2026, 7, 10)
            with csv_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=["date", "page", "query", "impressions", "clicks", "position", "conversions"],
                )
                writer.writeheader()
                for day in range(21):
                    current = start + timedelta(days=day)
                    recent = day >= 14
                    for page, query, base, now in [
                        ("/loss", "loss query", (200, 30, 4, 3), (120, 10, 7, 1)),
                        ("/gain", "gain query", (120, 10, 8, 1), (220, 28, 5, 3)),
                        ("/noise", "noise query", (150, 20, 6, 2), (152, 21, 6.1, 2)),
                    ]:
                        values = now if recent else base
                        writer.writerow(
                            dict(zip(
                                ["date", "page", "query", "impressions", "clicks", "position", "conversions"],
                                [current.isoformat(), page, query, *values],
                            ))
                        )
            out = root / "out.json"
            run_script(
                "skills/noimos-algorithm-adaptation/scripts/detect_changes.py",
                "--input", csv_path, "--baseline-days", "14", "--recent-days", "7", "--out", out,
            )
            counts = json.loads(out.read_text())["counts"]
            self.assertEqual(counts["material_loss"], 1)
            self.assertEqual(counts["material_gain"], 1)
            self.assertEqual(counts["stable_or_noise"], 1)

    def test_09_quality_gate_pass_and_block(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            passed = Path(temp) / "pass.json"
            run_script(
                "skills/noimos-content-quality-gate/scripts/quality_gate.py",
                "--content", FIXTURES / "quality-pass.md",
                "--claims", FIXTURES / "claims.json",
                "--brand", FIXTURES / "brand.json",
                "--approval", FIXTURES / "approval-approved.json",
                "--out", passed,
            )
            self.assertIn(json.loads(passed.read_text())["status"], {"PASS", "PASS_WITH_WARNINGS"})
            ai_only = Path(temp) / "ai-only.json"
            run_script(
                "skills/noimos-content-quality-gate/scripts/quality_gate.py",
                "--content", FIXTURES / "quality-pass.md",
                "--claims", FIXTURES / "claims.json",
                "--brand", FIXTURES / "brand.json",
                "--approval", FIXTURES / "approval-ai-only.json",
                "--out", ai_only,
            )
            ai_report = json.loads(ai_only.read_text())
            self.assertEqual(ai_report["status"], "PASS")
            self.assertEqual(ai_report["approval_mode"], "ai_only")
            blocked = Path(temp) / "block.json"
            run_script(
                "skills/noimos-content-quality-gate/scripts/quality_gate.py",
                "--content", FIXTURES / "quality-fail.md",
                "--claims", FIXTURES / "claims.json",
                "--brand", FIXTURES / "brand.json",
                "--approval", FIXTURES / "approval-missing.json",
                "--out", blocked,
                expected=1,
            )
            self.assertEqual(json.loads(blocked.read_text())["status"], "BLOCK")

    def test_10_thumbnail_generator_creates_text_free_icon_cover(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "thumbnail.svg"
            run_script(
                "scripts/generate_article_thumbnail.py",
                "--output", output,
                "--icon", "sparkles",
                "--palette", "purple",
                "--shape", "diagonal",
                "--seed", "test-thumbnail",
            )
            svg = output.read_text(encoding="utf-8")
            self.assertIn("viewBox=\"0 0 1600 900\"", svg)
            self.assertIn("icon-fill", svg)
            self.assertIn("linearGradient", svg)
            self.assertNotIn("Compare the system", svg)


if __name__ == "__main__":
    unittest.main()
