#!/usr/bin/env python3
"""
Fix country pages - ensure left-sidebar is inside the container
"""

import os
import re
from pathlib import Path

def fix_country_page(file_path):
    """Fix left-sidebar position in country pages"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Fix the pattern where left-sidebar is after </div></div>
    # Change: </div></div>\n        <aside class="left-sidebar"></aside>
    # To:    </div>\n        <aside class="left-sidebar"></aside>\n    </div>
    
    pattern = r'</div></div>\s*<aside class="left-sidebar"></aside>'
    if re.search(pattern, content):
        content = re.sub(
            pattern,
            '    </div>\n        <aside class="left-sidebar"></aside>\n    </div>',
            content
        )
    
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
