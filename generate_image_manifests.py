#!/usr/bin/env python3
"""
Generate images.json manifest files for each text directory.
This allows page-viewer.js to know which images exist after local files are deleted.
Also handles texts with blank pages (no actual images) defined in data.json.
"""

import os
import json
from pathlib import Path
from natsort import natsorted
from urllib.parse import quote

BASE_DIR = Path(__file__).parent
TEXTS_DIR = BASE_DIR / 'texts'

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}

def generate_manifests():
    """Generate images.json for each text directory with images or blank pages"""
    count = 0
    processed_dirs = set()
    
    # First pass: texts with actual image files
    for images_dir in TEXTS_DIR.rglob('images'):
        if not images_dir.is_dir():
            continue
        
        text_dir = images_dir.parent
        processed_dirs.add(text_dir)
        
        # Get all image files
        image_files = []
        for f in images_dir.iterdir():
            if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS:
                image_files.append(f.name)
        
        if not image_files:
            continue
        
        # Sort naturally (1, 2, 10 not 1, 10, 2)
        try:
            image_files = natsorted(image_files)
        except:
            image_files.sort()
        
        # Create manifest - URL-encode filenames for special characters like #
        manifest = {
            'images': [
                {
                    'url': f'images/{quote(name, safe="")}',
                    'label': Path(name).stem.replace('_', ' ')
                }
                for name in image_files
            ]
        }
        
        manifest_path = text_dir / 'images.json'
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        
        count += 1
        print(f'Created: {manifest_path} ({len(image_files)} images)')
    
    # Second pass: texts with blank pages in data.json but no images/ folder
    for data_json in TEXTS_DIR.rglob('data.json'):
        text_dir = data_json.parent
        
        # Skip if already processed or already has images.json
        if text_dir in processed_dirs:
            continue
        manifest_path = text_dir / 'images.json'
        if manifest_path.exists():
            continue
        
        # Load data.json and check for pages with isBlank
        try:
            with open(data_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            continue
        
        pages = data.get('pages', [])
        if not pages:
            continue
        
        # Check if any pages have isBlank or have labels/ids we should preserve
        has_blank_pages = any(p.get('isBlank') for p in pages)
        if not has_blank_pages:
            continue
        
        # Generate manifest from data.json pages
        images = []
        for page in pages:
            # Skip the first entry if it's just a works container (no id/label)
            if not page.get('label') and not page.get('id') and page.get('works'):
                continue
            
            if page.get('isBlank'):
                images.append({
                    'label': page.get('label', page.get('id', '')),
                    'isBlank': True
                })
            else:
                label = page.get('label', page.get('id', ''))
                if label:
                    images.append({
                        'url': f'images/{label}.jpg',
                        'label': label
                    })
        
        if images:
            manifest = {'images': images}
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2)
            
            blank_count = sum(1 for img in images if img.get('isBlank'))
            count += 1
            print(f'Created: {manifest_path} ({len(images)} pages, {blank_count} blank)')
    
    return count

if __name__ == '__main__':
    print('Generating image manifests...\n')
    
    try:
        from natsort import natsorted
    except ImportError:
        print('Installing natsort for natural sorting...')
        import subprocess
        subprocess.run(['pip3', 'install', 'natsort', '--quiet'])
        from natsort import natsorted
    
    count = generate_manifests()
    print(f'\nDone! Created {count} manifest files.')
