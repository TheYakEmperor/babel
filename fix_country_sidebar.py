#!/usr/bin/env python3
"""
Fix country pages - remove duplicate sidebar content at end of files
"""

import os
import re
from pathlib import Path

def fix_country_page(file_path):
    """Remove duplicate sidebar from end of country pages"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Pattern to match the duplicate sidebar at the end (after main content closes)
    # The duplicate appears as:
    # </div>
    # <aside class="right-sidebar">...</aside>
    # </div>
    # We need to remove from the second <aside class="right-sidebar"> to its </aside>
    # but keep the </div> that closes the flex container
    
    # Find all aside blocks
    aside_pattern = r'<aside class="right-sidebar">.*?</aside>'
    asides = list(re.finditer(aside_pattern, content, re.DOTALL))
    
    if len(asides) >= 2:
        # Remove the second (duplicate) aside
        second_aside = asides[1]
        # Remove the aside and any surrounding whitespace/newlines
        start = second_aside.start()
        end = second_aside.end()
        
        # Look for whitespace/newlines before and after
        while start > 0 and content[start-1] in '\n\r\t ':
            start -= 1
        while end < len(content) and content[end] in '\n\r\t ':
            end += 1
            
        content = content[:start] + content[end:]
    
    # Now add the left-sidebar if missing
    if '<aside class="left-sidebar"></aside>' not in content:
        # Add it before the closing </div> that closes the flex container
        # The structure should be: right-sidebar, main-content, left-sidebar
        # Find the </div> before the script tags
        
        # Find where main-content ends and add left-sidebar after it
        # Look for pattern: </div>\n    </div>\n\n    \n    <!-- Tree toggle
        pattern = r'(</div>\s*</div>)\s*(\n\s*<!-- Tree toggle)'
        if re.search(pattern, content):
            content = re.sub(pattern, r'\1\n        <aside class="left-sidebar"></aside>\2', content)
        else:
            # Alternative: add before the closing </div> before scripts
            # Find </div> followed by script tags
            pattern2 = r'(</div>)\s*(\n\s*<script)'
            match = re.search(pattern2, content)
            if match:
                # Check if left-sidebar already there
                content = re.sub(pattern2, r'        <aside class="left-sidebar"></aside>\n    </div>\2', content, count=1)
    
    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    countries_dir = Path('/Users/yakking/Downloads/Web-design/Babel/countries')
    
    fixed = 0
    for country_dir in countries_dir.iterdir():
        if country_dir.is_dir():
            index_file = country_dir / 'index.html'
            if index_file.exists():
                if fix_country_page(index_file):
                    print(f"Fixed: {country_dir.name}")
                    fixed += 1
    
    print(f"\nTotal fixed: {fixed} country pages")

if __name__ == '__main__':
    main()
