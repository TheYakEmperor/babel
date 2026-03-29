#!/usr/bin/env python3
"""Download Rothschild Canticles images from Yale IIIF manifest."""

import json
import os
import re
import urllib.request
import ssl
import time

MANIFEST_URL = "https://collections.library.yale.edu/manifests/2002755"
OUTPUT_DIR = "rothschild canticles"

def main():
    # Create SSL context that doesn't verify (for compatibility)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    print("Fetching IIIF manifest...")
    req = urllib.request.Request(MANIFEST_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ctx) as response:
        manifest = json.loads(response.read().decode('utf-8'))
    
    # Extract canvases - these contain the image info in order
    canvases = manifest.get('items', [])
    print(f"Found {len(canvases)} pages")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    for i, canvas in enumerate(canvases, 1):
        # Get the label for the filename
        label = canvas.get('label', {}).get('none', [''])[0]
        # Clean up label for filename
        label_clean = re.sub(r'[^\w\s-]', '', label).strip()
        label_clean = re.sub(r'\s+', '_', label_clean)
        
        # Get the image URL from the canvas
        try:
            items = canvas.get('items', [])
            if items:
                annotation_page = items[0]
                annotations = annotation_page.get('items', [])
                if annotations:
                    body = annotations[0].get('body', {})
                    image_url = body.get('id', '')
                    
                    if image_url:
                        # Create filename with zero-padded index
                        filename = f"{i:03d}_{label_clean}.jpg"
                        filepath = os.path.join(OUTPUT_DIR, filename)
                        
                        if os.path.exists(filepath):
                            print(f"[{i}/{len(canvases)}] Skipping {filename} (exists)")
                            continue
                        
                        print(f"[{i}/{len(canvases)}] Downloading {filename}...")
                        
                        img_req = urllib.request.Request(image_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(img_req, context=ctx) as img_response:
                            with open(filepath, 'wb') as f:
                                f.write(img_response.read())
                        
                        # Small delay to be polite to the server
                        time.sleep(0.3)
        except Exception as e:
            print(f"Error downloading page {i}: {e}")
            continue
    
    print(f"\nDone! Downloaded images to '{OUTPUT_DIR}'")

if __name__ == "__main__":
    main()
