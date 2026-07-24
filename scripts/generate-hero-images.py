#!/usr/bin/env python3
"""2026-07-22: AI顧問室トップ用ヒーロー画像を gpt-image-2 で生成する。

OPENAI_API_KEY は rensaimanga/.env または mangaagent3/.env から読み込む。
使い方:
  python3 scripts/generate-hero-images.py
  python3 scripts/generate-hero-images.py --only 01-consultation
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = ROOT / "scripts" / "hero-prompts"
OUT_DIR = ROOT / "assets" / "hero"
GENERATIONS_URL = "https://api.openai.com/v1/images/generations"
MODEL = os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-2")
SIZE = "1536x1024"  # hero 3:2
QUALITY = "medium"

ENV_CANDIDATES = [
    ROOT.parent / "rensaimanga" / ".env",
    ROOT.parent / "mangaagent3" / ".env",
]


def load_env_file(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val


def ensure_api_key() -> str:
    for env_path in ENV_CANDIDATES:
        load_env_file(env_path)
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        sys.exit(
            "OPENAI_API_KEY がありません。"
            "rensaimanga/.env または mangaagent3/.env を用意してください。"
        )
    return key


def call_generations(api_key: str, prompt: str) -> bytes:
    body = json.dumps(
        {
            "model": MODEL,
            "prompt": prompt,
            "n": 1,
            "size": SIZE,
            "quality": QUALITY,
        }
    ).encode()
    req = urllib.request.Request(
        GENERATIONS_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                payload = json.load(resp)
            return base64.b64decode(payload["data"][0]["b64_json"])
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf-8", errors="replace")
            if e.code in (429, 500, 502, 503, 504) and attempt < 2:
                time.sleep(2 ** attempt * 5)
                continue
            raise RuntimeError(f"OpenAI HTTP {e.code}: {msg[:500]}") from e


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only", help="生成する stem (例: 01-consultation)")
    args = ap.parse_args()

    api_key = ensure_api_key()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    prompt_files = sorted(PROMPTS_DIR.glob("*.md"))
    if args.only:
        prompt_files = [PROMPTS_DIR / f"{args.only}.md"]
        if not prompt_files[0].is_file():
            sys.exit(f"prompt not found: {prompt_files[0]}")

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": MODEL,
        "size": SIZE,
        "quality": QUALITY,
        "images": [],
    }

    for pf in prompt_files:
        stem = pf.stem
        out_png = OUT_DIR / f"hero-{stem.split('-', 1)[1] if '-' in stem else stem}.png"
        meta_path = out_png.with_suffix(".meta.json")
        prompt = pf.read_text(encoding="utf-8").strip()
        print(f"🎨 {stem} → {out_png.name}")
        png = call_generations(api_key, prompt)
        out_png.write_bytes(png)
        meta = {
            "stem": stem,
            "file": out_png.name,
            "model": MODEL,
            "size": SIZE,
            "quality": QUALITY,
            "bytes": len(png),
            "prompt_file": str(pf.relative_to(ROOT)),
        }
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        manifest["images"].append(meta)
        print(f"   ✓ {len(png)/1024:.1f} KB")

    (OUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Done. {len(manifest['images'])} images → {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
