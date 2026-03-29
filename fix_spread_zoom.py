#!/usr/bin/env python3
"""Complete rewrite of page viewer for spread-based zoom/pan"""
import os
import re

texts_dir = '/Users/yakking/Downloads/Web-design/Babel/texts'

# HTML changes - add spread wrapper
old_html = '''            <div class="page-viewer-main" id="pv-main">
                <div class="page-viewer-image-container" id="pv-container-1">
                    <img class="page-viewer-image" id="pv-image" src="" alt="Page image">
                </div>
                <div class="page-viewer-image-container" id="pv-container-2" style="display: none;">
                    <img class="page-viewer-image" id="pv-image-2" src="" alt="Page image">
                </div>'''

new_html = '''            <div class="page-viewer-main" id="pv-main">
                <div class="page-viewer-spread" id="pv-spread">
                    <div class="page-viewer-image-container" id="pv-container-1">
                        <img class="page-viewer-image" id="pv-image" src="" alt="Page image">
                    </div>
                    <div class="page-viewer-image-container" id="pv-container-2" style="display: none;">
                        <img class="page-viewer-image" id="pv-image-2" src="" alt="Page image">
                    </div>
                </div>'''

# JS changes - add spread element reference
old_js1 = '''        const mainContainer = document.getElementById('pv-main');
        const container1 = document.getElementById('pv-container-1');'''

new_js1 = '''        const mainContainer = document.getElementById('pv-main');
        const spread = document.getElementById('pv-spread');
        const container1 = document.getElementById('pv-container-1');'''

# JS changes - replace zoom/pan state
old_js2 = '''        // Zoom and pan state
        let zoomLevel = 1;
        const minZoom = 1;
        const maxZoom = 5;
        const zoomStep = 0.25;
        
        // Pan state for each container
        const panState = {
            1: { x: 0, y: 0, isDragging: false, startX: 0, startY: 0, scrollLeft: 0, scrollTop: 0 },
            2: { x: 0, y: 0, isDragging: false, startX: 0, startY: 0, scrollLeft: 0, scrollTop: 0 }
        };'''

new_js2 = '''        // Zoom and pan state
        let zoomLevel = 1;
        const minZoom = 1;
        const maxZoom = 5;
        const zoomStep = 0.25;
        let panX = 0, panY = 0;
        let isDragging = false, startX = 0, startY = 0;'''

# JS changes - replace applyZoom
old_js3 = '''        function applyZoom() {
            mainImage.style.transform = `scale(${zoomLevel})`;
            mainImage2.style.transform = `scale(${zoomLevel})`;
            
            mainContainer.classList.toggle('zoomed', zoomLevel > 1);
            
            updateZoomDisplay();
        }'''

new_js3 = '''        function applyZoom() {
            spread.style.transform = `scale(${zoomLevel}) translate(${panX}px, ${panY}px)`;
            mainContainer.classList.toggle('zoomed', zoomLevel > 1);
            updateZoomDisplay();
        }'''

# JS changes - replace resetPan and setupPanHandlers
old_js4 = '''        function resetPan() {
            panState[1] = { x: 0, y: 0, isDragging: false, startX: 0, startY: 0, scrollLeft: 0, scrollTop: 0 };
            panState[2] = { x: 0, y: 0, isDragging: false, startX: 0, startY: 0, scrollLeft: 0, scrollTop: 0 };
            mainImage.style.transformOrigin = 'center center';
            mainImage2.style.transformOrigin = 'center center';
        }
        
        function setupPanHandlers() {
            // Single pan handler on the main container - both images move together as one spread
            mainContainer.addEventListener('mousedown', (e) => {
                if (zoomLevel <= 1) return;
                if (e.target.closest('.page-viewer-zoom-controls')) return;
                e.preventDefault();
                
                panState[1].isDragging = true;
                panState[1].startX = e.clientX;
                panState[1].startY = e.clientY;
                mainContainer.classList.add('dragging');
            });
            
            mainContainer.addEventListener('mousemove', (e) => {
                if (zoomLevel <= 1) return;
                if (!panState[1].isDragging) return;
                e.preventDefault();
                
                const deltaX = e.clientX - panState[1].startX;
                const deltaY = e.clientY - panState[1].startY;
                const containerRect = mainContainer.getBoundingClientRect();
                
                // Update pan position (shared for both images)
                panState[1].x += deltaX;
                panState[1].y += deltaY;
                
                // Calculate limits based on combined spread width in dual mode
                let totalWidth, totalHeight;
                if (isDualMode && container2.style.display !== 'none') {
                    totalWidth = (mainImage.naturalWidth + mainImage2.naturalWidth) * zoomLevel;
                    totalHeight = Math.max(mainImage.naturalHeight, mainImage2.naturalHeight) * zoomLevel;
                } else {
                    totalWidth = mainImage.naturalWidth * zoomLevel;
                    totalHeight = mainImage.naturalHeight * zoomLevel;
                }
                
                const maxPanX = Math.max(0, (totalWidth - containerRect.width) / 2);
                const maxPanY = Math.max(0, (totalHeight - containerRect.height) / 2);
                panState[1].x = Math.max(-maxPanX, Math.min(maxPanX, panState[1].x));
                panState[1].y = Math.max(-maxPanY, Math.min(maxPanY, panState[1].y));
                
                // Apply same transform to both images
                const transform = `scale(${zoomLevel}) translate(${panState[1].x / zoomLevel}px, ${panState[1].y / zoomLevel}px)`;
                mainImage.style.transform = transform;
                if (isDualMode && container2.style.display !== 'none') {
                    mainImage2.style.transform = transform;
                }
                
                panState[1].startX = e.clientX;
                panState[1].startY = e.clientY;
            });
            
            mainContainer.addEventListener('mouseup', () => {
                panState[1].isDragging = false;
                mainContainer.classList.remove('dragging');
            });
            
            mainContainer.addEventListener('mouseleave', () => {
                panState[1].isDragging = false;
                mainContainer.classList.remove('dragging');
            });
            
            // Mouse wheel zoom
            mainContainer.addEventListener('wheel', (e) => {
                e.preventDefault();
                if (e.deltaY < 0) {
                    zoomIn();
                } else {
                    zoomOut();
                }
            }, { passive: false });
        }'''

new_js4 = '''        function resetPan() {
            panX = 0;
            panY = 0;
            applyZoom();
        }
        
        function setupPanHandlers() {
            // Pan handler - transform the spread as a single unit
            mainContainer.addEventListener('mousedown', (e) => {
                if (zoomLevel <= 1) return;
                if (e.target.closest('.page-viewer-zoom-controls')) return;
                e.preventDefault();
                
                isDragging = true;
                startX = e.clientX;
                startY = e.clientY;
                mainContainer.classList.add('dragging');
            });
            
            mainContainer.addEventListener('mousemove', (e) => {
                if (zoomLevel <= 1 || !isDragging) return;
                e.preventDefault();
                
                const deltaX = (e.clientX - startX) / zoomLevel;
                const deltaY = (e.clientY - startY) / zoomLevel;
                
                panX += deltaX;
                panY += deltaY;
                
                // Calculate limits based on spread size
                const spreadRect = spread.getBoundingClientRect();
                const containerRect = mainContainer.getBoundingClientRect();
                const scaledWidth = spreadRect.width;
                const scaledHeight = spreadRect.height;
                
                const maxPanX = Math.max(0, (scaledWidth - containerRect.width) / (2 * zoomLevel));
                const maxPanY = Math.max(0, (scaledHeight - containerRect.height) / (2 * zoomLevel));
                panX = Math.max(-maxPanX, Math.min(maxPanX, panX));
                panY = Math.max(-maxPanY, Math.min(maxPanY, panY));
                
                applyZoom();
                
                startX = e.clientX;
                startY = e.clientY;
            });
            
            mainContainer.addEventListener('mouseup', () => {
                isDragging = false;
                mainContainer.classList.remove('dragging');
            });
            
            mainContainer.addEventListener('mouseleave', () => {
                isDragging = false;
                mainContainer.classList.remove('dragging');
            });
            
            // Mouse wheel zoom
            mainContainer.addEventListener('wheel', (e) => {
                e.preventDefault();
                if (e.deltaY < 0) {
                    zoomIn();
                } else {
                    zoomOut();
                }
            }, { passive: false });
        }'''

count = 0
for root, dirs, files in os.walk(texts_dir):
    if 'index.html' in files:
        filepath = os.path.join(root, 'index.html')
        if 'moony' in filepath:
            continue  # Already updated
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        modified = False
        
        if old_html in content:
            content = content.replace(old_html, new_html)
            modified = True
            
        if old_js1 in content:
            content = content.replace(old_js1, new_js1)
            modified = True
            
        if old_js2 in content:
            content = content.replace(old_js2, new_js2)
            modified = True
            
        if old_js3 in content:
            content = content.replace(old_js3, new_js3)
            modified = True
            
        if old_js4 in content:
            content = content.replace(old_js4, new_js4)
            modified = True
            
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {filepath}")
            count += 1

print(f"\nUpdated {count} files")
