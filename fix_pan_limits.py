#!/usr/bin/env python3
"""Fix pan limits to use actual image/container dimensions"""
import os
import re

old_code = '''            container.addEventListener('mousemove', (e) => {
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
            });'''

new_code = '''            container.addEventListener('mousemove', (e) => {
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
            });'''

texts_dir = '/Users/yakking/Downloads/Web-design/Babel/texts'
count = 0

for root, dirs, files in os.walk(texts_dir):
    if 'index.html' in files:
        filepath = os.path.join(root, 'index.html')
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if old_code in content:
            content = content.replace(old_code, new_code)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {filepath}")
            count += 1

print(f"\nUpdated {count} files")
