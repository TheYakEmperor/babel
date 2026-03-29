#!/usr/bin/env python3
"""Update alias display to use displayAs - show title with '(as: displayAs)'."""

import os
from pathlib import Path

TEXTS_DIR = Path("/Users/yakking/Downloads/Web-design/Babel/texts")

# Replace work.alias with work.displayAs
old_alias1 = 'if (work.alias) html += ` <span class="work-alias">(as: ${work.alias})</span>`;'
new_alias1 = 'if (work.displayAs) html += ` <span class="work-alias">(as: ${work.displayAs})</span>`;'

count = 0
for html_file in TEXTS_DIR.rglob("index.html"):
    content = html_file.read_text(encoding='utf-8')
    modified = False
    
    if old_alias1 in content:
        content = content.replace(old_alias1, new_alias1)
        modified = True
    
    if modified:
        html_file.write_text(content, encoding='utf-8')
        count += 1
        print(f"Updated: {html_file}")

print(f"\nTotal updated: {count} files")
