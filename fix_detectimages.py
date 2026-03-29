#!/usr/bin/env python3
"""Update detectImages function in all text pages to scan directory listing"""

import re
from pathlib import Path

old_pattern = r'''        // Get images from pagesData or (?:detect by probing|scan images/ directory)
        async function detectImages\(\) \{
            // First check if pagesData has image properties
            const fromData = pagesData
                \.filter\(p => p\.image\)
                \.map\(p => \(\{ url: p\.image, label: p\.label \|\| '' \}\)\);
            
            if \(fromData\.length > 0\) \{
                return fromData;
            \}
            
            // Fall back to numeric detection
            const extensions = \['jpg', 'jpeg', 'png', 'webp', 'gif'\];
            const found = \[\];
            const pageCount = pagesData\.length \|\| 20;
            
            for \(let i = 0; i <= Math\.max\(pageCount, 20\); i\+\+\) \{
                for \(const ext of extensions\) \{
                    try \{
                        const url = `images/\$\{i\}\.\$\{ext\}`;
                        const resp = await fetch\(url, \{ method: 'HEAD' \}\);
                        if \(resp\.ok\) \{
                            found\.push\(\{ url: url, label: String\(i\) \}\);
                            break;
                        \}
                    \} catch \(e\) \{\}
                \}
            \}
            
            return found;
        \}'''

new_code = '''        // Get images from pagesData or scan images/ directory
        async function detectImages() {
            // First check if pagesData has image properties
            const fromData = pagesData
                .filter(p => p.image)
                .map(p => ({ url: p.image, label: p.label || '' }));
            
            if (fromData.length > 0) {
                return fromData;
            }
            
            // Scan images/ directory listing
            try {
                const resp = await fetch('images/');
                if (resp.ok) {
                    const html = await resp.text();
                    const imageExts = /\\.(jpg|jpeg|png|webp|gif)$/i;
                    const matches = html.match(/href="([^"]+)"/g) || [];
                    const found = matches
                        .map(m => m.replace(/href="|"/g, ''))
                        .filter(f => imageExts.test(f) && !f.startsWith('/'))
                        .sort()
                        .map(f => ({
                            url: 'images/' + f,
                            label: f.replace(/\\.[^.]+$/, '').replace(/_/g, ' ')
                        }));
                    if (found.length > 0) return found;
                }
            } catch (e) {}
            
            // Final fallback: probe numeric files
            const extensions = ['jpg', 'jpeg', 'png', 'webp', 'gif'];
            const found = [];
            for (let i = 0; i <= 20; i++) {
                for (const ext of extensions) {
                    try {
                        const url = `images/${i}.${ext}`;
                        const resp = await fetch(url, { method: 'HEAD' });
                        if (resp.ok) {
                            found.push({ url: url, label: String(i) });
                            break;
                        }
                    } catch (e) {}
                }
            }
            
            return found;
        }'''

texts_dir = Path('/Users/yakking/Downloads/Web-design/Babel/texts')

for html_file in texts_dir.rglob('index.html'):
    content = html_file.read_text()
    if 'async function detectImages()' in content:
        new_content = re.sub(old_pattern, new_code, content)
        if new_content != content:
            html_file.write_text(new_content)
            print(f"Fixed: {html_file}")
        else:
            print(f"Already up to date or pattern mismatch: {html_file}")
