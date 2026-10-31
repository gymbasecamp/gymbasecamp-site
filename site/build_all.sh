#!/bin/sh
# GYM BASECAMP: data/brands.csv + sources -> dist/gb.js (loaded by WordPress via jsDelivr)
set -e
cd "$(dirname "$0")"
python3 -I csv2json.py data/brands.csv
python3 -I build.py
node --check out/_check.js
python3 -I compact_js.py
node --check ../dist/gb.js
