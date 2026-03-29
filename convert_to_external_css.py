#!/usr/bin/env python3
"""
Remove inline styles from all index.html files and use external style.css instead.
"""

from pathlib import Path
import re

WORKSPACE_ROOT = Path(__file__).parent
LANGUAGES_DIR = WORKSPACE_ROOT / "languages"

def get_relative_path_to_root(file_path):
    """Calculate relative path from file to root (style.css)."""
    # Count how many directories deep the file is
    depth = len(file_path.relative_to(WORKSPACE_ROOT).parts) - 1  # -1 because last part is filename
    return "../" * depth

def update_index_file(file_path):
    """Update a single index.html file to use external CSS."""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Remove all style tags
        content = re.sub(r'<style>.*?</style>', '', content, flags=re.DOTALL)
        
        # Calculate relative path to style.css
        relative_path = get_relative_path_to_root(file_path)
        css_link = f'<link rel="stylesheet" href="{relative_path}style.css">'
        
        # Find head tag and add link
        head_end = content.find('</head>')
        if head_end != -1:
            content = content[:head_end] + '    ' + css_link + '\n    ' + content[head_end:]
        
        file_path.write_text(content, encoding='utf-8')
        return True
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def main():
    """Update all index.html files in the languages directory."""
    print("=" * 70)
    print("Converting inline styles to external stylesheet")
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
    print(f"Updated {updated} files")
    print(f"External stylesheet: style.css ({Path(WORKSPACE_ROOT / 'style.css').stat().st_size / 1024:.1f} KB)")
    print("=" * 70)
    print("Done! All pages now use external CSS.")
    print("=" * 70)

if __name__ == "__main__":
    main()
