#!/usr/bin/env python3
"""Add fullscreen mode to page viewer"""
import os

# HTML change - add fullscreen button
old_html = '''                    <button class="pv-view-toggle" id="pv-dual-toggle" title="Toggle dual-page view">Dual</button>
                    <button class="page-viewer-btn" id="pv-prev" disabled>◀ Prev</button>'''

new_html = '''                    <button class="pv-view-toggle" id="pv-dual-toggle" title="Toggle dual-page view">Dual</button>
                    <button class="pv-view-toggle" id="pv-fullscreen-toggle" title="Toggle fullscreen">Fullscreen</button>
                    <button class="page-viewer-btn" id="pv-prev" disabled>◀ Prev</button>'''

# JS change 1 - add fullscreen element and state
old_js1 = '''        const dualToggle = document.getElementById('pv-dual-toggle');
        const zoomInBtn = document.getElementById('pv-zoom-in');
        const zoomOutBtn = document.getElementById('pv-zoom-out');
        const zoomResetBtn = document.getElementById('pv-zoom-reset');
        const zoomLevelDisplay = document.getElementById('pv-zoom-level');
        
        let images = [];
        let currentIndex = 0;
        let isDualMode = false;
        
        // Zoom and pan state
        let zoomLevel = 1;'''

new_js1 = '''        const dualToggle = document.getElementById('pv-dual-toggle');
        const fullscreenToggle = document.getElementById('pv-fullscreen-toggle');
        const zoomInBtn = document.getElementById('pv-zoom-in');
        const zoomOutBtn = document.getElementById('pv-zoom-out');
        const zoomResetBtn = document.getElementById('pv-zoom-reset');
        const zoomLevelDisplay = document.getElementById('pv-zoom-level');
        
        let images = [];
        let currentIndex = 0;
        let isDualMode = false;
        let isFullscreen = false;
        
        // Zoom and pan state
        let zoomLevel = 1;'''

# JS change 2 - add fullscreen function and event handlers
old_js2 = '''            setupPanHandlers();
            
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
        });'''

new_js2 = '''            setupPanHandlers();
            
            // Fullscreen toggle function
            function toggleFullscreen() {
                isFullscreen = !isFullscreen;
                viewer.classList.toggle('fullscreen', isFullscreen);
                document.body.classList.toggle('viewer-fullscreen', isFullscreen);
                fullscreenToggle.textContent = isFullscreen ? 'Exit' : 'Fullscreen';
                resetZoom();
            }
            
            // Set up controls
            prevBtn.addEventListener('click', () => navigate(-1));
            nextBtn.addEventListener('click', () => navigate(1));
            dualToggle.addEventListener('click', toggleDualMode);
            fullscreenToggle.addEventListener('click', toggleFullscreen);
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
                if (e.key === 'Escape' && isFullscreen) toggleFullscreen();
            });
            
            showImage(0);
        });'''

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
        
        if old_html in content:
            content = content.replace(old_html, new_html)
            modified = True
            
        if old_js1 in content:
            content = content.replace(old_js1, new_js1)
            modified = True
            
        if old_js2 in content:
            content = content.replace(old_js2, new_js2)
            modified = True
            
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {filepath}")
            count += 1

print(f"\nUpdated {count} files")
