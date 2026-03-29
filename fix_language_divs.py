#!/usr/bin/env python3
"""
Fix language pages - the main-content div is closing too early,
leaving dialects/information/resources sections outside the container.
"""

import os
import re
from pathlib import Path

def fix_language_page(file_path):
    """Fix the premature closing of main-content in language pages"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # The problem: there are </div></div> closing tags appearing before </section> tags
    # These prematurely close the main-content and container
    
    # Pattern to find: </div>\n</div> followed by whitespace and then </section> or <script>
    # that appears BEFORE the final footer
    
    # Find the pattern where divs close prematurely before sections continue
    # Looking for: </div>\n</div>\n\n    </div>\n</div>\n\n    <script>
    
    # The issue is around the locality-section / geographic-info area
    # Remove the extra </div></div> that appear before </section>
    
    # Pattern: </div>\n</div>\n        \n    </div>\n</div>\n\n    <script>
    pattern1 = r'(</div>\n</div>)\s*\n\s*(</div>\n</div>)\s*(\n\s*<script>)'
    if re.search(pattern1, content):
        # Keep only one set of closing divs
        content = re.sub(pattern1, r'\1\3', content)
    
    # Also look for </div>\n</div> right before </section> tags (premature closure)
    # Pattern: </div>\n    </div>\n</div>\n        \n    </div>\n</div>\n\n    <script>
    pattern2 = r'</div>\n\s*</div>\n</div>\n\s*</div>\n</div>\n\n\s*<script>'
    if re.search(pattern2, content):
        content = re.sub(pattern2, '</div>\n    </div>\n\n    <script>', content)
    
    # The real fix: find where </div></div> appears before script tags but with sections after
    # We need to move content that's outside main-content back inside
    
    # Better approach: find the structure and fix it properly
    # Look for pattern where we have:
    # </div>\n</div>\n\n    </div>\n</div>\n\n    <script>...map init...</script>\n        </section>
    
    # This pattern catches the broken structure
    pattern3 = r'(</div>\n</div>)\s*(</div>\n</div>)\s*(<script>.*?</script>)\s*(</section>)'
    if re.search(pattern3, content, re.DOTALL):
        content = re.sub(pattern3, r'\1\n\3\n\4', content, flags=re.DOTALL)
    
    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    languages_dir = Path('/Users/yakking/Downloads/Web-design/Babel/languages')
    
    fixed = 0
    total = 0
    
    for root, dirs, files in os.walk(languages_dir):
        for filename in files:
            if filename == 'index.html':
                file_path = Path(root) / filename
                total += 1
                if fix_language_page(file_path):
                    fixed += 1
                    if fixed <= 10:
                        rel_path = file_path.relative_to(languages_dir)
                        print(f"Fixed: {rel_path}")
    
    print(f"\nTotal fixed: {fixed} / {total} language pages")

if __name__ == '__main__':
    main()
