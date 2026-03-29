#!/usr/bin/env python3
"""Add 'as: [alias]' display for works that use aliases."""

import os
from pathlib import Path

TEXTS_DIR = Path("/Users/yakking/Downloads/Web-design/Babel/texts")

# Old buildWorksHtml pattern (both page-only and regular cases)
old_page_link = 'html = `<a href="#" onclick="event.preventDefault(); if(window.goToViewerPage) window.goToViewerPage(${work.viewerPage - 1});">${work.title}</a>`;'
new_page_link = '''html = `<a href="#" onclick="event.preventDefault(); if(window.goToViewerPage) window.goToViewerPage(${work.viewerPage - 1});">${work.title}</a>`;
            if (work.alias) html += ` <span class="work-alias">(as: ${work.alias})</span>`;'''

old_regular = 'html = `<a href="#${elemId}">${work.title}</a>`;'
new_regular = '''html = `<a href="#${elemId}">${work.title}</a>`;
            if (work.alias) html += ` <span class="work-alias">(as: ${work.alias})</span>`;'''

count = 0
for html_file in TEXTS_DIR.rglob("index.html"):
    content = html_file.read_text(encoding='utf-8')
    modified = False
    
    # Check if already has alias support
    if 'work.alias' in content:
        continue
    
    if old_page_link in content:
        content = content.replace(old_page_link, new_page_link)
        modified = True
    
    if old_regular in content:
        content = content.replace(old_regular, new_regular)
        modified = True
    
    if modified:
        html_file.write_text(content, encoding='utf-8')
        count += 1
        print(f"Updated: {html_file}")

print(f"\nTotal updated: {count} files")
