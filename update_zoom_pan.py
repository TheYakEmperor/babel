#!/usr/bin/env python3
"""
Update page viewer to use pan/zoom instead of lightbox.
"""

import os
import re
import glob

# New HTML for page viewer with zoom controls
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
                <div class="page-viewer-image-container" id="pv-container-1">
                    <img class="page-viewer-image" id="pv-image" src="" alt="Page image">
                </div>
                <div class="page-viewer-image-container" id="pv-container-2" style="display: none;">
                    <img class="page-viewer-image" id="pv-image-2" src="" alt="Page image">
                </div>
                <div class="page-viewer-zoom-controls">
                    <button class="page-viewer-zoom-btn" id="pv-zoom-out" title="Zoom out">−</button>
                    <span class="page-viewer-zoom-level" id="pv-zoom-level">100%</span>
                    <button class="page-viewer-zoom-btn" id="pv-zoom-in" title="Zoom in">+</button>
                    <button class="page-viewer-zoom-reset" id="pv-zoom-reset">Reset</button>
                </div>
            </div>
            <div class="page-viewer-thumbnails" id="pv-thumbnails"></div>
        </div>'''

NEW_PAGE_VIEWER_JS = '''    // Page viewer initialization
    function initPageViewer(pageCount) {
        const viewer = document.getElementById('page-viewer');
        const mainContainer = document.getElementById('pv-main');
        const container1 = document.getElementById('pv-container-1');
        const container2 = document.getElementById('pv-container-2');
        const mainImage = document.getElementById('pv-image');
        const mainImage2 = document.getElementById('pv-image-2');
        const thumbContainer = document.getElementById('pv-thumbnails');
        const countDisplay = document.getElementById('pv-count');
        const prevBtn = document.getElementById('pv-prev');
        const nextBtn = document.getElementById('pv-next');
        const dualToggle = document.getElementById('pv-dual-toggle');
        const zoomInBtn = document.getElementById('pv-zoom-in');
        const zoomOutBtn = document.getElementById('pv-zoom-out');
        const zoomResetBtn = document.getElementById('pv-zoom-reset');
        const zoomLevelDisplay = document.getElementById('pv-zoom-level');
        
        let images = [];
        let currentIndex = 0;
        let isDualMode = false;
        
        // Zoom and pan state
        let zoomLevel = 1;
        const minZoom = 1;
        const maxZoom = 5;
        const zoomStep = 0.25;
        
        // Pan state for each container
        const panState = {
            1: { x: 0, y: 0, isDragging: false, startX: 0, startY: 0, scrollLeft: 0, scrollTop: 0 },
            2: { x: 0, y: 0, isDragging: false, startX: 0, startY: 0, scrollLeft: 0, scrollTop: 0 }
        };
        
        function updateZoomDisplay() {
            zoomLevelDisplay.textContent = Math.round(zoomLevel * 100) + '%';
        }
        
        function applyZoom() {
            mainImage.style.transform = `scale(${zoomLevel})`;
            mainImage2.style.transform = `scale(${zoomLevel})`;
            
            container1.classList.toggle('zoomed', zoomLevel > 1);
            container2.classList.toggle('zoomed', zoomLevel > 1);
            
            updateZoomDisplay();
        }
        
        function zoomIn() {
            zoomLevel = Math.min(maxZoom, zoomLevel + zoomStep);
            applyZoom();
        }
        
        function zoomOut() {
            zoomLevel = Math.max(minZoom, zoomLevel - zoomStep);
            if (zoomLevel === 1) resetPan();
            applyZoom();
        }
        
        function resetZoom() {
            zoomLevel = 1;
            resetPan();
            applyZoom();
        }
        
        function resetPan() {
            panState[1] = { x: 0, y: 0, isDragging: false, startX: 0, startY: 0, scrollLeft: 0, scrollTop: 0 };
            panState[2] = { x: 0, y: 0, isDragging: false, startX: 0, startY: 0, scrollLeft: 0, scrollTop: 0 };
            mainImage.style.transformOrigin = 'center center';
            mainImage2.style.transformOrigin = 'center center';
        }
        
        function setupPanHandlers(container, image, stateKey) {
            const state = panState[stateKey];
            
            container.addEventListener('mousedown', (e) => {
                if (zoomLevel <= 1) return;
                e.preventDefault();
                state.isDragging = true;
                state.startX = e.clientX;
                state.startY = e.clientY;
                container.classList.add('dragging');
            });
            
            container.addEventListener('mousemove', (e) => {
                if (!state.isDragging || zoomLevel <= 1) return;
                e.preventDefault();
                
                const deltaX = e.clientX - state.startX;
                const deltaY = e.clientY - state.startY;
                
                state.x += deltaX;
                state.y += deltaY;
                
                // Limit pan range based on zoom level
                const maxPan = (zoomLevel - 1) * 150;
                state.x = Math.max(-maxPan, Math.min(maxPan, state.x));
                state.y = Math.max(-maxPan, Math.min(maxPan, state.y));
                
                image.style.transform = `scale(${zoomLevel}) translate(${state.x / zoomLevel}px, ${state.y / zoomLevel}px)`;
                
                state.startX = e.clientX;
                state.startY = e.clientY;
            });
            
            container.addEventListener('mouseup', () => {
                state.isDragging = false;
                container.classList.remove('dragging');
            });
            
            container.addEventListener('mouseleave', () => {
                state.isDragging = false;
                container.classList.remove('dragging');
            });
            
            // Mouse wheel zoom
            container.addEventListener('wheel', (e) => {
                e.preventDefault();
                if (e.deltaY < 0) {
                    zoomIn();
                } else {
                    zoomOut();
                }
            }, { passive: false });
        }
        
        // Try to detect available images
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
        }
        
        function getSpreads() {
            if (images.length === 0) return [];
            const spreads = [];
            spreads.push([0]);
            for (let i = 1; i < images.length; i += 2) {
                if (i + 1 < images.length) {
                    spreads.push([i, i + 1]);
                } else {
                    spreads.push([i]);
                }
            }
            return spreads;
        }
        
        function showSingle(index) {
            if (index < 0 || index >= images.length) return;
            currentIndex = index;
            resetZoom();
            
            mainContainer.classList.remove('dual-page');
            mainImage.classList.remove('solo');
            mainImage.src = images[index];
            mainImage.alt = `Page ${index + 1}`;
            container1.style.display = '';
            container2.style.display = 'none';
            
            countDisplay.textContent = `${index + 1} / ${images.length}`;
            prevBtn.disabled = index === 0;
            nextBtn.disabled = index === images.length - 1;
            
            thumbContainer.querySelectorAll('.page-viewer-thumb').forEach((thumb, i) => {
                thumb.classList.toggle('active', i === index);
            });
        }
        
        function showSpread(spreadIndex) {
            const spreads = getSpreads();
            if (spreadIndex < 0 || spreadIndex >= spreads.length) return;
            currentIndex = spreadIndex;
            resetZoom();
            
            const spread = spreads[spreadIndex];
            mainContainer.classList.add('dual-page');
            
            if (spread.length === 1) {
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
                container1.style.display = '';
                
                mainImage2.src = images[spread[1]];
                mainImage2.alt = `Page ${spread[1] + 1}`;
                container2.style.display = '';
                
                countDisplay.textContent = `Pages ${spread[0] + 1}–${spread[1] + 1} (${spreadIndex + 1}/${spreads.length})`;
            }
            
            prevBtn.disabled = spreadIndex === 0;
            nextBtn.disabled = spreadIndex === spreads.length - 1;
            
            thumbContainer.querySelectorAll('.page-viewer-thumb').forEach((thumb, i) => {
                thumb.classList.toggle('active', spread.includes(i));
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
                const spreads = getSpreads();
                const pageIdx = spreads[currentIndex] ? spreads[currentIndex][0] : 0;
                showSingle(pageIdx);
            }
        }
        
        // Start detection
        detectImages().then(found => {
            if (found.length === 0) return;
            
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
            
            // Set up pan handlers for both containers
            setupPanHandlers(container1, mainImage, 1);
            setupPanHandlers(container2, mainImage2, 2);
            
            // Set up controls
            prevBtn.addEventListener('click', () => navigate(-1));
            nextBtn.addEventListener('click', () => navigate(1));
            dualToggle.addEventListener('click', toggleDualMode);
            zoomInBtn.addEventListener('click', zoomIn);
            zoomOutBtn.addEventListener('click', zoomOut);
            zoomResetBtn.addEventListener('click', resetZoom);
            
            // Keyboard navigation
            document.addEventListener('keydown', (e) => {
                if (e.key === 'ArrowLeft') navigate(-1);
                if (e.key === 'ArrowRight') navigate(1);
                if (e.key === '+' || e.key === '=') zoomIn();
                if (e.key === '-') zoomOut();
                if (e.key === '0') resetZoom();
            });
            
            showImage(0);
        });
    }
    </script>
</body>
</html>'''


def update_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Skip if already has zoom controls
    if 'pv-zoom-in' in content:
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
    print("Updating page viewers with pan/zoom controls...")
    updated = 0
    for filepath in glob.glob("texts/**/index.html", recursive=True):
        if update_file(filepath):
            updated += 1
    print(f"\nDone! Updated: {updated}")


if __name__ == "__main__":
    main()
