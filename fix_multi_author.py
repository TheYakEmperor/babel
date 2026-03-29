#!/usr/bin/env python3
"""Update text pages to support multiple authors (array)"""

import re
from pathlib import Path

texts_dir = Path('/Users/yakking/Downloads/Web-design/Babel/texts')

old_author_code = '''            // Author - look up from author.json
            if (data.author) {
                const authorId = data.author;
                // Try to fetch author name from author.json
                fetch(`../../../../authors/${authorId}/author.json`)
                    .then(r => r.ok ? r.json() : null)
                    .then(authorData => {
                        const authorName = authorData ? authorData.name : authorId;
                        const authorLink = `<a href="../../../../authors/${authorId}/index.html">${authorName}</a>`;
                        const authorP = document.createElement('p');
                        authorP.innerHTML = `<strong>Author:</strong> ${authorLink}`;
                        const metaDiv = document.getElementById('metadata');
                        const titleP = metaDiv.querySelector('p');
                        if (titleP) titleP.after(authorP);
                    })
                    .catch(() => {});
            }'''

new_author_code = '''            // Author(s) - look up from author.json
            // Slugify author name to match directory structure
            const slugifyAuthor = (name) => name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
            if (data.author) {
                const authors = Array.isArray(data.author) ? data.author : [data.author];
                Promise.all(authors.map(authorRaw => {
                    const authorSlug = slugifyAuthor(authorRaw);
                    return fetch(`../../../../authors/${authorSlug}/author.json`)
                        .then(r => r.ok ? r.json() : null)
                        .then(authorData => ({
                            id: authorSlug,
                            name: authorData ? authorData.name : authorRaw
                        }))
                        .catch(() => ({ id: authorSlug, name: authorRaw }));
                })).then(authorInfos => {
                    const authorLinks = authorInfos.map(a => 
                        `<a href="../../../../authors/${a.id}/index.html">${a.name}</a>`
                    ).join(', ');
                    const label = authorInfos.length > 1 ? 'Authors' : 'Author';
                    const authorP = document.createElement('p');
                    authorP.innerHTML = `<strong>${label}:</strong> ${authorLinks}`;
                    const metaDiv = document.getElementById('metadata');
                    const titleP = metaDiv.querySelector('p');
                    if (titleP) titleP.after(authorP);
                });
            }'''

for html_file in texts_dir.rglob('index.html'):
    content = html_file.read_text()
    if old_author_code in content:
        new_content = content.replace(old_author_code, new_author_code)
        html_file.write_text(new_content)
        print(f"Updated: {html_file}")

print("Done!")
