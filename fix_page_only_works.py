#!/usr/bin/env python3
"""Update renderWork to show page-only works as clickable links"""

import re
from pathlib import Path

texts_dir = Path('/Users/yakking/Downloads/Web-design/Babel/texts')

old_render = '''            // Helper to render works recursively (for nested subworks)
            function renderWork(work, parentTitle, parentId) {
                let html = '';
                const elemId = work.elementId || work.id;
                // workPage determines which work page to link to (can be overridden)
                const workPage = work.override || work.id;
                
                // Render this work if it has content OR music (both go in same gold box)
                if (work.content || work.music) {
                    const superworkAttr = parentTitle ? ` data-superwork-title="${parentTitle}" data-superwork-id="${parentId}"` : '';
                    // Add data-language if the work specifies a language
                    const langAttr = work.language ? ` data-language="${work.language}"` : '';
                    // Add data-viewer-page if work specifies which page it starts on
                    const viewerPageAttr = work.page !== undefined ? ` data-viewer-page="${work.page}"` : '';
                    html += `<div class="text-work" id="${elemId}" data-work-id="${work.id}" data-work-page="${workPage}" data-work-title="${work.title}"${superworkAttr}${langAttr}${viewerPageAttr}>`;
                    
                    // Render sheet music inside the work if present
                    if (work.music) {
                        const musicId = elemId + '-music';
                        html += `<div class="work-music" id="${musicId}" data-music-file="${work.music}">`;
                        html += '<div class="music-loading">Loading sheet music...</div>';
                        html += '</div>';
                    }
                    
                    // Render text content if present
                    if (work.content) {
                        html += work.content;
                    }
                    
                    html += '</div>';
                } else if (work.subworks) {
                    // Container work - add anchor span so links can target it
                    html += `<span id="${elemId}"></span>`;
                }'''

new_render = '''            // Helper to render works recursively (for nested subworks)
            function renderWork(work, parentTitle, parentId) {
                let html = '';
                const elemId = work.elementId || work.id;
                // workPage determines which work page to link to (can be overridden)
                const workPage = work.override || work.id;
                
                // Render this work if it has content OR music (both go in same gold box)
                if (work.content || work.music) {
                    const superworkAttr = parentTitle ? ` data-superwork-title="${parentTitle}" data-superwork-id="${parentId}"` : '';
                    // Add data-language if the work specifies a language
                    const langAttr = work.language ? ` data-language="${work.language}"` : '';
                    // Add data-viewer-page if work specifies which page it starts on
                    const viewerPageAttr = work.page !== undefined ? ` data-viewer-page="${work.page}"` : '';
                    html += `<div class="text-work" id="${elemId}" data-work-id="${work.id}" data-work-page="${workPage}" data-work-title="${work.title}"${superworkAttr}${langAttr}${viewerPageAttr}>`;
                    
                    // Render sheet music inside the work if present
                    if (work.music) {
                        const musicId = elemId + '-music';
                        html += `<div class="work-music" id="${musicId}" data-music-file="${work.music}">`;
                        html += '<div class="music-loading">Loading sheet music...</div>';
                        html += '</div>';
                    }
                    
                    // Render text content if present
                    if (work.content) {
                        html += work.content;
                    }
                    
                    html += '</div>';
                } else if (work.page !== undefined) {
                    // Page-only work - render as clickable link to page viewer
                    const viewerPageAttr = ` data-viewer-page="${work.page}"`;
                    const langAttr = work.language ? ` data-language="${work.language}"` : '';
                    html += `<div class="text-work page-link-work" id="${elemId}" data-work-id="${work.id}" data-work-page="${workPage}" data-work-title="${work.title}"${langAttr}${viewerPageAttr}>`;
                    html += `<a href="#${elemId}" class="page-link-title" onclick="event.preventDefault(); if(window.goToViewerPage) window.goToViewerPage(${work.page});">`;
                    html += `<span class="page-link-icon"></span> ${work.title}`;
                    html += `</a>`;
                    html += '</div>';
                } else if (work.subworks) {
                    // Container work - add anchor span so links can target it
                    html += `<span id="${elemId}"></span>`;
                }'''

for html_file in texts_dir.rglob('index.html'):
    content = html_file.read_text()
    
    if old_render in content:
        content = content.replace(old_render, new_render)
        html_file.write_text(content)
        print(f"Updated: {html_file}")

print("Done!")
