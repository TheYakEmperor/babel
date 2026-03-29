#!/usr/bin/env python3
"""Update page-only works to just jump to page viewer, no card in body."""

import os
import re
from pathlib import Path

TEXTS_DIR = Path("/Users/yakking/Downloads/Web-design/Babel/texts")

# New buildWorksHtml that makes page-only works jump directly to viewer
NEW_BUILD_WORKS = '''    function buildWorksHtml(works) {
        if (!works || works.length === 0) return '';
        
        const items = works.map(work => {
            const elemId = work.elementId || work.id;
            let html;
            // Page-only works: link jumps to page viewer
            if (work.page !== undefined && !work.content) {
                html = `<a href="#" onclick="event.preventDefault(); if(window.goToViewerPage) window.goToViewerPage(${work.page});">${work.title}</a>`;
            } else {
                html = `<a href="#${elemId}">${work.title}</a>`;
            }
            if (work.subworks && work.subworks.length > 0) {
                html += ` [${buildWorksHtml(work.subworks)}]`;
            }
            return html;
        });
        return items.join(', ');
    }'''

# Pattern for old buildWorksHtml
OLD_BUILD_WORKS_PATTERN = re.compile(
    r'    function buildWorksHtml\(works\) \{\s*'
    r"if \(!works \|\| works\.length === 0\) return '';\s*"
    r'const items = works\.map\(work => \{\s*'
    r'const elemId = work\.elementId \|\| work\.id;\s*'
    r'let html = `<a href="#\$\{elemId\}">\$\{work\.title\}</a>`;\s*'
    r'if \(work\.subworks && work\.subworks\.length > 0\) \{\s*'
    r'html \+= ` \[\$\{buildWorksHtml\(work\.subworks\)\}\]`;\s*'
    r'\}\s*'
    r'return html;\s*'
    r'\}\);\s*'
    r"return items\.join\(', '\);\s*"
    r'\}',
    re.DOTALL
)

# Pattern for page-only work card rendering to replace with just anchor span
OLD_PAGE_CARD = re.compile(
    r"} else if \(work\.page !== undefined\) \{\s*"
    r"// Page-only work - render as clickable link to page viewer\s*"
    r'const viewerPageAttr = ` data-viewer-page="\$\{work\.page\}"`;\s*'
    r"const langAttr = work\.language \? ` data-language=\"\$\{work\.language\}\"` : '';\s*"
    r'html \+= `<div class="text-work page-link-work" id="\$\{elemId\}"[^`]+`;\s*'
    r'html \+= `<a href="#\$\{elemId\}"[^`]+`;\s*'
    r'html \+= `<span class="page-link-icon"></span> \$\{work\.title\}`;\s*'
    r"html \+= `</a>`;\s*"
    r"html \+= '</div>';\s*"
    r'\} else if \(work\.subworks\)',
    re.DOTALL
)

NEW_PAGE_ANCHOR = '''} else if (work.page !== undefined) {
                    // Page-only work - just add anchor, link in Works: jumps to viewer
                    html += `<span id="${elemId}"></span>`;
                } else if (work.subworks)'''

count = 0
for html_file in TEXTS_DIR.rglob("index.html"):
    content = html_file.read_text(encoding='utf-8')
    modified = False
    
    # Update buildWorksHtml
    if OLD_BUILD_WORKS_PATTERN.search(content):
        content = OLD_BUILD_WORKS_PATTERN.sub(NEW_BUILD_WORKS, content)
        modified = True
    
    # Update page-only rendering (simpler approach - search and replace)
    if 'page-link-work' in content and 'Page-only work - render as clickable link' in content:
        # Use simpler string replacement
        old_block = '''} else if (work.page !== undefined) {
                    // Page-only work - render as clickable link to page viewer
                    const viewerPageAttr = ` data-viewer-page="${work.page}"`;
                    const langAttr = work.language ? ` data-language="${work.language}"` : '';
                    html += `<div class="text-work page-link-work" id="${elemId}" data-work-id="${work.id}" data-work-page="${workPage}" data-work-title="${work.title}"${langAttr}${viewerPageAttr}>`;
                    html += `<a href="#${elemId}" class="page-link-title" onclick="event.preventDefault(); if(window.goToViewerPage) window.goToViewerPage(${work.page});">`;
                    html += `<span class="page-link-icon"></span> ${work.title}`;
                    html += `</a>`;
                    html += '</div>';
                } else if (work.subworks)'''
        
        new_block = '''} else if (work.page !== undefined) {
                    // Page-only work - just add anchor span, Works: link jumps to viewer
                    html += `<span id="${elemId}"></span>`;
                } else if (work.subworks)'''
        
        if old_block in content:
            content = content.replace(old_block, new_block)
            modified = True
    
    if modified:
        html_file.write_text(content, encoding='utf-8')
        count += 1
        print(f"Updated: {html_file}")

print(f"\nTotal updated: {count} files")
