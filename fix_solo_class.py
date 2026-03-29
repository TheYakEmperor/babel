#!/usr/bin/env python3
"""Add solo class to container for title page sizing"""
import os

old_code = '''            if (spread.length === 1) {
                mainImage.src = images[spread[0]];
                mainImage.alt = `Page ${spread[0] + 1}`;
                mainImage.classList.add('solo');
                container1.style.display = '';
                container2.style.display = 'none';
                countDisplay.textContent = `Page ${spread[0] + 1} (${spreadIndex + 1}/${spreads.length})`;
            } else {
                mainImage.src = images[spread[0]];
                mainImage.alt = `Page ${spread[0] + 1}`;
                mainImage.classList.remove('solo');
                container1.style.display = '';'''

new_code = '''            if (spread.length === 1) {
                mainImage.src = images[spread[0]];
                mainImage.alt = `Page ${spread[0] + 1}`;
                mainImage.classList.add('solo');
                container1.classList.add('solo');
                container1.style.display = '';
                container2.style.display = 'none';
                countDisplay.textContent = `Page ${spread[0] + 1} (${spreadIndex + 1}/${spreads.length})`;
            } else {
                mainImage.src = images[spread[0]];
                mainImage.alt = `Page ${spread[0] + 1}`;
                mainImage.classList.remove('solo');
                container1.classList.remove('solo');
                container1.style.display = '';'''

texts_dir = '/Users/yakking/Downloads/Web-design/Babel/texts'
count = 0

for root, dirs, files in os.walk(texts_dir):
    if 'index.html' in files:
        filepath = os.path.join(root, 'index.html')
        if 'moony' in filepath:
            continue
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if old_code in content:
            content = content.replace(old_code, new_code)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {filepath}")
            count += 1

print(f"\nUpdated {count} files")
