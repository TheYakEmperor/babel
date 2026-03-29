#!/usr/bin/env python3
"""Update applyZoom to use mainContainer instead of containers"""
import os

old_code = '''        function applyZoom() {
            mainImage.style.transform = `scale(${zoomLevel})`;
            mainImage2.style.transform = `scale(${zoomLevel})`;
            
            container1.classList.toggle('zoomed', zoomLevel > 1);
            container2.classList.toggle('zoomed', zoomLevel > 1);
            
            updateZoomDisplay();
        }'''

new_code = '''        function applyZoom() {
            mainImage.style.transform = `scale(${zoomLevel})`;
            mainImage2.style.transform = `scale(${zoomLevel})`;
            
            mainContainer.classList.toggle('zoomed', zoomLevel > 1);
            
            updateZoomDisplay();
        }'''

texts_dir = '/Users/yakking/Downloads/Web-design/Babel/texts'
count = 0

for root, dirs, files in os.walk(texts_dir):
    if 'index.html' in files:
        filepath = os.path.join(root, 'index.html')
        if 'moony' in filepath:
            continue  # Already updated
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if old_code in content:
            content = content.replace(old_code, new_code)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {filepath}")
            count += 1

print(f"\nUpdated {count} files")
