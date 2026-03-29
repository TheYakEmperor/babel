#!/usr/bin/env python3
"""Move search container into sidebar HTML for all pages"""
import os
import re

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Skip if already has search in sidebar
    if 'sidebar-links' in content and 'search-container' in content:
        # Check if search is already inside sidebar
        sidebar_match = re.search(r'<aside class="right-sidebar">.*?</aside>', content, re.DOTALL)
        if sidebar_match and 'search-container' in sidebar_match.group():
            return False  # Already done
    
    # Extract the search container
    search_match = re.search(r'<div class="search-container">.*?</div>\s*</div>', content, re.DOTALL)
    if not search_match:
        search_match = re.search(r'<div class="search-container">\s*<input[^>]*>\s*<div[^>]*></div>\s*</div>', content, re.DOTALL)
    
    if not search_match:
        return False
    
    search_html = search_match.group()
    
    # Remove original search container from body start
    content = content.replace(search_html, '', 1)
    
    # Clean up extra whitespace left behind
    content = re.sub(r'<body>\s+\s+<div class="page-wrapper">', '<body>\n    <div class="page-wrapper">', content)
    
    # Insert search after <h3>Navigate</h3> in sidebar
    content = re.sub(
        r'(<nav class="sidebar-links">\s*<h3>Navigate</h3>)',
        r'\1\n            ' + search_html.replace('\n', '\n            '),
        content
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return True

count = 0
for root, dirs, files in os.walk('/Users/yakking/Downloads/Web-design/Babel'):
    # Skip hidden dirs and glottolog
    dirs[:] = [d for d in dirs if not d.startswith('.') and 'glottolog' not in d]
    for fname in files:
        if fname.endswith('.html'):
            filepath = os.path.join(root, fname)
            if process_file(filepath):
                count += 1

print(f"Updated {count} files")
