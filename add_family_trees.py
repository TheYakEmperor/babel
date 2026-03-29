#!/usr/bin/env python3
"""
Add interactive family tree to all language/dialect index.html files.
"""

import csv
from pathlib import Path
from collections import defaultdict

WORKSPACE_ROOT = Path(__file__).parent
LANGUAGES_DIR = WORKSPACE_ROOT / "languages"
CSV_FILE = WORKSPACE_ROOT / "languoid.csv"

def sanitize_folder_name(name):
    """Convert a language name to the folder name format."""
    folder_name = name.lower().replace(' ', '-').replace('/', '-')
    folder_name = ''.join(c for c in folder_name if c.isalnum() or c in ('-', '_'))
    return folder_name

def build_tree_path(languoid_id, language_data, memo=None):
    """Build the full path from root to a languoid."""
    if memo is None:
        memo = {}
    
    if languoid_id in memo:
        return memo[languoid_id]
    
    if languoid_id not in language_data:
        return []
    
    data = language_data[languoid_id]
    parent_id = data['parent_id']
    
    if parent_id and parent_id in language_data:
        path = build_tree_path(parent_id, language_data, memo)
    else:
        path = []
    
    path.append(languoid_id)
    memo[languoid_id] = path
    return path

def get_siblings(languoid_id, language_data, parent_map=None):
    """Get all siblings of a languoid."""
    if languoid_id not in language_data:
        return []
    
    parent_id = language_data[languoid_id]['parent_id']
    if not parent_id:
        return []
    
    # Use pre-built parent map for efficiency
    if parent_map and parent_id in parent_map:
        siblings = [lid for lid in parent_map[parent_id] if lid != languoid_id]
        return sorted(siblings, key=lambda x: language_data[x]['name'])
    
    return []

def generate_tree_html(languoid_id, language_data, parent_map, base_path=""):
    """Generate the interactive family tree HTML."""
    path_ids = build_tree_path(languoid_id, language_data)
    
    html_parts = []
    html_parts.append('<div class="family-tree">')
    html_parts.append('<details open>')
    
    # Build the tree from root
    for depth, node_id in enumerate(path_ids):
        node_data = language_data[node_id]
        node_name = node_data['name']
        siblings = get_siblings(node_id, language_data, parent_map)
        is_current = (node_id == languoid_id)
        
        # Create folder path for this node
        path_to_node = path_ids[:depth+1]
        folder_names = []
        for pid in path_to_node:
            pname = language_data[pid]['name']
            folder_names.append(sanitize_folder_name(pname))
        
        folder_path = '/'.join(folder_names)
        node_url = f"/{folder_path}/"
        
        # Determine if this node has children
        has_children = any(data['parent_id'] == node_id for data in language_data.values())
        
        indent = "  " * depth
        
        # Close previous level if we're going back up
        if depth > 0:
            html_parts.append(f'{indent}</details>')
            html_parts.append(f'{indent}</li>')
        
        if depth > 0:
            html_parts.append(f'{indent}<li>')
        
        # Current node
        current_class = ' class="current"' if is_current else ''
        html_parts.append(f'{indent}<a href="{node_url}"{current_class}>{node_name}</a>')
        
        # Show siblings
        if siblings:
            html_parts.append(f'{indent}<ul class="siblings">')
            for sib_id in siblings:
                sib_name = language_data[sib_id]['name']
                sib_path = path_ids[:depth] + [sib_id]
                sib_folder_names = []
                for pid in sib_path:
                    pname = language_data[pid]['name']
                    sib_folder_names.append(sanitize_folder_name(pname))
                sib_url = '/' + '/'.join(sib_folder_names) + '/'
                html_parts.append(f'{indent}  <li><a href="{sib_url}">{sib_name}</a></li>')
            html_parts.append(f'{indent}</ul>')
        
        # Open details for next level if not the last
        if depth < len(path_ids) - 1:
            html_parts.append(f'{indent}<details open>')
    
    # Close remaining details
    for depth in range(len(path_ids) - 2, -1, -1):
        indent = "  " * depth
        html_parts.append(f'{indent}</details>')
        if depth > 0:
            html_parts.append(f'{indent}</li>')
    
    html_parts.append('</details>')
    html_parts.append('</div>')
    
    return '\n'.join(html_parts)

def get_tree_css():
    """Get the CSS for the family tree."""
    return """
        .family-tree {
            background: #f9f9f9;
            border: 1px solid #e0e0e0;
            border-radius: 0;
            padding: 20px;
            margin: 20px 0;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 0.95em;
        }
        
        .family-tree details {
            margin: 8px 0;
        }
        
        .family-tree details > summary {
            cursor: pointer;
            user-select: none;
            color: #2c3e50;
            font-weight: 500;
            padding: 4px 0;
        }
        
        .family-tree details > summary:hover {
            color: #3498db;
        }
        
        .family-tree details > summary::marker {
            color: #3498db;
        }
        
        .family-tree a {
            color: #3498db;
            text-decoration: none;
            transition: all 0.2s ease;
        }
        
        .family-tree a:hover {
            color: #2980b9;
            text-decoration: underline;
        }
        
        .family-tree a.current {
            color: #27ae60;
            font-weight: bold;
            background: #d4edda;
            padding: 2px 6px;
            border-radius: 0;
        }
        
        .family-tree ul {
            list-style: none;
            padding: 4px 0 4px 20px;
            margin: 4px 0;
            border-left: 2px solid #ecf0f1;
        }
        
        .family-tree ul.siblings {
            border-left: 2px dashed #bdc3c7;
            margin: 8px 0 8px 0;
            padding-left: 20px;
        }
        
        .family-tree ul.siblings li {
            padding: 2px 0;
            font-size: 0.9em;
            color: #555;
        }
        
        .family-tree ul li {
            padding: 2px 0;
        }
"""

def inject_tree_into_html(html_content, tree_html, tree_css):
    """Inject the family tree into an existing HTML file."""
    # Add CSS to head if not already present
    if '<style>' not in html_content:
        head_end = html_content.find('</head>')
        if head_end != -1:
            style_tag = f'<style>{tree_css}</style>'
            html_content = html_content[:head_end] + style_tag + html_content[head_end:]
    else:
        # Add to existing style tag
        style_end = html_content.find('</style>')
        if style_end != -1:
            html_content = html_content[:style_end] + tree_css + html_content[style_end:]
    
    # Find where to inject the tree (after metadata section, before Information section)
    insert_marker = '<section>'
    insert_pos = html_content.find(insert_marker)
    if insert_pos == -1:
        # Fallback: insert before closing container
        insert_marker = '</div>\n</body>'
        insert_pos = html_content.find(insert_marker)
    
    if insert_pos != -1:
        tree_section = f'''
        <section>
            <h2>Language Family Tree</h2>
{tree_html}
        </section>
        
'''
        html_content = html_content[:insert_pos] + tree_section + html_content[insert_pos:]
    
    return html_content

def main():
    """Main execution."""
    print("=" * 70)
    print("Adding family trees to language index files")
    print("=" * 70)
    
    # Read the CSV file
    print("Reading languoid data...")
    language_data = {}
    languages_and_dialects = []
    
    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row:
                    continue
                
                languoid_id = row.get('id', '').strip()
                name = row.get('name', '').strip()
                parent_id = row.get('parent_id', '').strip()
                level = row.get('level', '').strip()
                
                if not languoid_id or not name:
                    continue
                
                language_data[languoid_id] = {
                    'name': name,
                    'parent_id': parent_id,
                    'level': level
                }
                
                if level in ['language', 'dialect']:
                    languages_and_dialects.append(languoid_id)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return
    
    print(f"Found {len(language_data)} total languoids")
    print(f"Found {len(languages_and_dialects)} languages and dialects")
    
    # Build parent map for efficiency
    print("Building parent map...")
    parent_map = defaultdict(list)
    for lid, data in language_data.items():
        if data['parent_id']:
            parent_map[data['parent_id']].append(lid)
    
    # Get CSS once
    tree_css = get_tree_css()
    
    # Update index.html files
    print("\nUpdating index.html files with family trees...")
    updated_count = 0
    error_count = 0
    
    for i, languoid_id in enumerate(languages_and_dialects):
        try:
            path_parts = build_tree_path(languoid_id, language_data)
            if not path_parts:
                continue
            
            # Convert to folder names
            folder_names = []
            for part_id in path_parts:
                part_name = language_data[part_id]['name']
                folder_name = sanitize_folder_name(part_name)
                folder_names.append(folder_name)
            
            # Find the index.html file
            folder_path = LANGUAGES_DIR / '/'.join(folder_names)
            index_file = folder_path / "index.html"
            
            if not index_file.exists():
                continue
            
            # Read current HTML
            html_content = index_file.read_text(encoding='utf-8')
            
            # Skip if tree already exists
            if 'family-tree' in html_content:
                continue
            
            # Generate tree
            tree_html = generate_tree_html(languoid_id, language_data, parent_map)
            
            # Inject tree
            updated_html = inject_tree_into_html(html_content, tree_html, tree_css)
            
            # Write back
            index_file.write_text(updated_html, encoding='utf-8')
            
            updated_count += 1
            
            if updated_count % 2000 == 0:
                print(f"  Updated {updated_count} files...")
        
        except Exception as e:
            error_count += 1
            if error_count <= 5:
                print(f"  Error for {languoid_id}: {e}")
    
    print(f"\nUpdated {updated_count} index.html files")
    if error_count > 0:
        print(f"{error_count} errors encountered")
    
    print("\n" + "=" * 70)
    print("Done! Family trees added to all language/dialect pages.")
    print("=" * 70)

if __name__ == '__main__':
    main()
