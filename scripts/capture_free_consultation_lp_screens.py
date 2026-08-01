#!/usr/bin/env python3
"""Capture the free-consultation research LPs without touching the prior 40-LP batch."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(__file__).with_name("capture_lp_screens_and_build_pdfs.py")
BASE = ROOT / "docs/meta-ad-library-research/2026-07-28-free-consultation-20"


def main() -> None:
    spec = importlib.util.spec_from_file_location("lp_capture_base", SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load capture module: {SOURCE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    module.BASE = BASE
    module.RECORDS_JSON = BASE / "records.json"
    module.RECORDS_CSV = BASE / "records.csv"
    module.SCREEN_ROOT = BASE / "output/lp-screens"
    module.PDF_ROOT = BASE / "output/lp-pdfs"
    module.INDEX_JSON = BASE / "output/lp-capture-index.json"
    module.INDEX_CSV = BASE / "output/lp-capture-index.csv"
    module.SESSION = "free-consult-capture"
    module.VIEWPORT_W = 1440
    module.VIEWPORT_H = 900
    module.STEP = 900
    module.MAX_SCREENS = 40
    module.main()


if __name__ == "__main__":
    main()
