#!/usr/bin/env python3
"""
Add page viewer functionality to all text index.html files.
The page viewer displays page images if an 'images' folder exists.
"""

import os
import re

TEXTS_DIR = "texts"

# HTML to insert for the page viewer
PAGE_VIEWER_HTML = '''
        <!-- Page Image Viewer (populated by JS if images exist) -->
        <div class="page-viewer" id="page-viewer" style="display: none;">
            <div class="page-viewer-header">
                <h3>Page Images</h3>
                <div class="page-viewer-controls">
                    <button class="page-viewer-btn" id="pv-prev" disabled>◀ Prev</button>
                    <span class="page-viewer-count" id="pv-count">1 / 1</span>
                    <button class="page-viewer-btn" id="pv-next">Next ▶</button>
                </div>
            </div>
            <div class="page-viewer-main">
                <img class="page-viewer-image" id="pv-image" src="" alt="Page image">
            </div>
            <div class="page-viewer-thumbnails" id="pv-thumbnails"></div>
        </div>
        
'''

# JavaScript for page viewer initialization
PAGE_VIEWER_JS = '''
            // Initialize page viewer if images exist
            initPageViewer(data.pages.length);
            
'''

PAGE_VIEWER_FUNCTION = '''
    // Page viewer initialization
    function initPageViewer(pageCount) {
        const viewer = document.getElementById('page-viewer');
        const mainImage = document.getElementById('pv-image');
        const thumbContainer = document.getElementById('pv-thumbnails');
        const countDisplay = document.getElementById('pv-count');
        const prevBtn = document.getElementById('pv-prev');
        const nextBtn = document.getElementById('pv-next');
        
        let images = [];
        let currentIndex = 0;
        
        // Try to detect available images by probing for common formats
        async function detectImages() {
            const extensions = ['jpg', 'jpeg', 'png', 'webp', 'gif'];
            const found = [];
            
            // Try numbered images (1.jpg, 2.jpg, etc.)
            for (let i = 1; i <= Math.max(pageCount, 20); i++) {
                for (const ext of extensions) {
                    try {
                        const url = `images/${i}.${ext}`;
                        const resp = await fetch(url, { method: 'HEAD' });
                        if (resp.ok) {
                            found.push(url);
                            break; // Found this page, move to next number
                        }
                    } catch (e) {
                        // Ignore fetch errors
                    }
                }
            }
            
            return found;
        }
        
        function showImage(index) {
            if (index < 0 || index >= images.length) return;
            currentIndex = index;
            mainImage.src = images[index];
            mainImage.alt = `Page ${index + 1}`;
            countDisplay.textContent = `${index + 1} / ${images.length}`;
            
            // Update button states
            prevBtn.disabled = index === 0;
            nextBtn.disabled = index === images.length - 1;
            
            // Update thumbnail active state
            thumbContainer.querySelectorAll('.page-viewer-thumb').forEach((thumb, i) => {
                thumb.classList.toggle('active', i === index);
            });
        }
        
        function createLightbox(src) {
            const lightbox = document.createElement('div');
            lightbox.className = 'page-viewer-lightbox';
            lightbox.innerHTML = `
                <img src="${src}" alt="Full size page">
                <button class="page-viewer-lightbox-close">×</button>
            `;
            lightbox.addEventListener('click', () => lightbox.remove());
            document.body.appendChild(lightbox);
        }
        
        // Start detection
        detectImages().then(found => {
            if (found.length === 0) {
                // No images found, keep viewer hidden
                return;
            }
            
            images = found;
            viewer.style.display = 'block';
            
            // Create thumbnails
            images.forEach((url, i) => {
                const thumb = document.createElement('img');
                thumb.className = 'page-viewer-thumb';
                thumb.src = url;
                thumb.alt = `Page ${i + 1}`;
                thumb.addEventListener('click', () => showImage(i));
                thumbContainer.appendChild(thumb);
            });
            
            // Set up controls
            prevBtn.addEventListener('click', () => showImage(currentIndex - 1));
            nextBtn.addEventListener('click', () => showImage(currentIndex + 1));
            mainImage.addEventListener('click', () => createLightbox(mainImage.src));
            
            // Keyboard navigation
            document.addEventListener('keydown', (e) => {
                if (e.key === 'ArrowLeft') showImage(currentIndex - 1);
                if (e.key === 'ArrowRight') showImage(currentIndex + 1);
            });
            
            // Show first image
            showImage(0);
        });
    }
'''

def update_text_page(filepath):
    """Update a text index.html with page viewer functionality."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Skip if already has page viewer
    if 'page-viewer' in content:
        print(f"  Skipping (already has page viewer): {filepath}")
        return False
    
    # Insert page viewer HTML before metadata div
    old_pattern = '<p class="language-status" id="language-status"></p>\n        \n        <div class="metadata"'
    new_pattern = '<p class="language-status" id="language-status"></p>\n' + PAGE_VIEWER_HTML + '<div class="metadata"'
    
    if old_pattern in content:
        content = content.replace(old_pattern, new_pattern)
    else:
        # Try alternate pattern
        old_pattern2 = '<p class="language-status" id="language-status"></p>\n\n        <div class="metadata"'
        if old_pattern2 in content:
            content = content.replace(old_pattern2, new_pattern)
        else:
            # More flexible pattern
            pattern = r'(<p class="language-status" id="language-status"></p>\s*)(<div class="metadata")'
            replacement = r'\1' + PAGE_VIEWER_HTML + r'\2'
            content = re.sub(pattern, replacement, content)
    
    # Insert call to initPageViewer after text-body is rendered
    old_js = "document.getElementById('text-body').innerHTML = bodyHtml;\n            \n            // Scroll to hash"
    new_js = "document.getElementById('text-body').innerHTML = bodyHtml;\n" + PAGE_VIEWER_JS + "            // Scroll to hash"
    
    if old_js in content:
        content = content.replace(old_js, new_js)
    else:
        # Try alternate pattern
        pattern = r"(document\.getElementById\('text-body'\)\.innerHTML = bodyHtml;\s*)(\n\s*// Scroll to hash)"
        replacement = r"\1" + PAGE_VIEWER_JS + r"\2"
        content = re.sub(pattern, replacement, content)
    
    # Insert page viewer function before closing </script>
    old_close = "    </script>\n</body>"
    new_close = PAGE_VIEWER_FUNCTION + "    </script>\n</body>"
    
    if old_close in content:
        content = content.replace(old_close, new_close)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  Updated: {filepath}")
    return True


def main():
    print("Adding page viewer to text pages...")
    
    updated = 0
    skipped = 0
    
    for root, dirs, files in os.walk(TEXTS_DIR):
        if 'index.html' in files:
            filepath = os.path.join(root, 'index.html')
            if update_text_page(filepath):
                updated += 1
            else:
                skipped += 1
    
    print(f"\nDone! Updated: {updated}, Skipped: {skipped}")


if __name__ == "__main__":
    main()
