#!/usr/bin/env bash
set -euo pipefail
# Assisted trace of corvid_logo.png into layered SVG parts using ImageMagick + Potrace

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
SRC="$ROOT_DIR/public/corvid_logo.png"
OUT_DIR="$ROOT_DIR/src/assets/parts"
TMP_DIR="$OUT_DIR/.tmp"

if ! command -v magick >/dev/null 2>&1 && ! command -v convert >/dev/null 2>&1; then
  echo "ImageMagick not found (magick/convert)." >&2; exit 1
fi
if ! command -v potrace >/dev/null 2>&1; then
  echo "Potrace not found." >&2; exit 1
fi

IM=${IM:-$(command -v magick >/dev/null 2>&1 && echo magick || echo convert)}

mkdir -p "$OUT_DIR" "$TMP_DIR"

# 1) Normalize and crop out the text portion (assumes bird occupies top ~78%)
read -r W H < <($IM identify -format "%w %h" "$SRC")
crop_h=$(python3 - <<PY
h=$H
print(int(h*0.78))
PY)

$IM "$SRC" -gravity north -crop ${W}x${crop_h}+0+0 +repage "$TMP_DIR/bird_top.png"

# 2) Create a clean silhouette bitmap for tracing
$IM "$TMP_DIR/bird_top.png" -colorspace Gray -alpha off -threshold 55% -type bilevel "$TMP_DIR/bird_top.pbm"

# 3) Trace full silhouette (body)
potrace -b svg "$TMP_DIR/bird_top.pbm" -o "$OUT_DIR/body.svg" --flat --turdsize 5 --longcurve 1 --opttolerance 0.2

# Helper: ROI mask function (normalized polygon coords 0..1)
roi_mask(){
  local name=$1; shift
  local poly=$* # e.g. "0.60,0.05 0.98,0.08 0.85,0.22 0.55,0.18"
  $IM "$TMP_DIR/bird_top.png" -fill black -colorize 100 \
    \( -size ${W}x${crop_h} xc:black -fill white -draw "polygon $poly" \) -compose copyopacity -composite \
    -colorspace Gray -alpha off -threshold 55% -type bilevel "$TMP_DIR/${name}.pbm"
  potrace -b svg "$TMP_DIR/${name}.pbm" -o "$OUT_DIR/${name}.svg" --flat --turdsize 5 --longcurve 1 --opttolerance 0.2 || true
}

# 4) Rough ROIs (based on logo layout, tweak as needed)
# upper beak
roi_mask beak_upper "0.58,0.00 0.99,0.00 0.99,0.18 0.62,0.18"
# lower beak
roi_mask beak_lower "0.60,0.10 0.99,0.08 0.99,0.28 0.62,0.28"
# wing front (outer)
roi_mask wing_f1 "0.14,0.20 0.62,0.08 0.72,0.30 0.14,0.55"
# wing mid
roi_mask wing_f2 "0.20,0.35 0.66,0.24 0.70,0.42 0.18,0.65"
# wing inner
roi_mask wing_f3 "0.22,0.46 0.62,0.36 0.64,0.52 0.20,0.72"
# tail
roi_mask tail "0.00,0.58 0.38,0.48 0.36,0.70 0.00,0.82"

echo "Traced parts written to: $OUT_DIR"

