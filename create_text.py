#!/usr/bin/env python3
"""
Text Archive Creator
====================
Creates new text archive entries with automatic language lookup.
Just fill in the simple fields and run!

Usage: python3 create_text.py
"""

import json
import os
import re
from pathlib import Path

# =============================================================================
# FILL OUT THIS SECTION - Edit these fields for each new text
# =============================================================================

TEXT_CONFIG = {
    # REQUIRED: Language name (will auto-lookup path, glottolog ID, etc.)
    # Can be the name or glottolog ID (e.g., "Sumerian" or "sume1241")
    "language": "Sumerian",
    
    # REQUIRED: Text title
    "title": "Hymn to Inanna",
    
    # OPTIONAL: English translation of title (leave empty if same as title)
    "title_english": "",
    
    # OPTIONAL: Source publication/manuscript
    "source": "",
    
    # OPTIONAL: Date or date range
    "date": "c. 2300 BCE",
    
    # REQUIRED: The actual text content
    # Use triple quotes for multi-line text
    # Can include <strong>, <em>, and line breaks
    "content": """
𒀭𒈹 𒌷𒀭𒈹𒆠
𒂗𒃶𒁺𒀭𒈾

nin me šar₂-ra
u₆ di-di

My lady of all the divine powers,
resplendent light...
""",
    
    # OPTIONAL: If the text spans multiple pages, define page breaks
    # List of line numbers where new pages start (1-indexed)
    # Leave empty [] for single page
    "page_breaks": [],
    
    # OPTIONAL: If there are multiple works on a page, define them
    # List of {"id": "work-id", "title": "Work Title", "start_line": N}
    # Leave empty [] for single work = entire content
    "works": [],
    
    # OPTIONAL: ISO 639-3 code override (auto-detected from language data)
    "iso_override": "",
    
    # OPTIONAL: Native language name override
    "native_name_override": "",
}

# =============================================================================
# END OF CONFIGURATION - Don't edit below unless you know what you're doing
# =============================================================================

def load_language_index():
    """Load the search index to look up language information."""
    search_index_path = Path(__file__).parent / "search-index.js"
    with open(search_index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract the JSON array from the JS file
    match = re.search(r'const LANGUAGE_INDEX = (\[[\s\S]*\]);?', content)
    if not match:
        raise ValueError("Could not parse search-index.js")
    
    return json.loads(match.group(1))

def find_language(language_index, query):
    """Find a language by name or glottolog ID."""
    query_lower = query.lower().strip()
    query_clean = query_lower.lstrip('†').strip()
    
    # First try exact ID match
    for lang in language_index:
        if lang['id'].lower() == query_clean:
            return lang
    
    # Then try exact name match (ignoring † prefix)
    for lang in language_index:
        name_clean = lang['name'].lstrip('†').strip().lower()
        if name_clean == query_clean:
            return lang
    
    # Then try partial match
    for lang in language_index:
        name_clean = lang['name'].lstrip('†').strip().lower()
        if query_clean in name_clean or name_clean in query_clean:
            return lang
    
    # Try alternate names
    for lang in language_index:
        for alt in lang.get('alt', []):
            if query_clean in alt.lower():
                return lang
    
    return None

def get_next_text_id():
    """Find the next available text ID."""
    texts_dir = Path(__file__).parent / "texts"
    if not texts_dir.exists():
        return 1
    
    max_id = 0
    for path in texts_dir.rglob("index.html"):
        # Extract ID from path like texts/00/00/0000000000000001/index.html
        id_dir = path.parent.name
        try:
            text_id = int(id_dir)
            max_id = max(max_id, text_id)
        except ValueError:
            continue
    
    return max_id + 1

def id_to_path(text_id):
    """Convert text ID to directory path."""
    id_str = f"{text_id:016d}"
    return f"texts/{id_str[0:2]}/{id_str[2:4]}/{id_str}"

def get_language_page_path(lang_url):
    """Get the path to the language's index.html to extract native name and ISO code."""
    lang_path = Path(__file__).parent / "languages" / lang_url
    if lang_path.exists():
        return lang_path
    return None

def extract_language_details(lang_path):
    """Extract native name and ISO code from language page."""
    details = {"native": "", "iso": ""}
    
    if not lang_path or not lang_path.exists():
        return details
    
    with open(lang_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract native name from meta tag
    native_match = re.search(r'<meta name="language-native" content="([^"]*)"', content)
    if native_match:
        details["native"] = native_match.group(1)
    
    # Extract ISO code from meta tag
    iso_match = re.search(r'<meta name="iso-639-3" content="([^"]*)"', content)
    if iso_match:
        details["iso"] = iso_match.group(1)
    
    return details

def generate_work_id(title):
    """Generate a URL-safe work ID from title."""
    return re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')

def create_text_html(config, lang_info, text_id, lang_details):
    """Generate the HTML for a text archive entry."""
    
    # Calculate relative path depth
    id_str = f"{text_id:016d}"
    rel_prefix = "../../../../"  # texts/XX/XX/XXXXXXXXXXXXXXXX/ = 4 levels deep
    
    # Language info
    lang_name = lang_info['name'].lstrip('†').strip()
    lang_id = lang_info['id']
    lang_url = lang_info['url']
    is_extinct = lang_info.get('extinct', False)
    
    # Use overrides if provided
    native_name = config.get('native_name_override') or lang_details.get('native') or lang_name
    iso_code = config.get('iso_override') or lang_details.get('iso') or ''
    
    # Detect HTML lang attribute (use ISO code if available)
    html_lang = iso_code if iso_code else lang_id[:3]
    
    # Title handling
    title = config['title']
    title_english = config.get('title_english', '')
    title_display = f"{title} <em>({title_english})</em>" if title_english else title
    
    # Build metadata section
    metadata_parts = [f'<p><strong>Title:</strong> {title_display}</p>']
    
    if config.get('source'):
        metadata_parts.append(f'<p><strong>Source:</strong> {config["source"]}</p>')
    
    if config.get('date'):
        metadata_parts.append(f'<p><strong>Date:</strong> {config["date"]}</p>')
    
    metadata_parts.append(f'<p><strong>Text ID:</strong> <code>{id_str}</code></p>')
    metadata_parts.append(f'<p><strong>Glottolog:</strong> <a href="https://glottolog.org/resource/languoid/id/{lang_id}">{lang_id}</a></p>')
    
    metadata_html = '\n            '.join(metadata_parts)
    
    # Process content into pages and works
    content = config['content'].strip()
    lines = content.split('\n')
    
    page_breaks = config.get('page_breaks', [])
    works = config.get('works', [])
    
    # Default single work if none specified
    if not works:
        works = [{
            'id': generate_work_id(title),
            'title': title,
            'start_line': 1
        }]
    
    # Default single page if no breaks
    if not page_breaks:
        page_breaks = [1]
    
    # Build pages
    pages_html = []
    page_num = 0
    
    for i, page_start in enumerate(page_breaks):
        page_num += 1
        page_end = page_breaks[i + 1] - 1 if i + 1 < len(page_breaks) else len(lines)
        page_lines = lines[page_start - 1:page_end]
        page_content = '\n'.join(page_lines)
        
        # Find works on this page
        works_on_page = []
        for w in works:
            w_start = w['start_line']
            # Work is on this page if it starts on or before the page end
            if page_start <= w_start <= page_end or (w_start < page_start and 
                (works.index(w) == len(works) - 1 or works[works.index(w) + 1]['start_line'] > page_start)):
                works_on_page.append(w)
        
        # For simplicity, wrap entire page content in single work container
        # (matching the structure of the Welsh example)
        work = works[0]  # Use first work for now
        work_id = work['id']
        work_title = work['title']
        
        page_html = f'''                <div class="text-page" id="page-{page_num}" data-page-label="{page_num}">
                    <div class="text-work" id="work-{work_id}-{page_num}" data-work-id="{work_id}" data-work-title="{work_title}">
                    <poem>
{page_content}
</poem>
                    </div>
                </div>'''
        pages_html.append(page_html)
    
    pages_combined = '\n                \n'.join(pages_html)
    
    # Language status line
    lang_link = f'{rel_prefix}languages/{lang_url}'
    if native_name and native_name != lang_name:
        lang_status = f'Text in <a href="{lang_link}"><strong>{lang_name}</strong></a> ({native_name})'
    else:
        lang_status = f'Text in <a href="{lang_link}"><strong>{lang_name}</strong></a>'
    
    # Full HTML template
    html = f'''<!DOCTYPE html>
<html lang="{html_lang}" data-language-id="{lang_id}" data-language-name="{lang_name}" data-text-id="{id_str}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="language-id" content="{lang_id}">
    <meta name="language-name" content="{lang_name}">
    <meta name="language-native" content="{native_name}">
    <meta name="iso-639-3" content="{iso_code}">
    <meta name="text-id" content="{id_str}">
    <title>{title} — Text Archive</title>
    <link rel="stylesheet" href="{rel_prefix}style.css">
</head>
<body>
    <div class="search-container">
        <input type="text" class="search-bar" id="searchInput" placeholder="Search languages..." autocomplete="off">
        <div class="search-results" id="searchResults"></div>
    </div>
    
    <div class="container">
        <nav class="breadcrumb-tree">
            <a href="{rel_prefix}index.html">Encyclopedia</a> ›
            <a href="{rel_prefix}texts-index.html">Text Archive</a> ›
            <span>{id_str}</span>
        </nav>

        <h1>{title}</h1>
        
        <p class="language-status">{lang_status}</p>
        
        <div class="metadata">
            {metadata_html}
        </div>

        <section>
            <h2>Transcription</h2>
            
            <div class="text-body">
{pages_combined}
            </div>
        </section>
    </div>

    <script src="{rel_prefix}search-index.js"></script>
    <script src="{rel_prefix}search.js"></script>
    <script src="{rel_prefix}text-reader.js"></script>
</body>
</html>
'''
    return html

def main():
    print("=" * 60)
    print("TEXT ARCHIVE CREATOR")
    print("=" * 60)
    
    # Load language index
    print("\nLoading language index...")
    language_index = load_language_index()
    print(f"   Loaded {len(language_index)} languages")
    
    # Find the language
    print(f"\nLooking up language: {TEXT_CONFIG['language']}")
    lang_info = find_language(language_index, TEXT_CONFIG['language'])
    
    if not lang_info:
        print(f"\nERROR: Could not find language '{TEXT_CONFIG['language']}'")
        print("   Try using the Glottolog ID (e.g., 'sume1241') or check spelling")
        return
    
    lang_name = lang_info['name'].lstrip('†').strip()
    print(f"   Found: {lang_name} ({lang_info['id']})")
    print(f"   Path: languages/{lang_info['url']}")
    
    # Get additional language details
    lang_path = get_language_page_path(lang_info['url'])
    lang_details = extract_language_details(lang_path)
    if lang_details['native']:
        print(f"   Native: {lang_details['native']}")
    if lang_details['iso']:
        print(f"   ISO: {lang_details['iso']}")
    
    # Get next text ID
    text_id = get_next_text_id()
    id_str = f"{text_id:016d}"
    print(f"\nAssigning text ID: {id_str}")
    
    # Generate output path
    output_dir = Path(__file__).parent / id_to_path(text_id)
    output_file = output_dir / "index.html"
    print(f"   Output: {output_file}")
    
    # Generate HTML
    print(f"\nGenerating HTML...")
    html = create_text_html(TEXT_CONFIG, lang_info, text_id, lang_details)
    
    # Create directory and write file
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\nSUCCESS! Created: {output_file}")
    print(f"\nView your text at:")
    print(f"   {output_file}")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
