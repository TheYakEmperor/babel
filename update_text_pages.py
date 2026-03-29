#!/usr/bin/env python3
"""
Update all JSON-driven text pages to add author support in metadata section.
"""

import os
import re
from pathlib import Path

def update_text_page(html_path):
    """Update a text page HTML to include author in metadata."""
    
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if it's a JSON-driven page (has data.json loading)
    if 'fetch(' not in content or 'data.json' not in content:
        return False
    
    # Check if author support already exists
    if 'data.author' in content:
        return False
    
    # Find the metadata section and add author support
    # Look for the pattern where source is added
    old_pattern = r"(if \(data\.source\) metaHtml \+= `<p><strong>Source:</strong> \$\{data\.source\}</p>`;)"
    
    # New code with author lookup and display
    new_code = '''// Author - look up from author.json
            if (data.author) {
                const authorId = data.author;
                // Try to fetch author name from author.json
                fetch(`../../../../authors/${authorId}/author.json`)
                    .then(r => r.ok ? r.json() : null)
                    .then(authorData => {
                        const authorName = authorData ? authorData.name : authorId;
                        const authorLink = `<a href="../../../../authors/${authorId}/index.html">${authorName}</a>`;
                        const authorP = document.createElement('p');
                        authorP.innerHTML = `<strong>Author:</strong> ${authorLink}`;
                        const metaDiv = document.getElementById('metadata');
                        const titleP = metaDiv.querySelector('p');
                        if (titleP) titleP.after(authorP);
                    })
                    .catch(() => {});
            }
            if (data.source) metaHtml += `<p><strong>Source:</strong> ${data.source}</p>`;'''
    
    new_content = re.sub(old_pattern, new_code, content)
    
    if new_content == content:
        print(f"  Could not find pattern to update in {html_path}")
        return False
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

def main():
    base_dir = Path(__file__).parent
    texts_dir = base_dir / 'texts'
    
    print("Updating JSON-driven text pages to add author support...\n")
    
    updated = 0
    skipped = 0
    
    for html_path in texts_dir.rglob('index.html'):
        if 'TEMPLATE' in str(html_path):
            continue
        
        # Check if there's a data.json
        data_json = html_path.parent / 'data.json'
        if not data_json.exists():
            continue
        
        if update_text_page(html_path):
            print(f"  Updated {html_path.relative_to(base_dir)}")
            updated += 1
        else:
            skipped += 1
    
    print(f"\nUpdated {updated} pages, skipped {skipped}")

if __name__ == '__main__':
    main()
