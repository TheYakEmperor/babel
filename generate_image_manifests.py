#!/usr/bin/env python3
"""
Generate images.json manifest files for each text directory.
This allows page-viewer.js to know which images exist after local files are deleted.
"""

import os
import json
from pathlib import Path
from natsort import natsorted

BASE_DIR = Path(__file__).parent
TEXTS_DIR = BASE_DIR / 'texts'

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}

def generate_manifests():
    """Generate images.json for each text directory with images"""
    count = 0
    
    for images_dir in TEXTS_DIR.rglob('images'):
        if not images_dir.is_dir():
            continue
        
        text_dir = images_dir.parent
        
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
        
        # Create manifest
        manifest = {
            'images': [
                {
                    'url': f'images/{name}',
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
