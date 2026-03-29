#!/usr/bin/env python3
"""Fix text pages to also traverse work.children (not just work.subworks)"""

from pathlib import Path

TEXTS_DIR = Path("/Users/yakking/Downloads/Web-design/Babel/texts")

# In renderWork - add children handling after subworks handling
old_render_subworks = '''                // Render subworks - pass this work's title and id as the parent
                if (work.subworks) {
                    const nextParentTitle = parentTitle || work.title;
                    const nextParentId = parentId || work.id;
                    work.subworks.forEach(subwork => {
                        html += renderWork(subwork, nextParentTitle, nextParentId);
                    });
                }'''

new_render_subworks = '''                // Render subworks/children - pass this work's title and id as the parent
                const childWorks = work.subworks || work.children;
                if (childWorks) {
                    const nextParentTitle = parentTitle || work.title;
                    const nextParentId = parentId || work.id;
                    childWorks.forEach(subwork => {
                        html += renderWork(subwork, nextParentTitle, nextParentId);
                    });
                }'''

# Also need to fix the container work check that uses subworks
old_container_check = '''} else if (work.subworks) {
                    // Container work - add anchor span so links can target it
                    html += `<span id="${elemId}"></span>`;
                }'''

new_container_check = '''} else if (work.subworks || work.children) {
                    // Container work - add anchor span so links can target it
                    html += `<span id="${elemId}"></span>`;
                }'''

# In buildWorkPageMap - add children handling after subworks
old_build_map = '''                    if (work.subworks) buildWorkPageMap(work.subworks);'''

new_build_map = '''                    if (work.subworks) buildWorkPageMap(work.subworks);
                    if (work.children) buildWorkPageMap(work.children);'''

count = 0
for html_file in TEXTS_DIR.rglob("index.html"):
    content = html_file.read_text(encoding='utf-8')
    modified = False
    
    if old_render_subworks in content:
        content = content.replace(old_render_subworks, new_render_subworks)
        modified = True
    
    if old_container_check in content:
        content = content.replace(old_container_check, new_container_check)
        modified = True
    
    if old_build_map in content:
        content = content.replace(old_build_map, new_build_map)
        modified = True
    
    if modified:
        html_file.write_text(content, encoding='utf-8')
        count += 1
        print(f"Updated: {html_file}")

print(f"\nTotal updated: {count} files")
