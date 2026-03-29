#!/bin/bash
# Lossless image compression using jpegtran and optipng

cd /Users/yakking/Downloads/Web-design/Babel

echo "=== Lossless Image Compression ==="
echo "Before:"
du -sm texts/00/00/*/images 2>/dev/null | awk '{sum+=$1} END {print sum " MB"}'

echo ""
echo "Compressing JPEGs with jpegtran (lossless)..."
find texts/00/00 -type f -iname "*.jpg" | while read f; do
    jpegtran -copy none -optimize -outfile "${f}.tmp" "$f" 2>/dev/null && mv "${f}.tmp" "$f"
done
echo "JPEGs done!"

echo ""
echo "Compressing PNGs with optipng (lossless)..."
find texts/00/00 -type f -iname "*.png" | while read f; do
    optipng -o2 -quiet "$f" 2>/dev/null
done
echo "PNGs done!"

echo ""
echo "After:"
du -sm texts/00/00/*/images 2>/dev/null | awk '{sum+=$1} END {print sum " MB"}'
echo "=== Complete ==="
