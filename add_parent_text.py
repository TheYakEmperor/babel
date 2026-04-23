"""Patch all text index.html files to display belongsTo parent chain."""
from pathlib import Path

BABEL = Path('/Users/yakking/Downloads/Web-design/Babel')

BELONGS_TO_BLOCK = """            // Parent text (belongsTo) - chase chain for full breadcrumb
            if (data.belongsTo) {
                (async function buildParentChain(startId) {
                    const ancestors = [];
                    const seen = new Set([data.id]);
                    let currentId = startId;
                    while (currentId && !seen.has(currentId)) {
                        seen.add(currentId);
                        try {
                            const parentRes = await fetch(`../../../../texts/00/00/${currentId}/data.json`);
                            if (!parentRes.ok) break;
                            const parentData = await parentRes.json();
                            ancestors.unshift({ id: currentId, title: parentData.title || currentId });
                            currentId = parentData.belongsTo || '';
                        } catch(e) { break; }
                    }
                    if (ancestors.length === 0) {
                        ancestors.push({ id: startId, title: startId });
                    }
                    const crumbs = ancestors.map(a =>
                        `<a href="../../../../texts/00/00/${a.id}/">${a.title}</a>`
                    ).join(' \u203a ');
                    const parentP = document.createElement('p');
                    parentP.innerHTML = `<strong>Parent:</strong> ${crumbs}`;
                    parentP.id = 'meta-parent';
                    const metaDiv = document.getElementById('metadata');
                    const groupP = document.getElementById('meta-groups') || document.getElementById('meta-collections') || document.getElementById('meta-provenances') || document.getElementById('meta-sources') || metaDiv.querySelector('p');
                    if (groupP) groupP.after(parentP);
                    else metaDiv.appendChild(parentP);
                })(data.belongsTo);
            }
"""

ANCHOR = "if (data.date) metaHtml +="
ALREADY_PATCHED = "if (data.belongsTo)"

patched = 0
skipped = 0
for html_file in BABEL.glob('texts/**/*.html'):
    if html_file.name != 'index.html':
        continue
    content = html_file.read_text(encoding='utf-8')
    if ALREADY_PATCHED in content:
        skipped += 1
        continue
    if ANCHOR not in content:
        print(f"No anchor in {html_file}")
        continue
    new_content = content.replace(ANCHOR, BELONGS_TO_BLOCK + ANCHOR, 1)
    html_file.write_text(new_content, encoding='utf-8')
    patched += 1

print(f"Patched: {patched}, Already done: {skipped}")
