#!/usr/bin/env python3
"""
Fix page viewers - remove duplicates and ensure proper placement after metadata.
Uses regex to handle varying whitespace.
"""

import os
import re
import glob

PAGE_VIEWER_HTML = '''        <!-- Page Image Viewer (populated by JS if images exist) -->
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
        </div>

'''

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count page-viewer occurrences to see if it needs fixing
    count = content.count('id="page-viewer"')
    if count <= 1:
        print(f"  OK ({count} viewer): {filepath}")
        return False
    
    print(f"  Fixing ({count} viewers): {filepath}")
    
    # Remove ALL page viewer blocks using regex
    # This pattern matches the comment + entire page-viewer div
    pattern = r'\s*<!-- Page Image Viewer \(populated by JS if images exist\) -->\s*<div class="page-viewer" id="page-viewer"[^>]*>.*?</div>\s*</div>\s*</div>\s*</div>'
    content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    # Now add back a single page viewer after metadata div, before section
    # Find the metadata div and section
    insert_pattern = r'(<div class="metadata" id="metadata"></div>)\s*(<section>)'
    replacement = r'\1\n\n' + PAGE_VIEWER_HTML + r'        \2'
    content = re.sub(insert_pattern, replacement, content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def main():
    print("Fixing page viewers...")
    fixed = 0
    for filepath in glob.glob("texts/**/index.html", recursive=True):
        if fix_file(filepath):
            fixed += 1
    print(f"\nDone! Fixed: {fixed}")

if __name__ == "__main__":
    main()
