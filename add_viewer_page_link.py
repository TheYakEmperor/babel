#!/usr/bin/env python3
"""Update text pages to support page viewer linking from works"""

import re
from pathlib import Path

texts_dir = Path('/Users/yakking/Downloads/Web-design/Babel/texts')

# Update renderWork to add data-viewer-page attribute
old_render = '''                // Add data-language if the work specifies a language
                    const langAttr = work.language ? ` data-language="${work.language}"` : '';
                    html += `<div class="text-work" id="${elemId}" data-work-id="${work.id}" data-work-page="${workPage}" data-work-title="${work.title}"${superworkAttr}${langAttr}>`;'''

new_render = '''                // Add data-language if the work specifies a language
                    const langAttr = work.language ? ` data-language="${work.language}"` : '';
                    // Add data-viewer-page if work specifies which page it starts on
                    const viewerPageAttr = work.page !== undefined ? ` data-viewer-page="${work.page}"` : '';
                    html += `<div class="text-work" id="${elemId}" data-work-id="${work.id}" data-work-page="${workPage}" data-work-title="${work.title}"${superworkAttr}${langAttr}${viewerPageAttr}>`;'''

# Add hashchange handler after showImage(0) area - we need to find a good spot
# Actually, add it to the end of the inline script, after initPageViewer call

old_init_end = '''            // Initialize page viewer if images exist
            initPageViewer(data.pages);'''

new_init_end = '''            // Initialize page viewer if images exist
            initPageViewer(data.pages);
            
            // Build work-to-page mapping for viewer navigation
            window.workPageMap = {};
            function buildWorkPageMap(works) {
                if (!works) return;
                works.forEach(work => {
                    if (work.page !== undefined) {
                        const elemId = work.elementId || work.id;
                        window.workPageMap[elemId] = work.page;
                    }
                    if (work.subworks) buildWorkPageMap(work.subworks);
                });
            }
            data.pages.forEach(page => {
                if (page.works) buildWorkPageMap(page.works);
            });
            
            // Jump to page viewer when clicking work or navigating via hash
            function jumpToWorkPage(hash) {
                if (!hash) return;
                const id = hash.replace('#', '');
                const pageIdx = window.workPageMap[id];
                if (pageIdx !== undefined && window.goToViewerPage) {
                    window.goToViewerPage(pageIdx);
                }
            }
            
            // Handle hash on load and hashchange
            if (window.location.hash) {
                setTimeout(() => jumpToWorkPage(window.location.hash), 500);
            }
            window.addEventListener('hashchange', () => {
                jumpToWorkPage(window.location.hash);
            });'''

for html_file in texts_dir.rglob('index.html'):
    content = html_file.read_text()
    modified = False
    
    if old_render in content:
        content = content.replace(old_render, new_render)
        modified = True
    
    if old_init_end in content:
        content = content.replace(old_init_end, new_init_end)
        modified = True
    
    if modified:
        html_file.write_text(content)
        print(f"Updated: {html_file}")

print("Done!")
