#!/usr/bin/env python3
"""Fix pan handlers to work on whole viewer area"""
import os

old_code = '''        function setupPanHandlers(container, image, stateKey) {
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
                
                // Limit pan range based on zoom level and image size
                const imgRect = image.getBoundingClientRect();
                const containerRect = mainContainer.getBoundingClientRect();
                const scaledWidth = image.naturalWidth * zoomLevel;
                const scaledHeight = image.naturalHeight * zoomLevel;
                const maxPanX = Math.max(0, (scaledWidth - containerRect.width) / 2);
                const maxPanY = Math.max(0, (scaledHeight - containerRect.height) / 2);
                state.x = Math.max(-maxPanX, Math.min(maxPanX, state.x));
                state.y = Math.max(-maxPanY, Math.min(maxPanY, state.y));
                
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
        }'''

new_code = '''        function setupPanHandlers() {
            // Single pan handler on the main container for both images
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
        }'''

old_call = '''            // Set up pan handlers for both containers
            setupPanHandlers(container1, mainImage, 1);
            setupPanHandlers(container2, mainImage2, 2);'''

new_call = '''            // Set up pan handlers
            setupPanHandlers();'''

texts_dir = '/Users/yakking/Downloads/Web-design/Babel/texts'
count = 0

for root, dirs, files in os.walk(texts_dir):
    if 'index.html' in files:
        filepath = os.path.join(root, 'index.html')
        if 'moony' in filepath:
            continue  # Already updated
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        modified = False
        if old_code in content:
            content = content.replace(old_code, new_code)
            modified = True
        
        if old_call in content:
            content = content.replace(old_call, new_call)
            modified = True
            
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {filepath}")
            count += 1

print(f"\nUpdated {count} files")
