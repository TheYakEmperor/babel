#!/usr/bin/env python3
"""Download images from Cambridge University Library IIIF manifest"""

import json
import os
import requests
import time
from pathlib import Path

MANIFEST_URL = "https://cudl.lib.cam.ac.uk/iiif/PR-SSS-00010-00006"
OUTPUT_DIR = Path("/Users/yakking/Downloads/Web-design/Babel/texts/00/00/cambridge-sss-10-6/images")
TARGET_WIDTH = 1024  # Same as British Library download

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Fetch manifest
print("Fetching manifest...")
resp = requests.get(MANIFEST_URL)
manifest = resp.json()

canvases = manifest['sequences'][0]['canvases']
print(f"Found {len(canvases)} pages")

for i, canvas in enumerate(canvases):
    label = canvas.get('label', str(i + 1))
    # Sanitize label for filename
    safe_label = label.replace('/', '-').replace('\\', '-').replace(' ', '_')
    filename = f"{i+1:03d}_{safe_label}.jpg"
    filepath = OUTPUT_DIR / filename
    
    if filepath.exists():
        print(f"  [{i+1}/{len(canvases)}] Already exists: {filename}")
        continue
    
    # Get IIIF image URL
    image_info = canvas['images'][0]['resource']
    base_url = image_info['service']['@id']
    
    # Try different sizes
    for size in [TARGET_WIDTH, 800, 'full']:
        if size == 'full':
            image_url = f"{base_url}/full/full/0/default.jpg"
        else:
            image_url = f"{base_url}/full/{size},/0/default.jpg"
        
        try:
            img_resp = requests.get(image_url, timeout=30)
            if img_resp.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(img_resp.content)
                print(f"  [{i+1}/{len(canvases)}] Downloaded: {filename} ({len(img_resp.content)//1024}KB)")
                break
            else:
                print(f"  [{i+1}/{len(canvases)}] {size}px failed ({img_resp.status_code}), trying smaller...")
        except Exception as e:
            print(f"  [{i+1}/{len(canvases)}] Error: {e}")
            continue
    else:
        print(f"  [{i+1}/{len(canvases)}] FAILED: {filename}")
    
    time.sleep(0.2)  # Be polite

print("Done!")
