#!/usr/bin/env python3
"""
Add simplified breadcrumb family tree and dialect lists to index.html files.
"""

import csv
import json
from pathlib import Path
from collections import defaultdict

WORKSPACE_ROOT = Path(__file__).parent
LANGUAGES_DIR = WORKSPACE_ROOT / "languages"
CSV_FILE = WORKSPACE_ROOT / "languoid.csv"
EXTINCTION_FILE = WORKSPACE_ROOT / "extinct_languages.json"
EXTINCTION_CACHE_FILE = WORKSPACE_ROOT / "extinction_cache.json"
ALTERNATE_NAMES_FILE = WORKSPACE_ROOT / "alternate_names.csv"

# Load extinct languages
EXTINCT_LANGUAGES = set()
if Path(EXTINCTION_FILE).exists():
    with open(EXTINCTION_FILE, 'r') as f:
        EXTINCT_LANGUAGES = set(json.load(f))

# Load full extinction status cache
EXTINCTION_STATUS = {}
if Path(EXTINCTION_CACHE_FILE).exists():
    with open(EXTINCTION_CACHE_FILE, 'r') as f:
        EXTINCTION_STATUS = json.load(f)

# Load alternate names with their language codes
ALTERNATE_NAMES = defaultdict(set)
ALTERNATE_NAMES_WITH_LANG = defaultdict(list)  # {lang_id: [(name, lang_code), ...]}
if Path(ALTERNATE_NAMES_FILE).exists():
    with open(ALTERNATE_NAMES_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            lang_id = row.get('Language_ID', '')
            name = row.get('Name', '')
            name_lang = row.get('lang', '').strip()
            if lang_id and name:
                ALTERNATE_NAMES[lang_id].add(name)
                if name_lang:
                    ALTERNATE_NAMES_WITH_LANG[lang_id].append((name, name_lang))

# ISO 639-1 (2-letter) to ISO 639-3 (3-letter) mapping for major languages
ISO_639_1_TO_3 = {
    'aa': 'aar', 'ab': 'abk', 'af': 'afr', 'ak': 'aka', 'am': 'amh', 'ar': 'ara', 'an': 'arg',
    'as': 'asm', 'av': 'ava', 'ay': 'aym', 'az': 'aze', 'ba': 'bak', 'be': 'bel', 'bg': 'bul',
    'bi': 'bis', 'bm': 'bam', 'bn': 'ben', 'bo': 'bod', 'br': 'bre', 'bs': 'bos', 'ca': 'cat',
    'ce': 'che', 'ch': 'cha', 'co': 'cos', 'cr': 'cre', 'cs': 'ces', 'cu': 'chu', 'cv': 'chv',
    'cy': 'cym', 'da': 'dan', 'de': 'deu', 'dv': 'div', 'dz': 'dzo', 'ee': 'ewe', 'el': 'ell',
    'en': 'eng', 'eo': 'epo', 'es': 'spa', 'et': 'est', 'eu': 'eus', 'fa': 'fas', 'ff': 'ful',
    'fi': 'fin', 'fj': 'fij', 'fo': 'fao', 'fr': 'fra', 'fy': 'fry', 'ga': 'gle', 'gd': 'gla',
    'gl': 'glg', 'gn': 'grn', 'gu': 'guj', 'gv': 'glv', 'ha': 'hau', 'he': 'heb', 'hi': 'hin',
    'ho': 'hmo', 'hr': 'hrv', 'ht': 'hat', 'hu': 'hun', 'hy': 'hye', 'hz': 'her', 'ia': 'ina',
    'id': 'ind', 'ie': 'ile', 'ig': 'ibo', 'ii': 'iii', 'ik': 'ipk', 'io': 'ido', 'is': 'isl',
    'it': 'ita', 'iu': 'iku', 'ja': 'jpn', 'jv': 'jav', 'ka': 'kat', 'kg': 'kon', 'ki': 'kik',
    'kj': 'kua', 'kk': 'kaz', 'kl': 'kal', 'km': 'khm', 'kn': 'kan', 'ko': 'kor', 'kr': 'kau',
    'ks': 'kas', 'ku': 'kur', 'kv': 'kom', 'kw': 'cor', 'ky': 'kir', 'la': 'lat', 'lb': 'ltz',
    'lg': 'lug', 'li': 'lim', 'ln': 'lin', 'lo': 'lao', 'lt': 'lit', 'lu': 'lub', 'lv': 'lav',
    'mg': 'mlg', 'mh': 'mah', 'mi': 'mri', 'mk': 'mkd', 'ml': 'mal', 'mn': 'mon', 'mr': 'mar',
    'ms': 'msa', 'mt': 'mlt', 'my': 'mya', 'na': 'nau', 'nb': 'nob', 'nd': 'nde', 'ne': 'nep',
    'ng': 'ndo', 'nl': 'nld', 'nn': 'nno', 'no': 'nor', 'nr': 'nbl', 'nv': 'nav', 'ny': 'nya',
    'oc': 'oci', 'oj': 'oji', 'om': 'orm', 'or': 'ori', 'os': 'oss', 'pa': 'pan', 'pi': 'pli',
    'pl': 'pol', 'ps': 'pus', 'pt': 'por', 'qu': 'que', 'rm': 'roh', 'rn': 'run', 'ro': 'ron',
    'ru': 'rus', 'rw': 'kin', 'sa': 'san', 'sc': 'srd', 'sd': 'snd', 'se': 'sme', 'sg': 'sag',
    'si': 'sin', 'sk': 'slk', 'sl': 'slv', 'sm': 'smo', 'sn': 'sna', 'so': 'som', 'sq': 'sqi',
    'sr': 'srp', 'ss': 'ssw', 'st': 'sot', 'su': 'sun', 'sv': 'swe', 'sw': 'swa', 'ta': 'tam',
    'te': 'tel', 'tg': 'tgk', 'th': 'tha', 'ti': 'tir', 'tk': 'tuk', 'tl': 'tgl', 'tn': 'tsn',
    'to': 'ton', 'tr': 'tur', 'ts': 'tso', 'tt': 'tat', 'tw': 'twi', 'ty': 'tah', 'ug': 'uig',
    'uk': 'ukr', 'ur': 'urd', 'uz': 'uzb', 've': 'ven', 'vi': 'vie', 'vo': 'vol', 'wa': 'wln',
    'wo': 'wol', 'xh': 'xho', 'yi': 'yid', 'yo': 'yor', 'za': 'zha', 'zh': 'zho', 'zu': 'zul',
    # Additional codes
    'ace': 'ace', 'aii': 'aii', 'ang': 'ang', 'arc': 'arc', 'arz': 'arz', 'ast': 'ast',
    'bar': 'bar', 'bcl': 'bcl', 'ceb': 'ceb', 'chr': 'chr', 'crh': 'crh', 'ext': 'ext',
    'frp': 'frp', 'fur': 'fur', 'gan': 'gan', 'got': 'got', 'gsw': 'gsw', 'hak': 'hak',
    'haw': 'haw', 'hif': 'hif', 'hsb': 'hsb', 'ilo': 'ilo', 'jbo': 'jbo', 'lad': 'lad',
    'lij': 'lij', 'lmo': 'lmo', 'lzh': 'lzh', 'mhr': 'mhr', 'nan': 'nan', 'nds': 'nds',
    'nov': 'nov', 'pam': 'pam', 'pms': 'pms', 'sah': 'sah', 'sco': 'sco', 'szl': 'szl',
    'tet': 'tet', 'tpi': 'tpi', 'vec': 'vec', 'vls': 'vls', 'wuu': 'wuu', 'yue': 'yue',
}

# Country code to name mapping
COUNTRY_NAMES = {
    # Major countries
    'ET': 'Ethiopia', 'GB': 'United Kingdom', 'US': 'United States', 'CA': 'Canada',
    'AU': 'Australia', 'IN': 'India', 'CN': 'China', 'JP': 'Japan', 'BR': 'Brazil',
    'MX': 'Mexico', 'DE': 'Germany', 'FR': 'France', 'IT': 'Italy', 'ES': 'Spain',
    'RU': 'Russia', 'ZA': 'South Africa', 'NG': 'Nigeria', 'KE': 'Kenya', 'EG': 'Egypt',
    'TR': 'Turkey', 'IR': 'Iran', 'SY': 'Syria', 'IQ': 'Iraq', 'SA': 'Saudi Arabia',
    'AE': 'United Arab Emirates', 'IL': 'Israel', 'PK': 'Pakistan', 'BD': 'Bangladesh',
    'TH': 'Thailand', 'MY': 'Malaysia', 'ID': 'Indonesia', 'PH': 'Philippines',
    'VN': 'Vietnam', 'KH': 'Cambodia', 'LA': 'Laos', 'MM': 'Myanmar', 'SG': 'Singapore',
    'TL': 'Timor-Leste', 'PG': 'Papua New Guinea', 'SB': 'Solomon Islands', 'FJ': 'Fiji',
    'NZ': 'New Zealand', 'NP': 'Nepal', 'BT': 'Bhutan', 'LK': 'Sri Lanka', 'MV': 'Maldives',
    'AF': 'Afghanistan', 'KZ': 'Kazakhstan', 'UZ': 'Uzbekistan', 'TM': 'Turkmenistan',
    'TJ': 'Tajikistan', 'KG': 'Kyrgyzstan', 'MN': 'Mongolia', 'KR': 'South Korea',
    'KP': 'North Korea', 'TW': 'Taiwan', 'CZ': 'Czech Republic',
    'SK': 'Slovakia', 'PL': 'Poland', 'HU': 'Hungary', 'RO': 'Romania', 'BG': 'Bulgaria',
    'GR': 'Greece', 'HR': 'Croatia', 'RS': 'Serbia', 'BA': 'Bosnia and Herzegovina',
    'ME': 'Montenegro', 'AL': 'Albania', 'MK': 'North Macedonia', 'UA': 'Ukraine',
    'BY': 'Belarus', 'MD': 'Moldova', 'SE': 'Sweden', 'NO': 'Norway', 'FI': 'Finland',
    'DK': 'Denmark', 'IE': 'Ireland', 'NL': 'Netherlands', 'BE': 'Belgium', 'LU': 'Luxembourg',
    'CH': 'Switzerland', 'AT': 'Austria', 'CY': 'Cyprus', 'MT': 'Malta', 'PT': 'Portugal',
    # Baltic states
    'LT': 'Lithuania', 'LV': 'Latvia', 'EE': 'Estonia',
    # Balkans
    'SI': 'Slovenia', 'XK': 'Kosovo',
    # North Africa and Middle East
    'MA': 'Morocco', 'DZ': 'Algeria', 'TN': 'Tunisia', 'LY': 'Libya', 'SD': 'Sudan',
    'SS': 'South Sudan', 'ER': 'Eritrea', 'DJ': 'Djibouti', 'SO': 'Somalia', 'UG': 'Uganda',
    'RW': 'Rwanda', 'BW': 'Botswana', 'ZW': 'Zimbabwe', 'MZ': 'Mozambique', 'ZM': 'Zambia',
    'MW': 'Malawi', 'TZ': 'Tanzania', 'NA': 'Namibia', 'AO': 'Angola', 'CG': 'Congo',
    'CD': 'Democratic Republic of the Congo', 'CM': 'Cameroon', 'CF': 'Central African Republic',
    # West Africa
    'GN': 'Guinea', 'GW': 'Guinea-Bissau', 'SL': 'Sierra Leone', 'LR': 'Liberia', 'ML': 'Mali',
    'SN': 'Senegal', 'GM': 'Gambia', 'MR': 'Mauritania', 'CV': 'Cape Verde', 'CI': "Côte d'Ivoire",
    'BF': 'Burkina Faso', 'GH': 'Ghana', 'TG': 'Togo', 'BJ': 'Benin', 'NE': 'Niger',
    # Central Africa
    'TD': 'Chad', 'GA': 'Gabon', 'GQ': 'Equatorial Guinea', 'ST': 'São Tomé and Príncipe',
    'BI': 'Burundi',
    # Southern Africa
    'LS': 'Lesotho', 'SZ': 'Eswatini',
    # Indian Ocean
    'SC': 'Seychelles', 'MU': 'Mauritius', 'KM': 'Comoros', 'MG': 'Madagascar', 'RE': 'Réunion',
    'YT': 'Mayotte',
    # Caucasus
    'GE': 'Georgia', 'AZ': 'Azerbaijan', 'AM': 'Armenia',
    # Middle East
    'LB': 'Lebanon', 'JO': 'Jordan', 'PS': 'Palestine', 'OM': 'Oman', 'YE': 'Yemen',
    'QA': 'Qatar', 'BH': 'Bahrain', 'KW': 'Kuwait',
    # South America
    'CL': 'Chile', 'AR': 'Argentina', 'UY': 'Uruguay', 'PY': 'Paraguay', 'PE': 'Peru',
    'EC': 'Ecuador', 'CO': 'Colombia', 'VE': 'Venezuela', 'GY': 'Guyana', 'SR': 'Suriname',
    'GF': 'French Guiana', 'BO': 'Bolivia',
    # Central America
    'HN': 'Honduras', 'SV': 'El Salvador', 'NI': 'Nicaragua', 'CR': 'Costa Rica', 'PA': 'Panama',
    'BZ': 'Belize', 'GT': 'Guatemala',
    # Caribbean
    'CU': 'Cuba', 'DO': 'Dominican Republic', 'HT': 'Haiti', 'JM': 'Jamaica', 'BS': 'Bahamas',
    'BB': 'Barbados', 'TT': 'Trinidad and Tobago', 'PR': 'Puerto Rico', 'VI': 'US Virgin Islands',
    'VG': 'British Virgin Islands', 'KY': 'Cayman Islands', 'AG': 'Antigua and Barbuda',
    'DM': 'Dominica', 'GD': 'Grenada', 'KN': 'Saint Kitts and Nevis', 'LC': 'Saint Lucia',
    'VC': 'Saint Vincent and the Grenadines', 'AW': 'Aruba', 'CW': 'Curaçao', 'SX': 'Sint Maarten',
    'BQ': 'Caribbean Netherlands', 'TC': 'Turks and Caicos Islands', 'AI': 'Anguilla',
    'MS': 'Montserrat', 'MF': 'Saint Martin', 'BL': 'Saint Barthélemy', 'GP': 'Guadeloupe',
    'MQ': 'Martinique',
    # North Atlantic
    'BM': 'Bermuda', 'GL': 'Greenland', 'IS': 'Iceland', 'FO': 'Faroe Islands',
    # European territories
    'GI': 'Gibraltar', 'GG': 'Guernsey', 'JE': 'Jersey', 'IM': 'Isle of Man',
    'LI': 'Liechtenstein', 'MC': 'Monaco', 'SM': 'San Marino', 'VA': 'Vatican City', 'AD': 'Andorra',
    # Pacific Islands
    'VU': 'Vanuatu', 'NC': 'New Caledonia', 'PF': 'French Polynesia', 'WF': 'Wallis and Futuna',
    'FM': 'Micronesia', 'GU': 'Guam', 'MP': 'Northern Mariana Islands', 'PW': 'Palau',
    'MH': 'Marshall Islands', 'KI': 'Kiribati', 'NR': 'Nauru', 'TV': 'Tuvalu',
    'WS': 'Samoa', 'AS': 'American Samoa', 'TO': 'Tonga', 'NU': 'Niue', 'CK': 'Cook Islands',
    'TK': 'Tokelau', 'PN': 'Pitcairn Islands', 'NF': 'Norfolk Island', 'CC': 'Cocos Islands',
    'CX': 'Christmas Island', 'HM': 'Heard and McDonald Islands',
    # Southeast Asia
    'BN': 'Brunei',
    # Miscellaneous territories
    'SH': 'Saint Helena', 'FK': 'Falkland Islands', 'GS': 'South Georgia', 'AQ': 'Antarctica',
    'IO': 'British Indian Ocean Territory', 'SJ': 'Svalbard and Jan Mayen', 'AX': 'Åland Islands',
    'EH': 'Western Sahara', 'PM': 'Saint Pierre and Miquelon', 'UM': 'US Minor Outlying Islands',
    'HK': 'Hong Kong', 'MO': 'Macau', 'TF': 'French Southern Territories'
}

def sanitize_folder_name(name):
    """Convert a language name to the folder name format."""
    folder_name = name.lower().replace(' ', '-').replace('/', '-')
    folder_name = ''.join(c for c in folder_name if c.isalnum() or c in ('-', '_'))
    return folder_name

def format_language_name(name, lang_id, language_data=None):
    """Format language name with extinction dagger if applicable - FOR TITLES/SEARCH."""
    # Use get_language_status for all types (languages, dialects, families)
    status = get_language_status(lang_id, language_data)
    if status == 'extinct':
        return f"† {name}"
    
    return name

def format_language_name_breadcrumb(name, lang_id, language_data=None):
    """Format language name for breadcrumb - ALWAYS show dagger if extinct in cache."""
    if lang_id in EXTINCT_LANGUAGES:
        return f"† {name}"
    
    # Also check computed family extinction
    if language_data and lang_id in language_data and language_data[lang_id]['level'] == 'family':
        if get_language_status(lang_id, language_data) == 'extinct':
            return f"† {name}"
    
    return name

def get_language_status(lang_id, language_data=None):
    """Get the language status from extinction cache."""
    # For families, ALWAYS compute based on children (ignore cache)
    if language_data and lang_id in language_data and language_data[lang_id]['level'] == 'family':
        direct_children = [cid for cid, data in language_data.items() 
                          if data.get('parent_id') == lang_id]
        
        if not direct_children:
            return None
        
        # Check if ANY direct child is NOT extinct
        for cid in direct_children:
            child_data = language_data.get(cid, {})
            if child_data['level'] == 'family':
                # Recursively check if subfamily is extinct
                child_status = get_language_status(cid, language_data)
                if child_status != 'extinct':
                    return None
            else:
                # It's a language/dialect
                if cid not in EXTINCT_LANGUAGES:
                    return None
        
        # All direct children are extinct
        return 'extinct'
    
    # For non-families, use cache
    if lang_id in EXTINCTION_STATUS and EXTINCTION_STATUS[lang_id]:
        return EXTINCTION_STATUS[lang_id]
    
    if lang_id in EXTINCT_LANGUAGES:
        return 'extinct'
    
    return None

def build_child_map(language_data):
    """Build a map of parent -> children."""
    from collections import defaultdict
    child_map = defaultdict(list)
    for lang_id, data in language_data.items():
        parent_id = data.get('parent_id')
        if parent_id:
            child_map[parent_id].append(lang_id)
    return child_map

def generate_status_badge(lang_id, language_data=None):
    """Generate a subtle status badge for the language."""
    status = get_language_status(lang_id, language_data)
    if not status:
        return ""
    
    # Map status values to display text
    status_display = {
        'extinct': 'Extinct',
        'moribund': 'Moribund',
        'nearly extinct': 'Nearly Extinct',
        'threatened': 'Threatened',
        'shifting': 'Shifting',
        'not endangered': 'Not Endangered',
    }
    
    display_text = status_display.get(status, status.title() if status else '')
    if not display_text:
        return ""
    
    return f'<p class="language-status">{display_text}</p>'

def get_native_name(lang_id, language_data):
    """Get the native name (endonym) for a language if available."""
    if lang_id not in language_data:
        return None
    
    iso_code = language_data[lang_id].get('iso639P3code', '')
    if not iso_code:
        return None
    
    # Look for alternate names where the name's language matches the language itself
    if lang_id not in ALTERNATE_NAMES_WITH_LANG:
        return None
    
    for name, name_lang in ALTERNATE_NAMES_WITH_LANG[lang_id]:
        # Convert 2-letter code to 3-letter if needed
        name_lang_3 = ISO_639_1_TO_3.get(name_lang, name_lang)
        if name_lang_3 == iso_code:
            return name
    
    return None


def generate_alternate_names_html(lang_id, primary_name, language_data=None):
    """Generate HTML for alternate names/synonyms, with native name highlighted."""
    if lang_id not in ALTERNATE_NAMES:
        return ""
    
    # Get the native name if available
    native_name = None
    if language_data:
        native_name = get_native_name(lang_id, language_data)
    
    # Get unique alternate names, excluding the primary name
    alt_names = sorted([n for n in ALTERNATE_NAMES[lang_id] if n.lower() != primary_name.lower()])
    
    if not alt_names:
        return ""
    
    # Build the native name display if we have one
    native_html = ""
    if native_name and native_name.lower() != primary_name.lower():
        native_html = f'<p class="native-name"><strong>Native name:</strong> <span class="endonym">{native_name}</span></p>\n'
        # Remove native name from alt_names list to avoid duplication
        alt_names = [n for n in alt_names if n != native_name]
    
    if not alt_names:
        return native_html.rstrip('\n') if native_html else ""
    
    # If 20 or fewer names, show all
    if len(alt_names) <= 20:
        names_text = ', '.join(alt_names)
        return f'{native_html}<p class="alternate-names"><strong>Also known as:</strong> {names_text}</p>'
    
    # More than 20 - show first 20 with expandable toggle
    visible_names = ', '.join(alt_names[:20])
    hidden_names = ', '.join(alt_names[20:])
    hidden_count = len(alt_names) - 20
    
    html = f'''{native_html}<p class="alternate-names"><strong>Also known as:</strong> {visible_names}<span class="hidden-names" id="hidden-{lang_id}" style="display: none;">, {hidden_names}</span> <a href="javascript:void(0)" class="names-toggle" id="toggle-{lang_id}" data-count="{hidden_count}">and {hidden_count} more...</a></p>
<script>
document.getElementById('toggle-{lang_id}').addEventListener('click', function() {{
    var hidden = document.getElementById('hidden-{lang_id}');
    var count = this.getAttribute('data-count');
    if (hidden.style.display === 'none') {{
        hidden.style.display = 'inline';
        this.textContent = 'show less';
    }} else {{
        hidden.style.display = 'none';
        this.textContent = 'and ' + count + ' more...';
    }}
}});
</script>'''
    
    return html

def get_relative_path(from_languoid_id, to_languoid_id, language_data):
    """Get relative path from one languoid to another."""
    from_path = build_tree_path(from_languoid_id, language_data)
    to_path = build_tree_path(to_languoid_id, language_data)
    
    if not from_path or not to_path:
        return "#"
    
    # Find common ancestor
    common_length = 0
    for i in range(min(len(from_path), len(to_path))):
        if from_path[i] == to_path[i]:
            common_length = i + 1
        else:
            break
    
    # Calculate number of levels to go up
    levels_up = len(from_path) - common_length
    
    # Build relative path
    relative = '../' * levels_up
    
    # Add path down to target
    remaining_path = to_path[common_length:]
    for pid in remaining_path:
        pname = language_data[pid]['name']
        folder_name = sanitize_folder_name(pname)
        relative += folder_name + '/'
    
    relative += 'index.html'
    return relative

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

def get_children(languoid_id, language_data, child_map):
    """Get all children of a languoid, sorted by name."""
    if languoid_id in child_map:
        children = child_map[languoid_id]
        return sorted(children, key=lambda x: language_data[x]['name'])
    return []

def generate_breadcrumb_html(languoid_id, language_data):
    """Generate a simple breadcrumb family tree."""
    path_ids = build_tree_path(languoid_id, language_data)
    
    if not path_ids:
        return ""
    
    # Build breadcrumb path
    breadcrumb_parts = []
    for pid in path_ids:
        pname = language_data[pid]['name']
        # Format name with extinction dagger - use breadcrumb version which always shows dagger for extinct
        formatted_name = format_language_name_breadcrumb(pname, pid, language_data)
        is_current = (pid == languoid_id)
        
        if is_current:
            badge = ""
            if is_isolate(languoid_id, language_data):
                badge = " " + generate_isolate_badge()
            breadcrumb_parts.append(f'<span class="current">{formatted_name}</span>{badge}')
        else:
            url = get_relative_path(languoid_id, pid, language_data)
            breadcrumb_parts.append(f'<a href="{url}">{formatted_name}</a>')
    
    
    breadcrumb = ' / '.join(breadcrumb_parts)
    
    html = f'''<div class="breadcrumb-tree">
    {breadcrumb}
</div>'''
    
    return html

def is_isolate(languoid_id, language_data):
    """Check if a languoid is an isolate (no parent family)."""
    if languoid_id not in language_data:
        return False
    data = language_data[languoid_id]
    # An isolate is a language with no parent_id
    return data['level'] == 'language' and not data['parent_id']

def generate_isolate_badge():
    """Generate HTML for isolate badge."""
    return '<span class="isolate-badge">Language Isolate</span>'

def get_family_countries(languoid_id, language_data, child_map):
    """Recursively collect all unique countries from descendant languages/dialects."""
    all_countries = set()
    
    def collect_countries(lid):
        if lid not in language_data:
            return
        data = language_data[lid]
        
        # If this item has countries, add them
        countries = data.get('country_ids', '')
        if countries:
            for c in countries.split():
                all_countries.add(c.strip())
        
        # Recursively check children
        if lid in child_map:
            for child_id in child_map[lid]:
                collect_countries(child_id)
    
    collect_countries(languoid_id)
    return sorted(all_countries)

# Primary/home country for major languages (Glottolog ID -> ISO 2-letter country code)
# This puts the "origin" country first in flag display
PRIMARY_COUNTRY = {
    # Romance languages
    'stan1288': 'ES',  # Spanish -> Spain
    'stan1290': 'FR',  # French -> France
    'port1283': 'PT',  # Portuguese -> Portugal
    'ital1282': 'IT',  # Italian -> Italy
    'roma1327': 'RO',  # Romanian -> Romania
    'stan1289': 'ES',  # Catalan -> Spain
    'gali1258': 'ES',  # Galician -> Spain
    # Germanic languages
    'stan1293': 'GB',  # English -> United Kingdom
    'stan1295': 'DE',  # German -> Germany
    'dutc1256': 'NL',  # Dutch -> Netherlands
    'swed1254': 'SE',  # Swedish -> Sweden
    'norw1258': 'NO',  # Norwegian -> Norway
    'dani1285': 'DK',  # Danish -> Denmark
    'luxe1241': 'LU',  # Luxembourgish -> Luxembourg
    # Slavic languages
    'russ1263': 'RU',  # Russian -> Russia
    'poli1260': 'PL',  # Polish -> Poland
    'ukra1253': 'UA',  # Ukrainian -> Ukraine
    'czec1258': 'CZ',  # Czech -> Czech Republic
    'slov1269': 'SK',  # Slovak -> Slovakia
    'bulg1262': 'BG',  # Bulgarian -> Bulgaria
    'serb1264': 'RS',  # Serbian -> Serbia
    'croa1245': 'HR',  # Croatian -> Croatia
    'slov1268': 'SI',  # Slovenian -> Slovenia
    'bela1254': 'BY',  # Belarusian -> Belarus
    # Celtic languages
    'iris1253': 'IE',  # Irish -> Ireland
    'scot1245': 'GB',  # Scottish Gaelic -> UK
    'wels1247': 'GB',  # Welsh -> UK
    'bret1244': 'FR',  # Breton -> France
    # Other European
    'gree1276': 'GR',  # Greek -> Greece
    'hung1274': 'HU',  # Hungarian -> Hungary
    'finn1318': 'FI',  # Finnish -> Finland
    'esto1258': 'EE',  # Estonian -> Estonia
    'latv1249': 'LV',  # Latvian -> Latvia
    'lith1251': 'LT',  # Lithuanian -> Lithuania
    'alba1267': 'AL',  # Albanian -> Albania
    'basq1248': 'ES',  # Basque -> Spain
    'malt1254': 'MT',  # Maltese -> Malta
    'nucl1301': 'TR',  # Turkish -> Turkey
    # Asian languages
    'mand1415': 'CN',  # Mandarin -> China
    'cant1236': 'CN',  # Cantonese -> China
    'hakk1236': 'CN',  # Hakka -> China
    'nucl1643': 'JP',  # Japanese -> Japan
    'kore1280': 'KR',  # Korean -> South Korea
    'viet1252': 'VN',  # Vietnamese -> Vietnam
    'thai1261': 'TH',  # Thai -> Thailand
    'indo1316': 'ID',  # Indonesian -> Indonesia
    'mala1479': 'MY',  # Malay -> Malaysia
    'taga1270': 'PH',  # Tagalog -> Philippines
    'beng1280': 'BD',  # Bengali -> Bangladesh
    'hind1269': 'IN',  # Hindi -> India
    'urdu1245': 'PK',  # Urdu -> Pakistan
    'panj1256': 'IN',  # Punjabi -> India
    'telu1262': 'IN',  # Telugu -> India
    'tami1289': 'IN',  # Tamil -> India
    'guja1252': 'IN',  # Gujarati -> India
    'mara1310': 'IN',  # Marathi -> India
    'newa1246': 'NP',  # Nepali -> Nepal
    'sinh1246': 'LK',  # Sinhala -> Sri Lanka
    'pers1254': 'IR',  # Persian -> Iran
    'dari1249': 'AF',  # Dari -> Afghanistan
    'kaza1248': 'KZ',  # Kazakh -> Kazakhstan
    'uzbe1247': 'UZ',  # Uzbek -> Uzbekistan
    'kirg1245': 'KG',  # Kyrgyz -> Kyrgyzstan
    'taji1245': 'TJ',  # Tajik -> Tajikistan
    'mong1331': 'MN',  # Mongolian -> Mongolia
    'geor1252': 'GE',  # Georgian -> Georgia
    'arme1241': 'AM',  # Armenian -> Armenia
    'hebr1245': 'IL',  # Hebrew -> Israel
    'arab1395': 'SA',  # Arabic (Standard) -> Saudi Arabia
    # African languages
    'sout2848': 'ZA',  # Zulu -> South Africa
    'xhos1239': 'ZA',  # Xhosa -> South Africa
    'swah1253': 'TZ',  # Swahili -> Tanzania
    'amha1245': 'ET',  # Amharic -> Ethiopia
    'hous1244': 'NG',  # Hausa -> Nigeria
    'igbo1259': 'NG',  # Igbo -> Nigeria
    'yoru1245': 'NG',  # Yoruba -> Nigeria
    'some1261': 'SO',  # Somali -> Somalia
    'kiny1244': 'RW',  # Kinyarwanda -> Rwanda
    # Americas
    'nahu1245': 'MX',  # Nahuatl -> Mexico
    'quec1387': 'PE',  # Quechua -> Peru
    'aymr1239': 'BO',  # Aymara -> Bolivia
    'guar1292': 'PY',  # Guarani -> Paraguay
    'mapu1245': 'CL',  # Mapudungun -> Chile
}

def inherit_geographic_data(language_data):
    """
    Inherit geographic data (latitude, longitude, country_ids) for dialects 
    that don't have their own coordinates from their parent language/dialect.
    Traverses the parent_id chain until finding a parent with coordinates.
    Returns the count of dialects that inherited geographic data.
    """
    inherited_count = 0
    
    def get_parent_coords(languoid_id, visited=None):
        """Recursively find coordinates from parent chain."""
        if visited is None:
            visited = set()
        
        # Prevent infinite loops
        if languoid_id in visited:
            return None, None, None
        visited.add(languoid_id)
        
        if languoid_id not in language_data:
            return None, None, None
        
        data = language_data[languoid_id]
        parent_id = data.get('parent_id', '')
        
        if not parent_id or parent_id not in language_data:
            return None, None, None
        
        parent_data = language_data[parent_id]
        parent_lat = parent_data.get('latitude', '')
        parent_lon = parent_data.get('longitude', '')
        parent_countries = parent_data.get('country_ids', '')
        
        # If parent has coordinates, use them
        if parent_lat and parent_lon:
            return parent_lat, parent_lon, parent_countries
        
        # Otherwise, keep climbing up the parent chain
        return get_parent_coords(parent_id, visited)
    
    # Process all dialects without coordinates
    for languoid_id, data in language_data.items():
        if data.get('level') != 'dialect':
            continue
        
        # Check if dialect already has its own coordinates
        lat = data.get('latitude', '')
        lon = data.get('longitude', '')
        
        if lat and lon:
            continue  # Already has coordinates
        
        # Try to inherit from parent chain
        parent_lat, parent_lon, parent_countries = get_parent_coords(languoid_id)
        
        if parent_lat and parent_lon:
            data['latitude'] = parent_lat
            data['longitude'] = parent_lon
            # Also inherit country_ids if dialect doesn't have its own
            if not data.get('country_ids', '') and parent_countries:
                data['country_ids'] = parent_countries
            inherited_count += 1
    
    return inherited_count

def get_country_folder_name(country_code):
    """Get the folder name for a country page."""
    country_name = COUNTRY_NAMES.get(country_code, country_code)
    return sanitize_folder_name(country_name)

def generate_country_flags_html(languoid_id, language_data, child_map=None):
    """Generate HTML for country flags in the top-right corner, linking to country pages."""
    if languoid_id not in language_data:
        return ""
    
    data = language_data[languoid_id]
    is_family = data.get('level') == 'family'
    
    # Get country codes
    if is_family and child_map:
        country_list = get_family_countries(languoid_id, language_data, child_map)
    else:
        countries = data.get('country_ids', '')
        country_list = [c.strip() for c in countries.split()] if countries else []
    
    if not country_list:
        return ""
    
    # Sort with primary country first if defined
    primary = PRIMARY_COUNTRY.get(languoid_id)
    if primary and primary in country_list:
        country_list = [primary] + [c for c in country_list if c != primary]
    
    # Calculate path depth from this language page to root
    path_ids = build_tree_path(languoid_id, language_data)
    depth = len(path_ids)
    # Path: go up from language page (depth levels for folders + 1 for languages dir), then to countries/
    relative_prefix = '../' * (depth + 1) + 'countries/'
    
    # Generate flag images using flagcdn.com - show ALL flags, linked to country pages
    flags_html = '<div class="country-flags">'
    for code in country_list:
        country_name = COUNTRY_NAMES.get(code, code)
        folder_name = get_country_folder_name(code)
        country_url = f'{relative_prefix}{folder_name}/index.html'
        # Use flagcdn.com for high-quality flag images, wrapped in links
        flags_html += f'<a href="{country_url}" title="{country_name}"><img src="https://flagcdn.com/w40/{code.lower()}.png" alt="{country_name}" class="country-flag"></a>'
    
    flags_html += '</div>'
    return flags_html

def generate_locality_html(languoid_id, language_data, child_map=None):
    """Generate geographic location section with map (if coordinates exist) and country/description info."""
    if languoid_id not in language_data:
        return ""
    
    data = language_data[languoid_id]
    lat = data.get('latitude', '')
    lon = data.get('longitude', '')
    countries = data.get('country_ids', '')
    description = data.get('description', '')
    
    # For families, aggregate countries from all descendant languages
    if data.get('level') == 'family' and child_map:
        country_list = get_family_countries(languoid_id, language_data, child_map)
    else:
        # Get country names from this languoid directly
        country_list = [c.strip() for c in countries.split()] if countries else []
    
    country_names = [COUNTRY_NAMES.get(code, code) for code in country_list]
    country_text = ', '.join(country_names) if country_names else 'Location not specified'
    
    # If no coordinates, return simplified geographic info section (no map)
    if not lat or not lon:
        html_parts = ['<div class="locality-section">']
        html_parts.append('    <h3>Geographic Information</h3>')
        html_parts.append('    <div class="geographic-info">')
        html_parts.append(f'        <p><strong>Countries:</strong> {country_text}</p>')
        if description:
            html_parts.append(f'        <p><strong>Description:</strong> {description}</p>')
        html_parts.append('    </div>')
        html_parts.append('</div>')
        return '\n'.join(html_parts)
    
    # Has coordinates - show map and full location data
    try:
        lat_val = float(lat)
        lon_val = float(lon)
    except (ValueError, TypeError):
        # Coordinates exist but are invalid, fall back to no-map version
        html_parts = ['<div class="locality-section">']
        html_parts.append('    <h3>Geographic Information</h3>')
        html_parts.append('    <div class="geographic-info">')
        html_parts.append(f'        <p><strong>Countries:</strong> {country_text}</p>')
        if description:
            html_parts.append(f'        <p><strong>Description:</strong> {description}</p>')
        html_parts.append('    </div>')
        html_parts.append('</div>')
        return '\n'.join(html_parts)
    
    map_id = f"map-{languoid_id.replace('.', '-')}"
    country_json = str(country_list).replace("'", '"')
    
    html = f'''<div class="locality-section">
    <h3>Geographic Location</h3>
    <div id="{map_id}" class="language-map" data-countries='{country_json}'></div>
    <div class="geographic-info">
        <p><strong>Countries:</strong> {country_text}</p>
        <p><strong>Coordinates:</strong> {lat_val:.4f}°, {lon_val:.4f}°</p>'''
    
    if description:
        html += f'\n        <p><strong>Description:</strong> {description}</p>'
    
    html += f'''
    </div>
</div>
<script>
    // Initialize map for {languoid_id}
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', function() {{
            initMap('{map_id}', {lat_val}, {lon_val});
        }});
    }} else {{
        initMap('{map_id}', {lat_val}, {lon_val});
    }}
</script>'''
    
    return html

def generate_isolate_badge():
    """Generate HTML for isolate badge."""
    return '<span class="isolate-badge">Language Isolate</span>'

def generate_children_html(languoid_id, language_data, child_map):
    """Generate a list of child families/languages for a family node."""
    children = get_children(languoid_id, language_data, child_map)
    
    if not children:
        return ""
    
    # Get direct children (not grandchildren)
    direct_children = [cid for cid in children if language_data[cid]['parent_id'] == languoid_id]
    
    if not direct_children:
        return ""
    
    # Sort by name
    direct_children = sorted(direct_children, key=lambda x: language_data[x]['name'])
    
    html_parts = []
    html_parts.append('<div class="children-section">')
    
    # Separate families and languages
    families = [cid for cid in direct_children if language_data[cid]['level'] == 'family']
    languages = [cid for cid in direct_children if language_data[cid]['level'] in ['language', 'dialect']]
    
    # Show families first
    if families:
        html_parts.append(f'<h3>Sub-families [{len(families)}]</h3>')
        html_parts.append('<ul class="children-list">')
        for fid in families:
            fname = language_data[fid]['name']
            formatted_fname = format_language_name(fname, fid, language_data)
            url = get_relative_path(languoid_id, fid, language_data)
            html_parts.append(f'<li><a href="{url}">{formatted_fname}</a></li>')
        html_parts.append('</ul>')
    
    # Always show all languages - use collapsible section if there are many
    if languages:
        is_large = len(languages) > 50
        if is_large:
            html_parts.append(f'<h3>Languages [{len(languages)}] <button class="tree-btn" onclick="toggleLargeList(this)">Show</button></h3>')
            html_parts.append('<ul class="children-list large-list" style="display: none;">')
        else:
            html_parts.append(f'<h3>Languages [{len(languages)}]</h3>')
            html_parts.append('<ul class="children-list">')
        for lid in languages:
            lname = language_data[lid]['name']
            formatted_lname = format_language_name(lname, lid, language_data)
            url = get_relative_path(languoid_id, lid, language_data)
            html_parts.append(f'<li><a href="{url}">{formatted_lname}</a></li>')
        html_parts.append('</ul>')
    
    html_parts.append('</div>')
    
    return '\n'.join(html_parts)

def generate_dialects_html(languoid_id, language_data, child_map):
    """Generate a list of dialects if any exist, grouped by parent."""
    children = get_children(languoid_id, language_data, child_map)
    
    # Filter for only dialects
    dialects = [cid for cid in children if language_data[cid]['level'] == 'dialect']
    
    if not dialects:
        return ""
    
    html_parts = []
    html_parts.append('<div class="dialects-section">')
    html_parts.append(f'<h3>Dialects [{len(dialects)}]</h3>')
    
    # Group dialects by their direct parent to preserve hierarchy
    dialect_groups = defaultdict(list)
    for did in dialects:
        dparent = language_data[did]['parent_id']
        dialect_groups[dparent].append(did)
    
    # Display each group
    for parent_id in sorted(dialect_groups.keys()):
        group_dialects = sorted(dialect_groups[parent_id], key=lambda x: language_data[x]['name'])
        
        if parent_id != languoid_id:
            # There's an intermediate group folder
            parent_name = language_data[parent_id]['name']
            formatted_parent_name = format_language_name(parent_name, parent_id, language_data)
            html_parts.append(f'<div class="dialect-group">')
            html_parts.append(f'<strong>{formatted_parent_name}</strong>')
            html_parts.append('<ul>')
        else:
            html_parts.append('<ul class="dialects-list">')
        
        for did in group_dialects:
            dname = language_data[did]['name']
            formatted_dname = format_language_name(dname, did, language_data)
            url = get_relative_path(languoid_id, did, language_data)
            html_parts.append(f'<li><a href="{url}">{formatted_dname}</a></li>')
        
        html_parts.append('</ul>')
        
        if parent_id != languoid_id:
            html_parts.append('</div>')
    
    html_parts.append('</div>')
    
    return '\n'.join(html_parts)

def inject_search_bar(html_content, folder_depth):
    """Inject search bar into HTML just after <body> tag."""
    import re
    # Need to go up one more level to get out of languages/ folder
    path_prefix = '../' * (folder_depth + 1)
    search_html = f'''    <div class="search-container">
        <input type="text" id="searchInput" class="search-bar" placeholder="Search languages and dialects...">
        <div id="searchResults" class="search-results"></div>
    </div>
'''
    
    # Remove old search container if exists (with or without scripts)
    html_content = re.sub(r'<div class="search-container">.*?</div>\s*(?:<script src="[^"]*search-index\.js"[^>]*></script>\s*)?(?:<script src="[^"]*search\.js"[^>]*></script>\s*)?(?:<script>\s*function toggleLargeList.*?</script>\s*)?', '', html_content, flags=re.DOTALL)
    
    # Insert after <body> tag
    body_match = re.search(r'<body[^>]*>', html_content)
    if body_match:
        insert_pos = body_match.end()
        html_content = html_content[:insert_pos] + '\n' + search_html + html_content[insert_pos:]
    
    # Add search scripts at end of body, before </body>
    scripts_html = f'''    <script src="{path_prefix}search-index.js"></script>
    <script src="{path_prefix}search.js"></script>
'''
    # Remove old scripts if they exist (could be anywhere)
    html_content = re.sub(r'<script src="[^"]*search-index\.js"[^>]*></script>\s*', '', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<script src="[^"]*search\.js"[^>]*></script>\s*', '', html_content, flags=re.DOTALL)
    
    # Insert before </body>
    body_end = html_content.rfind('</body>')
    if body_end != -1:
        html_content = html_content[:body_end] + scripts_html + html_content[body_end:]
    
    return html_content

def inject_into_html(html_content, breadcrumb_html, dialects_html, locality_html, folder_depth, languoid_id, children_html=None, language_data=None, child_map=None):
    """Inject the breadcrumb, dialects, locality, and status badge into an existing HTML file."""
    # Remove old sections if they exist
    import re
    html_content = re.sub(r'<section>\s*<h2>Language Family</h2>.*?</section>\s*', '', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<section>\s*<div class="dialects-section">.*?</section>\s*', '', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<section>\s*<div class="breadcrumb-tree">.*?</section>\s*', '', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<section>\s*<div class="locality-section">.*?</section>\s*', '', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<section>\s*<div class="children-section">.*?</section>\s*', '', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<script>\s*// Initialize map.*?</script>\s*', '', html_content, flags=re.DOTALL)
    # Remove old map-init.js script tag if present
    html_content = re.sub(r'<script src=["\'].*?map-init\.js["\']></script>\s*', '', html_content, flags=re.DOTALL)
    # Remove old status badges, native names, and alternate names (including toggle scripts)
    html_content = re.sub(r'<p class="language-status">.*?</p>\s*', '', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<p class="native-name">.*?</p>\s*', '', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<p class="alternate-names">.*?</p>\s*(?:<script>\s*document\.getElementById\([\'"]toggle-.*?</script>\s*)*', '', html_content, flags=re.DOTALL)
    # Remove old country flags
    html_content = re.sub(r'<div class="country-flags">.*?</div>\s*', '', html_content, flags=re.DOTALL)
    
    # Add search bar
    html_content = inject_search_bar(html_content, folder_depth)
    
    # Add style.css link with correct relative path
    style_path = '../' * (folder_depth + 1) + 'style.css'
    style_link = f'    <link rel="stylesheet" href="{style_path}">\n'
    head_end = html_content.find('</head>')
    if head_end != -1 and 'style.css' not in html_content:
        html_content = html_content[:head_end] + style_link + html_content[head_end:]
    
    # Add dagger to title if extinct and inject status badge
    status_badge_html = generate_status_badge(languoid_id, language_data)
    alt_names_html = generate_alternate_names_html(languoid_id, language_data[languoid_id]['name'], language_data)
    
    # Check if extinct using get_language_status which handles families correctly
    is_extinct = get_language_status(languoid_id, language_data) == 'extinct'
    
    # First, normalize the h1 - remove any existing dagger
    h1_match = re.search(r'<h1>†?\s*([^<]+)</h1>', html_content)
    if h1_match:
        clean_title = h1_match.group(1).strip()
        if is_extinct:
            new_title = f'<h1>† {clean_title}</h1>'
        else:
            new_title = f'<h1>{clean_title}</h1>'
        html_content = html_content[:h1_match.start()] + new_title + html_content[h1_match.end():]
    
    # Generate country flags for top banner (before title)
    country_flags_html = generate_country_flags_html(languoid_id, language_data, child_map)
    
    # Insert flags BEFORE the <h1> title
    if country_flags_html:
        h1_start = html_content.find('<h1>')
        if h1_start != -1:
            html_content = html_content[:h1_start] + country_flags_html + '\n' + html_content[h1_start:]
    
    # Insert status badge and alternate names after the <h1> title
    combined_html = ''
    if status_badge_html:
        combined_html += '\n' + status_badge_html
    if alt_names_html:
        combined_html += '\n' + alt_names_html
    
    if combined_html:
        # Find the closing </h1> tag and insert after it
        h1_end = html_content.find('</h1>')
        if h1_end != -1:
            insertion_point = h1_end + len('</h1>')
            html_content = html_content[:insertion_point] + combined_html + html_content[insertion_point:]
    
    # Add Leaflet CSS/JS to head if locality will be shown
    if locality_html:
        head_end = html_content.find('</head>')
        if head_end != -1:
            # Inline the map initialization function with country support
            leaflet_setup = '''    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
    <script>
function initMap(elementId, latitude, longitude) {
    const container = document.getElementById(elementId);
    if (!container) return;
    const map = L.map(elementId).setView([latitude, longitude], 5);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap',
        maxZoom: 19,
        minZoom: 2
    }).addTo(map);
    const countryCodes = JSON.parse(container.dataset.countries || '[]');
    
    // Draw country boundaries if available
    if (countryCodes && countryCodes.length > 0) {
        fetch('https://cdn.jsdelivr.net/npm/world-geojson/countries.geojson')
            .then(r => r.json())
            .then(geojson => {
                const countryFeatures = geojson.features.filter(f => {
                    const code = f.properties.ISO_A2 || f.properties.ADMIN || '';
                    return countryCodes.includes(code);
                });
                L.geoJSON({
                    type: 'FeatureCollection',
                    features: countryFeatures
                }, {
                    style: {
                        color: '#B85A4F',
                        weight: 1.5,
                        opacity: 0.5,
                        fillOpacity: 0.08
                    }
                }).addTo(map);
            })
            .catch(e => console.log(''));
    }
    
    
    // Center point marker
    L.circleMarker([latitude, longitude], {
        radius: 8,
        fillColor: '#B85A4F',
        color: '#8B4530',
        weight: 2.5,
        opacity: 1,
        fillOpacity: 0.9
    }).addTo(map).bindPopup(`${latitude.toFixed(4)}°, ${longitude.toFixed(4)}°`);
    
    setTimeout(() => { map.invalidateSize(); }, 150);
}

function toggleLargeList(btn) {
    const list = btn.closest('h3').nextElementSibling;
    if (list.style.display === 'none') {
        list.style.display = '';
        btn.textContent = 'Hide';
    } else {
        list.style.display = 'none';
        btn.textContent = 'Show';
    }
}
    </script>
'''
            
            # Remove old Leaflet setup if present
            html_content = re.sub(
                r'<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/[^"]*">\s*<script[^>]*src="https://cdnjs[^"]*</script>\s*<script[^>]*src="https://cdn[^"]*</script>\s*<script>\s*var countryBoundaries[^<]*</script>\s*<script src="https://cdn.jsdelivr[^"]*"></script>',
                '',
                html_content,
                flags=re.DOTALL
            )
            html_content = re.sub(
                r'<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/[^"]*">\s*<script[^>]*src="https://cdnjs[^"]*</script>\s*<script>[^<]*function initMap[^<]*</script>\s*<script[^>]*topojson[^<]*</script>',
                '',
                html_content,
                flags=re.DOTALL
            )
            
            # Add the setup only if not already present
            if 'function initMap' not in html_content:
                html_content = html_content[:head_end] + leaflet_setup + html_content[head_end:]

    
    # Find where to inject (after metadata section, before Information section)
    # The base template has: <section>\n            <h2>Information</h2>
    # We need to find this whole pattern and replace the opening <section> tag
    insert_marker = '<section>\n            <h2>Information</h2>'
    insert_pos = html_content.find(insert_marker)
    
    if insert_pos != -1:
        sections = []
        
        if breadcrumb_html:
            sections.append(f'''<section>
            <h2>Language Family</h2>
{breadcrumb_html}
        </section>
        ''')
        
        if locality_html:
            sections.append(f'''<section>
{locality_html}
        </section>
        ''')
        
        if dialects_html:
            sections.append(f'''<section>
{dialects_html}
        </section>
        ''')
        
        if children_html:
            sections.append(f'''<section>
{children_html}
        </section>
        ''')
        
        injection = ''.join(sections)
        # Insert before the <section> tag for Information, keeping the Information section intact
        html_content = html_content[:insert_pos] + injection + html_content[insert_pos:]
    
    return html_content

def main():
    """Main execution."""
    print("=" * 70)
    print("Adding simplified family tree and dialect lists")
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
                latitude = row.get('latitude', '').strip()
                longitude = row.get('longitude', '').strip()
                country_ids = row.get('country_ids', '').strip()
                description = row.get('description', '').strip()
                iso639P3code = row.get('iso639P3code', '').strip()
                
                if not languoid_id or not name:
                    continue
                
                language_data[languoid_id] = {
                    'name': name,
                    'parent_id': parent_id,
                    'level': level,
                    'latitude': latitude,
                    'longitude': longitude,
                    'country_ids': country_ids,
                    'description': description,
                    'iso639P3code': iso639P3code
                }
                
                if level in ['language', 'dialect', 'family']:
                    languages_and_dialects.append(languoid_id)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return
    
    print(f"Found {len(language_data)} total languoids")
    print(f"Found {len(languages_and_dialects)} languages and dialects")
    
    # Inherit geographic data for dialects without coordinates
    print("Inheriting geographic data for dialects...")
    inherited_count = inherit_geographic_data(language_data)
    print(f"Inherited geographic data for {inherited_count} dialects")
    
    # Build child map for efficiency
    print("Building child map...")
    child_map = defaultdict(list)
    for lid, data in language_data.items():
        if data['parent_id']:
            child_map[data['parent_id']].append(lid)
    
    # Update index.html files
    print("\nUpdating index.html files...")
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
            
            # Generate breadcrumb, locality, dialects, and children (for families)
            breadcrumb_html = generate_breadcrumb_html(languoid_id, language_data)
            locality_html = generate_locality_html(languoid_id, language_data, child_map)
            dialects_html = generate_dialects_html(languoid_id, language_data, child_map)
            children_html = generate_children_html(languoid_id, language_data, child_map) if language_data[languoid_id]['level'] == 'family' else None
            
            # Calculate folder depth (number of folders from languages/ to this page)
            folder_depth = len(folder_names)
            
            # Inject content
            updated_html = inject_into_html(html_content, breadcrumb_html, dialects_html, locality_html, folder_depth, languoid_id, children_html, language_data, child_map)
            
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
    
    # Generate search index
    print("\nGenerating search index...")
    search_index = []
    
    # Add languages/dialects/families
    for languoid_id, data in language_data.items():
        if data['level'] in ['language', 'dialect', 'family']:
            path_ids = build_tree_path(languoid_id, language_data)
            if path_ids:
                folder_names = [sanitize_folder_name(language_data[pid]['name']) for pid in path_ids]
                url = '/'.join(folder_names) + '/index.html'
                # Include extinction marker in search name
                display_name = format_language_name(data['name'], languoid_id, language_data)
                
                # Check if extinct (including families with all extinct children)
                is_extinct = languoid_id in EXTINCT_LANGUAGES or (data['level'] == 'family' and get_language_status(languoid_id, language_data) == 'extinct')
                
                # Get alternate names for this language (excluding primary name)
                alt_names = []
                if languoid_id in ALTERNATE_NAMES:
                    primary_lower = data['name'].lower()
                    alt_names = sorted([n for n in ALTERNATE_NAMES[languoid_id] if n.lower() != primary_lower])
                
                search_index.append({
                    'name': display_name,
                    'id': languoid_id,
                    'level': data['level'],
                    'url': url,
                    'extinct': is_extinct,
                    'alt': alt_names if alt_names else []  # Include all alt names for comprehensive search
                })
    
    # Add texts from the texts archive
    texts_dir = WORKSPACE_ROOT / "texts"
    if texts_dir.exists():
        import re
        text_count = 0
        for text_index_file in texts_dir.rglob("index.html"):
            try:
                content = text_index_file.read_text(encoding='utf-8')
                # Extract title (text name)
                title_match = re.search(r'<title>(.+?)\s*—\s*Text Archive</title>', content)
                # Extract language name from data attribute
                lang_match = re.search(r'data-language-name="([^"]+)"', content)
                
                if title_match:
                    text_name = title_match.group(1).strip()
                    
                    # Get relative URL
                    rel_path = text_index_file.relative_to(WORKSPACE_ROOT)
                    url = str(rel_path.parent) + '/'
                    
                    search_index.append({
                        'name': text_name,
                        'id': '',
                        'level': 'text',
                        'url': url,
                        'extinct': False,
                        'alt': []
                    })
                    text_count += 1
            except Exception as e:
                print(f"  Warning: Could not parse text file {text_index_file}: {e}")
        
        print(f"  Added {text_count} texts to search index")
    
    # Add countries to search index
    print("  Adding countries to search index...")
    countries_dir = WORKSPACE_ROOT / "countries"
    if countries_dir.exists():
        country_count = 0
        for country_folder in countries_dir.iterdir():
            if country_folder.is_dir() and (country_folder / "index.html").exists():
                # Get country code from folder name by reverse lookup
                folder_name = country_folder.name
                country_code = None
                country_name = None
                
                for code, name in COUNTRY_NAMES.items():
                    if sanitize_folder_name(name) == folder_name:
                        country_code = code
                        country_name = name
                        break
                
                if country_code and country_name:
                    url = f"countries/{folder_name}/index.html"
                    search_index.append({
                        'name': country_name,
                        'id': country_code.lower(),
                        'level': 'country',
                        'url': url,
                        'extinct': False,
                        'alt': [],
                        'code': country_code  # Store ISO code for flag display
                    })
                    country_count += 1
        
        print(f"  Added {country_count} countries to search index")
    
    # Write search index as JavaScript
    index_file_path = WORKSPACE_ROOT / "search-index.js"
    with open(index_file_path, 'w', encoding='utf-8') as f:
        f.write('const LANGUAGE_INDEX = ')
        import json
        f.write(json.dumps(search_index, ensure_ascii=False, indent=2))
        f.write(';\n')
    
    print(f"Generated search index with {len(search_index)} entries")
    
    print("\n" + "=" * 70)
    print("Done!")
    print("=" * 70)

if __name__ == '__main__':
    main()
