#!/usr/bin/env python3
"""
Add texts to the search index.
Scans all text archive pages and adds them to search-index.js
"""

import json
import os
import re
from pathlib import Path

# Load search index to look up language info
def load_language_index():
    """Load the search index and build a language lookup by Glottolog ID."""
    search_index_path = Path(__file__).parent / 'search-index.js'
    with open(search_index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    json_match = re.search(r'const LANGUAGE_INDEX = (\[.*\]);', content, re.DOTALL)
    if json_match:
        index = json.loads(json_match.group(1))
        lookup = {}
        for entry in index:
            if entry.get('level') not in ('text', 'work'):
                lookup[entry['id']] = entry['name'].lstrip('† ')
        return lookup
    return {}

def load_work_metadata():
    """Load all work.json files to get canonical titles."""
    works_dir = Path(__file__).parent / 'works'
    work_meta = {}
    if works_dir.exists():
        for work_json in works_dir.rglob('work.json'):
            try:
                with open(work_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                work_id = work_json.parent.name
                work_meta[work_id] = data
            except:
                pass
    return work_meta

LANGUAGE_LOOKUP = load_language_index()
WORK_METADATA = load_work_metadata()

def extract_text_info_from_json(json_path):
    """Extract title and other info from a data.json file."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    info = {
        'title': data.get('title', ''),
        'id': data.get('id', ''),
    }
    
    # Get language name(s)
    lang_data = data.get('language', '')
    if isinstance(lang_data, list):
        # Get first language name for display
        first_lang = lang_data[0] if lang_data else ''
        if isinstance(first_lang, str):
            info['language'] = LANGUAGE_LOOKUP.get(first_lang, first_lang)
        else:
            info['language'] = first_lang.get('name', LANGUAGE_LOOKUP.get(first_lang.get('id', ''), ''))
    elif isinstance(lang_data, str):
        info['language'] = LANGUAGE_LOOKUP.get(lang_data, lang_data)
    else:
        info['language'] = lang_data.get('name', LANGUAGE_LOOKUP.get(lang_data.get('id', ''), ''))
    
    # Extract works recursively
    def extract_works(work, works_list, seen):
        elem_id = work.get('elementId', work.get('id', ''))
        work_id = work.get('id', '')
        title = work.get('title', '')
        
        if work_id and work_id not in seen:
            seen.add(work_id)
            works_list.append({'id': elem_id, 'work_id': work_id, 'title': title})
        
        for subwork in work.get('subworks', []):
            extract_works(subwork, works_list, seen)
    
    works = []
    seen = set()
    for page in data.get('pages', []):
        for work in page.get('works', []):
            extract_works(work, works, seen)
    
    info['works'] = works
    return info

def extract_text_info(html_path):
    """Extract title and other info from a text HTML file or data.json."""
    
    # Check for data.json (JSON-driven text)
    data_json_path = html_path.parent / 'data.json'
    if data_json_path.exists():
        return extract_text_info_from_json(data_json_path)
    
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    info = {}
    
    # Extract title from <h1>
    h1_match = re.search(r'<h1[^>]*>([^<]+)</h1>', content)
    if h1_match:
        info['title'] = h1_match.group(1).strip()
    else:
        # Try title tag
        title_match = re.search(r'<title>([^—<]+)', content)
        if title_match:
            info['title'] = title_match.group(1).strip()
    
    # Extract text ID from path
    id_match = re.search(r'/(\d{16})/', str(html_path))
    if id_match:
        info['id'] = id_match.group(1)
    
    # Extract language name
    lang_match = re.search(r'Text in[^<]*<a[^>]*><strong>([^<]+)</strong>', content)
    if lang_match:
        info['language'] = lang_match.group(1).strip()
    
    # Extract work titles and IDs from data-work-title and id attributes
    # Pattern matches: id="work-xxx" ... data-work-id="xxx" data-work-title="Title"
    work_matches = re.findall(r'id="([^"]+)"[^>]*data-work-id="([^"]+)"[^>]*data-work-title="([^"]+)"', content)
    # Remove duplicates by work-id while preserving order
    seen = set()
    unique_works = []
    for element_id, work_id, title in work_matches:
        if work_id not in seen:
            seen.add(work_id)
            unique_works.append({'id': element_id, 'work_id': work_id, 'title': title})
    info['works'] = unique_works
    
    return info

def get_relative_url(html_path, base_dir):
    """Get the URL relative to the base directory."""
    rel = os.path.relpath(html_path, base_dir)
    return rel

def main():
    base_dir = Path(__file__).parent
    texts_dir = base_dir / 'texts'
    search_index_path = base_dir / 'search-index.js'
    
    # Read existing search index
    with open(search_index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse existing index
    match = re.search(r'const LANGUAGE_INDEX = (\[[\s\S]*?\]);', content)
    if not match:
        print("Could not parse search-index.js")
        return
    
    index = json.loads(match.group(1))
    
    # Remove existing text entries
    index = [entry for entry in index if entry.get('level') != 'text']
    print(f"Existing language entries: {len(index)}")
    
    # Find all text HTML files
    text_entries = []
    for html_path in texts_dir.rglob('index.html'):
        if 'TEMPLATE' in str(html_path):
            continue
        
        info = extract_text_info(html_path)
        if not info.get('title'):
            print(f"  Skipping {html_path} - no title found")
            continue
        
        # Build search entry
        entry = {
            'name': info['title'],
            'id': info.get('id', ''),
            'level': 'text',
            'url': get_relative_url(html_path, base_dir),
            'extinct': False,
            'alt': []
        }
        
        # Add work titles as searchable terms (with element ID for linking)
        for work in info.get('works', []):
            # Look up canonical title from work.json, fall back to data.json title
            work_id = work.get('work_id', work.get('id', ''))
            work_meta = WORK_METADATA.get(work_id, {})
            canonical_title = work_meta.get('title', work_meta.get('fullTitle', work['title']))
            
            if canonical_title != info['title']:  # Don't duplicate if work title = text title
                # Format: work:Title#element-id
                entry['alt'].append(f"work:{canonical_title}#{work['id']}")
        
        text_entries.append(entry)
        works_str = f" (works: {', '.join(w['title'] for w in info.get('works', []))})"
        print(f"  Added: {info['title']}{works_str if info.get('works') else ''}")
    
    print(f"Found {len(text_entries)} texts")
    
    # Add texts to index
    index.extend(text_entries)
    
    # Sort alphabetically by name
    index.sort(key=lambda x: x['name'].lstrip('†').lower())
    
    # Write back
    new_content = 'const LANGUAGE_INDEX = ' + json.dumps(index, indent=2, ensure_ascii=False) + ';'
    with open(search_index_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"\nUpdated search-index.js with {len(index)} total entries")

if __name__ == '__main__':
    main()
