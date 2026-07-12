#!/usr/bin/env python3
"""Generate one self-contained, reviewable tool page from a JSON spec.

Supported tool types: calculator, text-counter, and shell. The generated page
contains the tool UI plus AMIX-style explanation, FAQ, related links, and a
contextual service CTA. It is intentionally deterministic and has no external
runtime dependencies.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path


SAFE_FORMULA = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:\s*[+\-*/()]\s*[A-Za-z0-9_.]+)*$")
SAFE_SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{1,80}$")


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def json_script(value: object) -> str:
    return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")


def field_html(field: dict) -> str:
    field_id = esc(field["id"])
    label = esc(field.get("label", field["id"]))
    default = esc(field.get("default", 0))
    step = esc(field.get("step", "any"))
    return f'<label class="field"><span>{label}</span><input id="{field_id}" name="{field_id}" type="number" inputmode="decimal" step="{step}" value="{default}"></label>'


def tool_body(spec: dict) -> tuple[str, str, dict]:
    tool_type = spec.get("tool_type", "shell")
    if tool_type == "calculator":
        fields = spec.get("fields", [])
        if not fields:
            raise ValueError("calculator spec needs fields")
        formula = str(spec.get("result", {}).get("formula", "")).strip()
        if not formula or not SAFE_FORMULA.fullmatch(formula):
            raise ValueError("result.formula may contain only field ids, numbers, spaces, and + - * / ( )")
        declared = {str(field["id"]) for field in fields}
        used = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", formula))
        unknown = used - declared
        if unknown:
            raise ValueError(f"formula references unknown fields: {sorted(unknown)}")
        result_label = esc(spec.get("result", {}).get("label", "結果"))
        body = '<div class="tool-card"><form id="tool-form">' + "".join(field_html(field) for field in fields) + f'<button type="submit">計算する</button></form><output id="tool-result" aria-live="polite">{result_label}がここに表示されます</output></div>'
        field_ids = [field["id"] for field in fields]
        destructure = ", ".join(field_ids)
        script = f"""const values = Object.fromEntries({json.dumps(field_ids, ensure_ascii=False)}.map(id => [id, Number(document.getElementById(id).value) || 0]));
const {{ {destructure} }} = values;
const result = ({formula});
document.getElementById('tool-result').textContent = {json.dumps(result_label, ensure_ascii=False)} + ': ' + new Intl.NumberFormat('ja-JP').format(result) + ' ' + {json.dumps(spec.get('result', {}).get('unit', ''), ensure_ascii=False)};"""
        return body, script, {"type": tool_type, "formula": formula}
    if tool_type == "text-counter":
        body = '<div class="tool-card"><label class="field"><span>数える文章</span><textarea id="tool-text" rows="8" placeholder="ここに文章を入力"></textarea></label><output id="tool-result" aria-live="polite">0文字</output></div>'
        script = "document.getElementById('tool-text').addEventListener('input', event => { document.getElementById('tool-result').textContent = event.target.value.length.toLocaleString('ja-JP') + '文字'; });"
        return body, script, {"type": tool_type}
    body = '<div class="tool-card"><p>このツールの仕様を確認中です。公開前に入力・出力UIを実装してください。</p></div>'
    return body, "", {"type": "shell"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True)
    parser.add_argument("--root", default=".")
    parser.add_argument("--output-dir", default="tools")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    slug = str(spec.get("slug", "")).strip()
    if not SAFE_SLUG.fullmatch(slug):
        raise SystemExit("spec.slug must be lowercase ascii, e.g. ai-roi-calculator")
    title = str(spec.get("title", "")).strip()
    description = str(spec.get("description", "")).strip()
    if not title or not description:
        raise SystemExit("spec.title and spec.description are required")
    body, script, runtime = tool_body(spec)
    base_url = str(spec.get("base_url", "https://ai-komon.bivrost.co.jp")).rstrip("/")
    canonical = f"{base_url}/{args.output_dir.strip('/')}/{slug}/"
    explanations = spec.get("explanations", ["このツールが解決する課題と使い方を説明します。", "入力値や結果の注意点、プライバシー、対応範囲を説明します。"])
    faq = spec.get("faq", [{"q": "無料で使えますか？", "a": "はい。ブラウザから登録なしで利用できます。"}, {"q": "入力データは保存されますか？", "a": "このページの計算処理はブラウザ内で行い、入力値をサーバーへ送信しません。"}])
    related = spec.get("related_tools", [])
    related_html = "".join(f'<a class="related" href="{esc(item["url"])}"><strong>{esc(item["label"])}</strong><span>{esc(item.get("description", "関連する作業に使えます"))}</span></a>' for item in related)
    faq_html = "".join(f"<details><summary>{esc(item['q'])}</summary><p>{esc(item['a'])}</p></details>" for item in faq)
    cta = spec.get("cta", {})
    cta_html = f'<a class="cta" href="{esc(cta.get("url", "/diagnosis.html"))}">{esc(cta.get("label", "AI導入について相談する"))}</a>'
    html_page = f'''<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)} | AI顧問室</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{esc(canonical)}">
  <meta property="og:title" content="{esc(title)} | AI顧問室">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:type" content="website">
  <style>
    :root {{ color-scheme: light; --ink:#18222d; --muted:#647180; --line:#dfe6ed; --brand:#1769aa; --soft:#f3f7fb; }}
    * {{ box-sizing:border-box; }} body {{ margin:0; font-family:system-ui,-apple-system,BlinkMacSystemFont,"Noto Sans JP",sans-serif; color:var(--ink); line-height:1.8; background:#fff; }}
    main {{ width:min(960px,calc(100% - 32px)); margin:auto; }} header {{ padding:64px 0 32px; }} h1 {{ margin:0 0 8px; font-size:clamp(2rem,5vw,3.5rem); line-height:1.2; letter-spacing:-.03em; }} h2 {{ margin:48px 0 12px; font-size:1.5rem; }} h3 {{ margin-top:28px; }} .lead {{ color:var(--muted); font-size:1.1rem; }}
    .tool-card {{ padding:24px; border:1px solid var(--line); border-radius:20px; background:var(--soft); box-shadow:0 10px 30px #18334d12; }} .field {{ display:grid; gap:6px; margin:14px 0; font-weight:700; }} input,textarea {{ width:100%; border:1px solid #b8c7d5; border-radius:10px; padding:12px; background:#fff; font:inherit; }} button,.cta {{ display:inline-block; border:0; border-radius:999px; padding:12px 20px; background:var(--brand); color:#fff; font:inherit; font-weight:700; cursor:pointer; text-decoration:none; }} output {{ display:block; margin-top:18px; font-size:1.35rem; font-weight:800; }} .related-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:12px; }} .related {{ display:grid; gap:2px; border:1px solid var(--line); border-radius:14px; padding:14px; color:inherit; text-decoration:none; }} .related span {{ color:var(--muted); font-size:.9rem; }} details {{ border-bottom:1px solid var(--line); padding:14px 0; }} summary {{ cursor:pointer; font-weight:700; }} .cta-wrap {{ margin:40px 0; padding:24px; border-radius:18px; background:#172432; color:#fff; }} .cta-wrap p {{ color:#d7e2ec; }} footer {{ margin-top:64px; padding:24px 0 48px; color:var(--muted); border-top:1px solid var(--line); font-size:.9rem; }}
  </style>
</head>
<body>
<main>
  <header><p>AI顧問室 無料ツール</p><h1>{esc(title)}</h1><p class="lead">{esc(description)}</p></header>
  <section aria-labelledby="tool-heading"><h2 id="tool-heading">ツールを使う</h2>{body}</section>
  <section aria-labelledby="about-heading"><h2 id="about-heading">このツールでできること</h2><p>{esc(explanations[0])}</p><p>{esc(explanations[1] if len(explanations) > 1 else explanations[0])}</p></section>
  <section aria-labelledby="how-heading"><h2 id="how-heading">使い方と注意点</h2><p>入力値と結果は用途に合わせて確認してください。判断に影響する数値は、実際の業務条件や最新情報と照合して利用してください。</p><p>このページの標準処理はブラウザ内で行います。入力データを保存・送信する仕様に変更する場合は、公開前に保持期間と第三者提供を明記してください。</p></section>
  <section aria-labelledby="faq-heading"><h2 id="faq-heading">よくある質問</h2>{faq_html}</section>
  {f'<section aria-labelledby="related-heading"><h2 id="related-heading">関連する無料ツール</h2><div class="related-grid">{related_html}</div></section>' if related_html else ''}
  <section class="cta-wrap"><h2>業務に合わせたAI活用も相談できます</h2><p>無料ツールで整理した課題を、実際の業務フローに合わせて設計・導入したい場合はこちら。</p>{cta_html}</section>
  <footer><a href="/">AI顧問室</a> / <a href="/privacy.html">プライバシーポリシー</a></footer>
</main>
<script>
const runtime = {json_script(runtime)};
const form = document.getElementById('tool-form');
if (form) form.addEventListener('submit', event => {{ event.preventDefault(); try {{ {script} }} catch (error) {{ document.getElementById('tool-result').textContent = '入力値を確認してください'; }} }});
</script>
</body>
</html>
'''
    output = root / args.output_dir / slug / "index.html"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html_page, encoding="utf-8")
    print(f"generated {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
