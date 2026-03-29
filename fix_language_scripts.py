#!/usr/bin/env python3
"""
Fix language pages to move search scripts to end of body.
The scripts need to run AFTER the sidebar is in the DOM.
"""

import os
import re
from pathlib import Path

def fix_language_page(filepath):
    """Move search scripts to end of body in a language page."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if this page has the script-before-sidebar issue
    # Pattern: search scripts appear before </body> but right after search-container
    
    # Find and remove the search scripts from their current location (after search-container)
    script_pattern = r'(</div>\s*\n\s*)<script src="([^"]*search-index\.js)"></script>\s*\n\s*<script src="([^"]*search\.js)"></script>\s*\n\s*<script>\s*function toggleLargeList[^<]*</script>'
    
    match = re.search(script_pattern, content)
    if not match:
        return False  # Page doesn't have this pattern
    
    search_index_path = match.group(2)
    search_js_path = match.group(3)
    
    # Remove the scripts from their current location
    content = re.sub(script_pattern, r'\1', content)
    
    # Find </body> and insert scripts before it
    scripts_block = f'''
    <script src="{search_index_path}"></script>
    <script src="{search_js_path}"></script>
'''
    
    content = content.replace('</body>', scripts_block + '</body>')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def main():
    base_dir = Path(__file__).parent
    languages_dir = base_dir / 'languages'
    
    print("=" * 60)
    print("FIXING LANGUAGE PAGE SCRIPTS")
    print("=" * 60)
    
    fixed_count = 0
    total_count = 0
    
    for html_file in languages_dir.rglob('index.html'):
        total_count += 1
        if fix_language_page(html_file):
            fixed_count += 1
    
    print(f"\nFixed {fixed_count} of {total_count} language pages")

if __name__ == '__main__':
    main()
