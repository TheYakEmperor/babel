#!/usr/bin/env python3
"""
Download pages from Münchener Digitalisierungszentrum (MDZ) via IIIF.
Book: Von den Jüden vnd jren Lügen - Luther, Martin (1543)
BSB ID: bsb11924293
Source: Coburg, Landesbibliothek -- Cas A 1657
"""

import os
import time
import urllib.request
import ssl

# Bypass SSL certificate verification (macOS issue)
ssl._create_default_https_context = ssl._create_unverified_context

# Configuration
BSB_ID = "bsb11924293"
TOTAL_PAGES = 286
OUTPUT_DIR = "texts/00/00/luther-juden-1543/images"

# IIIF URL template - request full size images
# Format: /full/full/0/default.jpg = full region, full size, no rotation
BASE_URL = f"https://api.digitale-sammlungen.de/iiif/image/v2/{BSB_ID}_{{page_id}}/full/full/0/default.jpg"

def download_page(page_num, output_path):
    """Download a single page from MDZ IIIF."""
    # MDZ uses 5-digit zero-padded page numbers
    page_id = f"{page_num:05d}"
    url = BASE_URL.format(page_id=page_id)
    
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        with urllib.request.urlopen(req, timeout=60) as response:
            data = response.read()
            
            with open(output_path, 'wb') as f:
                f.write(data)
            
            return len(data)
    except Exception as e:
        return f"Error: {e}"

def main():
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("=" * 60)
    print("MDZ IIIF Downloader")
    print("=" * 60)
    print(f"BSB ID: {BSB_ID}")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Pages: {TOTAL_PAGES}")
    print("=" * 60)
    
    # First, remove the Google Books placeholder images (small 9KB files)
    print("\nRemoving Google Books placeholder images...")
    removed = 0
    for filename in os.listdir(OUTPUT_DIR):
        filepath = os.path.join(OUTPUT_DIR, filename)
        if os.path.isfile(filepath) and os.path.getsize(filepath) < 15000:  # < 15KB
            os.remove(filepath)
            removed += 1
    print(f"Removed {removed} placeholder images")
    
    print("\nDownloading from MDZ...")
    success = 0
    failed = 0
    
    for page_num in range(1, TOTAL_PAGES + 1):
        output_path = os.path.join(OUTPUT_DIR, f"{page_num:04d}.jpg")
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 50000:
            print(f"  Page {page_num} already exists and is valid, skipping")
            success += 1
            continue
        
        result = download_page(page_num, output_path)
        
        if isinstance(result, int):
            print(f"  Page {page_num}: {result:,} bytes")
            success += 1
        else:
            print(f"  Page {page_num}: {result}")
            failed += 1
        
        # Be polite to the server
        time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print(f"Download complete!")
    print(f"Success: {success}")
    print(f"Failed: {failed}")
    print("=" * 60)

if __name__ == "__main__":
    main()
