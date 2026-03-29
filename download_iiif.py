#!/usr/bin/env python3
"""
Download all images from a IIIF manifest.
"""

import json
import os
import requests
import time
from urllib.parse import urlparse

MANIFEST_URL = "https://bl.digirati.io/iiif/ark:/81055/vdc_100165157081.0x000001"
OUTPUT_DIR = "/Users/yakking/Downloads/Web-design/Babel/bl_manuscript"

# Use browser-like headers
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.bl.uk/',
}

def download_images():
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Fetch the manifest
    print(f"Fetching manifest from {MANIFEST_URL}...")
    response = requests.get(MANIFEST_URL, headers=HEADERS)
    response.raise_for_status()
    manifest = response.json()
    
    print(f"Manifest title: {manifest.get('label', {}).get('en', ['Unknown'])[0]}")
    
    # Get all canvases
    canvases = manifest.get('items', [])
    print(f"Found {len(canvases)} pages/canvases")
    
    for i, canvas in enumerate(canvases):
        canvas_label = canvas.get('label', {}).get('en', [f'page_{i+1}'])[0]
        # Clean up label for filename
        safe_label = canvas_label.replace(' ', '_').replace('[', '').replace(']', '').replace('/', '-')
        
        # Get the image URL from the canvas annotations
        items = canvas.get('items', [])
        for annotation_page in items:
            annotations = annotation_page.get('items', [])
            for annotation in annotations:
                if annotation.get('motivation') == 'painting':
                    body = annotation.get('body', {})
                    
                    # Get the IIIF Image Service to request images
                    services = body.get('service', [])
                    image_service = None
                    for svc in services:
                        if 'ImageService2' in svc.get('@type', '') or svc.get('type') == 'ImageService3':
                            image_service = svc.get('@id') or svc.get('id')
                            break
                    
                    if image_service:
                        # Request max 2000px width (more likely to be allowed)
                        image_url = f"{image_service}/full/2000,/0/default.jpg"
                    else:
                        # Fall back to the embedded URL
                        image_url = body.get('id', '')
                    
                    if image_url:
                        filename = f"{i+1:03d}_{safe_label}.jpg"
                        filepath = os.path.join(OUTPUT_DIR, filename)
                        
                        if os.path.exists(filepath):
                            print(f"[{i+1}/{len(canvases)}] Skipping {filename} (already exists)")
                            continue
                        
                        print(f"[{i+1}/{len(canvases)}] Downloading {filename}...")
                        
                        # Try different resolutions
                        resolutions = ['2000,', '1500,', '1024,', '800,']
                        success = False
                        
                        for res in resolutions:
                            try:
                                url = f"{image_service}/full/{res}/0/default.jpg"
                                img_response = requests.get(url, headers=HEADERS, timeout=60)
                                
                                if img_response.status_code == 200:
                                    with open(filepath, 'wb') as f:
                                        f.write(img_response.content)
                                    print(f"  Saved ({res}): {len(img_response.content) / 1024:.1f} KB")
                                    success = True
                                    break
                                elif img_response.status_code == 403:
                                    print(f"  Forbidden at {res}, trying smaller...")
                                else:
                                    print(f"  Status {img_response.status_code} at {res}")
                                    
                            except Exception as e:
                                print(f"  Error at {res}: {e}")
                        
                        if not success:
                            # Try the default URL from the manifest
                            try:
                                default_url = body.get('id', '')
                                if default_url:
                                    img_response = requests.get(default_url, headers=HEADERS, timeout=60)
                                    if img_response.status_code == 200:
                                        with open(filepath, 'wb') as f:
                                            f.write(img_response.content)
                                        print(f"  Saved (default): {len(img_response.content) / 1024:.1f} KB")
                                        success = True
                            except Exception as e:
                                print(f"  Default URL also failed: {e}")
                        
                        if not success:
                            print(f"  FAILED to download {filename}")
                        
                        # Be polite to the server
                        time.sleep(1)

    print(f"\nDone! Images saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    download_images()
