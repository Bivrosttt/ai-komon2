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


SAFE_FORMULA = re.compile(r"^[A-Za-z0-9_+\-*/().\s]+$")
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


def validate_formula(formula: str, declared: set[str]) -> str:
    if not formula or not SAFE_FORMULA.fullmatch(formula):
        raise ValueError("formula may contain only field ids, numbers, spaces, and + - * / ( )")
    used = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", formula))
    unknown = used - declared
    if unknown:
        raise ValueError(f"formula references unknown fields: {sorted(unknown)}")
    return formula


def tool_body(spec: dict) -> tuple[str, str, str, dict]:
    tool_type = spec.get("tool_type", "shell")
    if tool_type == "calculator":
        fields = spec.get("fields", [])
        if not fields:
            raise ValueError("calculator spec needs fields")
        declared = {str(field["id"]) for field in fields}
        results = spec.get("results") or [spec.get("result", {})]
        normalized_results = []
        for index, result in enumerate(results):
            normalized_results.append({
                "id": result.get("id", f"result-{index}"),
                "label": result.get("label", "結果"),
                "unit": result.get("unit", ""),
                "formula": validate_formula(str(result.get("formula", "")).strip(), declared),
            })
        result_html = "".join(f'<output id="calc-{esc(result["id"])}" aria-live="polite">{esc(result["label"])}がここに表示されます</output>' for result in normalized_results)
        body = '<div class="tool-card"><form id="tool-form"><div class="two-col">' + "".join(field_html(field) for field in fields) + f'</div><button type="submit">計算する</button></form><div id="calc-results">{result_html}</div></div>'
        field_ids = [field["id"] for field in fields]
        destructure = ", ".join(field_ids)
        lines = [f"const values = Object.fromEntries({json.dumps(field_ids, ensure_ascii=False)}.map(id => [id, Number(document.getElementById(id).value) || 0]));", f"const {{ {destructure} }} = values;"]
        for index, result in enumerate(normalized_results):
            value_name = f"resultValue{index}"
            lines.append(f"const {value_name} = {result['formula']}; document.getElementById('calc-{result['id']}').textContent = Number.isFinite({value_name}) ? {json.dumps(result['label'], ensure_ascii=False)} + ': ' + new Intl.NumberFormat('ja-JP').format({value_name}) + ' ' + {json.dumps(result['unit'], ensure_ascii=False)} : '入力値を確認してください';")
        return body, "", "\n".join(lines), {"type": tool_type, "results": normalized_results}
    if tool_type == "minutes-template":
        body = '''<div class="tool-card"><form id="tool-form"><div class="two-col">
<label class="field"><span>会議名</span><input id="mt-title" type="text" placeholder="例：営業定例会"></label>
<label class="field"><span>開催日</span><input id="mt-date" type="date"></label>
</div><label class="field"><span>参加者</span><input id="mt-attendees" type="text" placeholder="例：田中、佐藤、鈴木"></label>
<label class="field"><span>議題</span><textarea id="mt-agenda" rows="3" placeholder="話し合ったテーマを1行ずつ"></textarea></label>
<label class="field"><span>決定事項</span><textarea id="mt-decisions" rows="4" placeholder="決まったことを1行ずつ"></textarea></label>
<label class="field"><span>保留・確認事項</span><textarea id="mt-pending" rows="3" placeholder="確認が必要なことを1行ずつ"></textarea></label>
<label class="field"><span>ToDo（担当者・期限も入力可）</span><textarea id="mt-todos" rows="4" placeholder="例：田中｜見積を確認｜6/20"></textarea></label>
<div class="tool-actions"><button type="submit">議事録を生成</button><button type="button" id="mt-copy" class="button-secondary">コピー</button><button type="button" id="mt-download" class="button-secondary">Markdown保存</button></div></form>
<pre id="mt-output" class="result-pre" aria-live="polite">ここに議事録が表示されます</pre></div>'''
        setup = '''document.getElementById('mt-copy').addEventListener('click', async () => { const text = window.__minutesMarkdown || document.getElementById('mt-output').textContent; try { await navigator.clipboard.writeText(text); document.getElementById('mt-copy').textContent = 'コピーしました'; } catch { document.getElementById('mt-copy').textContent = '選択してコピーしてください'; } });
document.getElementById('mt-download').addEventListener('click', () => { const text = window.__minutesMarkdown || document.getElementById('mt-output').textContent; const blob = new Blob([text], {type: 'text/markdown;charset=utf-8'}); const link = document.createElement('a'); link.href = URL.createObjectURL(blob); link.download = 'gijiroku.md'; link.click(); URL.revokeObjectURL(link.href); });'''
        submit = '''const value = id => document.getElementById(id).value.trim();
const lines = text => text.split(/\\n+/).map(item => item.trim()).filter(Boolean);
const bullets = text => lines(text).map(item => `- ${item}`).join('\\n') || '- （なし）';
const todoLines = lines(value('mt-todos')).map((item, index) => `${index + 1}. ${item}`).join('\\n') || '1. （なし）';
const markdown = `# ${value('mt-title') || '議事録'}\\n\\n- 開催日: ${value('mt-date') || '未入力'}\\n- 参加者: ${value('mt-attendees') || '未入力'}\\n\\n## 議題\\n${bullets(value('mt-agenda'))}\\n\\n## 決定事項\\n${bullets(value('mt-decisions'))}\\n\\n## 保留・確認事項\\n${bullets(value('mt-pending'))}\\n\\n## ToDo\\n${todoLines}\\n`;
document.getElementById('mt-output').textContent = markdown;
window.__minutesMarkdown = markdown;'''
        return body, setup, submit, {"type": tool_type}
    if tool_type == "risk-checklist":
        items = spec.get("items", [])
        if not items:
            raise ValueError("risk-checklist spec needs items")
        groups = {}
        for item in items:
            groups.setdefault(item.get("category", "確認項目"), []).append(item)
        fieldsets = []
        for category, group in groups.items():
            checks = "".join(f'<label class="check-item"><input type="checkbox" data-risk-item="{esc(item["id"])}" data-advice="{esc(item.get("advice", item["label"]))}"><span>{esc(item["label"])}</span></label>' for item in group)
            fieldsets.append(f'<fieldset><legend>{esc(category)}</legend>{checks}</fieldset>')
        body = '<div class="tool-card"><form id="tool-form"><p class="muted">できている項目にチェックを入れてください。法的判断ではなく、社内で見直す論点を整理するための診断です。</p>' + "".join(fieldsets) + '<button type="submit">診断結果を見る</button></form><div id="risk-result" class="score-card" aria-live="polite">チェック後に結果が表示されます</div></div>'
        setup = '''const updateRisk = () => { const checks = [...document.querySelectorAll('[data-risk-item]')]; const checked = checks.filter(item => item.checked); const readiness = checks.length ? Math.round((checked.length / checks.length) * 100) : 0; const advice = checks.filter(item => !item.checked).slice(0, 5).map(item => `<li>${item.dataset.advice}</li>`).join(''); const band = readiness >= 80 ? '準備が進んでいます' : readiness >= 50 ? '優先課題があります' : 'まずルール整備から始めましょう'; document.getElementById('risk-result').innerHTML = `<strong>${band}</strong><span class="score-number">準備度 ${readiness}%</span><p>未チェックの優先項目</p><ul>${advice || '<li>大きな未チェック項目はありません。</li>'}</ul>`; };
document.querySelectorAll('[data-risk-item]').forEach(item => item.addEventListener('change', updateRisk));'''
        return body, setup, "updateRisk();", {"type": tool_type, "item_count": len(items)}
    if tool_type == "text-counter":
        body = '''<div class="tool-card"><label class="field"><span>数える文章</span><textarea id="tool-text" rows="8" placeholder="ここに文章を入力"></textarea></label><div class="counter-grid" aria-live="polite"><output id="count-all">0文字</output><output id="count-no-space">0文字（空白除外）</output><output id="count-lines">0行</output><output id="count-paragraphs">0段落</output><output id="count-bytes">0バイト</output><output id="count-manuscript">0枚（400字詰め）</output><output id="count-reading">読了目安 0分</output></div></div>'''
        setup = """document.getElementById('tool-text').addEventListener('input', event => { const text = event.target.value; const noSpace = text.replace(/\\s/g, ''); const lines = text ? text.split(/\\n/).length : 0; const paragraphs = text.trim() ? text.trim().split(/\\n\\s*\\n/).length : 0; const bytes = new Blob([text]).size; const manuscript = text ? Math.ceil(text.length / 400) : 0; const reading = text ? Math.ceil(text.length / 500) : 0; document.getElementById('count-all').textContent = text.length.toLocaleString('ja-JP') + '文字'; document.getElementById('count-no-space').textContent = noSpace.length.toLocaleString('ja-JP') + '文字（空白除外）'; document.getElementById('count-lines').textContent = lines.toLocaleString('ja-JP') + '行'; document.getElementById('count-paragraphs').textContent = paragraphs.toLocaleString('ja-JP') + '段落'; document.getElementById('count-bytes').textContent = bytes.toLocaleString('ja-JP') + 'バイト'; document.getElementById('count-manuscript').textContent = manuscript.toLocaleString('ja-JP') + '枚（400字詰め）'; document.getElementById('count-reading').textContent = '読了目安 ' + reading.toLocaleString('ja-JP') + '分'; });"""
        return body, setup, "", {"type": tool_type}
    body = '<div class="tool-card"><p>このツールの仕様を確認中です。公開前に入力・出力UIを実装してください。</p></div>'
    return body, "", "", {"type": "shell"}


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
    body, setup_script, submit_script, runtime = tool_body(spec)
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
  <script>(function(){{var h=location.hostname;if(h==='rakansens.github.io'||h==='bivrosttt.github.io'){{location.replace('https://ai-komon.bivrost.co.jp'+location.pathname.replace(/^\\/ai-komon2/,'')+location.search+location.hash);}}}})();</script>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)} | AI顧問室</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{esc(canonical)}">
  <meta property="og:title" content="{esc(title)} | AI顧問室">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:site_name" content="AI顧問室">
  <meta property="og:url" content="{esc(canonical)}">
  <meta property="og:image" content="{esc(base_url)}/assets/ogp.png">
  <meta name="twitter:card" content="summary_large_image">
  <meta property="og:type" content="website">
  <script src="../../analytics-config.js"></script>
  <script src="../../analytics.js"></script>
  <style>
    :root {{ color-scheme: light; --ink:#15243a; --muted:#68778a; --line:#d9e1ea; --brand:#1769aa; --soft:#f5f8fb; }}
    * {{ box-sizing:border-box; }} body {{ margin:0; font-family:system-ui,-apple-system,BlinkMacSystemFont,"Noto Sans JP",sans-serif; color:var(--ink); line-height:1.7; background:#fff; }}
    a {{ color:inherit; }} a:focus-visible,button:focus-visible,input:focus-visible,textarea:focus-visible,summary:focus-visible {{ outline:2px solid var(--brand); outline-offset:3px; }}
    .site-header {{ border-bottom:1px solid var(--line); }} .site-header-inner {{ display:flex; align-items:center; justify-content:space-between; min-height:62px; }} .site-header a {{ text-decoration:none; }} .wordmark {{ font-family:Georgia,"Noto Serif JP",serif; font-size:1rem; font-weight:700; }} .back-link {{ color:var(--muted); font-size:.78rem; }}
    main {{ width:min(960px,calc(100% - 32px)); margin:auto; }} header {{ padding:52px 0 26px; }} .eyebrow {{ margin:0 0 12px; color:var(--brand); font-size:.72rem; font-weight:800; letter-spacing:.12em; text-transform:uppercase; }} h1 {{ max-width:760px; margin:0 0 8px; font-size:clamp(2rem,5vw,3.5rem); line-height:1.18; letter-spacing:-.05em; }} h2 {{ margin:38px 0 10px; font-size:1.35rem; letter-spacing:-.03em; }} .lead {{ max-width:720px; margin:0; color:var(--muted); font-size:1rem; }} .tool-section {{ border-top:1px solid var(--line); padding-top:22px; }}
    .tool-card {{ padding:22px; border:1px solid var(--line); border-radius:8px; background:var(--soft); }} .field {{ display:grid; gap:5px; margin:12px 0; font-weight:700; font-size:.9rem; }} input,textarea {{ width:100%; border:1px solid #b8c7d5; border-radius:5px; padding:10px; background:#fff; font:inherit; }} button,.cta {{ display:inline-block; border:0; border-radius:5px; padding:9px 15px; background:var(--brand); color:#fff; font:inherit; font-size:.85rem; font-weight:700; cursor:pointer; text-decoration:none; }} .button-secondary {{ background:#fff; color:var(--brand); border:1px solid var(--brand); }} output {{ display:block; margin-top:14px; font-size:1.1rem; font-weight:800; }} .counter-grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; margin-top:14px; }} .counter-grid output {{ margin:0; padding:10px; border:1px solid var(--line); border-radius:5px; background:#fff; font-size:.95rem; }} .two-col {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:14px; }} .tool-actions {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:16px; }} .result-pre {{ white-space:pre-wrap; overflow:auto; background:#fff; border:1px solid var(--line); border-radius:5px; padding:14px; min-height:120px; }} fieldset {{ border:0; border-top:1px solid var(--line); margin:16px 0; padding:14px 0 0; }} legend {{ font-weight:800; padding:0 6px 0 0; }} .check-item {{ display:flex; gap:9px; align-items:flex-start; padding:8px 0; font-weight:500; font-size:.9rem; }} .check-item input {{ width:auto; margin-top:6px; }} .score-card {{ margin-top:16px; padding:15px; border-top:1px solid var(--line); background:#fff; }} .score-number {{ display:block; font-size:1.8rem; font-weight:800; color:var(--brand); }} .score-card li {{ margin:5px 0; }} .muted {{ color:var(--muted); }} .related-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:0 22px; border-top:1px solid var(--line); }} .related {{ display:grid; gap:2px; padding:13px 0; border-bottom:1px solid var(--line); color:inherit; text-decoration:none; }} .related:hover {{ color:var(--brand); }} .related span {{ color:var(--muted); font-size:.85rem; }} details {{ border-bottom:1px solid var(--line); padding:12px 0; }} summary {{ cursor:pointer; font-weight:700; font-size:.9rem; }} .cta-wrap {{ margin:38px 0; padding-top:20px; border-top:1px solid var(--line); }} .cta-wrap h2 {{ margin-top:0; }} .cta-wrap p {{ color:var(--muted); }} footer {{ margin-top:48px; padding:18px 0 36px; color:var(--muted); border-top:1px solid var(--line); font-size:.82rem; }} @media (max-width:680px) {{ main {{ width:calc(100% - 24px); }} .site-header-inner {{ min-height:56px; }} header {{ padding:38px 0 20px; }} h1 {{ font-size:clamp(2rem,10vw,2.8rem); }} h2 {{ margin-top:30px; }} .two-col,.counter-grid {{ grid-template-columns:1fr; }} .tool-card {{ padding:16px; }} .tool-actions {{ flex-direction:column; align-items:stretch; }} button,.cta {{ width:100%; text-align:center; }} }}
  </style>
</head>
<body>
<main>
  <div class="site-header"><div class="site-header-inner"><a class="wordmark" href="/">AI顧問室</a><a class="back-link" href="/tools/">無料ツール一覧へ</a></div></div>
  <header><p class="eyebrow">AI KOMON / FREE TOOL</p><h1>{esc(title)}</h1><p class="lead">{esc(description)}</p></header>
  <section class="tool-section" aria-labelledby="tool-heading"><h2 id="tool-heading">使う</h2>{body}</section>
  <section aria-labelledby="about-heading"><h2 id="about-heading">このツールについて</h2><p>{esc(explanations[0])}</p><p class="muted">{esc(explanations[1] if len(explanations) > 1 else explanations[0])}</p></section>
  <section aria-labelledby="faq-heading"><h2 id="faq-heading">注意点とFAQ</h2>{faq_html}</section>
  {f'<section aria-labelledby="related-heading"><h2 id="related-heading">関連する無料ツール</h2><div class="related-grid">{related_html}</div></section>' if related_html else ''}
  <section class="cta-wrap"><h2>業務に合わせて整える</h2><p>入力内容はブラウザ内で処理します。個別の業務設計や導入相談はこちら。</p>{cta_html}</section>
  <footer><a href="/">AI顧問室</a> / <a href="/privacy.html">プライバシーポリシー</a></footer>
</main>
<script>
const runtime = {json_script(runtime)};
{setup_script}
const form = document.getElementById('tool-form');
if (form) form.addEventListener('submit', event => {{ event.preventDefault(); try {{ {submit_script} }} catch (error) {{ const target = document.getElementById('tool-result') || document.getElementById('risk-result') || document.getElementById('mt-output'); if (target) target.textContent = '入力値を確認してください'; }} }});
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
