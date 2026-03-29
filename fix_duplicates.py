#!/usr/bin/env python3
"""
Fix duplicated page viewers - keep only one, after metadata.
"""

import os
import glob

CORRECT_STRUCTURE = '''        <p class="language-status" id="language-status"></p>
        
        <div class="metadata" id="metadata"></div>

        <!-- Page Image Viewer (populated by JS if images exist) -->
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

        <section>'''

# Pattern to find and replace (the duplicated version)
BROKEN_PATTERN = '''        <p class="language-status" id="language-status"></p>
        
        <!-- Page Image Viewer (populated by JS if images exist) -->
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
        
        <div class="metadata" id="metadata"></div>

        <!-- Page Image Viewer (populated by JS if images exist) -->
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

        <section>'''

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if BROKEN_PATTERN in content:
        content = content.replace(BROKEN_PATTERN, CORRECT_STRUCTURE)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  Fixed: {filepath}")
        return True
    else:
        print(f"  OK: {filepath}")
        return False

def main():
    print("Fixing duplicated page viewers...")
    fixed = 0
    for filepath in glob.glob("texts/**/index.html", recursive=True):
        if fix_file(filepath):
            fixed += 1
    print(f"\nDone! Fixed: {fixed}")

if __name__ == "__main__":
    main()
