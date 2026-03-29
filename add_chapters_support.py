#!/usr/bin/env python3
"""
Add support for chapters in text index.html files.
Chapters function like subworks in the TOC but don't have their own work pages.
"""

import os
import re
import glob

def update_index_html(filepath):
    """Update index.html to support chapters in buildWorksHtml."""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already updated (look for chapters handling)
    if 'work.chapters' in content:
        print(f"  Skipping {filepath} - already has chapters support")
        return False
    
    # Find the buildWorksHtml function and update it to handle chapters
    # The pattern we're looking for is the subworks recursion section
    old_pattern = r'''(// Recursively add subworks with increased indent\s+if \(work\.subworks && work\.subworks\.length > 0\) \{\s+itemHtml \+= buildWorksHtml\(work\.subworks, indent \+ 1\);\s+\})'''
    
    new_code = '''// Recursively add subworks with increased indent
            if (work.subworks && work.subworks.length > 0) {
                itemHtml += buildWorksHtml(work.subworks, indent + 1);
            }
            // Recursively add chapters with increased indent (chapters don't have work pages)
            if (work.chapters && work.chapters.length > 0) {
                itemHtml += buildWorksHtml(work.chapters, indent + 1);
            }'''
    
    new_content = re.sub(old_pattern, new_code, content)
    
    if new_content == content:
        print(f"  Warning: Pattern not found in {filepath}")
        return False
    
    # Also update collectTopLevelWorks to handle chapters in the merge logic
    # Find mergeSubworks and add a similar function for chapters
    
    # Check if we need to add chapter merging in collectTopLevelWorks
    old_merge_pattern = r'''(// Merge subworks if both have them\s+if \(existing\.subworks \|\| work\.subworks\) \{\s+existing\.subworks = mergeSubworks\(existing\.subworks, work\.subworks\);\s+\})'''
    
    new_merge_code = '''// Merge subworks if both have them
                    if (existing.subworks || work.subworks) {
                        existing.subworks = mergeSubworks(existing.subworks, work.subworks);
                    }
                    // Merge chapters if both have them (chapters don't have their own pages)
                    if (existing.chapters || work.chapters) {
                        existing.chapters = mergeSubworks(existing.chapters, work.chapters);
                    }'''
    
    new_content = re.sub(old_merge_pattern, new_merge_code, new_content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"  Updated {filepath}")
    return True

def main():
    base_dir = '/Users/yakking/Downloads/Web-design/Babel/texts/00/00'
    
    # Find all text index.html files
    pattern = os.path.join(base_dir, '*/index.html')
    files = glob.glob(pattern)
    
    print(f"Found {len(files)} text index.html files")
    
    updated = 0
    for filepath in sorted(files):
        if update_index_html(filepath):
            updated += 1
    
    print(f"\nUpdated {updated} files")

if __name__ == '__main__':
    main()
