#!/usr/bin/env python3
"""Update all text pages to show text title in fullscreen mode header."""

import os
import re

texts_dir = '/Users/yakking/Downloads/Web-design/Babel/texts'

# Find all index.html files with toggleFullscreen
for root, dirs, files in os.walk(texts_dir):
    for f in files:
        if f == 'index.html':
            filepath = os.path.join(root, f)
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            
            if 'toggleFullscreen' not in content:
                continue
            
            # Skip if already has the title update
            if "pvTitle.textContent = isFullscreen" in content:
                print(f"Already updated: {filepath}")
                continue
            
            # Find the toggleFullscreen function and add title update
            # Pattern: after fullscreenToggle.textContent line, before resetZoom()
            old_pattern = r"(fullscreenToggle\.textContent = isFullscreen \? '.*?' : 'Fullscreen';)\s*\n(\s*)(resetZoom\(\);)"
            
            new_replacement = r"""\1
\2// Update title
\2const pvTitle = document.getElementById('pv-title');
\2const pageTitle = document.getElementById('page-title').textContent;
\2pvTitle.textContent = isFullscreen ? pageTitle : 'Page Viewer';
\2\3"""
            
            new_content = re.sub(old_pattern, new_replacement, content)
            
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                print(f"Updated: {filepath}")
            else:
                print(f"No match found: {filepath}")

print("Done!")
