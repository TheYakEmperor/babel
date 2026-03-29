#!/opt/homebrew/bin/python3.12
"""
Provenance Index Generator
==========================
Scans all text archive pages, extracts provenances (origin locations), 
and generates provenance pages. Each provenance page lists all texts from that location.

Usage: python3 index_provenances.py
"""

import json
import os
import re
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).parent
TEXTS_DIR = BASE_DIR / 'texts'
PROVENANCES_DIR = BASE_DIR / 'provenances'


def load_provenance_registry():
    """Load all provenance.json files from provenances directories."""
    registry = {}
    if PROVENANCES_DIR.exists():
        for item in PROVENANCES_DIR.iterdir():
            if item.is_dir():
                provenance_json = item / 'provenance.json'
                if provenance_json.exists():
                    try:
                        with open(provenance_json, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            provenance_id = item.name
                            registry[provenance_id] = data
                    except:
                        pass
    return registry

PROVENANCE_REGISTRY = load_provenance_registry()


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


def generate_provenance_page(provenance_name, provenance_id, text_entries, base_dir):
    """Generate HTML for a provenance page."""
    
    # Build texts list HTML with data attributes for sorting
    texts_html = []
    for t in sorted(text_entries, key=lambda x: x.get('title', '').lower()):
        rel_path = os.path.relpath(t['_path'], base_dir / 'provenances' / provenance_id)
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
    <title>{escape_html(provenance_name)}</title>
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
        <h1>{escape_html(provenance_name)}</h1>

        <div class="metadata">
            <p><strong>Provenance ID:</strong> <code>{provenance_id}</code></p>
            <p><strong>Texts:</strong> {text_count}</p>
        </div>

        <section class="children-section">
            <h2>Texts from this Location</h2>
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
                <li><a href="../../collections/">Collections</a></li>
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


def generate_provenances_index(all_provenances):
    """Generate the main provenances index page."""
    
    provenances_html = []
    for provenance_id_or_name in sorted(all_provenances.keys(), key=str.lower):
        provenance_id = sanitize_folder_name(provenance_id_or_name)
        
        # Get display name from registry, or format from id/name
        if provenance_id in PROVENANCE_REGISTRY:
            provenance_name = PROVENANCE_REGISTRY[provenance_id]['name']
        else:
            provenance_name = ' '.join(word.capitalize() for word in provenance_id_or_name.replace('-', ' ').split())
        
        text_count = len(all_provenances[provenance_id_or_name])
        count_str = f"{text_count} text{'s' if text_count != 1 else ''}"
        
        provenances_html.append(f'''                <li class="child-language">
                    <a href="{provenance_id}/index.html">{escape_html(provenance_name)}</a> ({count_str})
                </li>''')
    
    provenances_list = '\n'.join(provenances_html)
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Provenances</title>
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
        <h1>Provenances</h1>

        <div class="metadata">
            <p><strong>Total Provenances:</strong> {len(all_provenances)}</p>
            <p>Browse texts by their origin location.</p>
        </div>

        <section class="children-section">
            <h2>All Provenances</h2>
            <ul class="children-list">
{provenances_list}
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
                <li><a href="./">Provenances</a></li>
                <li><a href="../collections/">Collections</a></li>
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
    print("PROVENANCE INDEX GENERATOR")
    print("=" * 60)
    
    # Load all texts
    print("\nLoading texts...")
    texts = load_all_texts()
    print(f"   Found {len(texts)} texts")
    
    # Group texts by provenance
    print("\nGrouping texts by provenance...")
    all_provenances = defaultdict(list)
    
    for text in texts:
        # Handle both old format (single string) and new format (array of codes)
        provenances_data = text.get('provenances', [])
        provenance_legacy = text.get('provenance', '')
        
        # If provenances array exists and is not empty, use it
        if provenances_data and isinstance(provenances_data, list):
            for provenance_code in provenances_data:
                if provenance_code:
                    all_provenances[provenance_code].append(text)
        # Fall back to legacy single provenance field
        elif provenance_legacy:
            provenance_legacy = provenance_legacy.strip()
            if provenance_legacy:
                all_provenances[provenance_legacy].append(text)
    
    print(f"   Found {len(all_provenances)} unique provenances")
    
    # Ensure provenances directory exists
    PROVENANCES_DIR.mkdir(exist_ok=True)
    
    # Generate individual provenance pages
    if all_provenances:
        print("\nGenerating provenance pages...")
        for provenance_id_or_name, text_entries in all_provenances.items():
            provenance_id = sanitize_folder_name(provenance_id_or_name)
            
            # Get display name from registry, or format from id/name
            if provenance_id in PROVENANCE_REGISTRY:
                provenance_name = PROVENANCE_REGISTRY[provenance_id]['name']
            else:
                provenance_name = ' '.join(word.capitalize() for word in provenance_id_or_name.replace('-', ' ').split())
            
            provenance_dir = PROVENANCES_DIR / provenance_id
            provenance_dir.mkdir(exist_ok=True)
            
            html = generate_provenance_page(provenance_name, provenance_id, text_entries, BASE_DIR)
            
            with open(provenance_dir / 'index.html', 'w', encoding='utf-8') as f:
                f.write(html)
            
            print(f"   {provenance_name} ({len(text_entries)} texts)")
    else:
        print("\n   No provenances found in texts yet.")
    
    # Generate index page
    print("\nGenerating provenances index page...")
    index_html = generate_provenances_index(all_provenances)
    
    with open(PROVENANCES_DIR / 'index.html', 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    # Update search index
    print("\nUpdating search index...")
    search_index_path = BASE_DIR / 'search-index.js'
    
    with open(search_index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    json_match = re.search(r'const LANGUAGE_INDEX = (\[.*\]);', content, re.DOTALL)
    if json_match:
        index = json.loads(json_match.group(1))
        
        # Remove existing provenance entries
        index = [entry for entry in index if entry.get('level') != 'provenance']
        
        # Add provenance entries
        for provenance_id_or_name, text_entries in all_provenances.items():
            provenance_id = sanitize_folder_name(provenance_id_or_name)
            
            if provenance_id in PROVENANCE_REGISTRY:
                provenance_name = PROVENANCE_REGISTRY[provenance_id]['name']
            else:
                provenance_name = ' '.join(word.capitalize() for word in provenance_id_or_name.replace('-', ' ').split())
            
            index.append({
                'name': provenance_name,
                'id': provenance_id,
                'level': 'provenance',
                'url': f'provenances/{provenance_id}/index.html',
                'extinct': False,
                'alt': []
            })
        
        new_content = f'const LANGUAGE_INDEX = {json.dumps(index, indent=2, ensure_ascii=False)};'
        with open(search_index_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"   Added {len(all_provenances)} provenances to search index")
    
    print(f"\nDone! Created {len(all_provenances)} provenance pages")


if __name__ == '__main__':
    main()
