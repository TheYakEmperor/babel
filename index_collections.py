#!/opt/homebrew/bin/python3.12
"""
Collection Index Generator
======================
Scans all text archive pages, extracts collections, 
and generates collection pages. Each collection page lists all texts from that collection.

Usage: python3 index_collections.py
"""

import json
import os
import re
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).parent
TEXTS_DIR = BASE_DIR / 'texts'
COLLECTIONS_DIR = BASE_DIR / 'collections'


def load_collection_registry():
    """Load collection metadata from collection.json files."""
    registry = {}
    if COLLECTIONS_DIR.exists():
        for item in COLLECTIONS_DIR.iterdir():
            if item.is_dir() and (item / 'collection.json').exists():
                try:
                    with open(item / 'collection.json', 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        registry[item.name] = {
                            'name': data.get('name', item.name.replace('-', ' ').title()),
                            'description': data.get('description', '')
                        }
                except:
                    pass
    return registry

COLLECTION_REGISTRY = load_collection_registry()


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
            if entry.get('level') not in ('text', 'work', 'author'):
                lookup[entry['id']] = {
                    'name': entry['name'].lstrip('† '),
                    'path': 'languages/' + entry['url'],
                    'level': entry.get('level', '')
                }
        return lookup
    return {}

LANGUAGE_LOOKUP = load_language_index()


def normalize_lang(lang):
    """Convert language code or object to normalized form with name."""
    if isinstance(lang, str):
        lang_info = LANGUAGE_LOOKUP.get(lang, {})
        return {
            'id': lang,
            'name': lang_info.get('name', lang),
            'path': lang_info.get('path', None),
        }
    else:
        lang_info = LANGUAGE_LOOKUP.get(lang.get('id', ''), {})
        return {
            'id': lang.get('id', ''),
            'name': lang.get('name') or lang_info.get('name', lang.get('id', '')),
            'path': lang.get('path') or lang_info.get('path', None),
        }


def sanitize_folder_name(name):
    """Convert a name to a safe folder name/ID."""
    name = name.lower().strip()
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[\s_]+', '-', name)
    name = re.sub(r'-+', '-', name)
    return name.strip('-')[:50]


def escape_html(text):
    """Escape HTML special characters."""
    if not text:
        return ''
    return (str(text)
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;'))


def load_all_texts():
    """Load all text data from the texts directory."""
    texts = []
    for data_path in TEXTS_DIR.rglob('data.json'):
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                text_data = json.load(f)
                text_data['_path'] = str(data_path.parent / 'index.html')
                texts.append(text_data)
        except Exception as e:
            print(f"  Warning: Could not load {data_path}: {e}")
    return texts


def parse_date_for_sort(date_str):
    """Extract a sortable year from a date string."""
    if not date_str:
        return ''
    date_str = str(date_str)
    # Try to find a 4-digit year
    year_match = re.search(r'(\d{4})', date_str)
    if year_match:
        return year_match.group(1)
    # Try 3-digit year
    year_match = re.search(r'(\d{3})', date_str)
    if year_match:
        return year_match.group(1)
    return ''


def generate_collection_page(collection_name, collection_id, text_entries, base_dir):
    """Generate HTML for a collection page."""
    
    # Build texts list HTML with data attributes for sorting
    texts_html = []
    for t in sorted(text_entries, key=lambda x: x.get('title', '').lower()):
        rel_path = os.path.relpath(t['_path'], base_dir / 'collections' / collection_id)
        title = escape_html(t.get('title', 'Untitled'))
        date = t.get('date', '')
        date_sort = parse_date_for_sort(date)
        date_display = f' ({date})' if date else ''
        
        # Get language info - convert codes to names
        lang_data = t.get('language', '')
        if isinstance(lang_data, list):
            langs = [normalize_lang(l) for l in lang_data]
        elif lang_data:
            langs = [normalize_lang(lang_data)]
        else:
            langs = []
        
        lang_names = '|'.join(l['name'] for l in langs if l.get('name'))
        lang_paths = {l['name']: l['path'] for l in langs if l.get('name') and l.get('path')}
        lang_paths_json = json.dumps(lang_paths).replace('"', '&quot;') if lang_paths else '{}'
        
        texts_html.append(f'''                <li class="child-language" data-title="{escape_html(t.get('title', ''))}" data-date="{date_sort}" data-langs="{escape_html(lang_names)}" data-lang-paths="{lang_paths_json}">
                    <a href="{rel_path}">{title}</a>{date_display}
                </li>''')
    
    texts_list = '\n'.join(texts_html)
    text_count = len(text_entries)
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape_html(collection_name)}</title>
    <link rel="icon" type="image/webp" href="../../favicon.webp">
    <link rel="stylesheet" href="../../style.css">
</head>
<body>
    <div class="search-container">
        <input type="text" id="searchInput" class="search-bar" placeholder="Search languages and dialects...">
        <div id="searchResults" class="search-results"></div>
    </div>
    
    <div class="page-wrapper">
    <div class="container">
        <h1>{escape_html(collection_name)}</h1>

        <div class="metadata">
            <p><strong>Collection ID:</strong> <code>{collection_id}</code></p>
            <p><strong>Texts:</strong> {text_count}</p>
        </div>

        <section class="children-section">
            <h2>Texts in this Collection</h2>
            <div class="sort-controls" id="texts-sort-controls">
                <span>Sort by:</span>
                <button class="sort-btn active" data-sort="alpha" data-target="texts-list">A-Z</button>
                <button class="sort-btn" data-sort="date" data-target="texts-list">Date</button>
                <button class="sort-btn" data-sort="lang" data-target="texts-list">Language</button>
            </div>
            <ul class="children-list sortable-list" id="texts-list">
{texts_list}
            </ul>
        </section>

    <aside class="right-sidebar">
        <a href="../../" class="sidebar-logo">
            <img src="../../Wikilogo.webp" alt="Babel Archive">
        </a>
        <nav class="sidebar-links">
            <h3>Navigate</h3>
            <ul>
                <li><a href="../../">Home</a></li>
                <li><a href="../../texts-index.html">All Texts</a></li>
                <li><a href="../../languages/">Languages</a></li>
                <li><a href="../../works/">Works Index</a></li>
                <li><a href="../../authors/">Authors</a></li>
                <li><a href="../../sources/">Sources</a></li>
                <li><a href="../../provenances/">Provenances</a></li>
                <li><a href="../">Collections</a></li>
            </ul>
        </nav>
    </aside>
</div>

    <script src="../../search-index.js"></script>
    <script src="../../search.js"></script>
    <script>
    // Sort functionality
    var originalItems = null;
    var langPaths = {{}};
    
    document.querySelectorAll('.sort-controls').forEach(function(controls) {{
        var targetId = controls.querySelector('.sort-btn').dataset.target;
        var list = document.getElementById(targetId);
        if (!list) return;
        
        controls.querySelectorAll('.sort-btn').forEach(function(btn) {{
            btn.addEventListener('click', function() {{
                controls.querySelectorAll('.sort-btn').forEach(function(b) {{ b.classList.remove('active'); }});
                btn.classList.add('active');
                
                var sortBy = btn.dataset.sort;
                
                if (!originalItems) {{
                    originalItems = Array.from(list.querySelectorAll('li.child-language')).map(function(li) {{
                        // Collect all language paths
                        try {{
                            var paths = JSON.parse(li.dataset.langPaths || '{{}}');
                            Object.keys(paths).forEach(function(lang) {{
                                if (paths[lang]) langPaths[lang] = paths[lang];
                            }});
                        }} catch(e) {{}}
                        return li.cloneNode(true);
                    }});
                }}
                
                list.innerHTML = '';
                
                if (sortBy === 'lang') {{
                    var groups = {{}};
                    originalItems.forEach(function(item) {{
                        var langsStr = item.dataset.langs || 'Unknown';
                        var langs = langsStr.split('|');
                        langs.forEach(function(lang) {{
                            lang = lang.trim();
                            if (!groups[lang]) groups[lang] = [];
                            groups[lang].push(item.cloneNode(true));
                        }});
                    }});
                    
                    Object.keys(groups).sort().forEach(function(lang) {{
                        var header = document.createElement('li');
                        header.className = 'lang-group-header';
                        if (langPaths[lang]) {{
                            header.innerHTML = '<strong><a href="../../' + langPaths[lang] + '" class="lang-group-link">' + lang + '</a></strong>';
                        }} else {{
                            header.innerHTML = '<strong>' + lang + '</strong>';
                        }}
                        list.appendChild(header);
                        groups[lang].forEach(function(item) {{ list.appendChild(item); }});
                    }});
                }} else {{
                    var sorted = originalItems.slice().sort(function(a, b) {{
                        if (sortBy === 'date') {{
                            var dateA = parseInt(a.dataset.date) || 9999;
                            var dateB = parseInt(b.dataset.date) || 9999;
                            return dateA - dateB;
                        }}
                        return (a.dataset.title || '').localeCompare(b.dataset.title || '');
                    }});
                    sorted.forEach(function(item) {{ list.appendChild(item.cloneNode(true)); }});
                }}
            }});
        }});
    }});
    </script>
</body>
</html>
'''
    return html


def generate_collections_index(all_collections):
    """Generate the main collections index page."""
    
    collections_html = []
    for collection_id in sorted(all_collections.keys(), key=str.lower):
        # Get name from registry or generate from code
        if collection_id in COLLECTION_REGISTRY:
            collection_name = COLLECTION_REGISTRY[collection_id]['name']
        else:
            collection_name = ' '.join(word.capitalize() for word in collection_id.split('-'))
        text_count = len(all_collections[collection_id])
        count_str = f"{text_count} text{'s' if text_count != 1 else ''}"
        
        collections_html.append(f'''                <li class="child-language">
                    <a href="{collection_id}/index.html">{escape_html(collection_name)}</a> <code>{collection_id}</code> ({count_str})
                </li>''')
    
    collections_list = '\n'.join(collections_html)
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Collections</title>
    <link rel="icon" type="image/webp" href="../favicon.webp">
    <link rel="stylesheet" href="../style.css">
</head>
<body>
    <div class="search-container">
        <input type="text" id="searchInput" class="search-bar" placeholder="Search languages and dialects...">
        <div id="searchResults" class="search-results"></div>
    </div>
    
    <div class="page-wrapper">
    <div class="container">
        <h1>Collections</h1>

        <div class="metadata">
            <p><strong>Total Collections:</strong> {len(all_collections)}</p>
            <p>Browse texts by their collection.</p>
        </div>

        <section class="children-section">
            <h2>All Collections</h2>
            <ul class="children-list">
{collections_list}
            </ul>
        </section>

    <aside class="right-sidebar">
        <a href="../" class="sidebar-logo">
            <img src="../Wikilogo.webp" alt="Babel Archive">
        </a>
        <nav class="sidebar-links">
            <h3>Navigate</h3>
            <ul>
                <li><a href="../">Home</a></li>
                <li><a href="../texts-index.html">All Texts</a></li>
                <li><a href="../languages/">Languages</a></li>
                <li><a href="../works/">Works Index</a></li>
                <li><a href="../authors/">Authors</a></li>
                <li><a href="../sources/">Sources</a></li>
                <li><a href="../provenances/">Provenances</a></li>
                <li><a href="./">Collections</a></li>
            </ul>
        </nav>
    </aside>
</div>

    <script src="../search-index.js"></script>
    <script src="../search.js"></script>
</body>
</html>
'''
    return html


def main():
    print("=" * 60)
    print("COLLECTION INDEX GENERATOR")
    print("=" * 60)
    
    # Load all texts
    print("\nLoading texts...")
    texts = load_all_texts()
    print(f"   Found {len(texts)} texts")
    
    # Group texts by collection (collections is now an array of codes)
    print("\nGrouping texts by collection...")
    all_collections = defaultdict(list)
    
    for text in texts:
        # Handle both old 'collection' string and new 'collections' array formats
        collections = text.get('collections') or []
        if isinstance(collections, str):
            collections = [collections] if collections.strip() else []
        # Also check old 'collection' field for backwards compatibility
        old_collection = text.get('collection')
        if old_collection and isinstance(old_collection, str):
            old_id = sanitize_folder_name(old_collection)
            if old_id and old_id not in collections:
                collections.append(old_id)
        
        for collection_id in collections:
            collection_id = collection_id.strip() if collection_id else ''
            if collection_id:
                # Sanitize collection ID to match folder structure
                sanitized_id = sanitize_folder_name(collection_id)
                all_collections[sanitized_id].append(text)
    
    print(f"   Found {len(all_collections)} unique collections")
    
    # Ensure collections directory exists
    COLLECTIONS_DIR.mkdir(exist_ok=True)
    
    # Generate individual collection pages
    print("\nGenerating collection pages...")
    for collection_id, text_entries in all_collections.items():
        # Get name from registry or generate from code
        if collection_id in COLLECTION_REGISTRY:
            collection_name = COLLECTION_REGISTRY[collection_id]['name']
        else:
            collection_name = ' '.join(word.capitalize() for word in collection_id.split('-'))
        collection_dir = COLLECTIONS_DIR / collection_id
        collection_dir.mkdir(exist_ok=True)
        
        html = generate_collection_page(collection_name, collection_id, text_entries, BASE_DIR)
        
        with open(collection_dir / 'index.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"   - {collection_id} ({len(text_entries)} texts)")
    
    # Generate index page
    print("\nGenerating collections index page...")
    index_html = generate_collections_index(all_collections)
    
    with open(COLLECTIONS_DIR / 'index.html', 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    # Update search index
    print("\nUpdating search index...")
    search_index_path = BASE_DIR / 'search-index.js'
    
    with open(search_index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    json_match = re.search(r'const LANGUAGE_INDEX = (\[.*\]);', content, re.DOTALL)
    if json_match:
        index = json.loads(json_match.group(1))
        
        # Remove existing collection entries
        index = [entry for entry in index if entry.get('level') != 'collection']
        
        # Add collection entries
        for collection_id, text_entries in all_collections.items():
            if collection_id in COLLECTION_REGISTRY:
                collection_name = COLLECTION_REGISTRY[collection_id]['name']
            else:
                collection_name = ' '.join(word.capitalize() for word in collection_id.split('-'))
            
            index.append({
                'name': collection_name,
                'id': collection_id,
                'level': 'collection',
                'url': f'collections/{collection_id}/index.html',
                'extinct': False,
                'alt': []
            })
        
        new_content = f'const LANGUAGE_INDEX = {json.dumps(index, indent=2, ensure_ascii=False)};'
        with open(search_index_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"   Added {len(all_collections)} collections to search index")
    
    print(f"\nDone! Created {len(all_collections)} collection pages")


if __name__ == '__main__':
    main()
