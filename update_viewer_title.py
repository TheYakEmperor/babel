#!/usr/bin/env python3
"""Update all text pages to change page viewer title."""

import os

def update_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Update the h3 tag
    content = content.replace(
        '<h3>Page Images</h3>',
        '<h3 id="pv-title">Page Viewer</h3>'
    )
    
    # Update toggleFullscreen to change title
    old_toggle = '''        function toggleFullscreen() {
            isFullscreen = !isFullscreen;
            viewer.classList.toggle('fullscreen', isFullscreen);
            document.body.classList.toggle('viewer-fullscreen', isFullscreen);
            fullscreenToggle.classList.toggle('active', isFullscreen);
            fullscreenToggle.textContent = isFullscreen ? 'Exit' : 'Fullscreen';
            resetZoom();
        }'''
    
    new_toggle = '''        function toggleFullscreen() {
            isFullscreen = !isFullscreen;
            viewer.classList.toggle('fullscreen', isFullscreen);
            document.body.classList.toggle('viewer-fullscreen', isFullscreen);
            fullscreenToggle.classList.toggle('active', isFullscreen);
            fullscreenToggle.textContent = isFullscreen ? 'Exit' : 'Fullscreen';
            // Update title
            const pvTitle = document.getElementById('pv-title');
            const pageTitle = document.getElementById('page-title').textContent;
            pvTitle.textContent = isFullscreen ? pageTitle : 'Page Viewer';
            resetZoom();
        }'''
    
    content = content.replace(old_toggle, new_toggle)
    
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
