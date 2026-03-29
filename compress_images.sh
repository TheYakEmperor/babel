#!/bin/bash
# Lossless image compression script for Babel texts

cd /Users/yakking/Downloads/Web-design/Babel

echo "=== Lossless Image Compression ==="
echo "Processing all images in texts/00/00/*/images..."

# Count files
jpg_count=$(find texts/00/00 -type f -iname "*.jpg" 2>/dev/null | wc -l)
png_count=$(find texts/00/00 -type f -iname "*.png" 2>/dev/null | wc -l)

echo "Found $jpg_count JPG files and $png_count PNG files"
echo ""

# Get initial size
initial_size=$(du -sm texts/00/00/*/images 2>/dev/null | awk '{sum+=$1} END {print sum}')
echo "Initial size: ${initial_size} MB"
echo ""

# Compress JPEGs (lossless - strips metadata only)
echo "Compressing JPEGs (lossless)..."
find texts/00/00 -type f -iname "*.jpg" -print0 2>/dev/null | xargs -0 -P 4 jpegoptim --strip-all --preserve --preserve-perms -q 2>/dev/null

echo "JPEG compression complete!"
echo ""

# Compress PNGs (lossless)
echo "Compressing PNGs (lossless)..."
find texts/00/00 -type f -iname "*.png" 2>/dev/null | while read -r file; do
    optipng -o2 -quiet "$file" 2>/dev/null
done

echo "PNG compression complete!"
echo ""

# Get final size
final_size=$(du -sm texts/00/00/*/images 2>/dev/null | awk '{sum+=$1} END {print sum}')
saved=$((initial_size - final_size))

echo "=== Results ==="
echo "Initial size: ${initial_size} MB"
echo "Final size: ${final_size} MB"
echo "Space saved: ${saved} MB"
echo "Done!"
