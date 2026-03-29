#!/usr/bin/env python3
"""
Update page viewer to support dual-page view mode.
"""

import os
import re
import glob

# New HTML for page viewer with dual-page support
NEW_PAGE_VIEWER_HTML = '''        <!-- Page Image Viewer (populated by JS if images exist) -->
        <div class="page-viewer" id="page-viewer" style="display: none;">
            <div class="page-viewer-header">
                <h3>Page Images</h3>
                <div class="page-viewer-controls">
                    <button class="pv-view-toggle" id="pv-dual-toggle" title="Toggle dual-page view">Dual</button>
                    <button class="page-viewer-btn" id="pv-prev" disabled>◀ Prev</button>
                    <span class="page-viewer-count" id="pv-count">1 / 1</span>
                    <button class="page-viewer-btn" id="pv-next">Next ▶</button>
                </div>
            </div>
            <div class="page-viewer-main" id="pv-main">
                <img class="page-viewer-image" id="pv-image" src="" alt="Page image">
                <img class="page-viewer-image" id="pv-image-2" src="" alt="Page image" style="display: none;">
            </div>
            <div class="page-viewer-thumbnails" id="pv-thumbnails"></div>
        </div>'''

# New JavaScript for page viewer with dual-page support
NEW_PAGE_VIEWER_JS = '''    // Page viewer initialization
    function initPageViewer(pageCount) {
        const viewer = document.getElementById('page-viewer');
        const mainContainer = document.getElementById('pv-main');
        const mainImage = document.getElementById('pv-image');
        const mainImage2 = document.getElementById('pv-image-2');
        const thumbContainer = document.getElementById('pv-thumbnails');
        const countDisplay = document.getElementById('pv-count');
        const prevBtn = document.getElementById('pv-prev');
        const nextBtn = document.getElementById('pv-next');
        const dualToggle = document.getElementById('pv-dual-toggle');
        
        let images = [];
        let currentIndex = 0;  // In single mode: page index. In dual mode: spread index
        let isDualMode = false;
        
        // Try to detect available images by probing for common formats
        async function detectImages() {
            const extensions = ['jpg', 'jpeg', 'png', 'webp', 'gif'];
            const found = [];
            
            // Try numbered images (0.jpg, 1.jpg, 2.jpg, etc.)
            for (let i = 0; i <= Math.max(pageCount, 20); i++) {
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
        
        // Get spreads for dual-page mode
        // Page 1 is solo (title page), then 2-3, 4-5, etc.
        function getSpreads() {
            if (images.length === 0) return [];
            const spreads = [];
            // First spread is just page 1 (title page)
            spreads.push([0]);
            // Subsequent spreads are pairs: 2-3, 4-5, etc.
            for (let i = 1; i < images.length; i += 2) {
                if (i + 1 < images.length) {
                    spreads.push([i, i + 1]);
                } else {
                    spreads.push([i]); // Last page alone if odd
                }
            }
            return spreads;
        }
        
        function getTotalSpreads() {
            return getSpreads().length;
        }
        
        function showSingle(index) {
            if (index < 0 || index >= images.length) return;
            currentIndex = index;
            
            mainContainer.classList.remove('dual-page');
            mainImage.classList.remove('solo');
            mainImage.src = images[index];
            mainImage.alt = `Page ${index + 1}`;
            mainImage.style.display = '';
            mainImage2.style.display = 'none';
            
            countDisplay.textContent = `${index + 1} / ${images.length}`;
            prevBtn.disabled = index === 0;
            nextBtn.disabled = index === images.length - 1;
            
            // Update thumbnail active state
            thumbContainer.querySelectorAll('.page-viewer-thumb').forEach((thumb, i) => {
                thumb.classList.toggle('active', i === index);
                thumb.classList.remove('spread-start', 'spread-end');
            });
        }
        
        function showSpread(spreadIndex) {
            const spreads = getSpreads();
            if (spreadIndex < 0 || spreadIndex >= spreads.length) return;
            currentIndex = spreadIndex;
            
            const spread = spreads[spreadIndex];
            mainContainer.classList.add('dual-page');
            
            if (spread.length === 1) {
                // Solo page (title or last odd page)
                mainImage.src = images[spread[0]];
                mainImage.alt = `Page ${spread[0] + 1}`;
                mainImage.classList.add('solo');
                mainImage.style.display = '';
                mainImage2.style.display = 'none';
                countDisplay.textContent = `Page ${spread[0] + 1} (${spreadIndex + 1}/${spreads.length})`;
            } else {
                // Two pages side by side
                mainImage.src = images[spread[0]];
                mainImage.alt = `Page ${spread[0] + 1}`;
                mainImage.classList.remove('solo');
                mainImage.style.display = '';
                
                mainImage2.src = images[spread[1]];
                mainImage2.alt = `Page ${spread[1] + 1}`;
                mainImage2.style.display = '';
                
                countDisplay.textContent = `Pages ${spread[0] + 1}–${spread[1] + 1} (${spreadIndex + 1}/${spreads.length})`;
            }
            
            prevBtn.disabled = spreadIndex === 0;
            nextBtn.disabled = spreadIndex === spreads.length - 1;
            
            // Update thumbnail active state for spread
            thumbContainer.querySelectorAll('.page-viewer-thumb').forEach((thumb, i) => {
                const isInSpread = spread.includes(i);
                thumb.classList.toggle('active', isInSpread);
                thumb.classList.remove('spread-start', 'spread-end');
            });
        }
        
        function showImage(index) {
            if (isDualMode) {
                showSpread(index);
            } else {
                showSingle(index);
            }
        }
        
        function navigate(delta) {
            showImage(currentIndex + delta);
        }
        
        function toggleDualMode() {
            isDualMode = !isDualMode;
            dualToggle.classList.toggle('active', isDualMode);
            dualToggle.textContent = isDualMode ? 'Single' : 'Dual';
            
            if (isDualMode) {
                // Convert single page index to spread index
                // Find which spread contains current page
                const spreads = getSpreads();
                let spreadIdx = 0;
                for (let i = 0; i < spreads.length; i++) {
                    if (spreads[i].includes(currentIndex)) {
                        spreadIdx = i;
                        break;
                    }
                }
                showSpread(spreadIdx);
            } else {
                // Convert spread index to first page of that spread
                const spreads = getSpreads();
                const pageIdx = spreads[currentIndex] ? spreads[currentIndex][0] : 0;
                showSingle(pageIdx);
            }
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
                thumb.addEventListener('click', () => {
                    if (isDualMode) {
                        // Find spread containing this page
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
            });
            
            // Set up controls
            prevBtn.addEventListener('click', () => navigate(-1));
            nextBtn.addEventListener('click', () => navigate(1));
            dualToggle.addEventListener('click', toggleDualMode);
            mainImage.addEventListener('click', () => createLightbox(mainImage.src));
            mainImage2.addEventListener('click', () => createLightbox(mainImage2.src));
            
            // Keyboard navigation
            document.addEventListener('keydown', (e) => {
                if (e.key === 'ArrowLeft') navigate(-1);
                if (e.key === 'ArrowRight') navigate(1);
            });
            
            // Show first image
            showImage(0);
        });
    }
    </script>
</body>
</html>'''

def update_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Skip if already has dual toggle
    if 'pv-dual-toggle' in content:
        print(f"  Skipping (already updated): {filepath}")
        return False
    
    # Skip if no page viewer
    if 'page-viewer' not in content:
        print(f"  Skipping (no page viewer): {filepath}")
        return False
    
    # Replace HTML block
    html_pattern = r'<!-- Page Image Viewer \(populated by JS if images exist\) -->.*?<div class="page-viewer-thumbnails" id="pv-thumbnails"></div>\s*</div>'
    content = re.sub(html_pattern, NEW_PAGE_VIEWER_HTML, content, flags=re.DOTALL)
    
    # Replace JS function
    js_pattern = r'    // Page viewer initialization\s*function initPageViewer.*?</script>\s*</body>\s*</html>'
    content = re.sub(js_pattern, NEW_PAGE_VIEWER_JS, content, flags=re.DOTALL)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  Updated: {filepath}")
    return True


def main():
    print("Updating page viewers for dual-page support...")
    updated = 0
    for filepath in glob.glob("texts/**/index.html", recursive=True):
        if update_file(filepath):
            updated += 1
    print(f"\nDone! Updated: {updated}")


if __name__ == "__main__":
    main()
