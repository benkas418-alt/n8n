#!/usr/bin/env bash
# Build the private site into web/dist: the dashboard files plus the Supabase layer.
# Run from any directory: football-intel/web/build.sh
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
static="$here/../src/footintel/api/static"
dist="$here/dist"
rm -rf "$dist"
mkdir -p "$dist"
cp "$static"/{index.html,app.js,style.css,value.html,value.js} "$here"/{site.js,site.css,config.js} "$dist"/
cp "$here/vercel.json" "$dist"/

SUPABASE_JS='<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.45.4/dist/umd/supabase.js"></script>'
for page in index.html:app.js value.html:value.js; do
  file="$dist/${page%%:*}"
  script="${page##*:}"
  grep -q "<script src=\"$script\"></script>" "$file"
  sed -i \
    -e "s|</head>|<meta name=\"robots\" content=\"noindex, nofollow\">\n<link rel=\"stylesheet\" href=\"site.css\">\n</head>|" \
    -e "s|<script src=\"$script\"></script>|$SUPABASE_JS\n<script src=\"config.js\"></script>\n<script src=\"site.js\"></script>\n<script src=\"$script\"></script>|" \
    "$file"
done
echo "Site built in $dist"
