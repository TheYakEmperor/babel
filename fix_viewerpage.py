#!/usr/bin/env python3
import os
import re

texts_dir = 'texts/00/00'

# Pattern to find: if(window.goToViewerPage) window.goToViewerPage(${work.viewerPage - 1});
# Replace with: if(window.goToViewerPageByLabel) window.goToViewerPageByLabel(work.viewerPage);

old_onclick = r'if\(window\.goToViewerPage\) window\.goToViewerPage\(\$\{work\.viewerPage - 1\}\);'
new_onclick = "if(window.goToViewerPageByLabel) window.goToViewerPageByLabel(work.viewerPage);"

# Also fix: window.workPageMap[elemId] = work.viewerPage - 1;
old_workpagemap = r'window\.workPageMap\[elemId\] = work\.viewerPage - 1;'
new_workpagemap = "window.workPageMap[elemId] = work.viewerPage;"

# Also fix: const viewerPageAttr = work.viewerPage !== undefined ? ` data-viewer-page="${work.viewerPage - 1}"` : '';
old_attr = r'const viewerPageAttr = work\.viewerPage !== undefined \? ` data-viewer-page="\$\{work\.viewerPage - 1\}"` : \'\';'
new_attr = 'const viewerPageAttr = work.viewerPage !== undefined ? ` data-viewer-page="${work.viewerPage}"` : \'\';'

# Fix: if (pageIdx !== undefined && window.goToViewerPage) { window.goToViewerPage(pageIdx);
# to: if (pageLabel !== undefined && window.goToViewerPageByLabel) { window.goToViewerPageByLabel(pageLabel);
old_pageclick = r'const pageIdx = window\.workPageMap\[workId\];\s*if \(pageIdx !== undefined && window\.goToViewerPage\) \{\s*window\.goToViewerPage\(pageIdx\);'
new_pageclick = '''const pageLabel = window.workPageMap[workId];
                if (pageLabel !== undefined && window.goToViewerPageByLabel) {
                    window.goToViewerPageByLabel(pageLabel);'''

updated = 0
for text_id in os.listdir(texts_dir):
    text_path = os.path.join(texts_dir, text_id)
    if not os.path.isdir(text_path):
        continue
    
    index_path = os.path.join(text_path, 'index.html')
    if not os.path.exists(index_path):
        continue
    
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content
    new_content = re.sub(old_onclick, new_onclick, new_content)
    new_content = re.sub(old_workpagemap, new_workpagemap, new_content)
    new_content = re.sub(old_attr, new_attr, new_content)
    new_content = re.sub(old_pageclick, new_pageclick, new_content)
    
    if new_content != content:
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        updated += 1
        print(f"Updated: {text_id}")
    else:
        print(f"No changes: {text_id}")

print(f"\nDone! Updated {updated} files")
