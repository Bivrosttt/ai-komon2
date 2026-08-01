#!/usr/bin/env python3
"""Generate Noimos-inspired, original article thumbnails as text-free SVGs.

The visual recipe is intentionally small and deterministic: a 16:9 gradient,
one abstract background motif, and one friendly white icon. It does not copy
Noimos assets; it provides reusable primitives for our own article system.

Example:
  python3 scripts/generate_article_thumbnail.py \
    --output articles/ai-marketing-tools-comparison/ai-marketing-tools-comparison-thumbnail.svg \
    --icon sparkles --palette ocean --shape diagonal --seed ai-marketing-tools
"""

from __future__ import annotations

import argparse
import hashlib
import html
import re
from pathlib import Path

WIDTH, HEIGHT = 1600, 900

# Center the actual icon geometry, not its nominal construction coordinates.
# Several asymmetric icons (for example the cloud and megaphone) have a visual
# bounding box that is offset from the 1600x900 canvas center.
ICON_TRANSLATIONS = {
    "globe": (0, 0),
    "cloud": (-67.5, 57),
    "bars": (0, -40),
    "sparkles": (-53, 4),
    "bot": (0, -12.5),
    "heart": (0, -15),
    "megaphone": (45, -35),
}

PALETTES = {
    "ocean": ("#2eabc3", "#69c4cf", "#b8eef0"),
    "teal": ("#063f43", "#167f78", "#a8e7d2"),
    "blue": ("#273db2", "#304fd0", "#aabaff"),
    "purple": ("#5630ba", "#9b65df", "#c5a9f5"),
    "navy": ("#09264b", "#2167a4", "#a8e1e7"),
    "coral": ("#9c3e52", "#e28478", "#ffd0ae"),
}


def safe_id(value: str) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", value.lower()).strip("-") or "thumb"


def stable_number(seed: str, maximum: int) -> int:
    return int(hashlib.sha256(seed.encode("utf-8")).hexdigest()[:8], 16) % maximum


def background(shape: str, seed: str) -> str:
    shift = stable_number(seed, 140)
    if shape == "diagonal":
        return f'''<path d="M-180 800 650 0h190L10 900h-190ZM420 900 1370 0h220L650 900H420ZM1050 900 1600 360v230l-320 310Z" fill="#fff" opacity=".13"/><path d="M-180 820 650 20h120L-40 900h-140ZM480 900 1400 20h130L620 900Z" fill="#fff" opacity=".06"/>'''
    if shape == "arcs":
        return f'''<circle cx="{260 + shift}" cy="-40" r="720" fill="none" stroke="#fff" stroke-width="140" opacity=".09"/><circle cx="{1110 - shift // 2}" cy="980" r="720" fill="none" stroke="#fff" stroke-width="120" opacity=".1"/>'''
    if shape == "waves":
        return '''<path d="M-60 160C270-40 520-40 820 150s550 210 850-30v230c-300 240-570 210-900 20S270 210-60 430Z" fill="#fff" opacity=".1"/><path d="M-80 590c310-230 580-210 900-20s570 220 860-30v210c-300 230-570 210-900 30S230 590-80 800Z" fill="#fff" opacity=".08"/>'''
    if shape == "rays":
        return '''<path d="M800 450 20 0h260l520 300L1320 0h260L800 450Zm0 0 780 450h-260L800 600 280 900H20l780-450Z" fill="#fff" opacity=".1"/><circle cx="800" cy="450" r="360" fill="none" stroke="#fff" stroke-width="80" opacity=".07"/>'''
    if shape == "blobs":
        return f'''<circle cx="{280 + shift}" cy="150" r="310" fill="#fff" opacity=".09"/><circle cx="1280" cy="760" r="390" fill="#fff" opacity=".1"/><path d="M0 710c240-150 430-160 630-40s450 150 970-180v410H0Z" fill="#fff" opacity=".06"/>'''
    raise ValueError(f"unknown shape: {shape}")


def icon(icon_name: str) -> str:
    stroke = 'fill="none" stroke="url(#icon-fill)" stroke-width="34" stroke-linecap="round" stroke-linejoin="round"'
    if icon_name == "globe":
        return f'''<g {stroke}><circle cx="800" cy="450" r="190"/><path d="M610 450h380M800 260c-88 90-88 290 0 380M800 260c88 90 88 290 0 380M670 330c80 45 180 45 260 0M670 570c80-45 180-45 260 0"/></g>'''
    if icon_name == "cloud":
        return '''<path d="M640 610c-80 0-145-65-145-145s65-145 145-145c24-104 117-180 228-180 121 0 220 88 232 203 78 7 140 72 140 151 0 84-68 152-152 152H640Z" fill="url(#icon-fill)"/>'''
    if icon_name == "bars":
        return '''<g fill="url(#icon-fill)"><rect x="620" y="510" width="76" height="170" rx="38"/><rect x="762" y="410" width="76" height="270" rx="38"/><rect x="904" y="300" width="76" height="380" rx="38"/></g>'''
    if icon_name == "sparkles":
        return '''<g fill="url(#icon-fill)"><path d="m800 210 30 150 150 30-150 30-30 150-30-150-150-30 150-30 30-150Z"/><path d="m1060 470 18 88 88 18-88 18-18 88-18-88-88-18 88-18 18-88Z"/><circle cx="570" cy="560" r="30"/><circle cx="1030" cy="250" r="20"/></g>'''
    if icon_name == "bot":
        return '''<g fill="none" stroke="url(#icon-fill)" stroke-width="30" stroke-linecap="round" stroke-linejoin="round"><rect x="610" y="330" width="380" height="260" rx="80"/><path d="M800 330v-75M770 255h60M700 670v-55M900 670v-55"/><circle cx="725" cy="460" r="20" fill="url(#icon-fill)" stroke="none"/><circle cx="875" cy="460" r="20" fill="url(#icon-fill)" stroke="none"/><path d="M735 525c40 30 90 30 130 0"/></g>'''
    if icon_name == "heart":
        return '''<path d="M800 680S570 545 570 390c0-82 61-140 137-140 46 0 78 23 93 59 15-36 47-59 93-59 76 0 137 58 137 140 0 155-230 290-230 290Z" fill="url(#icon-fill)"/>'''
    if icon_name == "megaphone":
        return '''<g fill="url(#icon-fill)"><path d="M630 415 1080 270v360L630 515Z"/><path d="M610 430H510c-44 0-80 36-80 80s36 80 80 80h100Z"/><path d="m700 570 50 130h110l-55-155Z"/></g>'''
    raise ValueError(f"unknown icon: {icon_name}")


def render(output: Path, icon_name: str, palette_name: str, shape: str, seed: str) -> None:
    start, end, icon_light = PALETTES[palette_name]
    ident = safe_id(seed)
    icon_tx, icon_ty = ICON_TRANSLATIONS[icon_name]
    title = html.escape(f"{seed} article thumbnail")
    desc = html.escape("A gradient background with a friendly white icon")
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">
  <title id="title">{title}</title>
  <desc id="desc">{desc}</desc>
  <defs>
    <linearGradient id="bg-{ident}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{start}"/><stop offset="1" stop-color="{end}"/></linearGradient>
    <linearGradient id="icon-fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff"/><stop offset=".34" stop-color="#fff"/><stop offset="1" stop-color="{icon_light}"/></linearGradient>
    <filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".72" numOctaves="2" stitchTiles="stitch"/><feColorMatrix type="saturate" values="0"/><feComponentTransfer><feFuncA type="table" tableValues="0 .055"/></feComponentTransfer></filter>
    <filter id="shadow" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="18" stdDeviation="18" flood-color="#052341" flood-opacity=".18"/></filter>
  </defs>
  <rect width="{WIDTH}" height="{HEIGHT}" rx="48" fill="url(#bg-{ident})"/>
  {background(shape, seed)}
  <rect width="{WIDTH}" height="{HEIGHT}" rx="48" filter="url(#grain)" opacity=".42"/>
  <g filter="url(#shadow)" transform="translate({icon_tx:g} {icon_ty:g})">{icon(icon_name)}</g>
</svg>
'''
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(svg, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--icon", choices=("globe", "cloud", "bars", "sparkles", "bot", "heart", "megaphone"), default="sparkles")
    parser.add_argument("--palette", choices=tuple(PALETTES), default="ocean")
    parser.add_argument("--shape", choices=("diagonal", "arcs", "waves", "rays", "blobs"), default="diagonal")
    parser.add_argument("--seed", default="article")
    args = parser.parse_args()
    render(args.output, args.icon, args.palette, args.shape, args.seed)
    print(args.output)


if __name__ == "__main__":
    main()
