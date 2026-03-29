#!/usr/bin/env python3
"""
Move page viewer to below the metadata box on all text pages.
"""

import os
import re

TEXTS_DIR = "texts"

# The page viewer HTML block
PAGE_VIEWER_BLOCK = '''        <!-- Page Image Viewer (populated by JS if images exist) -->
        <div class="page-viewer" id="page-viewer" style="display: none;">
            <div class="page-viewer-header">
                <h3>Page Images</h3>
                <div class="page-viewer-controls">
                    <button class="page-viewer-btn" id="pv-prev" disabled>◀ Prev</button>
                    <span class="page-viewer-count" id="pv-count">1 / 1</span>
                    <button class="page-viewer-btn" id="pv-next">Next ▶</button>
                </div>
            </div>
            <div class="page-viewer-main">
                <img class="page-viewer-image" id="pv-image" src="" alt="Page image">
            </div>
            <div class="page-viewer-thumbnails" id="pv-thumbnails"></div>
        </div>'''

def move_page_viewer(filepath):
    """Move page viewer to after metadata div."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'page-viewer' not in content:
        print(f"  Skipping (no page viewer): {filepath}")
        return False
    
    # Remove existing page viewer block (it's before metadata)
    # Pattern: the comment and div block before metadata
    pattern = r'<!-- Page Image Viewer.*?</div>\s*</div>\s*</div>\s*\n\s*(?=<div class="metadata")'
    content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    # Now insert page viewer after metadata div, before the section
    old_pattern = '<div class="metadata" id="metadata"></div>\n\n        <section>'
    new_pattern = f'<div class="metadata" id="metadata"></div>\n\n{PAGE_VIEWER_BLOCK}\n\n        <section>'
    
    if old_pattern in content:
        content = content.replace(old_pattern, new_pattern)
    else:
        # Try with different whitespace
        pattern2 = r'(<div class="metadata" id="metadata"></div>\s*)(<section>)'
        replacement = r'\1\n' + PAGE_VIEWER_BLOCK + r'\n\n        \2'
        content = re.sub(pattern2, replacement, content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  Updated: {filepath}")
    return True


def main():
    print("Moving page viewer below metadata box...")
    
    updated = 0
    
    for root, dirs, files in os.walk(TEXTS_DIR):
        if 'index.html' in files:
            filepath = os.path.join(root, 'index.html')
            if move_page_viewer(filepath):
                updated += 1
    
    print(f"\nDone! Updated: {updated}")


if __name__ == "__main__":
    main()
