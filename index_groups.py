#!/opt/homebrew/bin/python3.12
"""
Group Index Generator
======================
Scans all texts, works, and authors for group assignments
and generates group pages. Each group page lists all items in that group.

Usage: python3 index_groups.py
"""

import json
import os
import re
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).parent
TEXTS_DIR = BASE_DIR / 'texts'
WORKS_DIR = BASE_DIR / 'works'
AUTHORS_DIR = BASE_DIR / 'authors'
GROUPS_DIR = BASE_DIR / 'groups'


def load_group_registry():
    """Load group metadata from group.json files."""
    registry = {}
    if GROUPS_DIR.exists():
        for item in GROUPS_DIR.iterdir():
            if item.is_dir() and (item / 'group.json').exists():
                try:
                    with open(item / 'group.json', 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        registry[item.name] = {
                            'name': data.get('name', item.name.replace('-', ' ').title()),
                            'description': data.get('description', '')
                        }
                except:
                    pass
    return registry

GROUP_REGISTRY = load_group_registry()


# Load search index to look up language info
def load_language_index():
    """Load the search index and build a language lookup by Glottolog ID."""
    search_index_path = BASE_DIR / 'search-index.js'
    if not search_index_path.exists():
        return {}
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


def generate_group_page(group_id, texts, works, authors):
    """Generate a group page showing all items in that group."""
    group_info = GROUP_REGISTRY.get(group_id, {
        'name': group_id.replace('-', ' ').title(),
        'description': ''
    })
    group_name = group_info['name']
    description = group_info.get('description', '')
    
    # Build texts section
    texts_html = []
    for t in sorted(texts, key=lambda x: (x.get('title') or '').lower()):
        title = t.get('title', t['id'])
        date = t.get('date', '')
        date_display = f' <span class="date">({date})</span>' if date else ''
        date_sort = date if date else '9999'
        rel_path = f"../../texts/00/00/{t['id']}/"
        
        # Get languages
        lang_data = t.get('language', [])
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
                    <a href="{rel_path}">{escape_html(title)}</a>{date_display}
                </li>''')
    
    # Build works section
    works_html = []
    for w in sorted(works, key=lambda x: (x.get('title') or x['id']).lower()):
        title = w.get('fullTitle') or w.get('title') or w['id']
        date = w.get('date', '')
        date_display = f' <span class="date">({date})</span>' if date else ''
        rel_path = f"../../works/{w['id']}/"
        
        works_html.append(f'''                <li>
                    <a href="{rel_path}">{escape_html(title)}</a>{date_display}
                </li>''')
    
    # Build authors section
    authors_html = []
    for a in sorted(authors, key=lambda x: (x.get('name') or x['id']).lower()):
        name = a.get('name', a['id'])
        dates = ''
        if a.get('birth') or a.get('death'):
            dates = f" ({a.get('birth', '?')}–{a.get('death', '?')})"
        rel_path = f"../../authors/{a['id']}/"
        
        authors_html.append(f'''                <li>
                    <a href="{rel_path}">{escape_html(name)}{dates}</a>
                </li>''')
    
    texts_list = '\n'.join(texts_html) if texts_html else '<li class="no-items">No texts in this group</li>'
    works_list = '\n'.join(works_html) if works_html else '<li class="no-items">No works in this group</li>'
    authors_list = '\n'.join(authors_html) if authors_html else '<li class="no-items">No authors in this group</li>'
    
    text_count = len(texts)
    work_count = len(works)
    author_count = len(authors)
    total_count = text_count + work_count + author_count
    
    description_html = f'''
        <section class="description">
            <p>{escape_html(description)}</p>
        </section>
''' if description else ''
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape_html(group_name)}</title>
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
        <h1>{escape_html(group_name)}</h1>

        <div class="metadata">
            <p><strong>Group ID:</strong> <code>{group_id}</code></p>
            <p><strong>Items:</strong> {total_count} ({text_count} texts, {work_count} works, {author_count} authors)</p>
        </div>
{description_html}
        <section class="children-section">
            <h2>Texts</h2>
            <ul class="children-list sortable-list" id="texts-list">
{texts_list}
            </ul>
        </section>

        <section class="children-section">
            <h2>Works</h2>
            <ul class="children-list" id="works-list">
{works_list}
            </ul>
        </section>

        <section class="children-section">
            <h2>Authors</h2>
            <ul class="children-list" id="authors-list">
{authors_list}
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
                <li><a href="../">Groups</a></li>
            </ul>
        </nav>
    </aside>
</div>
</div>

    <script src="../../search-index.js"></script>
    <script src="../../search.js"></script>
</body>
</html>'''
    
    return html


def generate_groups_index(all_groups):
    """Generate the main groups index page."""
    groups_html = []
    
    for group_id in sorted(all_groups.keys(), key=lambda x: GROUP_REGISTRY.get(x, {}).get('name', x).lower()):
        group_info = GROUP_REGISTRY.get(group_id, {
            'name': group_id.replace('-', ' ').title(),
            'description': ''
        })
        group_name = group_info['name']
        
        text_count = len(all_groups[group_id]['texts'])
        work_count = len(all_groups[group_id]['works'])
        author_count = len(all_groups[group_id]['authors'])
        total = text_count + work_count + author_count
        
        groups_html.append(f'''            <li>
                <a href="{group_id}/">{escape_html(group_name)}</a>
                <span class="count">({total} items)</span>
            </li>''')
    
    groups_list = '\n'.join(groups_html) if groups_html else '<li class="no-items">No groups defined yet</li>'
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Groups - Babel Archive</title>
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
        <h1>Groups</h1>
        
        <p class="intro">Browse texts, works, and authors by category or topical grouping.</p>

        <section class="children-section">
            <ul class="children-list">
{groups_list}
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
                <li><a href="../collections/">Collections</a></li>
            </ul>
        </nav>
    </aside>
</div>
</div>

    <script src="../search-index.js"></script>
    <script src="../search.js"></script>
</body>
</html>'''
    
    return html


def main():
    print("Scanning for group assignments...")
    
    # Collect all items by group
    all_groups = defaultdict(lambda: {'texts': [], 'works': [], 'authors': []})
    
    # Scan texts
    texts_scanned = 0
    if TEXTS_DIR.exists():
        for path in TEXTS_DIR.glob('**/data.json'):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                groups = data.get('groups', [])
                if isinstance(groups, str):
                    groups = [groups] if groups else []
                
                for group_id in groups:
                    if group_id:
                        all_groups[group_id]['texts'].append({
                            'id': path.parent.name,
                            'title': data.get('title'),
                            'date': data.get('date'),
                            'language': data.get('language')
                        })
                
                texts_scanned += 1
            except Exception as e:
                print(f"  Error reading {path}: {e}")
    
    # Scan works
    works_scanned = 0
    if WORKS_DIR.exists():
        for path in WORKS_DIR.glob('*/work.json'):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                groups = data.get('groups', [])
                if isinstance(groups, str):
                    groups = [groups] if groups else []
                
                for group_id in groups:
                    if group_id:
                        all_groups[group_id]['works'].append({
                            'id': path.parent.name,
                            'title': data.get('title'),
                            'fullTitle': data.get('fullTitle'),
                            'date': data.get('date')
                        })
                
                works_scanned += 1
            except Exception as e:
                print(f"  Error reading {path}: {e}")
    
    # Scan authors
    authors_scanned = 0
    if AUTHORS_DIR.exists():
        for path in AUTHORS_DIR.glob('*/author.json'):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                groups = data.get('groups', [])
                if isinstance(groups, str):
                    groups = [groups] if groups else []
                
                for group_id in groups:
                    if group_id:
                        all_groups[group_id]['authors'].append({
                            'id': path.parent.name,
                            'name': data.get('name'),
                            'birth': data.get('birth'),
                            'death': data.get('death')
                        })
                
                authors_scanned += 1
            except Exception as e:
                print(f"  Error reading {path}: {e}")
    
    print(f"  Scanned {texts_scanned} texts, {works_scanned} works, {authors_scanned} authors")
    print(f"  Found {len(all_groups)} groups with assignments")
    
    # Ensure groups directory exists
    GROUPS_DIR.mkdir(exist_ok=True)
    
    # Also include groups from registry that may have no items yet
    for group_id in GROUP_REGISTRY:
        if group_id not in all_groups:
            all_groups[group_id] = {'texts': [], 'works': [], 'authors': []}
    
    # Generate group pages
    for group_id, items in all_groups.items():
        group_dir = GROUPS_DIR / group_id
        group_dir.mkdir(exist_ok=True)
        
        html = generate_group_page(group_id, items['texts'], items['works'], items['authors'])
        
        with open(group_dir / 'index.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        total = len(items['texts']) + len(items['works']) + len(items['authors'])
        print(f"  Generated: {group_id}/ ({total} items)")
    
    # Generate main groups index
    index_html = generate_groups_index(all_groups)
    with open(GROUPS_DIR / 'index.html', 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    print(f"Generated groups index with {len(all_groups)} groups")


if __name__ == '__main__':
    main()
