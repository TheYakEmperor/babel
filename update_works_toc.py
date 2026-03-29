#!/usr/bin/env python3
"""Update text index.html files to display works as a table of contents with page numbers."""

import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent

# New buildWorksHtml and collectTopLevelWorks functions
NEW_BUILD_WORKS = '''    // Build hierarchical works list for metadata - TABLE OF CONTENTS style
    function buildWorksHtml(works, indent = 0) {
        if (!works || works.length === 0) return '';
        
        const items = works.map(work => {
            const elemId = work.elementId || work.id;
            let linkHtml;
            // Page-only works: link jumps to page viewer
            if (work.viewerPage !== undefined && !work.content) {
                linkHtml = `<a href="javascript:void(0)" data-viewer-page="${work.viewerPage}" class="viewer-page-link">${work.title}</a>`;
            } else {
                linkHtml = `<a href="#${elemId}">${work.title}</a>`;
            }
            
            // Page number display - use firstPage or viewerPage as fallback
            const pageLabel = work.firstPage || (work.viewerPage !== undefined ? work.viewerPage : '');
            const pageHtml = `<span class="toc-page">${pageLabel}</span>`;
            
            // Build this item - page number fixed left, link indented
            let itemHtml = `<div class="toc-item">${pageHtml}<span class="toc-title" style="padding-left: ${indent * 30}px">${linkHtml}</span></div>`;
            
            // Recursively add subworks with increased indent
            if (work.subworks && work.subworks.length > 0) {
                itemHtml += buildWorksHtml(work.subworks, indent + 1);
            }
            return itemHtml;
        });
        return items.join('');
    }'''

NEW_COLLECT_WORKS = '''    // Collect all top-level works from all pages, merging subworks and tracking first page
    function collectTopLevelWorks(pages) {
        const workMap = new Map(); // id -> merged work object
        
        function mergeSubworks(existing, incoming) {
            if (!incoming || incoming.length === 0) return existing || [];
            if (!existing || existing.length === 0) return incoming;
            
            const subMap = new Map();
            // Add existing subworks - key by work_id (NOT override)
            existing.forEach(sw => subMap.set(sw.id, {...sw}));
            // Merge incoming subworks
            incoming.forEach(sw => {
                if (subMap.has(sw.id)) {
                    const existingSw = subMap.get(sw.id);
                    existingSw.subworks = mergeSubworks(existingSw.subworks, sw.subworks);
                    // Keep earliest firstPage
                } else {
                    subMap.set(sw.id, {...sw});
                }
            });
            return Array.from(subMap.values());
        }
        
        pages.forEach(page => {
            if (!page.works) return; // Skip pages with only images
            const pageLabel = page.label || page.id;
            page.works.forEach(work => {
                // Add firstPage to this work occurrence
                const workWithPage = {...work, firstPage: pageLabel};
                
                // Also add firstPage to all subworks in this occurrence
                function addPageToSubworks(w, label) {
                    if (w.subworks) {
                        w.subworks = w.subworks.map(sw => {
                            const swWithPage = {...sw, firstPage: sw.firstPage || label};
                            addPageToSubworks(swWithPage, label);
                            return swWithPage;
                        });
                    }
                }
                addPageToSubworks(workWithPage, pageLabel);
                
                if (workMap.has(work.id)) {
                    // Merge subworks from this occurrence
                    const existing = workMap.get(work.id);
                    existing.subworks = mergeSubworks(existing.subworks, workWithPage.subworks);
                    // Keep earliest firstPage
                } else {
                    // Deep clone to avoid mutating original
                    workMap.set(work.id, JSON.parse(JSON.stringify(workWithPage)));
                }
            });
        });
        return Array.from(workMap.values());
    }'''

# Pattern to find and replace buildWorksHtml function
BUILD_WORKS_PATTERN = re.compile(
    r'    // Build hierarchical works list for metadata\s*\n'
    r'    function buildWorksHtml\(works\) \{.*?'
    r'        return items\.join\(\', \'\);\s*\n    \}',
    re.DOTALL
)

# Alternative pattern (some files may have different comment)
BUILD_WORKS_PATTERN_ALT = re.compile(
    r'    function buildWorksHtml\(works\) \{\s*\n'
    r'        if \(!works \|\| works\.length === 0\) return \'\';\s*\n'
    r'.*?'
    r'        return items\.join\(\', \'\);\s*\n    \}',
    re.DOTALL
)

# Pattern for TOC-style buildWorksHtml (page on right, needs updating to page on left)
BUILD_WORKS_TOC_PATTERN = re.compile(
    r'    // Build hierarchical works list for metadata - TABLE OF CONTENTS style\s*\n'
    r'    function buildWorksHtml\(works, indent = 0\) \{.*?'
    r"        return items\.join\(''\);\s*\n    \}",
    re.DOTALL
)

# Pattern to find collectTopLevelWorks function
COLLECT_WORKS_PATTERN = re.compile(
    r'    // Collect all top-level works from all pages, merging subworks\s*\n'
    r'    function collectTopLevelWorks\(pages\) \{.*?'
    r'        return Array\.from\(workMap\.values\(\)\);\s*\n    \}',
    re.DOTALL
)

# Pattern for Works: line in metadata
WORKS_META_PATTERN = re.compile(
    r"metaHtml \+= `<p><strong>Works:</strong> \$\{worksHtml\}</p>`;"
)

# Also match the old non-collapsible version
WORKS_TOC_PATTERN = re.compile(
    r'metaHtml \+= `<div class="works-toc"><strong>Contents:</strong>\$\{worksHtml\}</div>`;'
)

NEW_WORKS_META = '''metaHtml += `<div class="works-toc collapsed">
                    <div class="works-toc-header" onclick="this.parentElement.classList.toggle('collapsed')">
                        <span class="works-toc-toggle">▼</span> Contents
                    </div>
                    <div class="works-toc-content">${worksHtml}</div>
                </div>`;'''

def update_text_file(filepath):
    """Update a single text index.html file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Replace buildWorksHtml function (various patterns from different versions)
    if BUILD_WORKS_PATTERN.search(content):
        content = BUILD_WORKS_PATTERN.sub(NEW_BUILD_WORKS, content)
    elif BUILD_WORKS_PATTERN_ALT.search(content):
        content = BUILD_WORKS_PATTERN_ALT.sub(NEW_BUILD_WORKS, content)
    elif BUILD_WORKS_TOC_PATTERN.search(content):
        content = BUILD_WORKS_TOC_PATTERN.sub(NEW_BUILD_WORKS, content)
    
    # Replace collectTopLevelWorks function
    if COLLECT_WORKS_PATTERN.search(content):
        content = COLLECT_WORKS_PATTERN.sub(NEW_COLLECT_WORKS, content)
    
    # Replace Works: metadata display (either old <p> style or old non-collapsible TOC)
    if WORKS_META_PATTERN.search(content):
        content = WORKS_META_PATTERN.sub(NEW_WORKS_META, content)
    elif WORKS_TOC_PATTERN.search(content):
        content = WORKS_TOC_PATTERN.sub(NEW_WORKS_META, content)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    print("Updating text index.html files with table of contents style works display...")
    
    # Find all text index.html files
    texts_dir = BASE_DIR / 'texts'
    updated = 0
    skipped = 0
    
    for index_file in texts_dir.glob('**/index.html'):
        # Skip non-data.json driven texts (those without data.json)
        data_json = index_file.parent / 'data.json'
        if not data_json.exists():
            continue
        
        if update_text_file(index_file):
            print(f"  Updated {index_file.relative_to(BASE_DIR)}")
            updated += 1
        else:
            print(f"  - Skipped {index_file.relative_to(BASE_DIR)} (no changes needed)")
            skipped += 1
    
    print(f"\nDone! Updated {updated} files, skipped {skipped} files.")

if __name__ == '__main__':
    main()
