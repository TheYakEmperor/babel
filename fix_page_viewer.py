#!/usr/bin/env python3
"""
Update all text pages to support loading images from data.json pages array.
Images can have any filename and will be loaded in order from data.pages[].image.
Falls back to numeric detection (0.jpg, 1.jpg...) if no image property exists.
"""

import os
import re

TEXTS_DIR = '/Users/yakking/Downloads/Web-design/Babel/texts'

# Old function signature
OLD_INIT_SIG = 'function initPageViewer(pageCount) {'
NEW_INIT_SIG = 'function initPageViewer(pagesData) {'

# Old call pattern
OLD_CALL = re.compile(r'initPageViewer\(data\.pages\.length\)')
NEW_CALL = 'initPageViewer(data.pages)'

# Old detectImages function
OLD_DETECT = '''        // Try to detect available images
        async function detectImages() {
            const extensions = ['jpg', 'jpeg', 'png', 'webp', 'gif'];
            const found = [];
            
            for (let i = 0; i <= Math.max(pageCount, 20); i++) {
                for (const ext of extensions) {
                    try {
                        const url = `images/${i}.${ext}`;
                        const resp = await fetch(url, { method: 'HEAD' });
                        if (resp.ok) {
                            found.push(url);
                            break;
                        }
                    } catch (e) {}
                }
            }
            
            return found;
        }'''

NEW_DETECT = '''        // Get images from pagesData or detect by probing
        async function detectImages() {
            // First check if pagesData has image properties
            const fromData = pagesData
                .filter(p => p.image)
                .map(p => ({ url: p.image, label: p.label || '' }));
            
            if (fromData.length > 0) {
                return fromData;
            }
            
            // Fall back to numeric detection
            const extensions = ['jpg', 'jpeg', 'png', 'webp', 'gif'];
            const found = [];
            const pageCount = pagesData.length || 20;
            
            for (let i = 0; i <= Math.max(pageCount, 20); i++) {
                for (const ext of extensions) {
                    try {
                        const url = `images/${i}.${ext}`;
                        const resp = await fetch(url, { method: 'HEAD' });
                        if (resp.ok) {
                            found.push({ url: url, label: String(i) });
                            break;
                        }
                    } catch (e) {}
                }
            }
            
            return found;
        }'''

# Update getPageName to use label if available
OLD_GETPAGENAME = '''        // Extract filename without path and extension
        function getPageName(url) {
            const filename = url.split('/').pop();
            return filename.replace(/\.[^.]+$/, '');
        }'''

NEW_GETPAGENAME = '''        // Extract page name - uses label if item is an object, otherwise filename
        function getPageName(item) {
            if (typeof item === 'object' && item.label) {
                return item.label;
            }
            const url = typeof item === 'object' ? item.url : item;
            const filename = url.split('/').pop();
            return filename.replace(/\.[^.]+$/, '');
        }
        
        function getPageUrl(item) {
            return typeof item === 'object' ? item.url : item;
        }'''

# Update image references to use getPageUrl
OLD_SHOW_SINGLE = '''        function showSingle(index) {
            if (index < 0 || index >= images.length) return;
            currentIndex = index;
            resetZoom();
            
            mainContainer.classList.remove('dual-page');
            mainImage.classList.remove('solo');
            mainImage.src = images[index];
            mainImage.alt = getPageName(images[index]);'''

NEW_SHOW_SINGLE = '''        function showSingle(index) {
            if (index < 0 || index >= images.length) return;
            currentIndex = index;
            resetZoom();
            
            mainContainer.classList.remove('dual-page');
            mainImage.classList.remove('solo');
            mainImage.src = getPageUrl(images[index]);
            mainImage.alt = getPageName(images[index]);'''

def update_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    modified = False
    
    # Update function signature
    if OLD_INIT_SIG in content:
        content = content.replace(OLD_INIT_SIG, NEW_INIT_SIG)
        modified = True
    
    # Update function call
    if OLD_CALL.search(content):
        content = OLD_CALL.sub(NEW_CALL, content)
        modified = True
    
    # Update detectImages
    if OLD_DETECT in content:
        content = content.replace(OLD_DETECT, NEW_DETECT)
        modified = True
    
    # Update getPageName
    if OLD_GETPAGENAME in content:
        content = content.replace(OLD_GETPAGENAME, NEW_GETPAGENAME)
        modified = True
    
    # Update showSingle to use getPageUrl
    if OLD_SHOW_SINGLE in content:
        content = content.replace(OLD_SHOW_SINGLE, NEW_SHOW_SINGLE)
        modified = True
    
    # Also update other image.src references
    # mainImage.src = images[...] -> mainImage.src = getPageUrl(images[...])
    content = re.sub(
        r'(mainImage2?\.src\s*=\s*)images\[([^\]]+)\](?!\.)',
        r'\1getPageUrl(images[\2])',
        content
    )
    
    # thumb.src = url -> thumb.src = getPageUrl(url)
    # But only in the thumbnail creation context
    content = re.sub(
        r"(thumb\.src\s*=\s*)url;",
        r"\1getPageUrl(url);",
        content
    )
    
    if content != original:
        modified = True
    
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    count = 0
    for root, dirs, files in os.walk(TEXTS_DIR):
        for fname in files:
            if fname == 'index.html':
                filepath = os.path.join(root, fname)
                if update_file(filepath):
                    print(f"Updated: {filepath}")
                    count += 1
    
    print(f"\nUpdated {count} files")

if __name__ == '__main__':
    main()
