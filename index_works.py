#!/opt/homebrew/bin/python3.12
"""
Work Index Generator
====================
Scans all text archive pages, extracts works, and generates/updates work pages.
Each work page automatically lists all texts containing that work.

Usage: python3 index_works.py
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
            if entry.get('level') not in ('text', 'work'):
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

def extract_works_from_json(json_path, html_path):
    """Extract work info from a data.json file."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    works = []
    text_title = data.get('title', '')
    text_date = data.get('date', '')  # Extract date from text
    
    # Support string, array of strings, object, or array of objects for language
    language_data = data.get('language', '')
    
    # Normalize to list of dicts with id, name, path, level
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
        """Add parent languages for any dialects that don't already have an ancestor in the list."""
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
    
    if isinstance(language_data, list):
        languages = add_parent_languages([normalize_lang(l) for l in language_data])
    else:
        languages = add_parent_languages([normalize_lang(language_data)])
    
    def extract_work_recursive(work, parent_chain, default_languages):
        """Recursively extract work and its subworks, tracking parent chain."""
        # Work can override languages
        work_lang_data = work.get('language')
        if work_lang_data:
            if isinstance(work_lang_data, list):
                work_languages = add_parent_languages([normalize_lang(l) for l in work_lang_data])
            else:
                work_languages = add_parent_languages([normalize_lang(work_lang_data)])
        else:
            work_languages = default_languages
        
        work_id = work.get('id', '')
        work_title = work.get('title', '')
        # Override allows a work to link to a different work page than its id
        work_page_id = work.get('override', work_id)
        
        # Only add if work has content or is a container (has subworks/children)
        has_content = work.get('content')
        has_subworks = work.get('subworks') or work.get('children')
        
        extracted = []
        
        # Add this work
        extracted.append({
            'element_id': work.get('elementId', work.get('id', '')),
            'work_id': work_id,
            'work_page_id': work_page_id,  # Which work page this links to
            'work_title': work_title,
            'work_author': work.get('author', ''),
            'text_path': str(html_path),
            'text_title': text_title,
            'text_date': text_date,  # Include text date
            'parent_chain': list(parent_chain),  # Chain of parent works (for display)
            'has_content': bool(has_content),
            'has_subworks': bool(has_subworks),
            'languages': work_languages,
            'language_id': work_languages[0]['id'] if work_languages else '',
            'language_name': work_languages[0]['name'] if work_languages else '',
            'language_path': work_languages[0]['path'] if work_languages else None,
        })
        
        # Process subworks (could be under 'subworks' or 'children')
        subwork_list = work.get('subworks') or work.get('children') or []
        if subwork_list:
            parent_element_id = work.get('elementId', work.get('id', ''))
            new_parent_chain = parent_chain + [{'id': work_id, 'title': work_title, 'element_id': parent_element_id}]
            for subwork in subwork_list:
                extracted.extend(extract_work_recursive(subwork, new_parent_chain, work_languages))
        
        return extracted
    
    for page in data.get('pages', []):
        for work in page.get('works', []):
            works.extend(extract_work_recursive(work, [], languages))
    
    return works

def extract_works_from_text(html_path):
    """Extract work info from a text HTML file or data.json."""
    
    # Check for data.json in same directory (JSON-driven text)
    data_json_path = html_path.parent / 'data.json'
    if data_json_path.exists():
        return extract_works_from_json(data_json_path, html_path)
    
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    works = []
    
    # Extract text title
    text_title = None
    h1_match = re.search(r'<h1[^>]*>([^<]+)</h1>', content)
    if h1_match:
        text_title = h1_match.group(1).strip()
    
    # Extract language info
    lang_match = re.search(r'Text in[^<]*<a[^>]*href="([^"]+)"[^>]*><strong>([^<]+)</strong>', content)
    language_path = lang_match.group(1) if lang_match else None
    language_name = lang_match.group(2).strip() if lang_match else None
    
    # Extract all works: id, data-work-id, data-work-title
    work_matches = re.findall(
        r'<div[^>]*id="([^"]+)"[^>]*data-work-id="([^"]+)"[^>]*data-work-title="([^"]+)"',
        content
    )
    
    for element_id, work_id, work_title in work_matches:
        works.append({
            'element_id': element_id,
            'work_id': work_id,
            'work_title': work_title,
            'text_path': str(html_path),
            'text_title': text_title,
            'language_name': language_name,
            'language_path': language_path,
        })
    
    return works

def generate_work_page(work_id, work_info, texts, base_dir, metadata, all_works, contains_works=None):
    """Generate HTML for a work page.
    
    Args:
        contains_works: List of work IDs that have belongsTo pointing to this work
    """
    
    # Use info from first occurrence for metadata
    first = texts[0]
    work_title = first['work_title']
    
    # Get custom metadata from work's own work.json
    work_meta = metadata.get(work_id, {})
    
    # Use fullTitle or title from work.json if available, fall back to text data
    display_title = work_meta.get('fullTitle') or work_meta.get('title') or work_title
    author_id = work_meta.get('author', '')  # This is an author ID, not a display name
    description = work_meta.get('description', '')
    work_date = work_meta.get('date', '')
    work_genre = work_meta.get('genre', '')
    original_language = work_meta.get('original_language', '')
    alias_data = work_meta.get('alias', [])
    country_data = work_meta.get('country', '')
    
    # Normalize alias to list and build display string
    if isinstance(alias_data, str):
        alias_data = [alias_data]
    alias_html = ', '.join(alias_data) if alias_data else ''
    
    # Convert country to flag emoji(s)
    country_flags = countries_to_flags(country_data)
    
    # Look up original language name(s) from the index - support string or array
    original_lang_html = ''
    if original_language:
        # Normalize to list
        lang_ids = original_language if isinstance(original_language, list) else [original_language]
        lang_links = []
        for lang_id in lang_ids:
            lang_info = LANGUAGE_LOOKUP.get(lang_id, {})
            lang_name = lang_info.get('name', lang_id)
            lang_path = lang_info.get('path', '')
            if lang_path:
                lang_links.append(f'<a href="../../{lang_path}">{lang_name}</a>')
            else:
                lang_links.append(lang_name)
        # Join with commas/and
        if len(lang_links) == 1:
            original_lang_html = lang_links[0]
        elif len(lang_links) == 2:
            original_lang_html = f'{lang_links[0]} and {lang_links[1]}'
        else:
            original_lang_html = ', '.join(lang_links[:-1]) + ', and ' + lang_links[-1]
    
    # Handle "belongsTo" relationship - this work is part of another work
    belongs_to = work_meta.get('belongsTo', '')
    belongs_to_html = ''
    if belongs_to:
        parent_meta = metadata.get(belongs_to, {})
        parent_title = parent_meta.get('fullTitle') or parent_meta.get('title') or belongs_to
        belongs_to_html = f'<a href="../{belongs_to}/index.html">{parent_title}</a>'
    
    # Handle "contains" - works that have belongsTo pointing to this work
    contains_html = ''
    if contains_works:
        contains_items = []
        for child_id in sorted(contains_works, key=lambda x: (metadata.get(x, {}).get('title') or x).lower()):
            child_meta = metadata.get(child_id, {})
            child_title = child_meta.get('fullTitle') or child_meta.get('title') or child_id
            contains_items.append(f'<li><a href="../{child_id}/index.html">{child_title}</a></li>')
        if contains_items:
            contains_html = '\n'.join(contains_items)
    
    # Generate author link(s) if author exists - support string or array
    author_html = ''
    if author_id:
        # Normalize to list
        author_ids = author_id if isinstance(author_id, list) else [author_id]
        author_links = []
        for aid in author_ids:
            if not aid:
                continue
            # Look up author display name from author.json
            author_json_path = base_dir / 'authors' / aid / 'author.json'
            if author_json_path.exists():
                with open(author_json_path, 'r', encoding='utf-8') as f:
                    author_data = json.load(f)
                    author_name = author_data.get('name', aid)
            else:
                author_name = aid  # Fallback to ID if no author.json
            author_links.append(f'<a href="../../authors/{aid}/index.html">{author_name}</a>')
        
        if len(author_links) == 1:
            author_html = author_links[0]
        elif len(author_links) == 2:
            author_html = f'{author_links[0]} and {author_links[1]}'
        elif author_links:
            author_html = ', '.join(author_links[:-1]) + ', and ' + author_links[-1]
    
    # Count all texts this work appears in (including as container)
    all_text_paths = set(t['text_path'] for t in texts)
    
    # Collect unique occurrences within each text
    # Group by (text_path, work_id) - same work_id in same text = one occurrence
    # Different work_id values are separate occurrences even if they link to same work page
    # Collect ALL languages from all entries with the same work_id (it may span pages)
    occurrence_map = {}  # (text_path, work_id) -> {info, languages}
    for t in texts:
        key = (t['text_path'], t['work_id'])
        if key not in occurrence_map:
            occurrence_map[key] = {
                'info': t,
                'languages': set(),
                'date': t.get('text_date', ''),  # Store date for sorting
            }
        # Always add languages from every entry
        for lang in t.get('languages', []):
            occurrence_map[key]['languages'].add((lang['name'], lang.get('path', '')))
    
    occurrences = list(occurrence_map.values())
    
    # Build texts list HTML - alphabetical by title
    texts_html = []
    for entry in sorted(occurrences, key=lambda e: e['info']['text_title'].lower()):
        t = entry['info']
        rel_path = os.path.relpath(t['text_path'], base_dir / 'works' / work_id)
        
        # Link to element if available, otherwise just to text
        if t['element_id']:
            link_href = f'{rel_path}#{t["element_id"]}'
        else:
            link_href = rel_path
        
        # Get date for sorting (extract numeric year if possible)
        text_date = entry.get('date', '') or ''
        date_sort = ''
        if text_date:
            year_match = re.search(r'(\d{3,4})', text_date)
            if year_match:
                date_sort = year_match.group(1)
        
        # Format: [text] ([date]), in: [superwork] (work name), as: [local name]
        # Start with text title and date - link to the specific work within the text
        date_display = f' ({date_sort})' if date_sort else ''
        display_html = f'<a href="{link_href}">{t["text_title"]}</a>{date_display}'
        
        # Add superwork if present
        parent_chain = t.get('parent_chain', [])
        if parent_chain:
            parent = parent_chain[-1]
            parent_id = parent.get('id', '')
            parent_title = parent.get('title', '')
            parent_element_id = parent.get('element_id', '')
            
            # Link to the parent work's element in the text
            if parent_element_id:
                parent_link_href = f'{rel_path}#{parent_element_id}'
            else:
                parent_link_href = rel_path
            
            # Look up the parent work's display name from metadata
            parent_meta = metadata.get(parent_id, {})
            parent_display_name = parent_meta.get('fullTitle') or parent_meta.get('title', '')
            
            # Add the work name in parentheses if it differs from the local title
            if parent_display_name and parent_display_name != parent_title:
                parent_name_suffix = f' ({parent_display_name})'
            else:
                parent_name_suffix = ''
            
            # Add "in: [superwork]" section
            display_html += f', in: <a href="{parent_link_href}"><em>{parent_title}</em></a>{parent_name_suffix}'
        
        # Show "as: [title override]" if text uses a different title for this work
        text_work_title = t.get('work_title', '')
        if text_work_title and text_work_title != display_title:
            display_html += f', <span class="title-override">as: <em>{text_work_title}</em></span>'
        
        # Collect all language names and paths for the data attribute (pipe-separated for multiple)
        lang_entries = sorted(list(entry['languages']), key=lambda x: x[0])
        all_langs = '|'.join([name for name, path in lang_entries])  # Store all languages for JS grouping
        # Store paths as JSON for JS to use
        lang_paths_json = json.dumps({name: path for name, path in lang_entries}).replace('"', '&quot;')
        
        texts_html.append(f'''                <li class="child-language" data-title="{t['text_title']}" data-date="{date_sort}" data-langs="{all_langs}" data-lang-paths="{lang_paths_json}">
                    {display_html}
                </li>''')
    
    texts_list = '\n'.join(texts_html)
    
    # Texts section (only show if there are texts with this work)
    texts_section = ''
    if all_text_paths:
        texts_section = f'''
        <section class="children-section">
            <h2>Texts</h2>
            <div class="sort-controls">
                <span>Sort by:</span>
                <button class="sort-btn active" data-sort="alpha">A-Z</button>
                <button class="sort-btn" data-sort="date">Date</button>
                <button class="sort-btn" data-sort="lang">Language</button>
            </div>
            <ul class="children-list sortable-list">
{texts_list}
            </ul>
        </section>
'''
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{display_title}</title>
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
        <h1>{display_title}</h1>

        <div class="metadata">{f'''
            <p><strong>Also known as:</strong> {alias_html}</p>''' if alias_html else ''}{f'''
            <p><strong>Belongs to:</strong> {belongs_to_html}</p>''' if belongs_to_html else ''}{f'''
            <p><strong>Author:</strong> {author_html}</p>''' if author_html else ''}{f'''
            <p><strong>Country:</strong> {country_flags}</p>''' if country_flags else ''}{f'''
            <p><strong>Date:</strong> {work_date}</p>''' if work_date else ''}{f'''
            <p><strong>Genre:</strong> {work_genre}</p>''' if work_genre else ''}{f'''
            <p><strong>Original Language:</strong> {original_lang_html}</p>''' if original_lang_html else ''}
            <p><strong>Work ID:</strong> <code>{work_id}</code></p>
            <p><strong>Appears in:</strong> {len(all_text_paths)} text(s)</p>
        </div>
{f'''
        <section class="description">
            <p>{description}</p>
        </section>
''' if description else ''}{f'''
        <section class="contains-section">
            <h2>Contains</h2>
            <ul class="contains-list">
{contains_html}
            </ul>
        </section>
''' if contains_html else ''}{texts_section}</div>
        <aside class="left-sidebar"></aside>
    </div>
</div>

    <script src="../../search-index.js"></script>
    <script src="../../search.js"></script>
    <script>
    // Sort functionality for texts list
    var originalItems = null;
    
    document.querySelectorAll('.sort-btn').forEach(function(btn) {{
        btn.addEventListener('click', function() {{
            // Update active state
            document.querySelectorAll('.sort-btn').forEach(function(b) {{ b.classList.remove('active'); }});
            btn.classList.add('active');
            
            var sortBy = btn.dataset.sort;
            var list = document.querySelector('.sortable-list');
            if (!list) return;
            
            // Store original items on first interaction
            if (!originalItems) {{
                originalItems = Array.from(list.querySelectorAll('li.child-language')).map(function(li) {{
                    return li.cloneNode(true);
                }});
            }}
            
            // Remove any language group headers and clear list
            list.innerHTML = '';
            
            if (sortBy === 'lang') {{
                // Group by language with hierarchy support
                var langPaths = {{}};
                var itemLangs = []; // Track each item's languages
                
                // First pass: collect all language paths and item associations
                originalItems.forEach(function(item, idx) {{
                    var langs = (item.dataset.langs || 'Unknown').split('|');
                    var paths = {{}};
                    try {{ paths = JSON.parse(item.dataset.langPaths || '{{}}'); }} catch(e) {{}}
                    
                    itemLangs[idx] = [];
                    langs.forEach(function(lang) {{
                        var path = paths[lang] || '';
                        itemLangs[idx].push({{ name: lang, path: path }});
                        if (!langPaths[lang]) langPaths[lang] = path;
                    }});
                }});
                
                // For each item, find the most specific language (longest path or child of another)
                var itemBestLang = [];
                originalItems.forEach(function(item, idx) {{
                    var langs = itemLangs[idx];
                    if (langs.length === 1) {{
                        itemBestLang[idx] = langs[0];
                    }} else {{
                        // Find if any language path contains another (child relationship)
                        var best = langs[0];
                        for (var i = 0; i < langs.length; i++) {{
                            var isChild = false;
                            for (var j = 0; j < langs.length; j++) {{
                                if (i !== j && langs[i].path && langs[j].path) {{
                                    // Check if langs[i] is a child of langs[j]
                                    if (langs[i].path.indexOf(langs[j].path) === 0 && langs[i].path.length > langs[j].path.length) {{
                                        isChild = true;
                                        break;
                                    }}
                                }}
                            }}
                            if (isChild) {{
                                best = langs[i]; // This is a child language, use it
                                break;
                            }}
                        }}
                        // If no clear child found, use longest path
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
                        // This lang has a parent in our set - add to children of parent
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
                    
                    // Render child languages first
                    if (childLangs[lang]) {{
                        childLangs[lang].sort().forEach(function(child) {{
                            renderLangGroup(child, true);
                        }});
                    }}
                    
                    // Render items only if this language has items directly
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
            }} else {{
                var items = originalItems.map(function(item) {{ return item.cloneNode(true); }});
                
                items.sort(function(a, b) {{
                    if (sortBy === 'alpha') {{
                        return (a.dataset.title || '').localeCompare(b.dataset.title || '');
                    }} else if (sortBy === 'date') {{
                        var dateA = parseInt(a.dataset.date) || 9999;
                        var dateB = parseInt(b.dataset.date) || 9999;
                        return dateA - dateB;
                    }}
                    return 0;
                }});
                
                items.forEach(function(item) {{ list.appendChild(item); }});
            }}
        }});
    }});
    </script>
</body>
</html>
'''
    return html

def main():
    base_dir = Path(__file__).parent
    texts_dir = base_dir / 'texts'
    works_dir = base_dir / 'works'
    
    # Ensure works directory exists
    works_dir.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("WORK INDEX GENERATOR")
    print("=" * 60)
    
    # Collect all works from all texts
    print("\nScanning texts for works...")
    all_works = defaultdict(list)
    
    for html_path in texts_dir.rglob('index.html'):
        if 'TEMPLATE' in str(html_path):
            continue
        
        works = extract_works_from_text(html_path)
        for w in works:
            # Group by work_page_id (which may differ from work_id if override is set)
            all_works[w['work_page_id']].append(w)
    
    print(f"   Found {len(all_works)} unique works across all texts")
    
    # Build global metadata dict first (load all work.json files)
    global_metadata = {}
    for work_id in all_works.keys():
        work_json_path = works_dir / work_id / 'work.json'
        if work_json_path.exists():
            with open(work_json_path, 'r', encoding='utf-8') as f:
                global_metadata[work_id] = json.load(f)
    
    # Also load work.json for works that may not be in texts yet (for belongsTo targets)
    for work_dir in works_dir.iterdir():
        if work_dir.is_dir():
            work_id = work_dir.name
            if work_id not in global_metadata:
                work_json_path = work_dir / 'work.json'
                if work_json_path.exists():
                    with open(work_json_path, 'r', encoding='utf-8') as f:
                        global_metadata[work_id] = json.load(f)
    
    # Build reverse lookup: which works "belong to" each container work
    contains_lookup = defaultdict(list)  # container_work_id -> [child_work_ids]
    for work_id, meta in global_metadata.items():
        belongs_to = meta.get('belongsTo', '')
        if belongs_to:
            contains_lookup[belongs_to].append(work_id)
    
    # Generate work pages
    print("\nGenerating work pages...")
    for work_id, texts in all_works.items():
        work_title = texts[0]['work_title']
        
        # Load per-work metadata from work.json if it exists, or create it
        work_dir = works_dir / work_id
        work_dir.mkdir(exist_ok=True)
        work_json_path = work_dir / 'work.json'
        if work_json_path.exists():
            # Already loaded in global_metadata
            pass
        else:
            # Auto-generate work.json from text data
            auto_meta = {
                'id': work_id,
                'title': work_title,
                'fullTitle': work_title
            }
            # Try to get more info from the first text occurrence
            first = texts[0]
            if first.get('superwork'):
                auto_meta['superwork'] = first['superwork']
            with open(work_json_path, 'w', encoding='utf-8') as f:
                json.dump(auto_meta, f, indent=2, ensure_ascii=False)
            global_metadata[work_id] = auto_meta
            print(f"   Created work.json for {work_id}")
        
        # Generate page (pass global_metadata for parent work lookup and contains_lookup)
        contains_works = contains_lookup.get(work_id, [])
        html = generate_work_page(work_id, texts[0], texts, base_dir, global_metadata, all_works, contains_works)
        
        # Write to file
        output_path = work_dir / "index.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        # Count unique texts for display
        seen = set()
        for t in texts:
            seen.add(t['text_path'])
        text_count = len(seen)
        print(f"   {work_title} ({work_id}) — {text_count} text(s)")
    
    # Clean up old work pages that no longer have any texts
    existing_dirs = {d for d in works_dir.iterdir() if d.is_dir()}
    valid_dirs = {works_dir / work_id for work_id in all_works.keys()}
    orphans = existing_dirs - valid_dirs
    
    for orphan in orphans:
        print(f"   Removing orphan: {orphan.name}/")
        import shutil
        shutil.rmtree(orphan)
    
    # Also clean up any stray .html files from old format
    for old_file in works_dir.glob('*.html'):
        print(f"   Removing old format: {old_file.name}")
        old_file.unlink()
    
    # Build global metadata dict for search index
    all_metadata = {}
    for work_id in all_works.keys():
        work_json_path = works_dir / work_id / 'work.json'
        if work_json_path.exists():
            with open(work_json_path, 'r', encoding='utf-8') as f:
                all_metadata[work_id] = json.load(f)
    
    # Update search index with works
    print("\nUpdating search index...")
    search_index_path = base_dir / 'search-index.js'
    
    with open(search_index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse existing index
    json_match = re.search(r'const LANGUAGE_INDEX = (\[.*\]);', content, re.DOTALL)
    if json_match:
        index = json.loads(json_match.group(1))
        
        # Remove existing work entries
        index = [entry for entry in index if entry.get('level') != 'work']
        
        # Add work entries
        for work_id, texts in all_works.items():
            first = texts[0]
            work_title = first['work_title']
            
            # Check for canonical name and aliases from work.json
            work_meta = all_metadata.get(work_id, {})
            canonical_name = work_meta.get('title', work_meta.get('fullTitle', work_title))
            aliases = work_meta.get('alias', [])
            if isinstance(aliases, str):
                aliases = [aliases]
            
            # Add the text's title as an alias if different from canonical
            if work_title != canonical_name and work_title not in aliases:
                aliases.append(work_title)
            
            index.append({
                'name': canonical_name,
                'id': work_id,
                'level': 'work',
                'url': f'works/{work_id}/index.html',
                'extinct': False,
                'alt': aliases  # Aliases for search matching
            })
        
        # Write back
        new_content = f'const LANGUAGE_INDEX = {json.dumps(index, indent=2, ensure_ascii=False)};'
        with open(search_index_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"   Added {len(all_works)} works to search index")
    
    print(f"\nGenerated {len(all_works)} work pages in /works/")
    print("=" * 60)

if __name__ == '__main__':
    main()
