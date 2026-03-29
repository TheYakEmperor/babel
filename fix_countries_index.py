#!/usr/bin/env python3
"""Fix countries-index.html layout"""

import re

with open('/Users/yakking/Downloads/Web-design/Babel/countries-index.html', 'r') as f:
    content = f.read()

# Check if already has the structure
if 'header-logo-container' in content:
    print('Already fixed')
    exit(0)

# Extract the countries grid section - need a different pattern since grid has nested divs
# Find everything between <div class="countries-grid"> and the closing </div> before scripts
grid_start = content.find('<div class="countries-grid">')
grid_end = content.find('</div>\n    </div>\n    \n    <!-- Search')
if grid_end == -1:
    grid_end = content.find('</div>\n    </div>\n\n    <!-- Search')
if grid_end == -1:
    grid_end = content.find('</div>\n    </div>\n    <script')

if grid_start == -1:
    print('Could not find countries grid start')
    exit(1)

# Find the actual end of the grid
temp_content = content[grid_start:]
# Count </a> tags to find all country cards, then find the closing </div>
card_count = temp_content.count('</a>')
print(f"Found {card_count} country cards")

# Find the closing </div> for countries-grid
last_card_end = 0
for i in range(card_count):
    last_card_end = temp_content.find('</a>', last_card_end + 1)
    
grid_end_in_temp = temp_content.find('</div>', last_card_end)
grid_content = temp_content[:grid_end_in_temp + 6]

# Build new content
new_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Countries — Babel Archive</title>
    <link rel="icon" type="image/webp" href="favicon.webp">
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="search-container">
        <input type="text" id="searchInput" class="search-bar" placeholder="Search languages and dialects...">
        <div id="searchResults" class="search-results"></div>
    </div>
    
    <div class="page-wrapper">
    <div class="header-logo-container"><a href="./" class="header-logo"><img src="Wikilogo.webp" alt="Babel Archive"></a></div>
        <div class="container">
        <aside class="right-sidebar">
            <a href="./" class="sidebar-logo">
                <img src="background-image/1111babel.png" alt="Babel Archive">
            </a>
            <nav class="sidebar-links">
                <h3>Navigate</h3>
                <ul>
                    <li><a href="./">Home</a></li>
                    <li><a href="texts-index.html">All Texts</a></li>
                    <li><a href="languages/">Languages</a></li>
                    <li><a href="works/">Works Index</a></li>
                    <li><a href="authors/">Authors</a></li>
                    <li><a href="sources/">Sources</a></li>
                    <li><a href="provenances/">Provenances</a></li>
                    <li><a href="collections/">Collections</a></li>
                </ul>
            </nav>
        </aside>
        <div class="main-content">
        <h1>Countries</h1>
        
        <div class="metadata">
            <p><strong>Total Countries:</strong> 246</p>
            <p>Browse languages by country. Sorted by number of languages.</p>
        </div>
        
        ''' + grid_content + '''
        </div>
        <aside class="left-sidebar"></aside>
    </div>
</div>

    <script src="search-index.js"></script>
    <script src="search.js"></script>
</body>
</html>
'''

with open('/Users/yakking/Downloads/Web-design/Babel/countries-index.html', 'w') as f:
    f.write(new_content)

print('Fixed countries-index.html')
