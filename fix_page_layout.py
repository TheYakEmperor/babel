#!/usr/bin/env python3
"""
Fix page layout for all non-text pages to match the new flex layout structure.
Converts old structure to new structure with header-logo-container and proper flex layout.
"""

import os
import re
import glob
from pathlib import Path

def get_relative_root(filepath):
    """Calculate relative path to root from a file"""
    rel = os.path.relpath(filepath, '/Users/yakking/Downloads/Web-design/Babel')
    depth = rel.count(os.sep)
    return '../' * depth

def fix_page_layout(filepath):
    """Fix the layout structure of a page"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Skip if already has the new structure
    if 'header-logo-container' in content:
        return False
    
    # Skip if doesn't have page-wrapper (root index pages)
    if '<div class="page-wrapper">' not in content:
        return False
    
    root_path = get_relative_root(filepath)
    
    # Pattern to find the old structure:
    # <div class="page-wrapper">
    # <div class="container">
    #   ... content ...
    #   <aside class="right-sidebar">
    #     <a href="..." class="sidebar-logo">
    #       <img src="...Wikilogo.webp" ...>
    #     </a>
    #     <nav class="sidebar-links">
    #       ...
    #     </nav>
    #   </aside>
    # </div>
    
    # First, extract sidebar content
    sidebar_match = re.search(
        r'<aside class="right-sidebar">\s*'
        r'<a href="[^"]*" class="sidebar-logo">\s*'
        r'<img[^>]*>\s*'
        r'</a>\s*'
        r'(<nav class="sidebar-links">.*?</nav>)\s*'
        r'</aside>',
        content,
        re.DOTALL
    )
    
    if not sidebar_match:
        # Try alternate pattern without sidebar-logo
        sidebar_match = re.search(
            r'<aside class="right-sidebar">\s*'
            r'(<nav class="sidebar-links">.*?</nav>)\s*'
            r'</aside>',
            content,
            re.DOTALL
        )
    
    if not sidebar_match:
        print(f"  Could not find sidebar in {filepath}")
        return False
    
    nav_content = sidebar_match.group(1)
    
    # Remove the old sidebar from content
    content = re.sub(
        r'\s*<aside class="right-sidebar">.*?</aside>\s*',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Find and replace the page-wrapper/container structure
    # Old: <div class="page-wrapper">\n<div class="container">
    # New: <div class="page-wrapper">\n    <div class="header-logo-container">...</div>\n        <div class="container">
    
    new_header = f'''<div class="page-wrapper">
    <div class="header-logo-container"><a href="{root_path}" class="header-logo"><img src="{root_path}Wikilogo.webp" alt="Babel Archive"></a></div>
        <div class="container">
        <aside class="right-sidebar">
            <a href="{root_path}" class="sidebar-logo">
                <img src="{root_path}background-image/1111babel.png" alt="Babel Archive">
            </a>
            {nav_content}
        </aside>
        <div class="main-content">'''
    
    content = re.sub(
        r'<div class="page-wrapper">\s*\n?\s*<div class="container">',
        new_header,
        content
    )
    
    # Find the closing </div> for container and add main-content closing + left-sidebar
    # We need to find </div>\s*</div> at the end (container close, page-wrapper close)
    # and insert the structure before it
    
    # Pattern: find the last </div> before scripts
    content = re.sub(
        r'</div>\s*(<script)',
        r'''</div>
        <aside class="left-sidebar"></aside>
    </div>
</div>

    \1''',
        content,
        count=1
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def main():
    base_path = '/Users/yakking/Downloads/Web-design/Babel'
    
    # Process different page types
    page_types = [
        ('authors', 'authors/*/index.html'),
        ('authors index', 'authors/index.html'),
        ('works', 'works/*/index.html'),
        ('works index', 'works/index.html'),
        ('sources', 'sources/*/index.html'),
        ('sources index', 'sources/index.html'),
        ('provenances', 'provenances/*/index.html'),
        ('provenances index', 'provenances/index.html'),
        ('collections', 'collections/*/index.html'),
        ('collections index', 'collections/index.html'),
        ('languages', 'languages/**/index.html'),
        ('texts-index', 'texts-index.html'),
        ('countries-index', 'countries-index.html'),
    ]
    
    total_fixed = 0
    
    for name, pattern in page_types:
        files = glob.glob(os.path.join(base_path, pattern), recursive=True)
        fixed = 0
        for f in files:
            # Skip text pages
            if '/texts/00/00/' in f:
                continue
            try:
                if fix_page_layout(f):
                    fixed += 1
            except Exception as e:
                print(f"Error processing {f}: {e}")
        
        if fixed > 0:
            print(f"{name}: fixed {fixed} pages")
            total_fixed += fixed
    
    print(f"\nTotal pages fixed: {total_fixed}")

if __name__ == '__main__':
    main()
