#!/usr/bin/env bash
# Downloads the CC0 wood scans used by render_pallet.py (ambientCG.com, public domain).
set -euo pipefail
cd "$(dirname "$0")"
tmp=$(mktemp -d)
for t in Wood096 Wood060; do
  mkdir -p "textures/$t"
  curl -sL -o "$tmp/$t.zip" "https://ambientcg.com/get?file=${t}_2K-JPG.zip"
  for k in Color Roughness Displacement; do
    unzip -o -j -q "$tmp/$t.zip" "${t}_2K-JPG_${k}.jpg" -d "textures/$t"
  done
done
rm -rf "$tmp"
echo "textures ready"
