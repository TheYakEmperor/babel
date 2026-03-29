#!/usr/bin/env python3
"""Remove the 'F' key fullscreen shortcut from all text pages."""

import os

texts_dir = '/Users/yakking/Downloads/Web-design/Babel/texts'
count = 0

for root, dirs, files in os.walk(texts_dir):
    if 'index.html' in files:
        filepath = os.path.join(root, 'index.html')
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove the F key line
        old_line = "                if (e.key === 'f' || e.key === 'F') toggleFullscreen();\n"
        
        if old_line in content:
            content = content.replace(old_line, '')
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            count += 1
            print(f"Updated: {filepath}")

print(f"\nUpdated {count} files")
