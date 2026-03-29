#!/opt/homebrew/bin/python3.12
"""
Author Index Generator
======================
Scans all text archive pages, extracts authors, and generates/updates author pages.
Each author page automatically lists all texts by that author.

Usage: python3 index_authors.py
"""

import json
import os
import re
from pathlib import Path
from collections import defaultdict

# Load search index to look up language info
def load_language_index():
    """Load the search index and build a language lookup by Glottolog ID."""
    search_index_path = Path(__file__).parent / 'search-index.js'
    with open(search_index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse the JavaScript array
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

# Country code to name mapping
COUNTRY_NAMES = {
    'US': 'United States', 'GB': 'United Kingdom', 'CA': 'Canada', 'AU': 'Australia',
    'DE': 'Germany', 'FR': 'France', 'IT': 'Italy', 'ES': 'Spain', 'MX': 'Mexico',
    'BR': 'Brazil', 'JP': 'Japan', 'CN': 'China', 'IN': 'India', 'RU': 'Russia',
    'NL': 'Netherlands', 'BE': 'Belgium', 'CH': 'Switzerland', 'AT': 'Austria',
    'SE': 'Sweden', 'NO': 'Norway', 'DK': 'Denmark', 'FI': 'Finland', 'IE': 'Ireland',
    'PT': 'Portugal', 'PL': 'Poland', 'GR': 'Greece', 'TR': 'Turkey', 'ZA': 'South Africa',
    'EG': 'Egypt', 'NG': 'Nigeria', 'KE': 'Kenya', 'AR': 'Argentina', 'CL': 'Chile',
    'CO': 'Colombia', 'PE': 'Peru', 'VE': 'Venezuela', 'CU': 'Cuba', 'JM': 'Jamaica',
    'NZ': 'New Zealand', 'PH': 'Philippines', 'ID': 'Indonesia', 'MY': 'Malaysia',
    'TH': 'Thailand', 'VN': 'Vietnam', 'KR': 'South Korea', 'TW': 'Taiwan',
    'HK': 'Hong Kong', 'SG': 'Singapore', 'IL': 'Israel', 'SA': 'Saudi Arabia',
    'AE': 'United Arab Emirates', 'PK': 'Pakistan', 'BD': 'Bangladesh', 'IR': 'Iran',
    'IQ': 'Iraq', 'SY': 'Syria', 'LB': 'Lebanon', 'JO': 'Jordan', 'UA': 'Ukraine',
    'CZ': 'Czech Republic', 'HU': 'Hungary', 'RO': 'Romania', 'BG': 'Bulgaria',
}

def country_code_to_slug(code):
    """Convert country code to URL slug."""
    name = COUNTRY_NAMES.get(code.upper(), code)
    return name.lower().replace(' ', '-').replace("'", '')

def country_to_flag(country_code, base_path='../../'):
    """Convert ISO 3166-1 alpha-2 country code to linked flag image HTML."""
    if not country_code or len(country_code) != 2:
        return ''
    code = country_code.lower()
    slug = country_code_to_slug(country_code)
    return f'<a href="{base_path}countries/{slug}/index.html"><img src="https://flagcdn.com/w40/{code}.png" alt="{country_code}" class="country-flag"></a>'

def countries_to_flags(country_data, base_path='../../'):
    """Convert country code(s) to linked flag image(s). Supports string or list."""
    if not country_data:
        return ''
    if isinstance(country_data, str):
        country_data = [country_data]
    return ' '.join(country_to_flag(c, base_path) for c in country_data if c)

def find_parent_languages(lang_path):
    """Find all parent languages for a given language path."""
    if not lang_path:
        return []
    
    # Convert path to directory for comparison
    lang_dir = lang_path.replace('/index.html', '') + '/'
    
    parents = []
    for lang_id, lang_info in LANGUAGE_LOOKUP.items():
        other_path = lang_info.get('path', '')
        if not other_path:
            continue
        other_dir = other_path.replace('/index.html', '') + '/'
        
        # Check if lang_dir starts with other_dir (meaning other is an ancestor)
        if lang_dir.startswith(other_dir) and len(lang_dir) > len(other_dir):
            parents.append({
                'id': lang_id,
                'name': lang_info['name'],
                'path': other_path,
                'depth': len(other_dir)  # For sorting - deeper = closer parent
            })
    
    # Sort by depth descending to get closest parent first
    parents.sort(key=lambda x: x['depth'], reverse=True)
    return parents

def load_author_names(authors_dir):
    """Load author names from author.json files in each author folder."""
    names = {}
    if authors_dir.exists():
        for author_dir in authors_dir.iterdir():
            if author_dir.is_dir():
                author_json = author_dir / 'author.json'
                if author_json.exists():
                    with open(author_json, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        names[author_dir.name] = data.get('name', author_dir.name)
    return names

def extract_authors_from_json(json_path, html_path):
    """Extract author info from a data.json file."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    authors = []
    text_title = data.get('title', '')
    text_date = data.get('date', '')
    
    # Get author - can be string (legacy) or object with id
    author_data = data.get('author', '')
    if not author_data:
        return authors
    
    # Normalize to list
    if not isinstance(author_data, list):
        author_data = [author_data]
    
    # Support string, array of strings, object, or array of objects for language
    language_data = data.get('language', '')
    
    def normalize_lang(lang):
        if isinstance(lang, str):
            lang_info = LANGUAGE_LOOKUP.get(lang, {})
            return {
                'id': lang,
                'name': lang_info.get('name', lang),
                'path': lang_info.get('path', None),
                'level': lang_info.get('level', '')
            }
        else:
            lang_info = LANGUAGE_LOOKUP.get(lang.get('id', ''), {})
            return {
                'id': lang.get('id', ''),
                'name': lang.get('name') or lang_info.get('name', lang.get('id', '')),
                'path': lang.get('path') or lang_info.get('path', None),
                'level': lang_info.get('level', '')
            }
    
    def add_parent_languages(langs):
        """Add parent languages for any dialects that don't already have their parent listed."""
        result = list(langs)
        existing_paths = {l.get('path') for l in result if l.get('path')}
        
        for lang in langs:
            lang_path = lang.get('path')
            if not lang_path:
                continue
            
            # Only add parent for dialects, not for full languages
            if lang.get('level') != 'dialect':
                continue
            
            lang_dir = lang_path.replace('/index.html', '') + '/'
            
            # Check if any other language in the list is already an ancestor of this one
            has_ancestor_in_list = False
            # Check if this language already has a descendant in the list (so it's already a parent)
            has_descendant_in_list = False
            
            for other in langs:
                other_path = other.get('path')
                if other_path and other_path != lang_path:
                    other_dir = other_path.replace('/index.html', '') + '/'
                    if lang_dir.startswith(other_dir):
                        has_ancestor_in_list = True
                    if other_dir.startswith(lang_dir):
                        has_descendant_in_list = True
            
            # Only add parent if this dialect has no ancestor AND no descendant in the list
            if not has_ancestor_in_list and not has_descendant_in_list:
                parents = find_parent_languages(lang_path)
                if parents:
                    # Get the closest parent (first in the sorted list)
                    closest_parent = parents[0]
                    if closest_parent['path'] not in existing_paths:
                        result.append({
                            'id': closest_parent['id'],
                            'name': closest_parent['name'],
                            'path': closest_parent['path']
                        })
                        existing_paths.add(closest_parent['path'])
        
        return result
        
        return result
    
    if isinstance(language_data, list):
        languages = add_parent_languages([normalize_lang(l) for l in language_data])
    else:
        languages = add_parent_languages([normalize_lang(language_data)])
    
    for author in author_data:
        if isinstance(author, str):
            # Legacy string format - skip or create ID from name
            if not author or author.lower() in ('', 'anonymous', 'unknown'):
                continue
            # Create ID from name (slugify)
            author_id = re.sub(r'[^a-z0-9]+', '-', author.lower()).strip('-')
            author_name = author
        else:
            # Object format with id
            author_id = author.get('id', '')
            author_name = author.get('name', author_id)
            if not author_id:
                continue
        
        authors.append({
            'author_id': author_id,
            'author_name': author_name,
            'text_path': str(html_path),
            'text_title': text_title,
            'text_date': text_date,
            'languages': languages,
        })
    
    return authors

def extract_authors_from_text(html_path):
    """Extract author info from a text HTML file or data.json."""
    
    # Check for data.json in same directory (JSON-driven text)
    data_json_path = html_path.parent / 'data.json'
    if data_json_path.exists():
        return extract_authors_from_json(data_json_path, html_path)
    
    return []

def generate_author_page(author_id, author_name, entries, base_dir, metadata, all_author_names):
    """Generate HTML for an author page."""
    
    # Get custom metadata from author's own author.json
    author_meta = metadata.get(author_id, {})
    birth_death = author_meta.get('dates', '')
    description = author_meta.get('description', '')
    associated_ids = author_meta.get('associated', [])
    alias_data = author_meta.get('alias', [])
    country_data = author_meta.get('country', '')
    
    # Normalize alias to list and build display string
    if isinstance(alias_data, str):
        alias_data = [alias_data]
    alias_html = ', '.join(alias_data) if alias_data else ''
    
    # Convert country to flag emoji(s)
    country_flags = countries_to_flags(country_data)
    
    # Normalize associated to list
    if isinstance(associated_ids, str):
        associated_ids = [associated_ids]
    
    # Build associated links
    associated_html = ''
    if associated_ids:
        associated_links = []
        for assoc_id in associated_ids:
            if not assoc_id:
                continue
            # Look up display name from all_author_names
            assoc_name = all_author_names.get(assoc_id, assoc_id)
            associated_links.append(f'<a href="../{assoc_id}/index.html">{assoc_name}</a>')
        
        if associated_links:
            if len(associated_links) == 1:
                associated_html = associated_links[0]
            elif len(associated_links) == 2:
                associated_html = f'{associated_links[0]} and {associated_links[1]}'
            else:
                associated_html = ', '.join(associated_links[:-1]) + ', and ' + associated_links[-1]
    
    # Separate texts and works
    text_entries = [e for e in entries if not e.get('is_work')]
    work_entries = [e for e in entries if e.get('is_work')]
    
    # Count all texts by this author
    all_text_paths = set(t['text_path'] for t in text_entries)
    all_work_ids = set(w['work_id'] for w in work_entries)
    
    # Collect unique texts with all their languages
    text_map = {}
    for t in text_entries:
        key = t['text_path']
        if key not in text_map:
            text_map[key] = {
                'info': t,
                'languages': set(),
                'date': t.get('text_date', ''),
            }
        for lang in t.get('languages', []):
            text_map[key]['languages'].add((lang['name'], lang.get('path', '')))
    
    text_list_entries = list(text_map.values())
    
    # Build texts list HTML
    texts_html = []
    for entry in sorted(text_list_entries, key=lambda e: e['info']['text_title'].lower()):
        t = entry['info']
        rel_path = os.path.relpath(t['text_path'], base_dir / 'authors' / author_id)
        
        # Collect all language names and paths
        lang_entries = sorted(list(entry['languages']), key=lambda x: x[0])
        all_langs = '|'.join([name for name, path in lang_entries])
        lang_paths_json = json.dumps({name: path for name, path in lang_entries}).replace('"', '&quot;')
        
        # Get date for sorting
        text_date = entry.get('date', '') or ''
        date_sort = ''
        if text_date:
            year_match = re.search(r'(\d{3,4})', text_date)
            if year_match:
                date_sort = year_match.group(1)
        
        date_display = f' ({date_sort})' if date_sort else ''
        
        texts_html.append(f'''                <li class="child-language" data-title="{t['text_title']}" data-date="{date_sort}" data-langs="{all_langs}" data-lang-paths="{lang_paths_json}">
                    <a href="{rel_path}">{t['text_title']}</a>{date_display}
                </li>''')
    
    texts_list = '\n'.join(texts_html)
    
    # Texts section
    texts_section = ''
    if all_text_paths:
        texts_section = f'''
        <section class="children-section">
            <h2>Texts</h2>
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
'''
    
    # Build works list HTML with data attributes for sorting
    # First, organize works by parent (belongsTo)
    works_by_id = {w['work_id']: w for w in work_entries}
    parent_works = []  # Works that have no parent or whose parent isn't by this author
    child_works = defaultdict(list)  # work_id -> list of child works
    
    for w in work_entries:
        belongs_to = w.get('belongs_to', '')
        if belongs_to and belongs_to in works_by_id:
            # This work belongs to another work by the same author
            child_works[belongs_to].append(w)
        else:
            # Top-level work (no parent, or parent not by this author)
            parent_works.append(w)
    
    def format_work_item(w, indent=''):
        rel_path = os.path.relpath(base_dir / w['work_path'], base_dir / 'authors' / author_id)
        
        # Get date for sorting
        work_date = w.get('work_date', '') or ''
        date_sort = ''
        if work_date:
            year_match = re.search(r'(\d{3,4})', work_date)
            if year_match:
                date_sort = year_match.group(1)
        
        date_display = f' ({date_sort})' if date_sort else ''
        
        # Get all original languages (for hierarchy display)
        work_languages = w.get('work_languages', [])
        lang_names = '|'.join(l['name'] for l in work_languages) if work_languages else ''
        lang_paths_dict = {l['name']: l['path'] for l in work_languages}
        lang_paths_json = json.dumps(lang_paths_dict).replace('"', '&quot;') if lang_paths_dict else '{}'
        
        return f'''{indent}<li class="child-language" data-title="{w['work_title']}" data-date="{date_sort}" data-langs="{lang_names}" data-lang-paths="{lang_paths_json}">
{indent}    <a href="{rel_path}">{w['work_title']}</a>{date_display}
{indent}</li>'''
    
    works_html = []
    for w in sorted(parent_works, key=lambda e: e['work_title'].lower()):
        works_html.append(format_work_item(w, '                '))
        
        # Add any child works indented under this parent
        children = child_works.get(w['work_id'], [])
        if children:
            works_html.append('                <ul class="contained-works">')
            for child in sorted(children, key=lambda e: e['work_title'].lower()):
                works_html.append(format_work_item(child, '                    '))
            works_html.append('                </ul>')
    
    works_list = '\n'.join(works_html)
    
    # Works section with sort controls
    works_section = ''
    if all_work_ids:
        works_section = f'''
        <section class="children-section">
            <h2>Works</h2>
            <div class="sort-controls" id="works-sort-controls">
                <span>Sort by:</span>
                <button class="sort-btn active" data-sort="alpha" data-target="works-list">A-Z</button>
                <button class="sort-btn" data-sort="date" data-target="works-list">Date</button>
                <button class="sort-btn" data-sort="lang" data-target="works-list">Language</button>
            </div>
            <ul class="children-list sortable-list" id="works-list">
{works_list}
            </ul>
        </section>
'''
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{author_name}</title>
    <link rel="icon" type="image/webp" href="../../favicon.webp">
    <link rel="stylesheet" href="../../style.css">
</head>
<body>
    <div class="search-container">
        <input type="text" id="searchInput" class="search-bar" placeholder="Search languages and dialects...">
        <div id="searchResults" class="search-results"></div>
    </div>
    
    <div class="page-wrapper">
    <div class="header-logo-container"><a href="../../" class="header-logo"><img src="../../Wikilogo.webp" alt="Babel Archive"></a></div>
    <div class="container">
        <aside class="right-sidebar">
            <a href="../../" class="sidebar-logo">
                <img src="../../background-image/1111babel.png" alt="Babel Archive">
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
        <div class="main-content">
        <h1>{author_name}</h1>

        <div class="metadata">{f'''
            <p><strong>Also known as:</strong> {alias_html}</p>''' if alias_html else ''}{f'''
            <p><strong>Country:</strong> {country_flags}</p>''' if country_flags else ''}{f'''
            <p><strong>Dates:</strong> {birth_death}</p>''' if birth_death else ''}
            <p><strong>Author ID:</strong> <code>{author_id}</code></p>{f'''
            <p><strong>Associated with:</strong> {associated_html}</p>''' if associated_html else ''}{f'''
            <p><strong>Texts:</strong> {len(all_text_paths)}</p>''' if all_text_paths else ''}{f'''
            <p><strong>Works:</strong> {len(all_work_ids)}</p>''' if all_work_ids else ''}
        </div>
{f'''
        <section class="description">
            <p>{description}</p>
        </section>
''' if description else ''}{works_section}{texts_section}
</div>
        <aside class="left-sidebar"></aside>
    </div>
</div>

    <script src="../../search-index.js"></script>
    <script src="../../search.js"></script>
    <script>
    // Sort functionality for both texts and works lists
    var originalHTMLMap = {{}};
    var flatItemsMap = {{}};
    
    document.querySelectorAll('.sort-controls').forEach(function(controls) {{
        var targetId = controls.querySelector('.sort-btn').dataset.target;
        var list = targetId ? document.getElementById(targetId) : controls.parentElement.querySelector('.sortable-list');
        if (!list) return;
        
        controls.querySelectorAll('.sort-btn').forEach(function(btn) {{
            btn.addEventListener('click', function() {{
                // Update active state only within this control group
                controls.querySelectorAll('.sort-btn').forEach(function(b) {{ b.classList.remove('active'); }});
                btn.classList.add('active');
                
                var sortBy = btn.dataset.sort;
                var listId = list.id || 'default';
                
                // Store original HTML (with hierarchy) on first interaction
                if (!originalHTMLMap[listId]) {{
                    originalHTMLMap[listId] = list.innerHTML;
                    // Also store flat list of items for non-alpha sorting
                    flatItemsMap[listId] = Array.from(list.querySelectorAll('li.child-language')).map(function(li) {{
                        return li.cloneNode(true);
                    }});
                }}
                
                // For alpha sort, restore original hierarchical HTML
                if (sortBy === 'alpha') {{
                    list.innerHTML = originalHTMLMap[listId];
                    return;
                }}
                
                var originalItems = flatItemsMap[listId];
                list.innerHTML = '';
                
                if (sortBy === 'lang') {{
                    // Group by language with hierarchy support
                    var langPaths = {{}};
                    var itemLangs = [];
                    
                    // First pass: collect all language paths and item associations
                    originalItems.forEach(function(item, idx) {{
                        var langs = (item.dataset.langs || 'Unknown').split('|');
                        var paths = {{}};
                        try {{ paths = JSON.parse(item.dataset.langPaths || '{{}}'); }} catch(e) {{}}
                        
                        itemLangs[idx] = [];
                        langs.forEach(function(lang) {{
                            if (!lang) lang = 'Unknown';
                            var path = paths[lang] || '';
                            itemLangs[idx].push({{ name: lang, path: path }});
                            if (!langPaths[lang]) langPaths[lang] = path;
                        }});
                    }});
                    
                    // For each item, find the most specific language
                    var itemBestLang = [];
                    originalItems.forEach(function(item, idx) {{
                        var langs = itemLangs[idx];
                        if (langs.length === 1) {{
                            itemBestLang[idx] = langs[0];
                        }} else {{
                            var best = langs[0];
                            for (var i = 0; i < langs.length; i++) {{
                                var isChild = false;
                                for (var j = 0; j < langs.length; j++) {{
                                    if (i !== j && langs[i].path && langs[j].path) {{
                                        if (langs[i].path.indexOf(langs[j].path) === 0 && langs[i].path.length > langs[j].path.length) {{
                                            isChild = true;
                                            break;
                                        }}
                                    }}
                                }}
                                if (isChild) {{
                                    best = langs[i];
                                    break;
                                }}
                            }}
                            if (best === langs[0]) {{
                                langs.forEach(function(l) {{
                                    if (l.path.length > best.path.length) best = l;
                                }});
                            }}
                            itemBestLang[idx] = best;
                        }}
                    }});
                    
                    // Build hierarchy: find parent languages for each language
                    var langParent = {{}};
                    var allLangs = Object.keys(langPaths);
                    allLangs.forEach(function(lang) {{
                        var path = langPaths[lang];
                        if (!path) return;
                        // Get directory path (strip /index.html)
                        var dir = path.replace(/\\/index\\.html$/, '') + '/';
                        allLangs.forEach(function(other) {{
                            if (lang === other) return;
                            var otherPath = langPaths[other];
                            if (!otherPath) return;
                            // Get other directory path
                            var otherDir = otherPath.replace(/\\/index\\.html$/, '') + '/';
                            // Check if this lang's dir starts with other's dir (meaning other is ancestor)
                            if (dir.indexOf(otherDir) === 0 && dir.length > otherDir.length) {{
                                // Keep the closest parent (longest path)
                                if (!langParent[lang] || langPaths[langParent[lang]].length < otherPath.length) {{
                                    langParent[lang] = other;
                                }}
                            }}
                        }});
                    }});
                    
                    // Group items by their best language
                    var groups = {{}};
                    originalItems.forEach(function(item, idx) {{
                        var lang = itemBestLang[idx].name;
                        if (!groups[lang]) groups[lang] = [];
                        groups[lang].push(item.cloneNode(true));
                    }});
                    
                    // Find top-level languages and build child map
                    var childLangs = {{}};
                    var topLangs = [];
                    Object.keys(groups).forEach(function(lang) {{
                        var parent = langParent[lang];
                        if (parent && langPaths[parent]) {{
                            if (!childLangs[parent]) childLangs[parent] = [];
                            childLangs[parent].push(lang);
                            // Make sure the parent is a top-level lang
                            if (topLangs.indexOf(parent) === -1) {{
                                topLangs.push(parent);
                            }}
                        }} else {{
                            topLangs.push(lang);
                        }}
                    }});
                    
                    topLangs.sort();
                    
                    function renderLangGroup(lang, indent) {{
                        var header = document.createElement('li');
                        header.className = 'lang-group-header' + (indent ? ' lang-subgroup' : '');
                        if (langPaths[lang]) {{
                            header.innerHTML = '<strong><a href="../../' + langPaths[lang] + '" class="lang-group-link">' + lang + '</a></strong>';
                        }} else {{
                            header.innerHTML = '<strong>' + lang + '</strong>';
                        }}
                        list.appendChild(header);
                        
                        if (childLangs[lang]) {{
                            childLangs[lang].sort().forEach(function(child) {{
                                renderLangGroup(child, true);
                            }});
                        }}
                        
                        if (groups[lang]) {{
                            groups[lang].forEach(function(item) {{
                                if (indent) item.classList.add('lang-subitem');
                                list.appendChild(item);
                            }});
                        }}
                    }}
                    
                    topLangs.forEach(function(lang) {{
                        renderLangGroup(lang, false);
                    }});
                }} else if (sortBy === 'date') {{
                    var items = originalItems.map(function(item) {{ return item.cloneNode(true); }});
                    
                    items.sort(function(a, b) {{
                        var dateA = parseInt(a.dataset.date) || 9999;
                        var dateB = parseInt(b.dataset.date) || 9999;
                        return dateA - dateB;
                    }});
                    
                    items.forEach(function(item) {{ list.appendChild(item); }});
                }}
            }});
        }});
    }});
    </script>
</body>
</html>
'''
    return html

def generate_authors_index(authors_dir, all_authors, author_names):
    """Generate the main authors index page."""
    
    authors_html = []
    for author_id in sorted(all_authors.keys(), key=lambda x: author_names.get(x, x).lower()):
        author_name = author_names.get(author_id, author_id)
        entries = all_authors[author_id]
        text_entries = [t for t in entries if not t.get('is_work')]
        work_entries = [t for t in entries if t.get('is_work')]
        text_count = len(set(t['text_path'] for t in text_entries)) if text_entries else 0
        work_count = len(set(t['work_id'] for t in work_entries)) if work_entries else 0
        
        counts = []
        if text_count:
            counts.append(f"{text_count} text{'s' if text_count != 1 else ''}")
        if work_count:
            counts.append(f"{work_count} work{'s' if work_count != 1 else ''}")
        count_str = ', '.join(counts) if counts else 'no entries'
        
        authors_html.append(f'''                <li class="child-language">
                    <a href="{author_id}/index.html">{author_name}</a> ({count_str})
                </li>''')
    
    authors_list = '\n'.join(authors_html)
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Authors</title>
    <link rel="icon" type="image/webp" href="../favicon.webp">
    <link rel="stylesheet" href="../style.css">
</head>
<body>
    <div class="search-container">
        <input type="text" id="searchInput" class="search-bar" placeholder="Search languages and dialects...">
        <div id="searchResults" class="search-results"></div>
    </div>
    
    <div class="page-wrapper">
    <div class="header-logo-container"><a href="../" class="header-logo"><img src="../Wikilogo.webp" alt="Babel Archive"></a></div>
    <div class="container">
        <aside class="right-sidebar">
            <a href="../" class="sidebar-logo">
                <img src="../background-image/1111babel.png" alt="Babel Archive">
            </a>
            <nav class="sidebar-links">
            <h3>Navigate</h3>
            <ul>
                <li><a href="../">Home</a></li>
                <li><a href="../texts-index.html">All Texts</a></li>
                <li><a href="../languages/">Languages</a></li>
                <li><a href="../works/">Works Index</a></li>
                <li><a href="./">Authors</a></li>
                <li><a href="../sources/">Sources</a></li>
                <li><a href="../provenances/">Provenances</a></li>
                <li><a href="../collections/">Collections</a></li>
            </ul>
        </nav>
        </aside>
        <div class="main-content">
        <h1>Authors</h1>

        <div class="metadata">
            <p><strong>Total Authors:</strong> {len(all_authors)}</p>
        </div>

        <section class="children-section">
            <h2>All Authors</h2>
            <ul class="children-list">
{authors_list}
            </ul>
        </section>
</div>
        <aside class="left-sidebar"></aside>
    </div>
</div>

    <script src="../search-index.js"></script>
    <script src="../search.js"></script>
</body>
</html>
'''
    return html

def main():
    base_dir = Path(__file__).parent
    texts_dir = base_dir / 'texts'
    works_dir = base_dir / 'works'
    authors_dir = base_dir / 'authors'
    
    # Ensure authors directory exists
    authors_dir.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("AUTHOR INDEX GENERATOR")
    print("=" * 60)
    
    # Collect all authors from all texts
    print("\nScanning texts for authors...")
    all_authors = defaultdict(list)
    
    for html_path in texts_dir.rglob('index.html'):
        if 'TEMPLATE' in str(html_path):
            continue
        
        authors = extract_authors_from_text(html_path)
        for a in authors:
            all_authors[a['author_id']].append(a)
    
    print(f"   Found {len(all_authors)} unique authors from texts")
    
    # Also scan work.json files for work authors
    print("\nScanning works for authors...")
    work_authors_count = 0
    for work_json_path in works_dir.rglob('work.json'):
        with open(work_json_path, 'r', encoding='utf-8') as f:
            work_data = json.load(f)
        
        author_data = work_data.get('author', '')
        if not author_data:
            continue
        
        work_id = work_json_path.parent.name
        work_title = work_data.get('title', work_id)
        
        # Normalize author to list
        if not isinstance(author_data, list):
            author_data = [author_data]
        
        for author in author_data:
            if isinstance(author, str):
                if not author or author.lower() in ('', 'anonymous', 'unknown'):
                    continue
                author_id = re.sub(r'[^a-z0-9]+', '-', author.lower()).strip('-')
                author_name = author
            else:
                author_id = author.get('id', '')
                author_name = author.get('name', author_id)
                if not author_id:
                    continue
            
            # Get additional work metadata
            work_date = work_data.get('date', '')
            work_genre = work_data.get('genre', '')
            original_language = work_data.get('original_language', '')
            
            # Look up original language name(s) - support string or array
            work_languages = []
            if original_language:
                # Normalize to list
                lang_ids = original_language if isinstance(original_language, list) else [original_language]
                for lang_id in lang_ids:
                    lang_info = LANGUAGE_LOOKUP.get(lang_id, {})
                    work_languages.append({
                        'name': lang_info.get('name', lang_id),
                        'path': lang_info.get('path', ''),
                        'level': lang_info.get('level', '')
                    })
                
                # Add parent languages for any dialects (not full languages)
                existing_paths = {l.get('path') for l in work_languages if l.get('path')}
                for lang in list(work_languages):
                    lang_path = lang.get('path')
                    # Only add parent for dialects, not for full languages
                    if lang_path and lang.get('level') == 'dialect':
                        parents = find_parent_languages(lang_path)
                        if parents:
                            closest_parent = parents[0]
                            if closest_parent['path'] not in existing_paths:
                                work_languages.append({
                                    'name': closest_parent['name'],
                                    'path': closest_parent['path']
                                })
                                existing_paths.add(closest_parent['path'])
            
            # Get belongsTo for hierarchical display
            belongs_to = work_data.get('belongsTo', '')
            
            # Add as a "work" entry instead of a text entry
            all_authors[author_id].append({
                'author_id': author_id,
                'author_name': author_name,
                'work_path': f'works/{work_id}/index.html',
                'work_id': work_id,
                'work_title': work_title,
                'work_date': work_date,
                'work_genre': work_genre,
                'work_languages': work_languages,  # All languages with names and paths
                'is_work': True,
                'languages': [],
                'belongs_to': belongs_to,
            })
            work_authors_count += 1
    
    print(f"   Found {work_authors_count} author entries from works")
    
    # Load author names from author.json files
    author_names = load_author_names(authors_dir)
    print(f"   Loaded {len(author_names)} author names from author.json files")
    
    # Generate author pages
    print("\nGenerating author pages...")
    for author_id, texts in all_authors.items():
        # Load per-author metadata if it exists
        author_dir = authors_dir / author_id
        author_dir.mkdir(exist_ok=True)
        
        # Create author.json if it doesn't exist
        author_json_path = author_dir / 'author.json'
        if not author_json_path.exists():
            default_name = texts[0]['author_name']
            with open(author_json_path, 'w', encoding='utf-8') as f:
                json.dump({'name': default_name}, f, indent=2, ensure_ascii=False)
            author_names[author_id] = default_name
            print(f"   Created author.json for {author_id}")
        
        # Get canonical name from author.json
        author_name = author_names.get(author_id, texts[0]['author_name'])
        
        metadata = {}
        if author_json_path.exists():
            with open(author_json_path, 'r', encoding='utf-8') as f:
                metadata = {author_id: json.load(f)}
        
        # Generate page
        html = generate_author_page(author_id, author_name, texts, base_dir, metadata, author_names)
        
        # Write to file
        output_path = author_dir / "index.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        # Count texts and works separately
        text_entries = [t for t in texts if not t.get('is_work')]
        work_entries = [t for t in texts if t.get('is_work')]
        text_count = len(set(t['text_path'] for t in text_entries)) if text_entries else 0
        work_count = len(set(t['work_id'] for t in work_entries)) if work_entries else 0
        counts = []
        if text_count:
            counts.append(f"{text_count} text(s)")
        if work_count:
            counts.append(f"{work_count} work(s)")
        print(f"   {author_name} ({author_id}) — {', '.join(counts) if counts else 'no entries'}")
    
    # Generate main authors index
    print("\nGenerating authors index page...")
    index_html = generate_authors_index(authors_dir, all_authors, author_names)
    with open(authors_dir / 'index.html', 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    # Clean up orphan author pages
    existing_dirs = {d for d in authors_dir.iterdir() if d.is_dir()}
    valid_dirs = {authors_dir / author_id for author_id in all_authors.keys()}
    orphans = existing_dirs - valid_dirs
    
    for orphan in orphans:
        print(f"   Removing orphan: {orphan.name}/")
        import shutil
        shutil.rmtree(orphan)
    
    # Update search index with authors
    print("\nUpdating search index...")
    search_index_path = base_dir / 'search-index.js'
    
    with open(search_index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    json_match = re.search(r'const LANGUAGE_INDEX = (\[.*\]);', content, re.DOTALL)
    if json_match:
        index = json.loads(json_match.group(1))
        
        # Remove existing author entries
        index = [entry for entry in index if entry.get('level') != 'author']
        
        # Add author entries
        for author_id, texts in all_authors.items():
            author_name = author_names.get(author_id, texts[0]['author_name'])
            
            index.append({
                'name': author_name,
                'id': author_id,
                'level': 'author',
                'url': f'authors/{author_id}/index.html',
                'extinct': False,
                'alt': []
            })
        
        # Write back
        new_content = f'const LANGUAGE_INDEX = {json.dumps(index, indent=2, ensure_ascii=False)};'
        with open(search_index_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"   Added {len(all_authors)} authors to search index")
    
    print(f"\nGenerated {len(all_authors)} author pages in /authors/")
    print("=" * 60)

if __name__ == '__main__':
    main()
