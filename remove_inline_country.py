#!/usr/bin/env python3
"""Remove inline country flag functions from text pages since they're now in text-reader.js"""

import re
from pathlib import Path

# Pattern to match the inline country flag helper block
pattern = re.compile(
    r'''    // Country flag helper functions\n'''
    r'''    const COUNTRY_NAMES = \{.*?\};\n'''
    r'''    function countryCodeToSlug\(code\) \{.*?\}\n'''
    r'''    function countryToFlag\(countryCode.*?\}\n'''
    r'''    function countriesToFlags\(countryData.*?\}\n'''
    r'''    \n''',
    re.DOTALL
)

texts_dir = Path('/Users/yakking/Downloads/Web-design/Babel/texts')

for html_file in texts_dir.rglob('index.html'):
    content = html_file.read_text()
    if 'const COUNTRY_NAMES' in content:
        new_content = pattern.sub('', content)
        if new_content != content:
            html_file.write_text(new_content)
            print(f"Fixed: {html_file}")
        else:
            print(f"Pattern not matched: {html_file}")
