#!/usr/bin/env python3
"""
Fix page layout for country pages to match the new flex layout structure.
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

def fix_country_page(filepath):
    """Fix the layout structure of a country page"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Skip if already has the new structure
    if 'header-logo-container' in content:
        return False
    
    root_path = get_relative_root(filepath)
    
    # Find search-container and page-wrapper
    if '<div class="page-wrapper">' not in content:
        return False
    
    # Replace the old structure
    # Old: <div class="page-wrapper">\n    <div class="container">
    # New: with header-logo-container and sidebars
    
    new_start = f'''<div class="page-wrapper">
    <div class="header-logo-container"><a href="{root_path}" class="header-logo"><img src="{root_path}Wikilogo.webp" alt="Babel Archive"></a></div>
        <div class="container">
        <aside class="right-sidebar">
            <a href="{root_path}" class="sidebar-logo">
                <img src="{root_path}background-image/1111babel.png" alt="Babel Archive">
            </a>
            <nav class="sidebar-links">
                <h3>Navigate</h3>
                <ul>
                    <li><a href="{root_path}">Home</a></li>
                    <li><a href="{root_path}texts-index.html">All Texts</a></li>
                    <li><a href="{root_path}languages/">Languages</a></li>
                    <li><a href="{root_path}works/">Works Index</a></li>
                    <li><a href="{root_path}authors/">Authors</a></li>
                    <li><a href="{root_path}sources/">Sources</a></li>
                    <li><a href="{root_path}provenances/">Provenances</a></li>
                    <li><a href="{root_path}collections/">Collections</a></li>
                </ul>
            </nav>
        </aside>
        <div class="main-content">'''
    
    content = re.sub(
        r'<div class="page-wrapper">\s*\n?\s*<div class="container">',
        new_start,
        content
    )
    
    # Add closing for main-content and left-sidebar before scripts at end
    # Find </div>\s*</div> before script tags
    content = re.sub(
        r'(</div>\s*)\n(\s*<script src="[^"]*search)',
        r'\1\n        </div>\n        <aside class="left-sidebar"></aside>\n    </div>\n</div>\n\n    \2',
        content
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def main():
    base_path = '/Users/yakking/Downloads/Web-design/Babel'
    
    # Process country pages
    files = glob.glob(os.path.join(base_path, 'countries/*/index.html'))
    fixed = 0
    for f in files:
        try:
            if fix_country_page(f):
                fixed += 1
        except Exception as e:
            print(f"Error processing {f}: {e}")
    
    print(f"Fixed {fixed} country pages")

if __name__ == '__main__':
    main()
