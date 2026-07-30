#!/usr/bin/env python3
"""Build a readable Markdown reference corpus from local Noimos SEO articles.

The corpus preserves visible copy, metadata, schemas, visual component classes,
inline CSS, image files, and source hashes. It is intentionally local-source
only: no competitor wording or external page body is copied into the corpus.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup, NavigableString
from markdownify import markdownify


ROOT = Path(__file__).resolve().parents[1]


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def local_path_from_src(html_path: Path, src: str) -> Path | None:
    if not src or src.startswith(("http://", "https://", "data:", "#")):
        return None
    path = (html_path.parent / src).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError:
        return None
    return path if path.exists() and path.is_file() else None


def schema_nodes(soup: BeautifulSoup) -> list[dict]:
    nodes: list[dict] = []
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = script.string or script.get_text()
        try:
            payload = json.loads(raw)
        except (TypeError, json.JSONDecodeError):
            continue
        if isinstance(payload, dict) and isinstance(payload.get("@graph"), list):
            nodes.extend(node for node in payload["@graph"] if isinstance(node, dict))
            base = {key: value for key, value in payload.items() if key != "@graph"}
            if base.get("@type"):
                nodes.insert(0, base)
        elif isinstance(payload, dict):
            nodes.append(payload)
        elif isinstance(payload, list):
            nodes.extend(node for node in payload if isinstance(node, dict))
    return nodes


def css_selectors(css: str) -> list[str]:
    selectors: list[str] = []
    for match in re.finditer(r"([^{}]+)\{", css):
        selector = clean(match.group(1))
        if selector and not selector.startswith(("@", "/*")):
            selectors.append(selector)
    return selectors


def image_dimensions(path: Path) -> str:
    try:
        from PIL import Image

        with Image.open(path) as image:
            return f"{image.width}×{image.height}"
    except Exception:
        return "unknown"


def markdown_body(article: BeautifulSoup, image_map: dict[str, str]) -> str:
    raw = markdownify(
        str(article),
        heading_style="ATX",
        bullets="-",
        strip=["script", "style"],
        strong_em_symbol="*",
    )
    for source, target in image_map.items():
        raw = raw.replace(f"]({source})", f"]({target})")
    raw = re.sub(r"\n{3,}", "\n\n", raw)
    return raw.strip()


def page_chrome(soup: BeautifulSoup) -> str:
    parts = []
    for selector, label in (("header", "header"), ("footer", "footer"), ("nav.breadcrumb", "breadcrumb")):
        element = soup.select_one(selector)
        if element:
            parts.append(f"- **{label}:** {clean(element.get_text(' ', strip=True))}")
    return "\n".join(parts) or "- ページクロームはarticle本文に統合されています。"


def component_inventory(article: BeautifulSoup) -> str:
    records: dict[str, dict] = {}
    for element in article.find_all(True):
        classes = element.get("class") or []
        for class_name in classes:
            record = records.setdefault(class_name, {"elements": Counter(), "sample": ""})
            record["elements"][element.name] += 1
            if not record["sample"]:
                text = clean(element.get_text(" ", strip=True))
                if text:
                    record["sample"] = text[:220]
    rows = ["| class | element count | purpose/sample |", "| --- | ---: | --- |"]
    for class_name in sorted(records):
        record = records[class_name]
        count = sum(record["elements"].values())
        elements = ", ".join(f"`{name}`×{count}" for name, count in sorted(record["elements"].items()))
        sample = record["sample"].replace("|", "\\|") or "(textなし / visual-only)"
        rows.append(f"| `{class_name}` | {elements} | {sample} |")
    return "\n".join(rows)


def article_record(html_path: Path, out_root: Path) -> dict:
    slug = html_path.parent.name
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8", errors="replace"), "html.parser")
    article = soup.find("article") or soup.find("main") or soup.body or soup
    title = clean(soup.title.get_text(" ", strip=True)) if soup.title else slug
    description = ""
    description_tag = soup.find("meta", attrs={"name": "description"})
    if description_tag:
        description = description_tag.get("content", "")
    canonical_tag = soup.find("link", attrs={"rel": "canonical"})
    canonical = canonical_tag.get("href", "") if canonical_tag else ""
    nodes = schema_nodes(soup)
    types = []
    published = ""
    modified = ""
    for node in nodes:
        node_type = node.get("@type")
        types.extend(node_type if isinstance(node_type, list) else [node_type] if node_type else [])
        published = published or str(node.get("datePublished", ""))
        modified = modified or str(node.get("dateModified", ""))

    media_root = out_root / "media" / slug
    media_root.mkdir(parents=True, exist_ok=True)
    image_map: dict[str, str] = {}
    media: list[dict] = []
    for image in article.find_all("img"):
        source = image.get("src", "")
        local = local_path_from_src(html_path, source)
        if not local:
            media.append({"src": source, "alt": image.get("alt", ""), "local": False})
            continue
        destination = media_root / local.name
        shutil.copy2(local, destination)
        # Per-article Markdown lives under reference/articles/, so media is one level up.
        relative = f"../media/{slug}/{destination.name}"
        image_map[source] = relative
        media.append(
            {
                "src": source,
                "local": True,
                "copied_to": relative,
                "alt": image.get("alt", ""),
                "caption": clean(image.find_next("figcaption").get_text(" ", strip=True))
                if image.find_next("figcaption")
                else "",
                "dimensions": image_dimensions(local),
                "sha256": sha256(local),
            }
        )

    inline_css = "\n\n".join(style.get_text() for style in soup.find_all("style") if style.get_text(strip=True))
    linked_stylesheets = [link.get("href", "") for link in soup.find_all("link", rel="stylesheet")]
    text = clean(article.get_text(" ", strip=True))
    japanese_chars = len(re.findall(r"[\u3040-\u30ff\u3400-\u9fff]", text))
    headings = {
        "h1": [clean(h.get_text(" ", strip=True)) for h in article.find_all("h1")],
        "h2": [clean(h.get_text(" ", strip=True)) for h in article.find_all("h2")],
        "h3": [clean(h.get_text(" ", strip=True)) for h in article.find_all("h3")],
    }
    hrefs = [a.get("href", "") for a in article.find_all("a") if a.get("href")]
    internal = [href for href in hrefs if href.startswith(("/", "./", "../")) or "ai-komon.bivrost.co.jp" in href]
    external = [href for href in hrefs if href.startswith("http") and "ai-komon.bivrost.co.jp" not in href]
    record = {
        "slug": slug,
        "source_html": str(html_path.relative_to(ROOT)),
        "source_sha256": sha256(html_path),
        "title": title,
        "description": description,
        "canonical": canonical,
        "datePublished": published,
        "dateModified": modified,
        "schema_types": sorted(set(types)),
        "japanese_chars": japanese_chars,
        "headings": headings,
        "tables": len(article.find_all("table")),
        "details": len(article.find_all("details")),
        "images": media,
        "internal_link_count": len(set(internal)),
        "external_link_count": len(set(external)),
        "classes": sorted({class_name for element in article.find_all(True) for class_name in (element.get("class") or [])}),
        "linked_stylesheets": linked_stylesheets,
        "inline_css_selectors": css_selectors(inline_css),
    }

    page_path = out_root / "articles" / f"{slug}.md"
    page_path.parent.mkdir(parents=True, exist_ok=True)
    image_lines = []
    for item in media:
        alt = item.get("alt") or "（alt未設定）"
        if item.get("local"):
            image_lines.append(f"### {alt}\n\n![{alt}]({item['copied_to']})\n\n- source: `{item['src']}`\n- dimensions: `{item['dimensions']}`\n- caption: {item.get('caption') or 'なし'}\n- sha256: `{item['sha256']}`")
        else:
            image_lines.append(f"### {alt}\n\n- source: `{item['src']}`（ローカルコピーなし）")
    schema_json = json.dumps(nodes, ensure_ascii=False, indent=2)
    styles_section = ""
    if inline_css:
        styles_section += "\n### Inline CSS（原文）\n\n```css\n" + inline_css.strip() + "\n```\n"
    if linked_stylesheets:
        styles_section += "\n### 外部 stylesheet\n\n" + "\n".join(f"- `{href}`" for href in linked_stylesheets) + "\n"
    body = markdown_body(article, image_map)
    frontmatter = [
        "---",
        f"slug: {slug}",
        f"source_html: {html_path.relative_to(ROOT)}",
        f"canonical: {canonical}",
        f"dateModified: {modified or '未設定'}",
        f"schema_types: [{', '.join(record['schema_types'])}]",
        f"japanese_chars: {japanese_chars}",
        f"reference_generated_at: {datetime.now(timezone.utc).isoformat()}",
        "---",
    ]
    lines = [
        *frontmatter,
        "",
        f"# {title}",
        "",
        "> この資料は、リポジトリ内の自社SEO記事を再利用できるように構造化した参照用転記です。競合ページの本文・画像・CSSは含めません。",
        "",
        "## SEOメタデータ",
        "",
        f"- title: {title}",
        f"- description: {description}",
        f"- canonical: `{canonical}`",
        f"- published: `{published or '未設定'}`",
        f"- modified: `{modified or '未設定'}`",
        f"- source HTML: [`{html_path.relative_to(ROOT)}`](../../../../{html_path.relative_to(ROOT)})",
        f"- source SHA-256: `{sha256(html_path)}`",
        "",
        "## ページ構造と計測用シグナル",
        "",
        f"- 日本語文字数（article本文）: `{japanese_chars}`",
        f"- H1: `{len(headings['h1'])}` / H2: `{len(headings['h2'])}` / H3: `{len(headings['h3'])}`",
        f"- table: `{record['tables']}` / details FAQ: `{record['details']}`",
        f"- internal links: `{record['internal_link_count']}` / external links: `{record['external_link_count']}`",
        f"- JSON-LD: `{', '.join(record['schema_types']) or 'なし'}`",
        "",
        "### 見出し一覧",
        "",
    ]
    for level in ("h1", "h2", "h3"):
        for heading in headings[level]:
            lines.append(f"- {level.upper()}: {heading}")
    lines += [
        "",
        "## ページクローム",
        "",
        page_chrome(soup),
        "",
        "## 装飾・レイアウトの再利用台帳",
        "",
        component_inventory(article),
        styles_section,
        "",
        "## 図解・画像",
        "",
        "\n\n".join(image_lines) if image_lines else "- inline画像なし。OGP画像・CSS背景のみのページです。",
        "",
        "## 構造化データ（JSON-LD原文）",
        "",
        "```json",
        schema_json or "[]",
        "```",
        "",
        "## 全文の文字起こし（装飾付き可読版）",
        "",
        body,
        "",
        "## 参照用リンク一覧",
        "",
    ]
    for href in sorted(set(hrefs)):
        lines.append(f"- {href}")
    page_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return record


def build(out_root: Path) -> None:
    out_root.mkdir(parents=True, exist_ok=True)
    articles = sorted((ROOT / "articles").glob("*/index.html"))
    records = [article_record(path, out_root) for path in articles]

    shared_styles = ROOT / "assets/articles/article.css"
    if shared_styles.exists():
        style_dest = out_root / "assets" / "article.css"
        style_dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(shared_styles, style_dest)

    inventory = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_root": str(ROOT),
        "scope": "articles/*/index.html",
        "article_count": len(records),
        "image_count": sum(len(record["images"]) for record in records),
        "articles": records,
    }
    (out_root / "inventory.json").write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    title_rows = ["| # | slug | title | chars | H2 | tables | images | schema |", "| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |"]
    for index, record in enumerate(records, start=1):
        title_rows.append(
            f"| {index} | [`{record['slug']}`](articles/{record['slug']}.md) | {record['title'].replace('|', '\\|')} | {record['japanese_chars']} | {len(record['headings']['h2'])} | {record['tables']} | {len(record['images'])} | {', '.join(record['schema_types']) or '—'} |"
        )
    (out_root / "INDEX.md").write_text(
        "# Noimos SEO記事リファレンス\n\n"
        "> 生成日: " + inventory["generated_at"] + "\n\n"
        "このディレクトリは、`articles/`配下の自社SEO記事を、Noimosの執筆・装飾・図解・計測設計を再利用するために整理した参照コーパスです。本文は可読Markdown、画像はローカルコピー、CSSとJSON-LDは原文または参照先を保持しています。\n\n"
        "## 使い方\n\n"
        "1. まず一覧で検索意図・文字量・H2数・表・画像・JSON-LDの傾向を確認する。\n"
        "2. 各記事の `装飾・レイアウトの再利用台帳` でコンポーネントとクラスを確認する。\n"
        "3. `全文の文字起こし` と `図解・画像` を、競合の表現をコピーせず新規記事の設計材料として使う。\n"
        "4. 変更時は元HTMLのsource SHA-256とdateModifiedを更新し、GSCの実測を別ログに残す。\n\n"
        "## 記事一覧\n\n" + "\n".join(title_rows) + "\n",
        encoding="utf-8",
    )

    # A compact research memo separates facts from reusable hypotheses.
    research = [
        "# Noimos SEO記事リサーチメモ",
        "",
        f"調査対象: `articles/*/index.html`（{len(records)}本）",
        f"生成日時: `{inventory['generated_at']}`",
        "",
        "## 観測した事実",
        "",
        f"- 記事数: `{len(records)}`",
        f"- JSON-LD Articleを持つ記事: `{sum('Article' in r['schema_types'] for r in records)}`",
        f"- FAQPageを持つ記事: `{sum('FAQPage' in r['schema_types'] for r in records)}`",
        f"- 画像をarticle本文に持つ記事: `{sum(bool(r['images']) for r in records)}`",
        f"- 表を持つ記事: `{sum(r['tables'] > 0 for r in records)}`",
        f"- 平均日本語文字数: `{round(sum(r['japanese_chars'] for r in records) / max(len(records), 1))}`",
        "",
        "## 事実・仮説・未取得データの分離",
        "",
        "- 事実: 上記の件数、文字数、見出し、クラス、画像、JSON-LD、リンク、元HTMLのSHA-256はローカルファイルから抽出した。",
        "- 仮説: `answer`・表・記事固有図解・人の承認・CTAを組み合わせる設計は、読者の意思決定を短くするための編集パターンとして再利用できる。これは順位・CVを保証する因果分析ではない。",
        "- 未取得: GSCの表示・クリック・CTR・掲載順位、記事別の問い合わせ、検索ボリューム、キーワード難易度、現在のSERP順位。",
        "",
        "## 記事群のテーマクラスター",
        "",
        "- 経営・導入判断: AI顧問比較、費用、ROI、メリット、リスク、ロードマップ、AI活用事例、AIエージェント",
        "- 営業・顧客対応: 営業効率化、営業メール、提案書、カスタマーサポート、見積、採用",
        "- バックオフィス: 議事録、契約書、請求書、タスク優先順位",
        "- ナレッジ・定着: マニュアル、社内ルール、研修、FAQ、ナレッジ検索、引き継ぎ、ChatGPT活用、業務効率化",
        "",
        "## 再利用できる記事設計パターン（観測からの抽象化）",
        "",
        "1. H1の直後に読者の判断を助ける短い結論を置く。",
        "2. 概念説明だけで終わらず、表・手順・判断条件・失敗時の戻し方へ進む。",
        "3. 顧客送信、契約、請求、権限、削除などは人の承認を残す。",
        "4. `answer`、`key-points`、`toc`、`steps`、`note`、`service-cta`、`related` など、本文の役割をCSSクラスで分ける。",
        "5. 記事固有の図解は、altとfigcaptionを隣接させ、JSON-LD・内部リンク・FAQと同じ公開単位で検証する。",
        "6. 料金・効果・実績の数値は主張台帳へ登録し、未取得の検索ボリュームや難易度を推測しない。",
        "",
        "## 参考にする際の制約",
        "",
        "- これは自社記事の構造研究であり、競合本文の転載ではない。",
        "- 既存記事のH2数や文字量を機械的にコピーせず、検索意図・情報利得・読者の判断に合わせて再設計する。",
        "- 画像は著作権と出典を確認した自社資産だけを再利用する。",
        "- 公開前に `noimos-seo-geo-article` の構造検証と `noimos-content-quality-gate` のAI-only検証を再実行する。",
    ]
    (out_root / "RESEARCH-MEMO.md").write_text("\n".join(research) + "\n", encoding="utf-8")

    media_rows = ["# Noimos SEO画像・図解マニフェスト", "", "| article | alt | file | dimensions | caption | sha256 |", "| --- | --- | --- | --- | --- | --- |"]
    for record in records:
        for item in record["images"]:
            if item.get("local"):
                media_rows.append(
                    f"| `{record['slug']}` | {item.get('alt','').replace('|','\\|')} | [{item['copied_to']}]({item['copied_to']}) | {item.get('dimensions','unknown')} | {(item.get('caption') or 'なし').replace('|','\\|')} | `{item.get('sha256','')}` |"
                )
            else:
                media_rows.append(f"| `{record['slug']}` | {item.get('alt','')} | `{item.get('src','')}` | external/unknown | — | — |")
    (out_root / "MEDIA-MANIFEST.md").write_text("\n".join(media_rows) + "\n", encoding="utf-8")

    class_counts = Counter(class_name for record in records for class_name in record["classes"])
    design = [
        "# Noimos SEO記事デザインシステム参照",
        "",
        "## 共通アセット",
        "",
        "- 外部CSS（原文コピー）: [`assets/article.css`](assets/article.css)",
        "- 記事ごとのinline CSSセレクタは各Markdownの「装飾・レイアウトの再利用台帳」に保存。",
        "",
        "## 横断的に使われるクラス",
        "",
        "| class | 記事数 | 役割の観測例 |",
        "| --- | ---: | --- |",
    ]
    for class_name, count in sorted(class_counts.items()):
        role = {
            "answer": "冒頭の結論・回答先出し",
            "key-points": "要点の箇条書き",
            "toc": "目次・ジャンプリンク",
            "hero-visual": "記事固有の視覚的導入",
            "steps": "工程・段階の視覚化",
            "note": "注意点・境界条件",
            "service-cta": "価値提供後のサービスCTA",
            "tool-cta": "ツール/サービス導線",
            "related": "関連記事の回遊カード",
            "sources": "出典・一次情報リスト",
            "table-scroll": "モバイル横スクロール可能な表",
        }.get(class_name, "記事固有の装飾またはレイアウト")
        design.append(f"| `{class_name}` | {count} | {role} |")
    design += [
        "",
        "## 再利用ルール",
        "",
        "- `answer`はH1直後に置き、検索意図への回答と判断ルールを短く書く。",
        "- 表は単なる機能一覧ではなく、向く条件・成果物・承認点・見落とし費用など意思決定項目にする。",
        "- `hero-visual`や図解画像に重要な主張を閉じ込めず、alt・figcaption・本文にも同じ条件を記述する。",
        "- `service-cta`は価値提供後に1つ置き、誇大な成果保証を避ける。",
        "- モバイルでは表の横スクロールとCTAのタップ領域を必ず実機幅で確認する。",
    ]
    (out_root / "DESIGN-SYSTEM.md").write_text("\n".join(design) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="seo/reference/noimos-seo-articles")
    args = parser.parse_args()
    out = (ROOT / args.out).resolve() if not Path(args.out).is_absolute() else Path(args.out)
    build(out)
    print(json.dumps({"out": str(out), "articles": len(list((out / 'articles').glob('*.md'))), "images": len(list((out / 'media').glob('*/*')))}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
