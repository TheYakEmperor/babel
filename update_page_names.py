#!/usr/bin/env python3
"""Update all text pages to use filenames instead of 'Page N' for page display."""

import os
import re

def update_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Add getPageName function if not present
    if 'function getPageName' not in content:
        content = content.replace(
            "function getSpreads() {\n            if (images.length === 0) return [];",
            """// Extract filename without path and extension
        function getPageName(url) {
            const filename = url.split('/').pop();
            return filename.replace(/\\.[^.]+$/, '');
        }
        
        function getSpreads() {
            if (images.length === 0) return [];"""
        )
    
    # Update showSingle countDisplay
    content = re.sub(
        r"countDisplay\.textContent = `\$\{index \+ 1\} / \$\{images\.length\}`;",
        "countDisplay.textContent = getPageName(images[index]);",
        content
    )
    
    # Update showSingle alt text
    content = re.sub(
        r'mainImage\.alt = `Page \$\{index \+ 1\}`;',
        'mainImage.alt = getPageName(images[index]);',
        content
    )
    
    # Update showSpread single page alt and countDisplay
    content = re.sub(
        r'mainImage\.alt = `Page \$\{spread\[0\] \+ 1\}`;',
        'mainImage.alt = getPageName(images[spread[0]]);',
        content
    )
    content = re.sub(
        r"countDisplay\.textContent = `Page \$\{spread\[0\] \+ 1\} \(\$\{spreadIndex \+ 1\}/\$\{spreads\.length\}\)`;",
        "countDisplay.textContent = getPageName(images[spread[0]]);",
        content
    )
    
    # Update showSpread dual page alt texts
    content = re.sub(
        r'mainImage2\.alt = `Page \$\{spread\[1\] \+ 1\}`;',
        'mainImage2.alt = getPageName(images[spread[1]]);',
        content
    )
    
    # Update showSpread dual page countDisplay
    content = re.sub(
        r"countDisplay\.textContent = `Pages \$\{spread\[0\] \+ 1\}–\$\{spread\[1\] \+ 1\} \(\$\{spreadIndex \+ 1\}/\$\{spreads\.length\}\)`;",
        "countDisplay.textContent = `${getPageName(images[spread[0]])} – ${getPageName(images[spread[1]])}`;",
        content
    )
    
    # Update thumbnail alt text
    content = re.sub(
        r'thumb\.alt = `Page \$\{i \+ 1\}`;',
        'thumb.alt = getPageName(url);\n                thumb.title = getPageName(url);',
        content
    )
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    texts_dir = os.path.join(os.path.dirname(__file__), 'texts')
    updated = 0
    
    for root, dirs, files in os.walk(texts_dir):
        if 'index.html' in files:
            filepath = os.path.join(root, 'index.html')
            if update_file(filepath):
                print(f"Updated: {filepath}")
                updated += 1
    
    print(f"\nTotal files updated: {updated}")

if __name__ == '__main__':
    main()
