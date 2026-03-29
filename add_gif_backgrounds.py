#!/usr/bin/env python3
"""
Add inline styles to inject background GIFs with correct relative paths for each HTML file.
"""

from pathlib import Path
import re

WORKSPACE_ROOT = Path(__file__).parent
LANGUAGES_DIR = WORKSPACE_ROOT / "languages"

def get_relative_path_to_root(file_path):
    """Calculate relative path from file to root."""
    depth = len(file_path.relative_to(WORKSPACE_ROOT).parts) - 1
    return "../" * depth

def update_index_file(file_path):
    """Update a single index.html file with background image styles."""
    try:
        content = file_path.read_text(encoding='utf-8')
        relative_path = get_relative_path_to_root(file_path)
        
        # Create inline style for backgrounds that overrides style.css
        # This injects the correct relative paths for GIFs
        inline_style = f'''    <style>
        body {{
            background-image: url('{relative_path}gifs/stars.gif') !important;
        }}
        body::before {{
            background-image: url('{relative_path}gifs/planets.gif') !important;
        }}
    </style>'''
        
        # Remove old inline styles if any
        content = re.sub(r'<style>.*?</style>', '', content, flags=re.DOTALL)
        
        # Find head tag and add inline style
        head_end = content.find('</head>')
        if head_end != -1:
            content = content[:head_end] + inline_style + '\n    ' + content[head_end:]
        
        file_path.write_text(content, encoding='utf-8')
        return True
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def main():
    """Update all index.html files with background image styles."""
    print("=" * 70)
    print("Adding GIF background styles with correct relative paths")
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
    print(f"Updated {updated} files with GIF background styles")
    print(f"Stars GIF: gifs/stars.gif")
    print(f"Planets GIF: gifs/planets.gif")
    print("=" * 70)
    print("Done!")
    print("=" * 70)

if __name__ == "__main__":
    main()
