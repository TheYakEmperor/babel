// Simple search functionality
console.log('[search] search.js loaded');

// === CONVERT TO STEPPED SEARCH BAR (runs immediately) ===
(function() {
    // Get base path from existing relative links in the page
    function getBasePath() {
        // Check stylesheet link which is always present
        const stylesheet = document.querySelector('link[href*="style.css"]');
        if (stylesheet) {
            const href = stylesheet.getAttribute('href');
            return href.replace('style.css', '');
        }
        // Fallback: check favicon
        const favicon = document.querySelector('link[href*="favicon"]');
        if (favicon) {
            const href = favicon.getAttribute('href');
            return href.replace(/favicon\.(webp|ico|png)/, '');
        }
        return '';
    }
    
    const basePath = getBasePath();
    const searchContainer = document.querySelector('.search-container');
    
    // Convert non-stepped search containers to stepped immediately
    if (searchContainer && !searchContainer.classList.contains('stepped')) {
        // Add stepped class
        searchContainer.classList.add('stepped');
        
        // Completely replace content with stepped version
        searchContainer.innerHTML = `
            <a href="${basePath || './'}"><img src="${basePath}Wikilogo.webp" alt="Babel Archive" class="search-logo"></a>
            <div class="rainbow-buttons">
                <a href="#" class="rainbow-btn" style="background:#ff0000; color:#fff;">Link-1</a>
                <a href="#" class="rainbow-btn" style="background:#ffa500; color:#000;">Link-2</a>
                <a href="#" class="rainbow-btn" style="background:#ffff00; color:#000;">Link-3</a>
            </div>
            <div class="search-bar-wrapper">
                <input type="text" id="searchInput" class="search-bar" placeholder="Search...">
                <div id="searchResults" class="search-results"></div>
            </div>
            <div class="rainbow-buttons">
                <a href="#" class="rainbow-btn" style="background:#008001; color:#fff;">Link-4</a>
                <a href="#" class="rainbow-btn" style="background:#0000ff; color:#fff;">Link-5</a>
                <a href="#" class="rainbow-btn" style="background:#800080; color:#fff;">Link-7</a>
            </div>
        `;
    }
    
    // === ADD SIDEBAR DECORATION IMAGES (after DOM ready) ===
    document.addEventListener('DOMContentLoaded', function() {
        const leftSidebar = document.querySelector('.left-sidebar');
        if (leftSidebar && !leftSidebar.querySelector('.sidebar-decoration')) {
            const decorDiv = document.createElement('div');
            decorDiv.className = 'sidebar-decoration';
            decorDiv.innerHTML = `
                <img src="${basePath}background-image/grannyniggles.gif" alt="">
                <img src="${basePath}background-image/construction.jpg" alt="Under Construction">
            `;
            leftSidebar.insertBefore(decorDiv, leftSidebar.firstChild);
        }
    });
})();

// === MOVE SEARCH INTO SIDEBAR & SCROLL BEHAVIOR ===
(function() {
    // Run immediately for sidebar positioning (no flash)
    const sidebar = document.querySelector('.right-sidebar');
    const initialTop = 200;
    const stuckTop = 20;
    
    // Set initial sidebar position immediately to avoid lag
    if (sidebar) {
        // Estimate logo height (will be refined after load)
        const estimatedLogoHeight = 120;
        const sidebarStuckTop = stuckTop - estimatedLogoHeight;
        
        function updatePositions(logoHeight) {
            const actualStuckTop = stuckTop - logoHeight;
            const scrollY = window.scrollY;
            
            let sidebarTop = initialTop - scrollY;
            if (sidebarTop < actualStuckTop) {
                sidebarTop = actualStuckTop;
            }
            
            sidebar.style.top = sidebarTop + 'px';
        }
        
        // Initial position with estimated values
        updatePositions(estimatedLogoHeight);
        
        // Refine after DOM is ready
        document.addEventListener('DOMContentLoaded', function() {
            const sidebarLogo = document.querySelector('.sidebar-logo');
            
            let logoHeight = estimatedLogoHeight;
            if (sidebarLogo) {
                logoHeight = sidebarLogo.offsetHeight + 40;
            }
            
            // Update with actual logo height
            updatePositions(logoHeight);
            
            // Attach scroll listener with actual logo height
            window.addEventListener('scroll', function() {
                updatePositions(logoHeight);
            });
        });
    }
})();

function initializeSearch() {
    // Support both ID formats (camelCase from language pages, kebab-case from country pages)
    const searchInput = document.getElementById('searchInput') || document.getElementById('search-input');
    const searchResults = document.getElementById('searchResults') || document.getElementById('search-results');
    
    if (!searchInput) {
        console.error('[search] searchInput not found');
        return;
    }
    
    if (!searchResults) {
        console.error('[search] searchResults not found');
        return;
    }
    
    if (typeof LANGUAGE_INDEX === 'undefined') {
        console.error('[search] LANGUAGE_INDEX not available');
        return;
    }
    
    console.log('[search] initialized with', LANGUAGE_INDEX.length, 'entries');
    
    // Handle typing (show results as you type)
    searchInput.addEventListener('input', function() {
        const query = this.value.trim().toLowerCase();
        
        if (query.length === 0) {
            searchResults.innerHTML = '';
            searchResults.style.display = 'none';
            return;
        }
        
        // Filter matching entries - check name, id, and alternate names
        // Score: exact match > starts with > contains; name > alt > id
        const matches = LANGUAGE_INDEX.map(entry => {
            const name = (entry.name || '').toLowerCase();
            const id = (entry.id || '').toLowerCase();
            const altNames = entry.alt || [];
            let score = 0;
            let matchedAlt = null;
            let matchType = null;
            
            // Check primary name (highest priority)
            if (name === query) {
                score = 100; // Exact match
                matchType = 'name';
            } else if (name.startsWith(query)) {
                score = 80; // Starts with
                matchType = 'name';
            } else if (name.includes(query)) {
                score = 60; // Contains
                matchType = 'name';
            }
            
            // Check alternate names
            if (score < 90) { // Only if we don't have an exact primary match
                for (let i = 0; i < altNames.length; i++) {
                    const alt = altNames[i].toLowerCase();
                    if (alt === query && score < 90) {
                        score = 90; // Exact alt match
                        matchedAlt = altNames[i];
                        matchType = 'alt';
                    } else if (alt.startsWith(query) && score < 70) {
                        score = 70; // Alt starts with
                        matchedAlt = altNames[i];
                        matchType = 'alt';
                    } else if (alt.includes(query) && score < 50) {
                        score = 50; // Alt contains
                        matchedAlt = altNames[i];
                        matchType = 'alt';
                    }
                }
            }
            
            // Check Glottolog ID (lowest priority)
            if (score === 0 && id.includes(query)) {
                score = 30;
                matchType = 'id';
            }
            
            if (score > 0) {
                // Boost languages over families/dialects slightly
                if (entry.level === 'language') score += 5;
                return { entry: entry, matchedAlt: matchedAlt, matchType: matchType, score: score };
            }
            return null;
        }).filter(match => match !== null)
          .sort((a, b) => b.score - a.score)
          .slice(0, 100);
        
        console.log('[search] input="' + query + '" matches=' + matches.length);
        
        if (matches.length === 0) {
            searchResults.innerHTML = '<div class="search-no-results">No results found</div>';
            searchResults.style.display = 'block';
            return;
        }
        
        // Calculate base path from current page to root
        // This handles pages at different depths (e.g., /countries/mexico/index.html)
        const pathParts = window.location.pathname.split('/').filter(p => p.length > 0);
        // Remove the filename if present
        if (pathParts.length > 0 && pathParts[pathParts.length - 1].includes('.')) {
            pathParts.pop();
        }
        const basePath = pathParts.length > 0 ? '../'.repeat(pathParts.length) : './';
        
        // Build HTML for results
        let html = '';
        matches.forEach(match => {
            const entry = match.entry;
            let badge = '';
            if (entry.level === 'country') {
                // Show flag for countries
                const code = entry.code ? entry.code.toLowerCase() : entry.id;
                badge = ' <img src="https://flagcdn.com/w20/' + code + '.png" class="result-flag" alt="">';
            } else if (entry.level === 'text') {
                badge = ' <span class="result-badge text-badge">text</span>';
            } else if (entry.level === 'work') {
                badge = ' <span class="result-badge work-badge">work</span>';
            } else if (entry.level === 'author') {
                badge = ' <span class="result-badge author-badge">author</span>';
            } else if (entry.level === 'source') {
                badge = ' <span class="result-badge source-badge">source</span>';
            } else if (entry.level === 'provenance') {
                badge = ' <span class="result-badge provenance-badge">provenance</span>';
            } else if (entry.level === 'collection') {
                badge = ' <span class="result-badge collection-badge">collection</span>';
            } else if (entry.level === 'dialect') {
                badge = ' <span class="result-badge">dialect</span>';
            } else if (entry.level === 'family') {
                badge = ' <span class="result-badge">family</span>';
            }
            
            // Different URL paths for different entry types
            let fullUrl;
            if (entry.level === 'country') {
                fullUrl = basePath + entry.url;
            } else if (entry.level === 'text' || entry.level === 'work' || entry.level === 'author' || entry.level === 'source' || entry.level === 'provenance' || entry.level === 'collection') {
                fullUrl = basePath + entry.url;
            } else {
                fullUrl = basePath + 'languages/' + entry.url;
            }
            
            // Check if this is a work match - extract anchor from matchedAlt
            let workTitle = null;
            if (match.matchedAlt && entry.level === 'text' && match.matchedAlt.startsWith('work:')) {
                const workPart = match.matchedAlt.slice(5); // Remove "work:" prefix
                const hashIndex = workPart.indexOf('#');
                if (hashIndex !== -1) {
                    workTitle = workPart.slice(0, hashIndex);
                    const elementId = workPart.slice(hashIndex + 1);
                    fullUrl += '#' + elementId;
                } else {
                    workTitle = workPart;
                }
            }
            
            html += '<a href="' + fullUrl + '" class="search-result-item">';
            html += '<div class="result-row"><span class="result-name">' + escapeHtml(entry.name) + '</span>' + badge + '</div>';
            // Show matched alternate name or work title
            if (workTitle) {
                html += '<div class="result-alt-match">Containing: ' + escapeHtml(workTitle) + '</div>';
            } else if (match.matchedAlt && entry.level !== 'text') {
                html += '<div class="result-alt-match">Also known as: ' + escapeHtml(match.matchedAlt) + '</div>';
            }
            html += '</a>';
        });
        
        searchResults.innerHTML = html;
        searchResults.style.display = 'block';
    });
    
    // Handle Enter key - navigate to first result
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            const firstLink = searchResults.querySelector('.search-result-item');
            if (firstLink && firstLink.href) {
                console.log('[search] navigating to', firstLink.href);
                window.location.href = firstLink.href;
            } else {
                console.log('[search] Enter pressed but no results to navigate');
            }
        }
    });
    
    // Close on Escape
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            searchResults.innerHTML = '';
            searchResults.style.display = 'none';
            this.value = '';
        }
    });
    
    // Close when clicking outside search
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.search-container')) {
            searchResults.innerHTML = '';
            searchResults.style.display = 'none';
        }
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Toggle function for alternate names - make it global
window.toggleNames = function(element) {
    const parent = element.parentElement;
    const hiddenSpan = parent.querySelector('.hidden-names');
    if (hiddenSpan.style.display === 'none') {
        hiddenSpan.style.display = 'inline';
        element.textContent = 'show less';
    } else {
        hiddenSpan.style.display = 'none';
        const count = hiddenSpan.textContent.split(',').length;
        element.textContent = 'and ' + count + ' more...';
    }
};

// Wait for DOM to be ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeSearch);
} else {
    initializeSearch();
}
