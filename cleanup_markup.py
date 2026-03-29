#!/usr/bin/env python3
"""
Strip out all unnecessary HTML markup - keep only essential content.
Remove planet containers, extra divs, and clean up the structure.
"""

from pathlib import Path
import re

WORKSPACE_ROOT = Path(__file__).parent
LANGUAGES_DIR = WORKSPACE_ROOT / "languages"

def update_index_file(file_path):
    """Clean up a single index.html file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Remove the entire planet-container div and all planet divs
        content = re.sub(r'\s*<div class="planet-container">.*?</div>\s*', '', content, flags=re.DOTALL)
        content = re.sub(r'\s*<div class="planet[^"]*"[^>]*></div>\s*', '', content, flags=re.DOTALL)
        
        # Clean up excessive whitespace/newlines
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        
        file_path.write_text(content, encoding='utf-8')
        return True
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def main():
    """Clean up all index.html files."""
    print("=" * 70)
    print("Removing unnecessary planet markup from HTML")
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
    print(f"Cleaned {updated} files")
    print("=" * 70)
    print("Done!")
    print("=" * 70)

if __name__ == "__main__":
    main()
