#!/usr/bin/env python3
"""Replace inline page viewer with external page-viewer.js script"""

import re
from pathlib import Path

texts_dir = Path('/Users/yakking/Downloads/Web-design/Babel/texts')

# Pattern to match the entire inline initPageViewer function
pattern = re.compile(
    r'    // Page viewer initialization\n    function initPageViewer\(pagesData\) \{.*?\n    \}\n',
    re.DOTALL
)

for html_file in texts_dir.rglob('index.html'):
    content = html_file.read_text()
    
    if 'function initPageViewer(pagesData)' not in content:
        continue
    
    # Remove inline initPageViewer
    new_content = pattern.sub('', content)
    
    # Add page-viewer.js script tag after text-reader.js if not already there
    if 'page-viewer.js' not in new_content:
        new_content = new_content.replace(
            '<script src="../../../../text-reader.js"></script>',
            '<script src="../../../../text-reader.js"></script>\n    <script src="../../../../page-viewer.js"></script>'
        )
    
    if new_content != content:
        html_file.write_text(new_content)
        print(f"Updated: {html_file}")
