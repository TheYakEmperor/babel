#!/usr/bin/env python3
"""
Create index.html files for each language and dialect in Glottolog.
"""

import csv
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).parent
LANGUAGES_DIR = WORKSPACE_ROOT / "languages"
CSV_FILE = WORKSPACE_ROOT / "languoid.csv"

def sanitize_folder_name(name):
    """Convert a language name to the folder name format."""
    folder_name = name.lower().replace(' ', '-').replace('/', '-')
    # Remove special characters
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

def generate_index_html(name, languoid_id, level, iso_code=None, folder_depth=1):
    """Generate HTML content for an index.html file."""
    status = "Extinct" if level == "dialect" else "Active"
    iso_info = f"<p><strong>ISO 639-3 Code:</strong> {iso_code}</p>" if iso_code else ""
    
    # Calculate relative path to root based on folder depth
    # Language pages are in /languages/..., so we need one extra level up
    root_path = '../' * (folder_depth + 1)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name}</title>
    <link rel="icon" type="image/webp" href="{root_path}favicon.webp">
    <link rel="stylesheet" href="{root_path}style.css">
    <!-- Stylesheet injected by update_family_trees.py -->
</head>
<body>
    <div class="page-wrapper">
    <div class="container">
        <h1>{name}</h1>
        
        <div class="metadata">
            <p><strong>Type:</strong> <span class="level-tag {level.lower()}">{level.capitalize()}</span></p>
            <p><strong>Glottolog ID:</strong> {languoid_id}</p>
            {iso_info}
        </div>
        
        <section>
            <h2>Information</h2>
            <p>This page is for the {name} language/dialect.</p>
            <p>Data sourced from <a href="https://glottolog.org">Glottolog</a>, a comprehensive reference information for the world's languages.</p>
        </section>
        
        <section>
            <h2>Resources</h2>
            <ul>
                <li><a href="https://glottolog.org/resource/languoid/id/{languoid_id}">View on Glottolog</a></li>
                <li><a href="https://www.wals.info">World Atlas of Language Structures (WALS)</a></li>
                <li><a href="https://www.ethnologue.com">Ethnologue</a></li>
            </ul>
        </section>
        
        <hr>
        <footer>
            <p><small>Generated from Glottolog 5.2 data. Last updated: January 12, 2026</small></p>
        </footer>
    </div>
    
    <aside class="right-sidebar">
        <a href="{root_path}" class="sidebar-logo">
            <img src="{root_path}Wikilogo.webp" alt="Babel Archive">
        </a>
        <nav class="sidebar-links">
            <h3>Navigate</h3>
            <ul>
                <li><a href="{root_path}">Home</a></li>
                <li><a href="{root_path}texts-index.html">All Texts</a></li>
                <li><a href="{root_path}languages/">Languages</a></li>
                <li><a href="{root_path}works/">Works Index</a></li>
                <li><a href="{root_path}authors/">Authors</a></li>
                <li><a href="{root_path}sources/">Sources</a></li>
                <li><a href="{root_path}provenances/">Provenances</a></li>
                <li><a href="{root_path}collections/">Collections</a></li>
            </ul>
        </nav>
    </aside>
    </div>
</body>
</html>"""
    return html

def main():
    """Main execution."""
    print("=" * 70)
    print("Creating index.html files for languages and dialects")
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
                iso_code = row.get('iso639P3code', '').strip()
                
                if not languoid_id or not name:
                    continue
                
                language_data[languoid_id] = {
                    'name': name,
                    'parent_id': parent_id,
                    'level': level,
                    'iso_code': iso_code
                }
                
                # Track languages, dialects, and families
                if level in ['language', 'dialect', 'family']:
                    languages_and_dialects.append({
                        'id': languoid_id,
                        'name': name,
                        'level': level,
                        'iso_code': iso_code
                    })
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return
    
    print(f"Found {len(language_data)} total languoids")
    print(f"Found {len(languages_and_dialects)} languages and dialects")
    
    # Create index.html files
    print("\nCreating index.html files...")
    created_count = 0
    missing_count = 0
    error_count = 0
    
    for item in languages_and_dialects:
        try:
            languoid_id = item['id']
            name = item['name']
            level = item['level']
            iso_code = item['iso_code']
            
            # Build the folder path
            path_parts = build_tree_path(languoid_id, language_data)
            if not path_parts:
                missing_count += 1
                continue
            
            # Convert to folder names
            folder_names = []
            for part_id in path_parts:
                part_name = language_data[part_id]['name']
                folder_name = sanitize_folder_name(part_name)
                folder_names.append(folder_name)
            
            # Create the index.html file
            folder_path = LANGUAGES_DIR / '/'.join(folder_names)
            index_file = folder_path / "index.html"
            
            if not folder_path.exists():
                missing_count += 1
                continue
            
            # folder_depth is the number of subfolders from languages/
            folder_depth = len(folder_names)
            html_content = generate_index_html(name, languoid_id, level, iso_code, folder_depth)
            index_file.write_text(html_content, encoding='utf-8')
            
            created_count += 1
            
            if created_count % 1000 == 0:
                print(f"  Created {created_count} index files...")
        
        except Exception as e:
            error_count += 1
            if error_count <= 10:  # Print first 10 errors
                print(f"  Error for {languoid_id}: {e}")
    
    print(f"\nCreated {created_count} index.html files")
    if missing_count > 0:
        print(f"{missing_count} folders not found")
    if error_count > 0:
        print(f"{error_count} errors encountered")
    
    print("\n" + "=" * 70)
    print("Done!")
    print("=" * 70)

if __name__ == '__main__':
    main()
