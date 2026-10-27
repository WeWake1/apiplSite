#!/usr/bin/env bash
# Renders every product in src/data/products.json ({"slug", "pallet"}) with this site's
# markings (tools/render/brand.json):
#   src/assets/products/<slug>/<n>.webp     studio renders (5 views; collar 4)
#   public/models/<slug>.glb                web 3D model, if brand.json has "glb": true
# Usage: tools/render/render_all.sh [slug ...]      (no slugs = everything)
set -euo pipefail
cd "$(dirname "$0")/../.."
BLENDER=${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}
RES=${RES:-1600}
SAMPLES=${SAMPLES:-128}
OUT=tools/render/out
mkdir -p "$OUT" src/assets/products
[ -d tools/render/textures/Wood096 ] || tools/render/fetch_textures.sh
python3 tools/render/pallets.py > /dev/null                      # refresh recipes.json
python3 tools/render/make_stamps.py tools/render/brand.json > /dev/null
GLB=$(python3 -c "import json; print('1' if json.load(open('tools/render/brand.json')).get('glb') else '')")
if [ $# -gt 0 ]; then
  slugs=("$@")
else
  slugs=($(python3 -c "import json; print(' '.join(p['slug'] for p in json.load(open('src/data/products.json'))))"))
fi
for slug in "${slugs[@]}"; do
  pallet=$(python3 -c "import json, sys; print(next(p['pallet'] for p in json.load(open('src/data/products.json')) if p['slug'] == sys.argv[1]))" "$slug")
  start=$(date +%s)
  extra=()
  if [ -n "$GLB" ]; then mkdir -p public/models; extra=(--glb "public/models/$slug.glb"); fi
  "$BLENDER" --background --factory-startup --python tools/render/render_pallet.py -- \
    --recipe "$pallet" --name "$slug" --out "$OUT" --res "$RES" --samples "$SAMPLES" ${extra[@]+"${extra[@]}"} 2>&1 \
    | grep -E "WROTE|WARNING|Error|Traceback" || true
  rm -rf "src/assets/products/$slug"
  mkdir -p "src/assets/products/$slug"
  for png in "$OUT/$slug"-[0-9].png; do
    [ -f "$png" ] || continue
    v=$(basename "$png" .png); v=${v##*-}
    cwebp -quiet -q 90 -m 6 "$png" -o "src/assets/products/$slug/$v.webp"
  done
  echo "done $slug ($pallet) in $(( $(date +%s) - start ))s"
done
