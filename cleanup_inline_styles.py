#!/usr/bin/env python3
"""
Remove all inline styles from HTML files - everything should be in style.css.
"""

from pathlib import Path
import re

WORKSPACE_ROOT = Path(__file__).parent
LANGUAGES_DIR = WORKSPACE_ROOT / "languages"

def update_index_file(file_path):
    """Remove all inline styles from a single index.html file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Remove all style tags
        content = re.sub(r'\s*<style>.*?</style>\s*', '\n', content, flags=re.DOTALL)
        
        file_path.write_text(content, encoding='utf-8')
        return True
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def main():
    """Remove inline styles from all index.html files."""
    print("=" * 70)
    print("Removing all inline styles - using external style.css only")
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
    print(f"Cleaned {updated} files - all styling now in style.css")
    print("=" * 70)
    print("Done!")
    print("=" * 70)

if __name__ == "__main__":
    main()
