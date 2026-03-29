#!/usr/bin/env python3
"""Fix page indexing - treat work.page as 1-based (human readable), subtract 1 for 0-based array."""

import os
from pathlib import Path

TEXTS_DIR = Path("/Users/yakking/Downloads/Web-design/Babel/texts")

count = 0
for html_file in TEXTS_DIR.rglob("index.html"):
    content = html_file.read_text(encoding='utf-8')
    modified = False
    
    # Fix buildWorksHtml - change goToViewerPage(${work.page}) to goToViewerPage(${work.page - 1})
    old = 'goToViewerPage(${work.page})'
    new = 'goToViewerPage(${work.page - 1})'
    if old in content:
        content = content.replace(old, new)
        modified = True
    
    # Fix workPageMap assignment - store as 0-based index
    old2 = 'window.workPageMap[elemId] = work.page;'
    new2 = 'window.workPageMap[elemId] = work.page - 1;'
    if old2 in content:
        content = content.replace(old2, new2)
        modified = True
    
    # Fix data-viewer-page attribute if used for click handlers
    old3 = 'data-viewer-page="${work.page}"'
    new3 = 'data-viewer-page="${work.page - 1}"'
    if old3 in content:
        content = content.replace(old3, new3)
        modified = True
    
    if modified:
        html_file.write_text(content, encoding='utf-8')
        count += 1
        print(f"Updated: {html_file}")

print(f"\nTotal updated: {count} files")
