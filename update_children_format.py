#!/usr/bin/env python3
"""
Update text index.html files to support unified children array format.
This replaces the old separate subworks/chapters handling with a single children array.
"""

import os
import re
import glob

def update_index_html(filepath):
    """Update index.html to support unified children format."""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already updated
    if 'work.children' in content and 'child.isChapter' in content:
        print(f"  Skipping {filepath} - already updated")
        return False
    
    # Find and replace the subworks/chapters handling in buildWorksHtml
    old_pattern = r'''(// Recursively add subworks with increased indent\s+if \(work\.subworks && work\.subworks\.length > 0\) \{\s+itemHtml \+= buildWorksHtml\(work\.subworks, indent \+ 1\);\s+\}\s+// Recursively add chapters with increased indent \(chapters don't have work pages\)\s+if \(work\.chapters && work\.chapters\.length > 0\) \{\s+itemHtml \+= buildWorksHtml\(work\.chapters, indent \+ 1\);\s+\})'''
    
    new_code = '''// Recursively add children (unified subworks + chapters, preserves order)
            if (work.children && work.children.length > 0) {
                itemHtml += buildWorksHtml(work.children, indent + 1);
            }
            // Backward compatibility: also check old separate arrays
            if (work.subworks && work.subworks.length > 0) {
                itemHtml += buildWorksHtml(work.subworks, indent + 1);
            }
            if (work.chapters && work.chapters.length > 0) {
                itemHtml += buildWorksHtml(work.chapters, indent + 1);
            }'''
    
    new_content = re.sub(old_pattern, new_code, content)
    
    if new_content == content:
        # Try simpler pattern
        old_pattern2 = r'''// Recursively add subworks with increased indent\s+if \(work\.subworks && work\.subworks\.length > 0\) \{\s+itemHtml \+= buildWorksHtml\(work\.subworks, indent \+ 1\);\s+\}\s+// Recursively add chapters with increased indent \(chapters don't have work pages\)\s+if \(work\.chapters && work\.chapters\.length > 0\) \{\s+itemHtml \+= buildWorksHtml\(work\.chapters, indent \+ 1\);\s+\}'''
        
        new_content = re.sub(old_pattern2, new_code, content)
    
    if new_content == content:
        print(f"  Warning: Pattern not found in {filepath}")
        return False
    
    # Also update collectTopLevelWorks to merge children arrays
    # Find the mergeSubworks section and add children merging
    old_merge = r'''(// Merge subworks if both have them\s+if \(existing\.subworks \|\| work\.subworks\) \{\s+existing\.subworks = mergeSubworks\(existing\.subworks, work\.subworks\);\s+\}\s+// Merge chapters if both have them \(chapters don't have their own pages\)\s+if \(existing\.chapters \|\| work\.chapters\) \{\s+existing\.chapters = mergeSubworks\(existing\.chapters, work\.chapters\);\s+\})'''
    
    new_merge = '''// Merge children if both have them (new unified format)
                    if (existing.children || work.children) {
                        existing.children = mergeSubworks(existing.children, work.children);
                    }
                    // Merge subworks if both have them (backward compat)
                    if (existing.subworks || work.subworks) {
                        existing.subworks = mergeSubworks(existing.subworks, work.subworks);
                    }
                    // Merge chapters if both have them (backward compat)
                    if (existing.chapters || work.chapters) {
                        existing.chapters = mergeSubworks(existing.chapters, work.chapters);
                    }'''
    
    new_content = re.sub(old_merge, new_merge, new_content)
    
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
