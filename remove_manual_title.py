#!/usr/bin/env python3
"""Remove manual title update code from text pages - now handled automatically by text-reader.js"""

import os
import re

texts_dir = '/Users/yakking/Downloads/Web-design/Babel/texts'

# Find all index.html files
for root, dirs, files in os.walk(texts_dir):
    for f in files:
        if f == 'index.html':
            filepath = os.path.join(root, f)
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            
            if 'toggleFullscreen' not in content:
                continue
            
            # Remove the title update lines from toggleFullscreen
            # Pattern matches the 4 lines we added
            pattern = r"\n\s*// Update title\n\s*const pvTitle = document\.getElementById\('pv-title'\);\n\s*const pageTitle = document\.getElementById\('page-title'\)\.textContent;\n\s*pvTitle\.textContent = isFullscreen \? pageTitle : 'Page Viewer';"
            
            new_content = re.sub(pattern, '', content)
            
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                print(f"Cleaned: {filepath}")
            else:
                print(f"No manual code found: {filepath}")

print("Done!")
