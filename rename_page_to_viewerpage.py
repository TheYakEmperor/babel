#!/usr/bin/env python3
"""Rename work.page to work.viewerPage to avoid confusion with data.pages array."""

import os
import re
from pathlib import Path

TEXTS_DIR = Path("/Users/yakking/Downloads/Web-design/Babel/texts")

# Patterns to replace in index.html files
replacements = [
    # In buildWorksHtml
    ('work.page !== undefined && !work.content', 'work.viewerPage !== undefined && !work.content'),
    ('goToViewerPage(${work.page - 1})', 'goToViewerPage(${work.viewerPage - 1})'),
    
    # In renderWork - data-viewer-page attribute
    ('work.page !== undefined ? ` data-viewer-page="${work.page - 1}"', 
     'work.viewerPage !== undefined ? ` data-viewer-page="${work.viewerPage - 1}"'),
    
    # In renderWork - page-only check
    ('} else if (work.page !== undefined) {',
     '} else if (work.viewerPage !== undefined) {'),
    
    # In buildWorkPageMap
    ('if (work.page !== undefined) {',
     'if (work.viewerPage !== undefined) {'),
    ('window.workPageMap[elemId] = work.page - 1;',
     'window.workPageMap[elemId] = work.viewerPage - 1;'),
]

count = 0
for html_file in TEXTS_DIR.rglob("index.html"):
    content = html_file.read_text(encoding='utf-8')
    modified = False
    
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            modified = True
    
    if modified:
        html_file.write_text(content, encoding='utf-8')
        count += 1
        print(f"Updated: {html_file}")

print(f"\nTotal updated: {count} files")

# Also update any data.json files that use "page" in works
print("\n--- Updating data.json files ---")
import json
for json_file in TEXTS_DIR.rglob("data.json"):
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        json_modified = [False]
        
        def update_works(works, flag):
            for work in works:
                if 'page' in work:
                    work['viewerPage'] = work.pop('page')
                    flag[0] = True
                if 'subworks' in work:
                    update_works(work['subworks'], flag)
        
        for page in data.get('pages', []):
            if 'works' in page:
                update_works(page['works'], json_modified)
        
        if json_modified[0]:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Updated: {json_file}")
    except Exception as e:
        print(f"Error with {json_file}: {e}")

print("\nDone!")
