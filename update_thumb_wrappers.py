#!/usr/bin/env python3
"""Update all text pages to use thumbnail wrappers with labels."""

import os
import re

def update_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Update thumbnail creation
    old_thumb_creation = '''            // Create thumbnails
            images.forEach((url, i) => {
                const thumb = document.createElement('img');
                thumb.className = 'page-viewer-thumb';
                thumb.src = url;
                thumb.alt = getPageName(url);
                thumb.title = getPageName(url);
                thumb.addEventListener('click', () => {
                    if (isDualMode) {
                        const spreads = getSpreads();
                        for (let s = 0; s < spreads.length; s++) {
                            if (spreads[s].includes(i)) {
                                showSpread(s);
                                break;
                            }
                        }
                    } else {
                        showSingle(i);
                    }
                });
                thumbContainer.appendChild(thumb);
            });'''
    
    new_thumb_creation = '''            // Create thumbnails
            images.forEach((url, i) => {
                const wrapper = document.createElement('div');
                wrapper.className = 'page-viewer-thumb-wrapper';
                
                const thumb = document.createElement('img');
                thumb.className = 'page-viewer-thumb';
                thumb.src = url;
                thumb.alt = getPageName(url);
                
                const label = document.createElement('span');
                label.className = 'page-viewer-thumb-label';
                label.textContent = getPageName(url);
                
                wrapper.appendChild(thumb);
                wrapper.appendChild(label);
                wrapper.addEventListener('click', () => {
                    if (isDualMode) {
                        const spreads = getSpreads();
                        for (let s = 0; s < spreads.length; s++) {
                            if (spreads[s].includes(i)) {
                                showSpread(s);
                                break;
                            }
                        }
                    } else {
                        showSingle(i);
                    }
                });
                thumbContainer.appendChild(wrapper);
            });'''
    
    content = content.replace(old_thumb_creation, new_thumb_creation)
    
    # Update active class toggles in showSingle
    content = re.sub(
        r"thumbContainer\.querySelectorAll\('\.page-viewer-thumb'\)\.forEach\(\(thumb, i\) => \{\s*\n\s*thumb\.classList\.toggle\('active', i === index\);",
        "thumbContainer.querySelectorAll('.page-viewer-thumb-wrapper').forEach((wrapper, i) => {\n                wrapper.classList.toggle('active', i === index);",
        content
    )
    
    # Update active class toggles in showSpread
    content = re.sub(
        r"thumbContainer\.querySelectorAll\('\.page-viewer-thumb'\)\.forEach\(\(thumb, i\) => \{\s*\n\s*thumb\.classList\.toggle\('active', spread\.includes\(i\)\);",
        "thumbContainer.querySelectorAll('.page-viewer-thumb-wrapper').forEach((wrapper, i) => {\n                wrapper.classList.toggle('active', spread.includes(i));",
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
