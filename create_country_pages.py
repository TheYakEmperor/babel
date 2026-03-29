#!/usr/bin/env python3
"""
Generate country pages for the Babel language archive.
Each country page shows:
- Country name and flag
- Map with country location
- All languages spoken in that country, organized hierarchically by family
"""

import os
import csv
import json
from collections import defaultdict

BASE_DIR = '/Users/yakking/Downloads/Web-design/Babel'
CSV_FILE = os.path.join(BASE_DIR, 'languoid.csv')
LANGUAGES_DIR = os.path.join(BASE_DIR, 'languages')
COUNTRIES_DIR = os.path.join(BASE_DIR, 'countries')
EXTINCT_FILE = os.path.join(BASE_DIR, 'extinct_languages.json')

# Load extinct languages
EXTINCT_LANGUAGES = set()
try:
    with open(EXTINCT_FILE, 'r', encoding='utf-8') as f:
        EXTINCT_LANGUAGES = set(json.load(f))
except:
    pass

# Country names mapping (ISO 2-letter to full name)
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
    'LT': 'Lithuania', 'LV': 'Latvia', 'EE': 'Estonia',
    'SI': 'Slovenia', 'XK': 'Kosovo',
    'MA': 'Morocco', 'DZ': 'Algeria', 'TN': 'Tunisia', 'LY': 'Libya', 'SD': 'Sudan',
    'SS': 'South Sudan', 'ER': 'Eritrea', 'DJ': 'Djibouti', 'SO': 'Somalia', 'UG': 'Uganda',
    'RW': 'Rwanda', 'BW': 'Botswana', 'ZW': 'Zimbabwe', 'MZ': 'Mozambique', 'ZM': 'Zambia',
    'MW': 'Malawi', 'TZ': 'Tanzania', 'NA': 'Namibia', 'AO': 'Angola', 'CG': 'Congo',
    'CD': 'Democratic Republic of the Congo', 'CM': 'Cameroon', 'CF': 'Central African Republic',
    'GN': 'Guinea', 'GW': 'Guinea-Bissau', 'SL': 'Sierra Leone', 'LR': 'Liberia', 'ML': 'Mali',
    'SN': 'Senegal', 'GM': 'Gambia', 'MR': 'Mauritania', 'CV': 'Cape Verde', 'CI': "Côte d'Ivoire",
    'BF': 'Burkina Faso', 'GH': 'Ghana', 'TG': 'Togo', 'BJ': 'Benin', 'NE': 'Niger',
    'TD': 'Chad', 'GA': 'Gabon', 'GQ': 'Equatorial Guinea', 'ST': 'São Tomé and Príncipe',
    'BI': 'Burundi',
    'LS': 'Lesotho', 'SZ': 'Eswatini',
    'SC': 'Seychelles', 'MU': 'Mauritius', 'KM': 'Comoros', 'MG': 'Madagascar', 'RE': 'Réunion',
    'YT': 'Mayotte',
    'GE': 'Georgia', 'AZ': 'Azerbaijan', 'AM': 'Armenia',
    'LB': 'Lebanon', 'JO': 'Jordan', 'PS': 'Palestine', 'OM': 'Oman', 'YE': 'Yemen',
    'QA': 'Qatar', 'BH': 'Bahrain', 'KW': 'Kuwait',
    'CL': 'Chile', 'AR': 'Argentina', 'UY': 'Uruguay', 'PY': 'Paraguay', 'PE': 'Peru',
    'EC': 'Ecuador', 'CO': 'Colombia', 'VE': 'Venezuela', 'GY': 'Guyana', 'SR': 'Suriname',
    'GF': 'French Guiana', 'BO': 'Bolivia',
    'HN': 'Honduras', 'SV': 'El Salvador', 'NI': 'Nicaragua', 'CR': 'Costa Rica', 'PA': 'Panama',
    'BZ': 'Belize', 'GT': 'Guatemala',
    'CU': 'Cuba', 'DO': 'Dominican Republic', 'HT': 'Haiti', 'JM': 'Jamaica', 'BS': 'Bahamas',
    'BB': 'Barbados', 'TT': 'Trinidad and Tobago', 'PR': 'Puerto Rico', 'VI': 'US Virgin Islands',
    'VG': 'British Virgin Islands', 'KY': 'Cayman Islands', 'AG': 'Antigua and Barbuda',
    'DM': 'Dominica', 'GD': 'Grenada', 'KN': 'Saint Kitts and Nevis', 'LC': 'Saint Lucia',
    'VC': 'Saint Vincent and the Grenadines', 'AW': 'Aruba', 'CW': 'Curaçao', 'SX': 'Sint Maarten',
    'BQ': 'Caribbean Netherlands', 'TC': 'Turks and Caicos Islands', 'AI': 'Anguilla',
    'MS': 'Montserrat', 'MF': 'Saint Martin', 'BL': 'Saint Barthélemy', 'GP': 'Guadeloupe',
    'MQ': 'Martinique',
    'BM': 'Bermuda', 'GL': 'Greenland', 'IS': 'Iceland', 'FO': 'Faroe Islands',
    'GI': 'Gibraltar', 'GG': 'Guernsey', 'JE': 'Jersey', 'IM': 'Isle of Man',
    'LI': 'Liechtenstein', 'MC': 'Monaco', 'SM': 'San Marino', 'VA': 'Vatican City', 'AD': 'Andorra',
    'VU': 'Vanuatu', 'NC': 'New Caledonia', 'PF': 'French Polynesia', 'WF': 'Wallis and Futuna',
    'FM': 'Micronesia', 'GU': 'Guam', 'MP': 'Northern Mariana Islands', 'PW': 'Palau',
    'MH': 'Marshall Islands', 'KI': 'Kiribati', 'NR': 'Nauru', 'TV': 'Tuvalu',
    'WS': 'Samoa', 'AS': 'American Samoa', 'TO': 'Tonga', 'NU': 'Niue', 'CK': 'Cook Islands',
    'TK': 'Tokelau', 'PN': 'Pitcairn Islands', 'NF': 'Norfolk Island', 'CC': 'Cocos Islands',
    'CX': 'Christmas Island', 'HM': 'Heard and McDonald Islands',
    'BN': 'Brunei',
    'SH': 'Saint Helena', 'FK': 'Falkland Islands', 'GS': 'South Georgia', 'AQ': 'Antarctica',
    'IO': 'British Indian Ocean Territory', 'SJ': 'Svalbard and Jan Mayen', 'AX': 'Åland Islands',
    'EH': 'Western Sahara', 'PM': 'Saint Pierre and Miquelon', 'UM': 'US Minor Outlying Islands',
    'HK': 'Hong Kong', 'MO': 'Macau', 'TF': 'French Southern Territories'
}

# Country coordinates (approximate center points for map display)
COUNTRY_COORDS = {
    'AF': (33.93911, 67.709953), 'AL': (41.153332, 20.168331), 'DZ': (28.033886, 1.659626),
    'AD': (42.546245, 1.601554), 'AO': (-11.202692, 17.873887), 'AG': (17.060816, -61.796428),
    'AR': (-38.416097, -63.616672), 'AM': (40.069099, 45.038189), 'AU': (-25.274398, 133.775136),
    'AT': (47.516231, 14.550072), 'AZ': (40.143105, 47.576927), 'BS': (25.03428, -77.39628),
    'BH': (26.0667, 50.5577), 'BD': (23.684994, 90.356331), 'BB': (13.193887, -59.543198),
    'BY': (53.709807, 27.953389), 'BE': (50.503887, 4.469936), 'BZ': (17.189877, -88.49765),
    'BJ': (9.30769, 2.315834), 'BT': (27.514162, 90.433601), 'BO': (-16.290154, -63.588653),
    'BA': (43.915886, 17.679076), 'BW': (-22.328474, 24.684866), 'BR': (-14.235004, -51.92528),
    'BN': (4.535277, 114.727669), 'BG': (42.733883, 25.48583), 'BF': (12.238333, -1.561593),
    'BI': (-3.373056, 29.918886), 'KH': (12.565679, 104.990963), 'CM': (7.369722, 12.354722),
    'CA': (56.130366, -106.346771), 'CV': (16.002082, -24.013197), 'CF': (6.611111, 20.939444),
    'TD': (15.454166, 18.732207), 'CL': (-35.675147, -71.542969), 'CN': (35.86166, 104.195397),
    'CO': (4.570868, -74.297333), 'KM': (-11.875001, 43.872219), 'CG': (-0.228021, 15.827659),
    'CD': (-4.038333, 21.758664), 'CR': (9.748917, -83.753428), 'CI': (7.539989, -5.54708),
    'HR': (45.1, 15.2), 'CU': (21.521757, -77.781167), 'CY': (35.126413, 33.429859),
    'CZ': (49.817492, 15.472962), 'DK': (56.26392, 9.501785), 'DJ': (11.825138, 42.590275),
    'DM': (15.414999, -61.370976), 'DO': (18.735693, -70.162651), 'EC': (-1.831239, -78.183406),
    'EG': (26.820553, 30.802498), 'SV': (13.794185, -88.89653), 'GQ': (1.650801, 10.267895),
    'ER': (15.179384, 39.782334), 'EE': (58.595272, 25.013607), 'SZ': (-26.522503, 31.465866),
    'ET': (9.145, 40.489673), 'FJ': (-17.713371, 178.065032), 'FI': (61.92411, 25.748151),
    'FR': (46.227638, 2.213749), 'GA': (-0.803689, 11.609444), 'GM': (13.443182, -15.310139),
    'GE': (42.315407, 43.356892), 'DE': (51.165691, 10.451526), 'GH': (7.946527, -1.023194),
    'GR': (39.074208, 21.824312), 'GD': (12.262776, -61.604171), 'GT': (15.783471, -90.230759),
    'GN': (9.945587, -9.696645), 'GW': (11.803749, -15.180413), 'GY': (4.860416, -58.93018),
    'HT': (18.971187, -72.285215), 'HN': (15.199999, -86.241905), 'HU': (47.162494, 19.503304),
    'IS': (64.963051, -19.020835), 'IN': (20.593684, 78.96288), 'ID': (-0.789275, 113.921327),
    'IR': (32.427908, 53.688046), 'IQ': (33.223191, 43.679291), 'IE': (53.41291, -8.24389),
    'IL': (31.046051, 34.851612), 'IT': (41.87194, 12.56738), 'JM': (18.109581, -77.297508),
    'JP': (36.204824, 138.252924), 'JO': (30.585164, 36.238414), 'KZ': (48.019573, 66.923684),
    'KE': (-0.023559, 37.906193), 'KI': (-3.370417, -168.734039), 'KP': (40.339852, 127.510093),
    'KR': (35.907757, 127.766922), 'KW': (29.31166, 47.481766), 'KG': (41.20438, 74.766098),
    'LA': (19.85627, 102.495496), 'LV': (56.879635, 24.603189), 'LB': (33.854721, 35.862285),
    'LS': (-29.609988, 28.233608), 'LR': (6.428055, -9.429499), 'LY': (26.3351, 17.228331),
    'LI': (47.166, 9.555373), 'LT': (55.169438, 23.881275), 'LU': (49.815273, 6.129583),
    'MG': (-18.766947, 46.869107), 'MW': (-13.254308, 34.301525), 'MY': (4.210484, 101.975766),
    'MV': (3.202778, 73.22068), 'ML': (17.570692, -3.996166), 'MT': (35.937496, 14.375416),
    'MH': (7.131474, 171.184478), 'MR': (21.00789, -10.940835), 'MU': (-20.348404, 57.552152),
    'MX': (23.634501, -102.552784), 'FM': (7.425554, 150.550812), 'MD': (47.411631, 28.369885),
    'MC': (43.750298, 7.412841), 'MN': (46.862496, 103.846656), 'ME': (42.708678, 19.37439),
    'MA': (31.791702, -7.09262), 'MZ': (-18.665695, 35.529562), 'MM': (21.913965, 95.956223),
    'NA': (-22.95764, 18.49041), 'NR': (-0.522778, 166.931503), 'NP': (28.394857, 84.124008),
    'NL': (52.132633, 5.291266), 'NZ': (-40.900557, 174.885971), 'NI': (12.865416, -85.207229),
    'NE': (17.607789, 8.081666), 'NG': (9.081999, 8.675277), 'MK': (41.512305, 21.6314),
    'NO': (60.472024, 8.468946), 'OM': (21.512583, 55.923255), 'PK': (30.375321, 69.345116),
    'PW': (7.51498, 134.58252), 'PS': (31.952162, 35.233154), 'PA': (8.537981, -80.782127),
    'PG': (-6.314993, 143.95555), 'PY': (-23.442503, -58.443832), 'PE': (-9.189967, -75.015152),
    'PH': (12.879721, 121.774017), 'PL': (51.919438, 19.145136), 'PT': (39.399872, -8.224454),
    'QA': (25.354826, 51.183884), 'RO': (45.943161, 24.96676), 'RU': (61.52401, 105.318756),
    'RW': (-1.940278, 29.873888), 'KN': (17.357822, -62.782998), 'LC': (13.909444, -60.978893),
    'VC': (12.984305, -61.287228), 'WS': (-13.759029, -172.104629), 'SM': (43.94236, 12.457777),
    'ST': (0.18636, 6.613081), 'SA': (23.885942, 45.079162), 'SN': (14.497401, -14.452362),
    'RS': (44.016521, 21.005859), 'SC': (-4.679574, 55.491977), 'SL': (8.460555, -11.779889),
    'SG': (1.352083, 103.819836), 'SK': (48.669026, 19.699024), 'SI': (46.151241, 14.995463),
    'SB': (-9.64571, 160.156194), 'SO': (5.152149, 46.199616), 'ZA': (-30.559482, 22.937506),
    'SS': (6.877, 31.307), 'ES': (40.463667, -3.74922), 'LK': (7.873054, 80.771797),
    'SD': (12.862807, 30.217636), 'SR': (3.919305, -56.027783), 'SE': (60.128161, 18.643501),
    'CH': (46.818188, 8.227512), 'SY': (34.802075, 38.996815), 'TW': (23.69781, 120.960515),
    'TJ': (38.861034, 71.276093), 'TZ': (-6.369028, 34.888822), 'TH': (15.870032, 100.992541),
    'TL': (-8.874217, 125.727539), 'TG': (8.619543, 0.824782), 'TO': (-21.178986, -175.198242),
    'TT': (10.691803, -61.222503), 'TN': (33.886917, 9.537499), 'TR': (38.963745, 35.243322),
    'TM': (38.969719, 59.556278), 'TV': (-7.109535, 177.64933), 'UG': (1.373333, 32.290275),
    'UA': (48.379433, 31.16558), 'AE': (23.424076, 53.847818), 'GB': (55.378051, -3.435973),
    'US': (37.09024, -95.712891), 'UY': (-32.522779, -55.765835), 'UZ': (41.377491, 64.585262),
    'VU': (-15.376706, 166.959158), 'VA': (41.902916, 12.453389), 'VE': (6.42375, -66.58973),
    'VN': (14.058324, 108.277199), 'YE': (15.552727, 48.516388), 'ZM': (-13.133897, 27.849332),
    'ZW': (-19.015438, 29.154857),
    # Territories
    'HK': (22.396428, 114.109497), 'MO': (22.198745, 113.543873), 'PR': (18.220833, -66.590149),
    'GU': (13.444304, 144.793731), 'AS': (-14.270972, -170.132217), 'VI': (18.335765, -64.896335),
    'MP': (15.0979, 145.6739), 'GL': (71.706936, -42.604303), 'FO': (61.892635, -6.911806),
    'AW': (12.52111, -69.968338), 'CW': (12.16957, -68.99002), 'SX': (18.0425, -63.0548),
    'BQ': (12.1784, -68.2385), 'AI': (18.220554, -63.068615), 'VG': (18.420695, -64.639968),
    'KY': (19.513469, -80.566956), 'BM': (32.321384, -64.75737), 'TC': (21.694025, -71.797928),
    'MS': (16.742498, -62.187366), 'GI': (36.137741, -5.345374), 'IM': (54.236107, -4.548056),
    'GG': (49.465691, -2.585278), 'JE': (49.214439, -2.13125), 'SH': (-15.965, -5.7089),
    'FK': (-51.796253, -59.523613), 'GS': (-54.429579, -36.587909), 'PM': (46.941936, -56.27111),
    'NC': (-20.904305, 165.618042), 'PF': (-17.679742, -149.406843), 'WF': (-13.768752, -177.156097),
    'TK': (-9.200199, -171.848403), 'CK': (-21.236736, -159.777671), 'NU': (-19.054445, -169.867233),
    'PN': (-24.703615, -127.439308), 'NF': (-29.040835, 167.954712), 'CX': (-10.447525, 105.690449),
    'CC': (-12.164165, 96.870956), 'AX': (60.178524, 19.915617), 'SJ': (77.553604, 23.670272),
    'IO': (-6.343194, 71.876519), 'TF': (-49.280366, 69.348557), 'RE': (-21.115141, 55.536384),
    'YT': (-12.8275, 45.166244), 'EH': (24.215527, -12.885834), 'XK': (42.602636, 20.902977),
    'GP': (16.265, -61.551), 'MQ': (14.641528, -61.024174), 'GF': (3.933889, -53.125782),
    'BL': (17.9, -62.833), 'MF': (18.0731, -63.0822),
}

def sanitize_folder_name(name):
    """Convert a name to folder-safe format."""
    folder_name = name.lower().replace(' ', '-').replace('/', '-').replace("'", '')
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

def get_language_path(languoid_id, language_data):
    """Get the relative URL path to a language page from the countries/{country}/ folder."""
    path_ids = build_tree_path(languoid_id, language_data)
    if not path_ids:
        return None
    
    path_parts = []
    for pid in path_ids:
        name = language_data[pid]['name']
        path_parts.append(sanitize_folder_name(name))
    
    # From countries/{country}/index.html, go up twice to root, then into languages/
    return '../../languages/' + '/'.join(path_parts) + '/index.html'

def format_name_with_extinction(name, lang_id):
    """Format a language name with extinction dagger if applicable."""
    if lang_id in EXTINCT_LANGUAGES:
        return f"† {name}"
    return name

def organize_languages_by_family(languages_in_country, language_data):
    """
    Organize languages into a hierarchical structure by family.
    Returns a dict: { top_family_id: { 'name': ..., 'children': [...] } }
    """
    # First, find the top-level family for each language
    language_to_top_family = {}
    
    for lang_id in languages_in_country:
        if lang_id not in language_data:
            continue
        
        path = build_tree_path(lang_id, language_data)
        if path:
            # Top family is the first element in path
            top_family = path[0]
            language_to_top_family[lang_id] = top_family
        else:
            # Isolate - treat as its own family
            language_to_top_family[lang_id] = lang_id
    
    # Group languages by top-level family
    family_groups = defaultdict(list)
    for lang_id, top_family in language_to_top_family.items():
        family_groups[top_family].append(lang_id)
    
    return family_groups

def build_hierarchy_tree(lang_ids, language_data, child_map):
    """
    Build a hierarchical tree structure from a flat list of language IDs.
    Returns nested structure for display.
    """
    if not lang_ids:
        return []
    
    # Find common ancestors and build tree
    # We need to include intermediate nodes (subfamilies) between languages
    
    # Get all paths
    all_nodes = set()
    for lang_id in lang_ids:
        path = build_tree_path(lang_id, language_data)
        all_nodes.update(path)
    
    # Build tree from nodes
    roots = []
    node_children = defaultdict(list)
    
    for node_id in all_nodes:
        if node_id not in language_data:
            continue
        parent_id = language_data[node_id]['parent_id']
        if parent_id and parent_id in all_nodes:
            node_children[parent_id].append(node_id)
        elif not parent_id or parent_id not in all_nodes:
            roots.append(node_id)
    
    def build_subtree(node_id, target_langs):
        """Build subtree recursively, only including branches that lead to target languages."""
        if node_id not in language_data:
            return None
        
        data = language_data[node_id]
        children_ids = sorted(node_children.get(node_id, []), 
                             key=lambda x: language_data.get(x, {}).get('name', ''))
        
        # Filter children to only those that are in all_nodes
        children = []
        for cid in children_ids:
            child_tree = build_subtree(cid, target_langs)
            if child_tree:
                children.append(child_tree)
        
        # Include this node if it's a target language OR has children leading to targets
        is_target = node_id in target_langs
        if is_target or children:
            return {
                'id': node_id,
                'name': data['name'],
                'level': data['level'],
                'children': children,
                'is_target': is_target
            }
        return None
    
    target_set = set(lang_ids)
    result = []
    for root_id in sorted(roots, key=lambda x: language_data.get(x, {}).get('name', '')):
        tree = build_subtree(root_id, target_set)
        if tree:
            result.append(tree)
    
    return result

def render_language_tree_html(tree_nodes, language_data, depth=0):
    """Render a hierarchical language tree as nested HTML lists with collapsible nodes."""
    if not tree_nodes:
        return ""
    
    html_parts = []
    indent = "    " * depth
    
    if depth == 0:
        html_parts.append(f'{indent}<ul class="language-tree">')
    else:
        html_parts.append(f'{indent}<ul class="language-subtree">')
    
    for node in tree_nodes:
        lang_id = node['id']
        name = node['name']
        level = node['level']
        children = node.get('children', [])
        is_target = node.get('is_target', False)
        
        formatted_name = format_name_with_extinction(name, lang_id)
        path = get_language_path(lang_id, language_data)
        
        level_class = f"level-{level}"
        target_class = "target-language" if is_target else "intermediate-node"
        has_children_class = "has-children" if children else ""
        
        html_parts.append(f'{indent}    <li class="{level_class} {target_class} {has_children_class}">')
        
        # Add toggle button if node has children
        if children:
            html_parts.append(f'{indent}        <span class="tree-toggle expanded" onclick="toggleTree(this)">▼</span>')
        
        if path:
            html_parts.append(f'{indent}        <a href="{path}">{formatted_name}</a>')
        else:
            html_parts.append(f'{indent}        <span>{formatted_name}</span>')
        
        if children:
            html_parts.append(render_language_tree_html(children, language_data, depth + 2))
        
        html_parts.append(f'{indent}    </li>')
    
    html_parts.append(f'{indent}</ul>')
    
    return '\n'.join(html_parts)

def count_target_languages(tree_nodes):
    """Count the number of target languages (actual languages in this country) in a tree."""
    count = 0
    for node in tree_nodes:
        if node.get('is_target', False):
            count += 1
        count += count_target_languages(node.get('children', []))
    return count

def generate_country_page(country_code, languages_in_country, language_data, child_map):
    """Generate HTML content for a country page."""
    country_name = COUNTRY_NAMES.get(country_code, country_code)
    coords = COUNTRY_COORDS.get(country_code)
    
    # Organize languages by family
    family_groups = organize_languages_by_family(languages_in_country, language_data)
    
    # Build tree for each family group
    family_trees = {}
    for top_family_id, lang_ids in family_groups.items():
        tree = build_hierarchy_tree(lang_ids, language_data, child_map)
        if tree:
            family_trees[top_family_id] = tree
    
    # Sort families by name
    sorted_families = sorted(family_trees.keys(), 
                            key=lambda x: language_data.get(x, {}).get('name', ''))
    
    # Count languages
    total_languages = len(languages_in_country)
    family_count = len(family_trees)
    
    # Build HTML - matching language page style
    html_parts = []
    html_parts.append(f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Languages of {country_name} — Babel</title>
    <link rel="icon" type="image/webp" href="../../favicon.webp">
    <link rel="stylesheet" href="../../style.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
</head>
<body>
    <!-- Search Bar -->
    <div class="search-container">
        <input type="text" class="search-bar" placeholder="Search languages, families, texts..." id="search-input">
        <div class="search-results" id="search-results"></div>
    </div>

    <div class="page-wrapper">
    <div class="container">
        <div class="country-header">
            <img src="https://flagcdn.com/w160/{country_code.lower()}.png" 
                 alt="{country_name} flag" 
                 class="country-flag-large">
            <h1>Languages of {country_name}</h1>
        </div>
        
        <div class="metadata">
            <p><strong>Languages:</strong> {total_languages}</p>
            <p><strong>Language Families:</strong> {family_count}</p>
        </div>
''')

    # Add map if we have coordinates
    if coords:
        lat, lon = coords
        map_id = f"country-map-{country_code.lower()}"
        html_parts.append(f'''
        <div class="locality-section">
            <h3>Location</h3>
            <div id="{map_id}" class="country-map"></div>
        </div>
        <script>
            (function() {{
                var map = L.map('{map_id}').setView([{lat}, {lon}], 4);
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    attribution: '© OpenStreetMap',
                    maxZoom: 19,
                    minZoom: 2
                }}).addTo(map);
                L.circleMarker([{lat}, {lon}], {{
                    radius: 8,
                    fillColor: '#B85A4F',
                    color: '#8B4530',
                    weight: 2.5,
                    opacity: 1,
                    fillOpacity: 0.9
                }}).addTo(map).bindPopup('<b>{country_name}</b>');
                setTimeout(function() {{ map.invalidateSize(); }}, 150);
            }})();
        </script>
''')

    # Add language families with expand/collapse controls
    html_parts.append('''        <div class="tree-controls">
            <h2>Languages by Family</h2>
            <div class="tree-buttons">
                <button onclick="expandAll()" class="tree-btn">Expand All</button>
                <button onclick="collapseAll()" class="tree-btn">Collapse All</button>
            </div>
        </div>
''')
    
    for family_id in sorted_families:
        tree = family_trees[family_id]
        family_name = language_data.get(family_id, {}).get('name', family_id)
        family_name_formatted = format_name_with_extinction(family_name, family_id)
        lang_count = count_target_languages(tree)
        
        family_path = get_language_path(family_id, language_data)
        
        html_parts.append(f'''
        <div class="family-section">
            <div class="family-header">
                <h3>''')
        
        if family_path:
            html_parts.append(f'<a href="{family_path}">{family_name_formatted}</a>')
        else:
            html_parts.append(family_name_formatted)
        
        html_parts.append(f'''</h3>
                <span class="family-count">({lang_count} language{'s' if lang_count != 1 else ''})</span>
            </div>
{render_language_tree_html(tree, language_data, 3)}
        </div>
''')

    html_parts.append('''
    </div>
    
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
            </ul>
        </nav>
    </aside>
</div>

    
    <!-- Tree toggle functionality -->
    <script>
        function toggleTree(toggle) {
            const li = toggle.parentElement;
            const subtree = li.querySelector('.language-subtree');
            if (subtree) {
                if (toggle.classList.contains('expanded')) {
                    toggle.classList.remove('expanded');
                    toggle.classList.add('collapsed');
                    toggle.textContent = '▶';
                    subtree.style.display = 'none';
                } else {
                    toggle.classList.remove('collapsed');
                    toggle.classList.add('expanded');
                    toggle.textContent = '▼';
                    subtree.style.display = 'block';
                }
            }
        }
        
        function expandAll() {
            document.querySelectorAll('.tree-toggle').forEach(toggle => {
                toggle.classList.remove('collapsed');
                toggle.classList.add('expanded');
                toggle.textContent = '▼';
                const subtree = toggle.parentElement.querySelector('.language-subtree');
                if (subtree) subtree.style.display = 'block';
            });
        }
        
        function collapseAll() {
            document.querySelectorAll('.tree-toggle').forEach(toggle => {
                toggle.classList.remove('expanded');
                toggle.classList.add('collapsed');
                toggle.textContent = '▶';
                const subtree = toggle.parentElement.querySelector('.language-subtree');
                if (subtree) subtree.style.display = 'none';
            });
        }
    </script>
    
    <!-- Search functionality -->
    <script src="../../search-index.js"></script>
    <script src="../../search.js"></script>
</body>
</html>''')

    return ''.join(html_parts)

def update_flag_links_in_language_pages(country_pages_created):
    """Update language page flags to link to country pages."""
    # This will be handled by modifying generate_country_flags_html in update_family_trees.py
    pass

def main():
    print("=" * 70)
    print("Generating country pages")
    print("=" * 70)
    
    # Load language data
    print("Loading language data...")
    language_data = {}
    
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
                country_ids = row.get('country_ids', '').strip()
                
                if not languoid_id or not name:
                    continue
                
                language_data[languoid_id] = {
                    'name': name,
                    'parent_id': parent_id,
                    'level': level,
                    'country_ids': country_ids
                }
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return
    
    print(f"Loaded {len(language_data)} languoids")
    
    # Build child map
    child_map = defaultdict(list)
    for lid, data in language_data.items():
        if data['parent_id']:
            child_map[data['parent_id']].append(lid)
    
    # Build country -> languages mapping (only languages and dialects, not families)
    print("Building country-language mappings...")
    country_languages = defaultdict(set)
    
    for lang_id, data in language_data.items():
        if data['level'] not in ['language', 'dialect']:
            continue
        
        country_ids = data.get('country_ids', '')
        if not country_ids:
            continue
        
        for country_code in country_ids.split():
            country_code = country_code.strip().upper()
            if country_code:
                country_languages[country_code].add(lang_id)
    
    print(f"Found {len(country_languages)} countries with languages")
    
    # Create countries directory
    os.makedirs(COUNTRIES_DIR, exist_ok=True)
    
    # Generate country pages
    print("\nGenerating country pages...")
    created_count = 0
    
    for country_code, lang_ids in sorted(country_languages.items()):
        country_name = COUNTRY_NAMES.get(country_code, country_code)
        folder_name = sanitize_folder_name(country_name)
        country_dir = os.path.join(COUNTRIES_DIR, folder_name)
        
        os.makedirs(country_dir, exist_ok=True)
        
        html_content = generate_country_page(country_code, lang_ids, language_data, child_map)
        
        index_path = os.path.join(country_dir, 'index.html')
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        created_count += 1
        
        if created_count % 50 == 0:
            print(f"  Created {created_count} pages...")
    
    print(f"\nCreated {created_count} country pages in {COUNTRIES_DIR}")
    
    # Create countries index page
    print("\nGenerating countries index page...")
    create_countries_index(country_languages, language_data)
    print("Created countries index page")
    
    print("\n" + "=" * 70)
    print("Done! Now run update_family_trees.py to update flag links in language pages.")
    print("=" * 70)

def create_countries_index(country_languages, language_data):
    """Create an index page listing all countries."""
    
    # Sort countries by language count (descending), then by name
    sorted_countries = sorted(
        country_languages.items(),
        key=lambda x: (-len(x[1]), COUNTRY_NAMES.get(x[0], x[0]))
    )
    
    total_countries = len(sorted_countries)
    
    html_parts = [f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Countries — Babel</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <!-- Search Bar -->
    <div class="search-container">
        <input type="text" class="search-bar" placeholder="Search languages, families, texts..." id="search-input">
        <div class="search-results" id="search-results"></div>
    </div>

    <div class="container">
        <h1>Countries</h1>
        
        <div class="metadata">
            <p><strong>Total Countries:</strong> {total_countries}</p>
            <p>Browse languages by country. Sorted by number of languages.</p>
        </div>
        
        <div class="countries-grid">
''']
    
    for country_code, lang_ids in sorted_countries:
        country_name = COUNTRY_NAMES.get(country_code, country_code)
        folder_name = sanitize_folder_name(country_name)
        lang_count = len(lang_ids)
        
        html_parts.append(f'''            <a href="countries/{folder_name}/index.html" class="country-card">
                <img src="https://flagcdn.com/w80/{country_code.lower()}.png" alt="{country_name}">
                <div class="country-info">
                    <div class="country-name">{country_name}</div>
                    <div class="language-count">{lang_count} language{'s' if lang_count != 1 else ''}</div>
                </div>
            </a>
''')
    
    html_parts.append('''        </div>
    </div>
    
    <!-- Search functionality -->
    <script src="search-index.js"></script>
    <script src="search.js"></script>
</body>
</html>''')
    
    index_path = os.path.join(BASE_DIR, 'countries-index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(''.join(html_parts))

if __name__ == '__main__':
    main()
