#!/usr/bin/env python3
"""
Update all image references to point to Backblaze B2.
Changes relative paths like 'images/1.jpg' to absolute B2 URLs.
"""

import os
import re
import json
from pathlib import Path

# Configuration
B2_BASE_URL = 'https://babel-images.s3.us-east-005.backblazeb2.com'
BASE_DIR = Path(__file__).parent
TEXTS_DIR = BASE_DIR / 'texts'

# Image extensions
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp', '.gif')

def update_data_json_files():
    """Update image references in data.json files"""
    updated_files = 0
    
    for data_file in TEXTS_DIR.rglob('data.json'):
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original = content
            
            # Get the relative path from Babel root to this text's directory
            text_dir = data_file.parent
            rel_path = text_dir.relative_to(BASE_DIR)
            
            # Update "image": "images/..." to full B2 URL
            def replace_image_ref(match):
                img_path = match.group(1)
                # If it's already an absolute URL, skip
                if img_path.startswith('http'):
                    return match.group(0)
                # Build full B2 URL
                full_path = f'{B2_BASE_URL}/{rel_path}/{img_path}'
                return f'"image": "{full_path}"'
            
            content = re.sub(r'"image":\s*"(images/[^"]+)"', replace_image_ref, content)
            
            if content != original:
                with open(data_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                updated_files += 1
                print(f'Updated: {data_file}')
        
        except Exception as e:
            print(f'Error processing {data_file}: {e}')
    
    return updated_files

def update_index_html_files():
    """Update image src in index.html files within texts/"""
    updated_files = 0
    
    for html_file in TEXTS_DIR.rglob('index.html'):
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original = content
            
            # Get the relative path from Babel root to this text's directory
            text_dir = html_file.parent
            rel_path = text_dir.relative_to(BASE_DIR)
            
            # Update src="images/..." to full B2 URL
            def replace_src(match):
                attr = match.group(1)  # src or href
                img_path = match.group(2)
                # If it's already an absolute URL, skip
                if img_path.startswith('http') or img_path.startswith('//'):
                    return match.group(0)
                # Build full B2 URL
                full_path = f'{B2_BASE_URL}/{rel_path}/{img_path}'
                return f'{attr}="{full_path}"'
            
            # Match src="images/..." or href="images/..."
            content = re.sub(r'(src|href)="(images/[^"]+)"', replace_src, content)
            
            if content != original:
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                updated_files += 1
                print(f'Updated: {html_file}')
        
        except Exception as e:
            print(f'Error processing {html_file}: {e}')
    
    return updated_files

def update_page_viewer():
    """Update page-viewer.js to handle B2 URLs"""
    # The page viewer already handles full URLs, but let's check data.json references
    pass

def main():
    print('Updating image references to Backblaze B2...\n')
    
    print('=== Updating data.json files ===')
    json_count = update_data_json_files()
    
    print('\n=== Updating index.html files ===')
    html_count = update_index_html_files()
    
    print(f'\n=== DONE ===')
    print(f'Updated {json_count} data.json files')
    print(f'Updated {html_count} index.html files')
    print(f'\nYou can now delete the local images/ folders in texts/ to save space.')
    print(f'Run: find texts/ -type d -name "images" -exec rm -rf {{}} +')

if __name__ == '__main__':
    main()
