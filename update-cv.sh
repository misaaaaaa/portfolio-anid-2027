#!/usr/bin/env bash
# ============================================================
# update-cv.sh — Regenera las páginas de CV condensado desde
# https://misaa.cc/cv.md (sin docencia, residencias ni prensa).
# Requiere pandoc y playwright (igual que export-pdf.sh).
# ============================================================
set -e
PY=/Library/Frameworks/Python.framework/Versions/3.12/bin/python3
TMP=$(mktemp -d)
curl -sfL https://misaa.cc/cv.md -o "$TMP/cv.md"
JSON=$("$PY" tools/cvgen.py "$TMP/cv.md" . 83.8mm)
"$PY" tools/cvpack.py "$JSON" content.md
echo "✓ CV actualizado en content.md. Corre ./export-pdf.sh para regenerar el PDF."
