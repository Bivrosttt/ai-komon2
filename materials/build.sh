#!/bin/bash
# materials/src/*.html を PDF に変換する
cd "$(dirname "$0")"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
for src in src/*.html; do
  name=$(basename "$src" .html)
  "$CHROME" --headless --disable-gpu --no-pdf-header-footer \
    --virtual-time-budget=15000 \
    --print-to-pdf="$name.pdf" "file://$(pwd)/$src" 2>/dev/null
  echo "built: materials/$name.pdf"
done
