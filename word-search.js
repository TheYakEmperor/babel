// Word Search functionality for Babel Archive
// Searches OCR text and transcriptions across all indexed texts

(function() {
    'use strict';
    
    const RESULTS_PER_PAGE = 20;
    let currentPage = 0;
    let currentResults = [];
    
    // Wait for DOM and content index
    document.addEventListener('DOMContentLoaded', function() {
        if (typeof CONTENT_INDEX === 'undefined') {
            console.error('[word-search] CONTENT_INDEX not loaded');
            showError('Content index not loaded. Please try refreshing the page.');
            return;
        }
        
        console.log('[word-search] Loaded', CONTENT_INDEX.length, 'texts');
        
        initWordSearch();
    });
    
    function initWordSearch() {
        const searchInput = document.getElementById('wordSearchInput');
        const searchBtn = document.getElementById('wordSearchBtn');
        const resultsContainer = document.getElementById('wordSearchResults');
        
        if (!searchInput || !searchBtn || !resultsContainer) {
            console.error('[word-search] Required elements not found');
            return;
        }
        
        // Handle search button click
        searchBtn.addEventListener('click', performSearch);
        
        // Handle Enter key
        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                performSearch();
            }
        });
        
        // Check for URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const queryParam = urlParams.get('q');
        if (queryParam) {
            searchInput.value = queryParam;
            performSearch();
        }
    }
    
    function performSearch() {
        const searchInput = document.getElementById('wordSearchInput');
        const query = searchInput.value.trim();
        
        if (!query) {
            showMessage('Please enter a word or phrase to search.');
            return;
        }
        
        // Get search options
        const searchOcr = document.getElementById('searchOcr').checked;
        const searchTranscription = document.getElementById('searchTranscription').checked;
        const caseSensitive = document.getElementById('caseSensitive').checked;
        const wholeWord = document.getElementById('wholeWord').checked;
        
        if (!searchOcr && !searchTranscription) {
            showMessage('Please select at least one content type to search.');
            return;
        }
        
        // Update URL
        const url = new URL(window.location);
        url.searchParams.set('q', query);
        window.history.replaceState({}, '', url);
        
        // Show loading
        showLoading();
        
        // Perform search (use setTimeout to allow UI to update)
        setTimeout(function() {
            const results = searchContent(query, {
                searchOcr,
                searchTranscription,
                caseSensitive,
                wholeWord
            });
            
            currentResults = results;
            currentPage = 0;
            
            displayResults(results, query);
        }, 10);
    }
    
    function searchContent(query, options) {
        const results = [];
        
        // Build regex for search
        let searchQuery = options.caseSensitive ? query : query.toLowerCase();
        let regex;
        
        if (options.wholeWord) {
            // Escape special regex characters
            const escaped = searchQuery.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
            regex = new RegExp('\\b' + escaped + '\\b', options.caseSensitive ? 'g' : 'gi');
        } else {
            const escaped = searchQuery.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
            regex = new RegExp(escaped, options.caseSensitive ? 'g' : 'gi');
        }
        
        // Search through all texts
        for (const text of CONTENT_INDEX) {
            for (const content of text.content) {
                // Check content type filter
                if (content.type === 'ocr' && !options.searchOcr) continue;
                if (content.type === 'transcription' && !options.searchTranscription) continue;
                
                const textToSearch = content.text || '';
                const compareText = options.caseSensitive ? textToSearch : textToSearch.toLowerCase();
                
                // Find all matches
                const matches = [];
                let match;
                regex.lastIndex = 0; // Reset regex state
                
                while ((match = regex.exec(textToSearch)) !== null) {
                    matches.push({
                        index: match.index,
                        match: match[0]
                    });
                }
                
                if (matches.length > 0) {
                    // Find the specific work for this content (if any)
                    let matchingWorks = [];
                    if (content.workId && text.works) {
                        const work = text.works.find(w => w.id === content.workId);
                        if (work) {
                            matchingWorks = [work];
                        }
                    }
                    
                    results.push({
                        textId: text.id,
                        textPath: text.path,
                        textTitle: text.title || text.id,
                        textWorks: matchingWorks,
                        contentType: content.type,
                        page: content.page,
                        regionTitle: content.title || '',
                        fullText: textToSearch,
                        matches: matches,
                        matchCount: matches.length
                    });
                }
            }
        }
        
        // Sort by match count (most matches first)
        results.sort((a, b) => b.matchCount - a.matchCount);
        
        return results;
    }
    
    function displayResults(results, query) {
        const statsDiv = document.getElementById('wordSearchStats');
        const resultsContainer = document.getElementById('wordSearchResults');
        const paginationDiv = document.getElementById('pagination');
        
        // Show stats
        const totalMatches = results.reduce((sum, r) => sum + r.matchCount, 0);
        const uniqueTexts = new Set(results.map(r => r.textId)).size;
        
        if (results.length === 0) {
            statsDiv.style.display = 'none';
            resultsContainer.innerHTML = '';
            paginationDiv.style.display = 'none';
            showMessage(`No results found for "${escapeHtml(query)}"`);
            return;
        }
        
        statsDiv.textContent = `Found ${totalMatches} occurrence${totalMatches !== 1 ? 's' : ''} in ${results.length} page${results.length !== 1 ? 's' : ''} across ${uniqueTexts} text${uniqueTexts !== 1 ? 's' : ''}`;
        statsDiv.style.display = 'block';
        
        // Display current page of results
        const startIdx = currentPage * RESULTS_PER_PAGE;
        const endIdx = Math.min(startIdx + RESULTS_PER_PAGE, results.length);
        const pageResults = results.slice(startIdx, endIdx);
        
        let html = '';
        for (const result of pageResults) {
            const excerpt = getExcerpt(result.fullText, result.matches[0].index, query);
            const highlightedExcerpt = highlightMatches(excerpt, query);
            
            // Build URL to the text page
            const textUrl = result.textPath + '/index.html#page=' + encodeURIComponent(result.page);
            
            // Build works list (only shows works that contain the match)
            let worksHtml = '';
            if (result.textWorks && result.textWorks.length > 0) {
                const workLinks = result.textWorks.map(w => 
                    `<a href="works/${escapeHtml(w.id)}/index.html">${escapeHtml(w.title)}</a>`
                ).join(', ');
                worksHtml = `<div class="result-works">Work: ${workLinks}</div>`;
            }
            
            html += `
                <li class="word-search-result">
                    <div class="result-text-title">
                        <a href="${escapeHtml(textUrl)}">${escapeHtml(result.textTitle)}</a>
                    </div>
                    ${worksHtml}
                    <div class="result-meta">
                        <span class="result-type-badge ${result.contentType}">${result.contentType}</span>
                        Page ${escapeHtml(result.page)}
                        ${result.regionTitle ? ' • ' + escapeHtml(result.regionTitle) : ''}
                        • ${result.matchCount} match${result.matchCount !== 1 ? 'es' : ''}
                    </div>
                    <div class="result-excerpt">${highlightedExcerpt}</div>
                </li>
            `;
        }
        
        resultsContainer.innerHTML = html;
        
        // Show pagination if needed
        const totalPages = Math.ceil(results.length / RESULTS_PER_PAGE);
        if (totalPages > 1) {
            renderPagination(totalPages, query);
            paginationDiv.style.display = 'flex';
        } else {
            paginationDiv.style.display = 'none';
        }
    }
    
    function getExcerpt(text, matchIndex, query) {
        const contextLength = 100;
        const start = Math.max(0, matchIndex - contextLength);
        const end = Math.min(text.length, matchIndex + query.length + contextLength);
        
        let excerpt = text.slice(start, end);
        
        // Add ellipsis
        if (start > 0) excerpt = '...' + excerpt;
        if (end < text.length) excerpt = excerpt + '...';
        
        return excerpt;
    }
    
    function highlightMatches(text, query) {
        const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const regex = new RegExp('(' + escaped + ')', 'gi');
        return escapeHtml(text).replace(regex, '<mark>$1</mark>');
    }
    
    function renderPagination(totalPages, query) {
        const paginationDiv = document.getElementById('pagination');
        
        let html = '';
        
        // Previous button
        html += `<button ${currentPage === 0 ? 'disabled' : ''} onclick="wordSearchGoToPage(${currentPage - 1}, '${escapeHtml(query)}')">&laquo; Prev</button>`;
        
        // Page indicator
        html += `<span class="page-indicator">Page ${currentPage + 1} of ${totalPages}</span>`;
        
        // Next button
        html += `<button ${currentPage >= totalPages - 1 ? 'disabled' : ''} onclick="wordSearchGoToPage(${currentPage + 1}, '${escapeHtml(query)}')"">Next &raquo;</button>`;
        
        paginationDiv.innerHTML = html;
    }
    
    // Global function for pagination
    window.wordSearchGoToPage = function(page, query) {
        currentPage = page;
        displayResults(currentResults, query);
        
        // Scroll to top of results
        document.getElementById('wordSearchStats').scrollIntoView({ behavior: 'smooth' });
    };
    
    function showLoading() {
        const resultsContainer = document.getElementById('wordSearchResults');
        const statsDiv = document.getElementById('wordSearchStats');
        const paginationDiv = document.getElementById('pagination');
        
        statsDiv.style.display = 'none';
        paginationDiv.style.display = 'none';
        resultsContainer.innerHTML = '<li class="word-search-loading">Searching...</li>';
    }
    
    function showMessage(message) {
        const resultsContainer = document.getElementById('wordSearchResults');
        resultsContainer.innerHTML = `<li class="word-search-empty">${escapeHtml(message)}</li>`;
    }
    
    function showError(message) {
        const resultsContainer = document.getElementById('wordSearchResults');
        resultsContainer.innerHTML = `<li class="word-search-empty" style="color: #dc2626;">${escapeHtml(message)}</li>`;
    }
    
    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
})();
