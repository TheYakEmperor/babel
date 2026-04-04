#!/usr/bin/env python3
"""
Move page viewer to appear above the info box and language status line.
Current order: h1 → language-status → metadata → page-viewer → Transcription
New order: h1 → page-viewer → language-status → metadata → Transcription
"""

import os
import re
from pathlib import Path

def extract_page_viewer(content):
    """Extract the entire page-viewer div including all nested content."""
    # Find start of page-viewer
    start_marker = '<div class="page-viewer" id="page-viewer"'
    start_idx = content.find(start_marker)
    
    if start_idx == -1:
        return None, None, None
    
    # Check for preceding comment
    comment_pattern = r'<!--\s*Page Image Viewer[^>]*-->\s*$'
    text_before = content[:start_idx]
    comment_match = re.search(comment_pattern, text_before)
    if comment_match:
        actual_start = text_before.rfind('<!--', 0, comment_match.start() + 1)
        if actual_start == -1:
            actual_start = comment_match.start()
    else:
        actual_start = start_idx
    
    # Find matching closing </div> by counting
    depth = 0
    pos = start_idx
    end_idx = None
    
    while pos < len(content):
        open_div = content.find('<div', pos)
        close_div = content.find('</div>', pos)
        
        if close_div == -1:
            break
        
        if open_div != -1 and open_div < close_div:
            depth += 1
            pos = open_div + 4
        else:
            if depth == 1:
                end_idx = close_div + 6
                break
            depth -= 1
            pos = close_div + 6
    
    if end_idx is None:
        return None, None, None
    
    return actual_start, end_idx, content[actual_start:end_idx]

def move_page_viewer(content):
    """Move the page-viewer div to right after h1, before language-status and metadata."""
    
    start_idx, end_idx, page_viewer_html = extract_page_viewer(content)
    
    if page_viewer_html is None:
        return None, "Page viewer not found"
    
    # Check current position
    pv_pos = content.find('id="page-viewer"')
    meta_pos = content.find('id="metadata"')
    lang_pos = content.find('id="language-status"')
    
    # If page-viewer comes before both metadata and language-status, already done
    before_meta = meta_pos <= 0 or pv_pos < meta_pos
    before_lang = lang_pos <= 0 or pv_pos < lang_pos
    
    if before_meta and before_lang:
        return None, "Already in correct position"
    
    # Remove page-viewer from its current location
    content_without_pv = content[:start_idx].rstrip() + '\n\n        ' + content[end_idx:].lstrip()
    
    # Find the h1 end tag to insert after
    h1_pattern = r'<h1[^>]*id="page-title"[^>]*>[^<]*</h1>'
    h1_match = re.search(h1_pattern, content_without_pv)
    
    if not h1_match:
        # Try simpler pattern
        h1_pattern = r'<h1[^>]*>[^<]*</h1>'
        h1_match = re.search(h1_pattern, content_without_pv)
    
    if not h1_match:
        return None, "Could not find h1 tag"
    
    insert_pos = h1_match.end()
    
    # Clean up the page_viewer_html (remove extra whitespace)
    page_viewer_html = page_viewer_html.strip()
    
    # Build new content with page-viewer after h1
    new_content = (
        content_without_pv[:insert_pos] +
        '\n        \n        ' + page_viewer_html + '\n' +
        content_without_pv[insert_pos:]
    )
    
    return new_content, "Moved"

def process_text_file(filepath):
    """Process a single text index.html file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if page-viewer exists
    if 'page-viewer' not in content:
        return False, "No page-viewer"
    
    result, message = move_page_viewer(content)
    
    if result is None:
        return False, message
    
    if result == content:
        return False, "No changes needed"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(result)
    
    return True, message

def main():
    texts_dir = Path(__file__).parent / 'texts' / '00' / '00'
    
    if not texts_dir.exists():
        print(f"Texts directory not found: {texts_dir}")
        return
    
    updated = 0
    skipped = 0
    errors = 0
    
    for text_dir in sorted(texts_dir.iterdir()):
        if not text_dir.is_dir():
            continue
        
        index_file = text_dir / 'index.html'
        if not index_file.exists():
            continue
        
        success, message = process_text_file(index_file)
        
        text_id = text_dir.name
        if success:
            print(f"✓ {text_id}: {message}")
            updated += 1
        else:
            if "Already" in message or "No page-viewer" in message:
                skipped += 1
            else:
                print(f"✗ {text_id}: {message}")
                errors += 1
    
    print(f"\nSummary: {updated} updated, {skipped} skipped, {errors} errors")

if __name__ == "__main__":
    main()
