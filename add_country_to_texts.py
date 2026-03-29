#!/usr/bin/env python3
"""Add country field support to all text pages."""

import os
import re

texts_dir = '/Users/yakking/Downloads/Web-design/Babel/texts'

# Pattern to match the metadata building section without country
old_pattern = r'''(\s*\.catch\(\(\) => \{\}\);
            \}
            if \(data\.source\))'''

new_replacement = r'''\1
            if (data.country) {
                const flags = countriesToFlags(data.country);
                metaHtml += `<p><strong>Country:</strong> <span class="country-flags">${flags}</span></p>`;
            }
            if (data.source)'''

# Find all index.html files
for root, dirs, files in os.walk(texts_dir):
    for f in files:
        if f == 'index.html':
            filepath = os.path.join(root, f)
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Skip if doesn't have the pattern or already has country
            if 'if (data.source)' not in content:
                continue
            if 'if (data.country)' in content:
                print(f"Already has country: {filepath}")
                continue
            
            # Add country check before source
            new_content = re.sub(
                r'(\.catch\(\(\) => \{\}\);\s*\n\s*\}\s*\n\s*)(if \(data\.source\))',
                r'\1if (data.country) {\n                const flags = countriesToFlags(data.country);\n                metaHtml += `<p><strong>Country:</strong> <span class="country-flags">${flags}</span></p>`;\n            }\n            \2',
                content
            )
            
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                print(f"Updated: {filepath}")
            else:
                print(f"No match: {filepath}")

print("Done!")
