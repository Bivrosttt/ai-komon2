#!/usr/bin/env python3
"""Apply the shared article CTA copy and responsive ordering.

The CTA remains a single article child so the desktop grid can pin it to the
right rail. Moving it to the end of the article in the source order makes the
mobile reading order natural without relying on CSS-only reordering.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


CTA_RE = re.compile(
    r'<div\b(?=[^>]*class=["\'][^"\']*(?:service-cta|tool-cta)[^"\']*["\'])[^>]*>.*?</div>',
    flags=re.IGNORECASE | re.DOTALL,
)
ARTICLE_RE = re.compile(r'<article\b[^>]*>.*?</article>', flags=re.IGNORECASE | re.DOTALL)


def refresh_cta(block: str) -> str:
    block = re.sub(r'(<h[23]\b[^>]*>).*?(</h[23]>)', r'\1無料でコンサル1回分をプレゼント\2', block, count=1, flags=re.IGNORECASE | re.DOTALL)
    block = re.sub(
        r'<p\b[^>]*>.*?</p>',
        '<p>対象業務、AI導入の課題、実装範囲を整理するコンサルティングを1回分、無料でお試しいただけます。</p>',
        block,
        count=1,
        flags=re.IGNORECASE | re.DOTALL,
    )
    block = re.sub(
        r'(<a\b[^>]*>).*?(</a>)',
        r'\1無料でコンサル1回分を受け取る\2',
        block,
        count=1,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return block


def refresh_page(page: Path) -> bool:
    source = page.read_text(encoding="utf-8")
    article_match = ARTICLE_RE.search(source)
    if not article_match:
        return False
    article = article_match.group(0)
    matches = list(CTA_RE.finditer(article))
    if len(matches) != 1:
        return False
    cta = refresh_cta(matches[0].group(0))
    without_cta = article[: matches[0].start()] + article[matches[0].end() :]
    # Keep one clean block at the end of the article. This is idempotent.
    without_cta = re.sub(r'\n{3,}', '\n\n', without_cta)
    end = without_cta.lower().rfind('</article>')
    updated_article = without_cta[:end].rstrip() + '\n  ' + cta + '\n' + without_cta[end:]
    updated = source[: article_match.start()] + updated_article + source[article_match.end() :]
    if updated == source:
        return False
    page.write_text(updated, encoding="utf-8")
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    pages = sorted(p for p in (root / "articles").glob("*/index.html") if p.parent.name != "index")
    changed = [str(p.relative_to(root)) for p in pages if refresh_page(p)]
    print({"article_count": len(pages), "changed": len(changed), "pages": changed})


if __name__ == "__main__":
    main()
