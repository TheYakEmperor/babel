#!/usr/bin/env python3
"""
Extract Glottolog language family tree structure and create folder hierarchy.
"""

import os
import csv
import urllib.request
import zipfile
import tempfile
from pathlib import Path
from collections import defaultdict

# Configuration
GLOTTOLOG_CSV_URL = "https://cdstar.eva.mpg.de//bitstreams/EAEA0-2198-D710-AA36-0/glottolog_languoid.csv.zip"
WORKSPACE_ROOT = Path(__file__).parent
LANGUAGES_DIR = WORKSPACE_ROOT / "languages"

def download_glottolog_csv():
    """Load the Glottolog languoid CSV file."""
    print("Loading Glottolog data...")
    csv_path = WORKSPACE_ROOT / "languoid.csv"
    
    try:
        if csv_path.exists():
            print(f"Found local copy at {csv_path}")
            return csv_path.read_text(encoding='utf-8')
        else:
            print(f"CSV file not found at {csv_path}")
            print("Please download glottolog_languoid.csv.zip from https://glottolog.org/meta/downloads")
            return None
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return None

def parse_glottolog_data(csv_content):
    """Parse the Glottolog CSV data and build language family tree."""
    lines = csv_content.strip().split('\n')
    reader = csv.DictReader(lines)
    
    language_data = {}
    family_hierarchy = defaultdict(list)
    
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
        
        if parent_id:
            family_hierarchy[parent_id].append(languoid_id)
    
    return language_data, family_hierarchy

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

def create_folder_structure(language_data, languages_dir):
    """Create the folder structure based on the language tree."""
    print(f"Creating folder structure in {languages_dir}...")
    
    languages_dir.mkdir(parents=True, exist_ok=True)
    
    created_count = 0
    failed_count = 0
    
    for languoid_id, data in language_data.items():
        try:
            # Build the full path
            path_parts = build_tree_path(languoid_id, language_data)
            
            # Convert path parts to language names
            folder_names = []
            for part_id in path_parts:
                part_name = language_data[part_id]['name']
                # Convert name to valid folder name
                folder_name = part_name.lower().replace(' ', '-').replace('/', '-')
                # Remove special characters
                folder_name = ''.join(c for c in folder_name if c.isalnum() or c in ('-', '_'))
                folder_names.append(folder_name)
            
            # Create the folder
            folder_path = languages_dir / '/'.join(folder_names)
            folder_path.mkdir(parents=True, exist_ok=True)
            
            created_count += 1
            
            if created_count % 100 == 0:
                print(f"  Created {created_count} folders...")
        
        except Exception as e:
            failed_count += 1
            if failed_count <= 10:  # Only print first 10 errors
                print(f"  Error creating folder for {languoid_id}: {e}")
    
    print(f"Created {created_count} folders ({failed_count} errors)")

def main():
    """Main execution."""
    print("=" * 60)
    print("Glottolog Language Family Tree Extractor")
    print("=" * 60)
    
    # Download and parse data
    csv_content = download_glottolog_csv()
    if not csv_content:
        print("Failed to download Glottolog data.")
        return
    
    print("Parsing language data...")
    language_data, family_hierarchy = parse_glottolog_data(csv_content)
    print(f"Found {len(language_data)} languoids")
    
    # Create folder structure
    create_folder_structure(language_data, LANGUAGES_DIR)
    
    print("\n" + "=" * 60)
    print("Done! Language folder structure created.")
    print(f"Location: {LANGUAGES_DIR}")
    print("=" * 60)

if __name__ == '__main__':
    main()
