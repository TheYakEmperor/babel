#!/usr/bin/env python3
"""
Fix language pages - move left-sidebar to correct position
The left-sidebar was incorrectly inserted in the middle of content.
It needs to be after main-content closes, before container closes.
"""

import os
import re
from pathlib import Path

def fix_language_page(file_path):
    """Fix left-sidebar position in language pages"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Check if left-sidebar is misplaced (not at the end before </div></div>)
    if '<aside class="left-sidebar"></aside>' not in content:
        return False  # No left-sidebar to fix
    
    # Remove the misplaced left-sidebar
    content = content.replace('<aside class="left-sidebar"></aside>', '')
    
    # Clean up any extra whitespace left behind
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    # Now we need to add it back in the right place
    # The correct structure ends with:
    # </footer>
    # </div></div>
    # <script>
    
    # Find the pattern where main-content should end and add left-sidebar
    # Looking for </div></div> followed by script tags
    pattern = r'(</footer>\s*)(</div></div>)(\s*<script)'
    
    if re.search(pattern, content):
        content = re.sub(
            pattern,
            r'\1    </div>\n        <aside class="left-sidebar"></aside>\n    </div>\3',
            content
        )
    else:
        # Alternative pattern - just </div></div> before scripts
        pattern2 = r'(</div></div>)(\s*<script src=)'
        if re.search(pattern2, content):
            content = re.sub(
                pattern2,
                r'    </div>\n        <aside class="left-sidebar"></aside>\n    </div>\2',
                content
            )
    
    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    languages_dir = Path('/Users/yakking/Downloads/Web-design/Babel/languages')
    
    fixed = 0
    total = 0
    
    for root, dirs, files in os.walk(languages_dir):
        for filename in files:
            if filename == 'index.html':
                file_path = Path(root) / filename
                total += 1
                if fix_language_page(file_path):
                    # Show relative path
                    rel_path = file_path.relative_to(languages_dir)
                    if fixed < 20:  # Only show first 20
                        print(f"Fixed: {rel_path}")
                    fixed += 1
    
    print(f"\nTotal fixed: {fixed} / {total} language pages")

if __name__ == '__main__':
    main()
