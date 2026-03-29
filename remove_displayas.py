#!/usr/bin/env python3
"""Remove unused displayAs feature from text pages."""

import os
from pathlib import Path

TEXTS_DIR = Path("/Users/yakking/Downloads/Web-design/Babel/texts")

# Remove the displayAs lines
old_line = '''            if (work.displayAs) html += ` <span class="work-alias">(as: ${work.displayAs})</span>`;'''

count = 0
for html_file in TEXTS_DIR.rglob("index.html"):
    content = html_file.read_text(encoding='utf-8')
    
    if old_line in content:
        content = content.replace(old_line + '\n', '')
        html_file.write_text(content, encoding='utf-8')
        count += 1
        print(f"Updated: {html_file}")

print(f"\nTotal updated: {count} files")
