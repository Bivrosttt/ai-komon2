#!/usr/bin/env python3
"""Apply article-specific Noimos-style thumbnails to existing article pages.

The refresh is intentionally scoped to share previews and the opening article
cover: canonical URLs, article copy, detailed source assets, and redirects are
left unchanged. Running it repeatedly is safe because metadata and cover
placement are replaced by the same canonical thumbnail URL.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from generate_article_thumbnail import PALETTES, render  # noqa: E402

SHAPES = ("diagonal", "arcs", "waves", "rays", "blobs")
ICONS = ("cloud", "globe", "bars", "sparkles", "bot", "heart", "megaphone")

SPECIAL = {
    "ai-marketing-tools-comparison": ("cloud", "purple", "diagonal"),
    "ai-advisor-comparison": ("globe", "ocean", "diagonal"),
    "ai-advisor-cost": ("bars", "purple", "arcs"),
    "ai-roi": ("bars", "blue", "waves"),
    "customer-support-ai": ("heart", "coral", "blobs"),
    "sales-efficiency": ("megaphone", "teal", "rays"),
    "gijiroku-ai": ("bot", "navy", "arcs"),
    "internal-knowledge-search": ("globe", "blue", "waves"),
}


def choice(slug: str, values: tuple[str, ...], offset: int = 0) -> str:
    digest = hashlib.sha256(f"{slug}:{offset}".encode("utf-8")).hexdigest()
    return values[int(digest[:8], 16) % len(values)]


def replace_meta(html: str, attr: str, url: str) -> str:
    pattern = re.compile(rf'<meta\s+(?=[^>]*{re.escape(attr)})[^>]*>', flags=re.IGNORECASE)
    matches = list(pattern.finditer(html))
    if not matches:
        return html

    # Keep exactly one tag. Earlier runs of this refresh may have appended a
    # duplicate when an article used a compact head; cleaning here makes the
    # operation idempotent and avoids duplicate share metadata.
    for match in reversed(matches[1:]):
        html = html[: match.start()] + html[match.end() :]

    match = pattern.search(html)
    assert match is not None
    tag = match.group(0)
    if re.search(r'content=["\'][^"\']*["\']', tag, flags=re.IGNORECASE):
        tag = re.sub(r'content=["\'][^"\']*["\']', f'content="{url}"', tag, count=1, flags=re.IGNORECASE)
    return html[: match.start()] + tag + html[match.end() :]


def ensure_meta(html: str, attr: str, url: str, after_attr: str) -> str:
    updated = replace_meta(html, attr, url)
    # A replacement can be byte-identical when the URL is already current;
    # presence, rather than string inequality, determines whether insertion
    # is needed.
    if re.search(rf'<meta\s+(?=[^>]*{re.escape(attr)})[^>]*>', updated, flags=re.IGNORECASE):
        return updated
    marker = re.search(rf'<meta\s+[^>]*{re.escape(after_attr)}[^>]*>', html, flags=re.IGNORECASE)
    tag = f'<meta {attr} content="{url}">'
    if marker:
        return html[: marker.end()] + tag + html[marker.end() :]
    canonical = re.search(r'<link\s+rel="canonical"[^>]*>', html, flags=re.IGNORECASE)
    if canonical:
        return html[: canonical.end()] + tag + html[canonical.end() :]
    return html


def replace_jsonld_image(html: str, url: str) -> str:
    chunks = html.split('<script type="application/ld+json">')
    if len(chunks) == 1:
        return html
    for index in range(1, len(chunks)):
        chunks[index] = re.sub(
            r'("image"\s*:\s*")[^"]*(")',
            rf'\g<1>{url}\g<2>',
            chunks[index],
            count=1,
        )
    return '<script type="application/ld+json">'.join(chunks)


def replace_visible_cover(page_html: str, slug: str) -> str:
    """Place the generated SVG immediately after the article metadata.

    The Noimos pattern uses one simple cover between the author/date line and
    the article body. The old custom hero block is removed; detailed source
    assets are not deleted.
    """
    figure_match = re.search(r'<figure\b[^>]*>.*?</figure>', page_html, flags=re.IGNORECASE | re.DOTALL)
    if not figure_match or not re.search(r'<img\b', figure_match.group(0), flags=re.IGNORECASE):
        return page_html
    h1_match = re.search(r'<h1\b[^>]*>(.*?)</h1>', page_html, flags=re.IGNORECASE | re.DOTALL)
    title = re.sub(r'<[^>]+>', '', h1_match.group(1)).strip() if h1_match else slug.replace('-', ' ')
    alt = html.escape(f'{title}のシンプルな記事サムネイル', quote=True)
    caption = html.escape(f'{title}のカバー画像')
    new_img = (
        f'<img src="{slug}-thumbnail.svg" alt="{alt}" width="1600" height="900" '
        'loading="eager" fetchpriority="high">'
    )
    figure = figure_match.group(0)
    figure = re.sub(r'<img\b[^>]*>', new_img, figure, count=1, flags=re.IGNORECASE)
    # Keep the required semantic caption without displaying a duplicate line
    # under the thumbnail.
    figure = re.sub(r'<figcaption\b[^>]*>.*?</figcaption>', '', figure, count=1, flags=re.IGNORECASE | re.DOTALL)
    figure = figure.replace('</figure>', f'<figcaption class="visually-hidden">{caption}</figcaption></figure>', 1)
    without_cover = page_html[: figure_match.start()] + page_html[figure_match.end() :]

    # Remove the former text-heavy hero block wherever it was inserted.
    without_cover = re.sub(
        r'\s*(?:<!--\s*noimos-refresh:hero\s*-->\s*)?<div class="hero-visual">.*?<div class="hero-badges">.*?</div>\s*</div>',
        '',
        without_cover,
        count=1,
        flags=re.IGNORECASE | re.DOTALL,
    )
    meta_match = re.search(r'<p\b[^>]*>.*?公開日:.*?</p>', without_cover, flags=re.IGNORECASE | re.DOTALL)
    if not meta_match:
        return without_cover + '\n' + figure
    return without_cover[: meta_match.end()] + '\n  ' + figure + without_cover[meta_match.end() :]


def refresh_page(page: Path, root: Path) -> dict[str, str | bool]:
    slug = page.parent.name
    article_url = f"https://ai-komon.bivrost.co.jp/articles/{slug}/{slug}-thumbnail.svg"
    thumbnail = page.parent / f"{slug}-thumbnail.svg"
    icon, palette, shape = SPECIAL.get(
        slug,
        (choice(slug, ICONS, 1), choice(slug, tuple(PALETTES), 2), choice(slug, SHAPES, 3)),
    )
    render(thumbnail, icon, palette, shape, slug)

    before = page.read_text(encoding="utf-8")
    after = before
    after = ensure_meta(after, 'property="og:image"', article_url, 'property="og:url"')
    after = ensure_meta(after, 'name="twitter:image"', article_url, 'name="twitter:card"')
    after = replace_jsonld_image(after, article_url)
    after = replace_visible_cover(after, slug)
    if after != before:
        page.write_text(after, encoding="utf-8")
    return {
        "slug": slug,
        "thumbnail": str(thumbnail.relative_to(root)),
        "icon": icon,
        "palette": palette,
        "shape": shape,
        "visible_cover": f"articles/{slug}/{slug}-thumbnail.svg",
        "html_changed": after != before,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    pages = sorted(p for p in (root / "articles").glob("*/index.html") if p.parent.name != "index")
    results = [refresh_page(page, root) for page in pages]
    report = {"article_count": len(results), "changed_html": sum(bool(item["html_changed"]) for item in results), "articles": results}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"article_count": report["article_count"], "changed_html": report["changed_html"], "out": str(args.out)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
