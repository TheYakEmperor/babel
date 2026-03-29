#!/usr/bin/env python3
"""
Final cleanup - remove orphaned closing tags and extra divs.
"""

from pathlib import Path
import re

WORKSPACE_ROOT = Path(__file__).parent
LANGUAGES_DIR = WORKSPACE_ROOT / "languages"

def update_index_file(file_path):
    """Final cleanup of a single index.html file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Remove orphaned closing tags that have no opening
        # Remove lines that are just closing divs at the start of body
        content = re.sub(r'<body>\s*(?:</div>)+', '<body>', content)
        
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        
        # Clean up spaces in head
        content = re.sub(r'</title>\s+<link', '</title>\n        <link', content)
        
        file_path.write_text(content, encoding='utf-8')
        return True
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def main():
    """Final cleanup of all index.html files."""
    print("=" * 70)
    print("Final cleanup - removing orphaned tags")
    print("=" * 70)
    
    html_files = list(LANGUAGES_DIR.glob('**/index.html'))
    print(f"Found {len(html_files)} index.html files")
    
    updated = 0
    for i, file_path in enumerate(html_files, 1):
        if update_index_file(file_path):
            updated += 1
        
        if i % 2000 == 0:
            print(f"  Processed {i} files...")
    
    print()
    print("=" * 70)
    print(f"Final cleanup complete")
    print("=" * 70)

if __name__ == "__main__":
    main()
