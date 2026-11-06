#!/usr/bin/env bash
# Builds the site and packs the contents of dist/ (including the hidden .htaccess files) into
# deploy/ambica-site-<date>.zip, ready to upload to public_html in Hostinger's File Manager and extract.
set -euo pipefail
cd "$(dirname "$0")/../.."
npm run build
mkdir -p deploy
zip_path="deploy/ambica-site-$(date +%Y-%m-%d-%H%M).zip"
(cd dist && zip -qr -X "../$zip_path" . -x '.DS_Store' -x '*/.DS_Store')
echo "Ready: $zip_path ($(du -h "$zip_path" | cut -f1)), $(unzip -l "$zip_path" | tail -1 | awk '{print $2}') files"
listing=$(unzip -l "$zip_path")
for f in .htaccess _astro/.htaccess contact.php; do
  if grep -Eq "[[:space:]]${f//./\\.}\$" <<<"$listing"; then echo "  $f included"; else echo "  WARNING: $f missing"; exit 1; fi
done
