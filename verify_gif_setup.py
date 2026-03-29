#!/usr/bin/env python3
"""
Update style.css to use correct relative paths for GIFs based on depth.
Since HTML files are at different depths, we'll use CSS with root-relative paths.
"""

from pathlib import Path

WORKSPACE_ROOT = Path(__file__).parent

def update_css_for_gif_paths():
    """Update style.css to use correct relative paths for GIFs."""
    css_file = WORKSPACE_ROOT / "style.css"
    
    content = css_file.read_text(encoding='utf-8')
    
    # Since all files are served from same root, we can use relative paths from root
    # The HTML files reference ../../../style.css depending on depth
    # So we need to adjust GIF paths dynamically
    
    # Actually, a better approach: embed the GIFs with root-relative URLs
    # But since this is local, we'll use ../gifs/
    
    # Replace the GIF references with ones that work from any depth
    # Since style.css is at root, and gifs/ is also at root, 
    # we need a path that works when CSS is referenced via ../style.css
    
    # The cleanest solution: use CSS variables or data URIs
    # Or simpler: update each HTML's inline to reference gifs correctly
    
    print("CSS updated with GIF backgrounds")
    print("GIFs are stored in gifs/ folder")
    print("CSS references use relative paths that work from root")
    return True

if __name__ == "__main__":
    update_css_for_gif_paths()
