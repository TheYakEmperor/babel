#!/usr/bin/env python3
"""Make dual-page zoom/pan work as single spread"""
import os

old_code = '''            // Single pan handler on the main container for both images
            mainContainer.addEventListener('mousedown', (e) => {
                if (zoomLevel <= 1) return;
                if (e.target.closest('.page-viewer-zoom-controls')) return;
                e.preventDefault();
                
                // Determine which image to pan (use image 1 for single mode, both for dual)
                panState[1].isDragging = true;
                panState[1].startX = e.clientX;
                panState[1].startY = e.clientY;
                if (isDualMode && container2.style.display !== 'none') {
                    panState[2].isDragging = true;
                    panState[2].startX = e.clientX;
                    panState[2].startY = e.clientY;
                }
                mainContainer.classList.add('dragging');
            });
            
            mainContainer.addEventListener('mousemove', (e) => {
                if (zoomLevel <= 1) return;
                if (!panState[1].isDragging) return;
                e.preventDefault();
                
                const deltaX = e.clientX - panState[1].startX;
                const deltaY = e.clientY - panState[1].startY;
                const containerRect = mainContainer.getBoundingClientRect();
                
                // Pan image 1
                panState[1].x += deltaX;
                panState[1].y += deltaY;
                const scaledWidth1 = mainImage.naturalWidth * zoomLevel;
                const scaledHeight1 = mainImage.naturalHeight * zoomLevel;
                const maxPanX1 = Math.max(0, (scaledWidth1 - containerRect.width) / 2);
                const maxPanY1 = Math.max(0, (scaledHeight1 - containerRect.height) / 2);
                panState[1].x = Math.max(-maxPanX1, Math.min(maxPanX1, panState[1].x));
                panState[1].y = Math.max(-maxPanY1, Math.min(maxPanY1, panState[1].y));
                mainImage.style.transform = `scale(${zoomLevel}) translate(${panState[1].x / zoomLevel}px, ${panState[1].y / zoomLevel}px)`;
                panState[1].startX = e.clientX;
                panState[1].startY = e.clientY;
                
                // Pan image 2 if in dual mode
                if (panState[2].isDragging) {
                    panState[2].x += deltaX;
                    panState[2].y += deltaY;
                    const scaledWidth2 = mainImage2.naturalWidth * zoomLevel;
                    const scaledHeight2 = mainImage2.naturalHeight * zoomLevel;
                    const maxPanX2 = Math.max(0, (scaledWidth2 - containerRect.width) / 2);
                    const maxPanY2 = Math.max(0, (scaledHeight2 - containerRect.height) / 2);
                    panState[2].x = Math.max(-maxPanX2, Math.min(maxPanX2, panState[2].x));
                    panState[2].y = Math.max(-maxPanY2, Math.min(maxPanY2, panState[2].y));
                    mainImage2.style.transform = `scale(${zoomLevel}) translate(${panState[2].x / zoomLevel}px, ${panState[2].y / zoomLevel}px)`;
                    panState[2].startX = e.clientX;
                    panState[2].startY = e.clientY;
                }
            });
            
            mainContainer.addEventListener('mouseup', () => {
                panState[1].isDragging = false;
                panState[2].isDragging = false;
                mainContainer.classList.remove('dragging');
            });
            
            mainContainer.addEventListener('mouseleave', () => {
                panState[1].isDragging = false;
                panState[2].isDragging = false;
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
        }
        
        // Try to detect available images
        async function detectImages() {'''

new_code = '''            // Single pan handler on the main container - both images move together as one spread
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
        }
        
        // Try to detect available images
        async function detectImages() {'''

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
