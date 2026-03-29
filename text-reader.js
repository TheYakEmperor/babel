/**
 * Text Reader - Interactive word selection for text archive pages
 * Provides word hover effects, single-word selection (red), and phrase selection (blue)
 * Also links multi-part works that span pages
 */

// Global helper: Convert ISO 3166-1 alpha-2 country code(s) to linked flag image(s)
const COUNTRY_NAMES = {
    'US': 'United States', 'GB': 'United Kingdom', 'CA': 'Canada', 'AU': 'Australia',
    'DE': 'Germany', 'FR': 'France', 'IT': 'Italy', 'ES': 'Spain', 'MX': 'Mexico',
    'BR': 'Brazil', 'JP': 'Japan', 'CN': 'China', 'IN': 'India', 'RU': 'Russia',
    'NL': 'Netherlands', 'BE': 'Belgium', 'CH': 'Switzerland', 'AT': 'Austria',
    'SE': 'Sweden', 'NO': 'Norway', 'DK': 'Denmark', 'FI': 'Finland', 'IE': 'Ireland',
    'PT': 'Portugal', 'PL': 'Poland', 'GR': 'Greece', 'TR': 'Turkey', 'ZA': 'South Africa',
    'EG': 'Egypt', 'NG': 'Nigeria', 'KE': 'Kenya', 'AR': 'Argentina', 'CL': 'Chile',
    'CO': 'Colombia', 'PE': 'Peru', 'VE': 'Venezuela', 'CU': 'Cuba', 'JM': 'Jamaica',
    'NZ': 'New Zealand', 'PH': 'Philippines', 'ID': 'Indonesia', 'MY': 'Malaysia',
    'TH': 'Thailand', 'VN': 'Vietnam', 'KR': 'South Korea', 'TW': 'Taiwan',
    'HK': 'Hong Kong', 'SG': 'Singapore', 'IL': 'Israel', 'SA': 'Saudi Arabia',
    'AE': 'United Arab Emirates', 'PK': 'Pakistan', 'BD': 'Bangladesh', 'IR': 'Iran',
    'IQ': 'Iraq', 'SY': 'Syria', 'LB': 'Lebanon', 'JO': 'Jordan', 'UA': 'Ukraine',
    'CZ': 'Czech Republic', 'HU': 'Hungary', 'RO': 'Romania', 'BG': 'Bulgaria',
};

function countryCodeToSlug(code) {
    const name = COUNTRY_NAMES[code.toUpperCase()] || code;
    return name.toLowerCase().replace(/ /g, '-').replace(/'/g, '');
}

function countryToFlag(countryCode, basePath = '../../../../') {
    if (!countryCode || countryCode.length !== 2) return '';
    const code = countryCode.toLowerCase();
    const slug = countryCodeToSlug(countryCode);
    return `<a href="${basePath}countries/${slug}/index.html"><img src="https://flagcdn.com/w40/${code}.png" alt="${countryCode}" class="country-flag"></a>`;
}

function countriesToFlags(countryData, basePath = '../../../../') {
    if (!countryData) return '';
    const countries = Array.isArray(countryData) ? countryData : [countryData];
    return countries.filter(c => c).map(c => countryToFlag(c, basePath)).join(' ');
}

// Expose init function globally so it can be called after dynamic content loads
window.initTextReader = function() {
    // Prevent double initialization
    if (window._textReaderInitialized) return;
    window._textReaderInitialized = true;
    
    _initTextReaderInternal();
};

function _initTextReaderInternal() {
    // === MOVE SEARCH INTO SIDEBAR & SCROLL BEHAVIOR ===
    const sidebar = document.querySelector('.right-sidebar');
    const initialTop = 200;
    const stuckTop = 20;
    const estimatedLogoHeight = 120;
    
    function updateSidebarPositions(logoHeight) {
        const actualStuckTop = stuckTop - logoHeight;
        const scrollY = window.scrollY;
        
        let sidebarTop = initialTop - scrollY;
        if (sidebarTop < actualStuckTop) {
            sidebarTop = actualStuckTop;
        }
        
        if (sidebar) {
            sidebar.style.top = sidebarTop + 'px';
        }
    }
    
    // Set initial position immediately with estimated values
    updateSidebarPositions(estimatedLogoHeight);
    
    // Refine after DOM elements are measured
    const sidebarLogo = document.querySelector('.sidebar-logo');
    
    let logoHeight = estimatedLogoHeight;
    if (sidebarLogo) {
        logoHeight = sidebarLogo.offsetHeight + 40;
    }
    
    // Update with actual logo height
    updateSidebarPositions(logoHeight);
    
    // Attach scroll listener
    window.addEventListener('scroll', function() {
        updateSidebarPositions(logoHeight);
    });

    // === JUSTIFY-LINES PROCESSING ===
    // Pure CSS approach: container shrinks to longest line, others fill 100%
    document.querySelectorAll('.justify-lines').forEach(el => {
        const html = el.innerHTML;
        const lines = html.split('\n').filter(line => line.replace(/<[^>]*>/g, '').trim());
        
        // Wrap in structure: outer inline-block container + inner lines
        el.innerHTML = `<span class="jline-container">${
            lines.map(line => `<span class="jline">${line}</span>`).join('')
        }</span>`;
    });
    // === SUPERWORK INDICATORS ===
    // Create fixed indicators at top-right and bottom-left to show superwork name
    const superworkTopRight = document.createElement('a');
    superworkTopRight.className = 'superwork-indicator top-right';
    document.body.appendChild(superworkTopRight);
    
    const superworkBottomLeft = document.createElement('a');
    superworkBottomLeft.className = 'superwork-indicator bottom-left';
    document.body.appendChild(superworkBottomLeft);
    
    let keepIndicatorVisible = false;
    let currentSuperworkId = null;
    
    // Get the transcription section and container to use as boundaries
    const transcriptionSection = document.querySelector('.text-body')?.closest('section') || document.querySelector('.text-body');
    const container = document.querySelector('.container');
    const searchContainerEl = document.querySelector('.search-container');
    
    // Update indicator positions and max-width based on page box
    function updateIndicatorPositions() {
        if (!transcriptionSection || !container) return;
        const sectionRect = transcriptionSection.getBoundingClientRect();
        const containerRect = container.getBoundingClientRect();
        const searchBottom = searchContainerEl ? searchContainerEl.getBoundingClientRect().bottom + 10 : 60;
        
        // The top indicator should stay:
        // 1. Below the search bar
        // 2. Below the container top (stay on white)
        // 3. Below the transcription section top
        const minTop = Math.max(searchBottom, containerRect.top + 10, sectionRect.top);
        superworkTopRight.style.top = minTop + 'px';
        
        // The bottom indicator should stay above the container bottom (stay on white)
        const viewportHeight = window.innerHeight;
        const distanceFromBottom = viewportHeight - containerRect.bottom;
        // If container bottom is above viewport bottom, move indicator up
        if (distanceFromBottom > 0) {
            superworkBottomLeft.style.bottom = (distanceFromBottom + 20) + 'px';
        } else {
            superworkBottomLeft.style.bottom = '20px';
        }
        
        // Find the first visible page box to determine width constraints
        const pageBox = document.querySelector('.text-page');
        if (pageBox) {
            const pageRect = pageBox.getBoundingClientRect();
            // Max width is distance from indicator position to page box edge, with some padding
            const maxWidth = Math.max(80, pageRect.left - containerRect.left - 24);
            superworkTopRight.style.maxWidth = maxWidth + 'px';
            superworkBottomLeft.style.maxWidth = maxWidth + 'px';
        }
    }
    
    // Update position on scroll and resize
    window.addEventListener('scroll', updateIndicatorPositions, { passive: true });
    window.addEventListener('resize', updateIndicatorPositions);
    updateIndicatorPositions();
    
    // Keep indicators visible when hovered and highlight all subworks
    superworkTopRight.addEventListener('mouseenter', () => { 
        keepIndicatorVisible = true;
        superworkTopRight.classList.add('visible');
        superworkBottomLeft.classList.add('visible');
        // Highlight all subworks of this superwork
        if (currentSuperworkId) {
            document.querySelectorAll(`.text-work[data-superwork-id="${currentSuperworkId}"]`).forEach(w => {
                w.classList.add('work-hover');
            });
        }
    });
    superworkTopRight.addEventListener('mouseleave', () => { 
        keepIndicatorVisible = false;
        // Remove highlight from subworks
        if (currentSuperworkId) {
            document.querySelectorAll(`.text-work[data-superwork-id="${currentSuperworkId}"]`).forEach(w => {
                w.classList.remove('work-hover');
            });
        }
        // Revert to selected work's superwork if one exists
        const selectedWithSuperwork = document.querySelector('.text-work.selected[data-superwork-id]');
        if (selectedWithSuperwork) {
            const title = selectedWithSuperwork.dataset.superworkTitle;
            const workId = selectedWithSuperwork.dataset.superworkId;
            showSuperwork(title, workId, true);
        } else {
            hideSuperwork();
        }
    });
    superworkBottomLeft.addEventListener('mouseenter', () => { 
        keepIndicatorVisible = true;
        superworkTopRight.classList.add('visible');
        superworkBottomLeft.classList.add('visible');
        // Highlight all subworks of this superwork
        if (currentSuperworkId) {
            document.querySelectorAll(`.text-work[data-superwork-id="${currentSuperworkId}"]`).forEach(w => {
                w.classList.add('work-hover');
            });
        }
    });
    superworkBottomLeft.addEventListener('mouseleave', () => { 
        keepIndicatorVisible = false;
        // Remove highlight from subworks
        if (currentSuperworkId) {
            document.querySelectorAll(`.text-work[data-superwork-id="${currentSuperworkId}"]`).forEach(w => {
                w.classList.remove('work-hover');
            });
        }
        // Revert to selected work's superwork if one exists
        const selectedWithSuperwork = document.querySelector('.text-work.selected[data-superwork-id]');
        if (selectedWithSuperwork) {
            const title = selectedWithSuperwork.dataset.superworkTitle;
            const workId = selectedWithSuperwork.dataset.superworkId;
            showSuperwork(title, workId, true);
        } else {
            hideSuperwork();
        }
    });
    
    let pendingSuperworkChange = null;
    
    function showSuperwork(title, workId, withFade) {
        // If changing to a different superwork while visible, always crossfade
        if (currentSuperworkId && currentSuperworkId !== workId && 
            superworkTopRight.classList.contains('visible')) {
            // Cancel any pending change but still do fade
            if (pendingSuperworkChange) clearTimeout(pendingSuperworkChange);
            // Fade out
            superworkTopRight.classList.remove('visible');
            superworkBottomLeft.classList.remove('visible');
            // After fade out, update and fade back in
            pendingSuperworkChange = setTimeout(() => {
                currentSuperworkId = workId;
                superworkTopRight.textContent = title;
                superworkBottomLeft.textContent = title;
                superworkTopRight.href = '/works/' + workId;
                superworkBottomLeft.href = '/works/' + workId;
                superworkTopRight.classList.add('visible');
                superworkBottomLeft.classList.add('visible');
                pendingSuperworkChange = null;
            }, 150); // Match CSS transition duration
        } else if (pendingSuperworkChange) {
            // A crossfade is in progress - update the pending content instead
            clearTimeout(pendingSuperworkChange);
            pendingSuperworkChange = setTimeout(() => {
                currentSuperworkId = workId;
                superworkTopRight.textContent = title;
                superworkBottomLeft.textContent = title;
                superworkTopRight.href = '/works/' + workId;
                superworkBottomLeft.href = '/works/' + workId;
                superworkTopRight.classList.add('visible');
                superworkBottomLeft.classList.add('visible');
                pendingSuperworkChange = null;
            }, 150);
        } else {
            // No crossfade needed, just show
            currentSuperworkId = workId;
            superworkTopRight.textContent = title;
            superworkBottomLeft.textContent = title;
            superworkTopRight.href = '/works/' + workId;
            superworkBottomLeft.href = '/works/' + workId;
            superworkTopRight.classList.add('visible');
            superworkBottomLeft.classList.add('visible');
        }
        if (withFade) {
            superworkTopRight.classList.add('target-fade');
            superworkBottomLeft.classList.add('target-fade');
        } else {
            superworkTopRight.classList.remove('target-fade');
            superworkBottomLeft.classList.remove('target-fade');
        }
    }
    
    function hideSuperwork() {
        if (keepIndicatorVisible) return;
        if (pendingSuperworkChange) clearTimeout(pendingSuperworkChange);
        pendingSuperworkChange = null;
        superworkTopRight.classList.remove('visible');
        superworkBottomLeft.classList.remove('visible');
        superworkTopRight.classList.remove('target-fade');
        superworkBottomLeft.classList.remove('target-fade');
    }

    // === EQUALIZE WORK WIDTHS WITHIN EACH PAGE ===
    // Make all work boxes within a page the same width as the widest one
    document.querySelectorAll('.text-page').forEach(page => {
        const works = page.querySelectorAll('.text-work');
        if (works.length < 2) return;
        
        let maxWidth = 0;
        works.forEach(work => {
            const width = work.getBoundingClientRect().width;
            if (width > maxWidth) maxWidth = width;
        });
        
        works.forEach(work => {
            work.style.minWidth = maxWidth + 'px';
        });
    });

    // === WORK TITLE LINKS ===
    // Inject clickable title links into each work container (outside left and right)
    document.querySelectorAll('.text-work[data-work-id]').forEach(work => {
        const workId = work.dataset.workId;
        // workPage determines which work page to link to (can be overridden via data-work-page)
        const workPage = work.dataset.workPage || workId;
        const workTitle = work.dataset.workTitle || workId;
        
        // Left side link
        const linkLeft = document.createElement('a');
        linkLeft.className = 'work-title-link';
        linkLeft.href = '/works/' + workPage;
        linkLeft.textContent = workTitle;
        work.appendChild(linkLeft);
        
        // Right side link
        const linkRight = document.createElement('a');
        linkRight.className = 'work-title-link right';
        linkRight.href = '/works/' + workPage;
        linkRight.textContent = workTitle;
        work.appendChild(linkRight);
    });
    
    // === WORK LINKING ===
    // Link work parts that share the same data-work-id across pages
    const workParts = {};
    document.querySelectorAll('.text-work[data-work-id]').forEach(work => {
        const workId = work.dataset.workId;
        if (!workParts[workId]) workParts[workId] = [];
        workParts[workId].push(work);
    });
    
    // When hovering on any part, highlight all parts of that work
    document.querySelectorAll('.text-work[data-work-id]').forEach(work => {
        work.addEventListener('mouseenter', () => {
            const workId = work.dataset.workId;
            if (workParts[workId]) {
                workParts[workId].forEach(part => part.classList.add('work-hover'));
            }
            // Show superwork if this work has one
            if (work.dataset.superworkTitle) {
                showSuperwork(work.dataset.superworkTitle, work.dataset.superworkId, false);
            }
        });
        work.addEventListener('mouseleave', () => {
            const workId = work.dataset.workId;
            if (workParts[workId]) {
                workParts[workId].forEach(part => part.classList.remove('work-hover'));
            }
            // Revert to selected work's superwork if one is selected, otherwise hide
            revertToSelectedSuperwork();
        });
    });
    
    // Revert superwork indicator to the currently selected work (if any)
    function revertToSelectedSuperwork() {
        const selectedWithSuperwork = document.querySelector('.text-work.selected[data-superwork-id]');
        if (selectedWithSuperwork && selectedWithSuperwork.dataset.superworkTitle) {
            showSuperwork(
                selectedWithSuperwork.dataset.superworkTitle, 
                selectedWithSuperwork.dataset.superworkId, 
                false
            );
        } else {
            hideSuperwork();
        }
    }
    
    // === TARGET HIGHLIGHT FOR MULTI-PART WORKS ===
    // When a work is targeted via anchor, highlight all parts of that work
    // Also handles superwork targeting - highlights all subworks
    function highlightTargetedWork() {
        // Remove previous target highlights
        document.querySelectorAll('.work-target').forEach(el => el.classList.remove('work-target'));
        
        const hash = window.location.hash;
        if (!hash) return;
        
        const targetId = hash.slice(1); // Remove the #
        
        // First check if this is a superwork ID - if so, highlight all subworks
        const subworks = document.querySelectorAll(`.text-work[data-superwork-id="${targetId}"]`);
        if (subworks.length > 0) {
            // This is a superwork - highlight all its subworks
            subworks.forEach(work => work.classList.add('work-target'));
            // Get superwork title from first subwork
            const firstSubwork = subworks[0];
            if (firstSubwork.dataset.superworkTitle) {
                showSuperwork(firstSubwork.dataset.superworkTitle, targetId, true);
            }
            // Scroll to first subwork
            firstSubwork.scrollIntoView({ behavior: 'smooth', block: 'center' });
            // Remove after animation duration
            setTimeout(() => {
                subworks.forEach(work => work.classList.remove('work-target'));
                hideSuperwork();
            }, 2000);
            return;
        }
        
        // Otherwise check for regular work target
        const target = document.querySelector(hash);
        if (!target || !target.classList.contains('text-work')) return;
        
        const workId = target.dataset.workId;
        if (workId && workParts[workId]) {
            workParts[workId].forEach(part => part.classList.add('work-target'));
            // Show superwork for targeted work with fade animation
            if (target.dataset.superworkTitle) {
                showSuperwork(target.dataset.superworkTitle, target.dataset.superworkId, true);
            }
            // Remove after animation duration
            setTimeout(() => {
                workParts[workId].forEach(part => part.classList.remove('work-target'));
                hideSuperwork();
            }, 2000);
        }
    }
    
    highlightTargetedWork();
    window.addEventListener('hashchange', highlightTargetedWork);
    
    // === PAGE/WORK SELECTION ===
    // Click on page or work box to toggle selection (persistent highlight)
    // Track if a word interaction is in progress
    let wordInteractionActive = false;
    
    // Click outside page/work boxes to deselect all and hide superwork
    document.addEventListener('click', e => {
        // If clicked on something inside a text-page or text-work, let those handlers deal with it
        if (e.target.closest('.text-page') || e.target.closest('.text-work')) return;
        // If clicked on superwork indicator, don't deselect
        if (e.target.closest('.superwork-indicator')) return;
        // If clicked on search, don't deselect
        if (e.target.closest('.search-container')) return;
        
        // Clicked outside - deselect everything
        document.querySelectorAll('.text-work.selected, .text-page.selected').forEach(el => {
            el.classList.remove('selected');
        });
        // Hide superwork indicator
        keepIndicatorVisible = false;
        superworkTopRight.classList.remove('visible');
        superworkBottomLeft.classList.remove('visible');
        superworkTopRight.classList.remove('target-fade');
        superworkBottomLeft.classList.remove('target-fade');
    });
    
    document.querySelectorAll('.text-page').forEach(page => {
        page.addEventListener('click', e => {
            // Don't toggle if word interaction is happening
            if (wordInteractionActive) return;
            // Only toggle if clicking the page itself (padding area), not content
            if (e.target === page) {
                page.classList.toggle('selected');
            }
        });
    });
    
    document.querySelectorAll('.text-work').forEach(work => {
        work.addEventListener('click', e => {
            // Stop propagation so page doesn't get toggled
            e.stopPropagation();
            // Don't toggle if word interaction is happening or clicking on a word/link
            if (wordInteractionActive) return;
            if (e.target.classList.contains('word')) return;
            if (e.target.closest('a')) return;
            
            // Toggle all parts of this work (multi-page works)
            const workId = work.dataset.workId;
            const isSelected = work.classList.contains('selected');
            if (workId && workParts[workId]) {
                workParts[workId].forEach(part => {
                    if (isSelected) {
                        part.classList.remove('selected');
                    } else {
                        part.classList.add('selected');
                    }
                });
            } else {
                work.classList.toggle('selected');
            }
            
            // Update superwork indicator based on selection state
            updateSuperworkForSelection();
        });
    });
    
    // Show superwork indicator if any subwork with that superwork is selected
    function updateSuperworkForSelection() {
        // Check if any work with a superwork is selected
        const selectedWithSuperwork = document.querySelector('.text-work.selected[data-superwork-id]');
        if (selectedWithSuperwork) {
            const title = selectedWithSuperwork.dataset.superworkTitle;
            const id = selectedWithSuperwork.dataset.superworkId;
            if (title && id) {
                keepIndicatorVisible = true;
                showSuperwork(title, id, false);
            }
        } else {
            // No selected works with superwork - force hide
            keepIndicatorVisible = false;
            superworkTopRight.classList.remove('visible');
            superworkBottomLeft.classList.remove('visible');
            superworkTopRight.classList.remove('target-fade');
            superworkBottomLeft.classList.remove('target-fade');
        }
    }
    
    // === WORD WRAPPING ===
    // Wrap words in spans for hover effect - works in both .text-work and .text-page
    document.querySelectorAll('.text-work poem, .text-work p, .text-page poem, .text-page p').forEach(el => {
        const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null, false);
        const textNodes = [];
        while (walker.nextNode()) textNodes.push(walker.currentNode);
        
        textNodes.forEach(node => {
            const text = node.textContent;
            if (!text.trim()) return;
            
            const fragment = document.createDocumentFragment();
            // Split into words and non-words (whitespace + punctuation, but hyphen and apostrophe count as word)
            // Include curly double quotes as punctuation separators, but keep apostrophes/single quotes with words
            text.split(/(\s+|[.,;:!?""\"()…—–]+)/).forEach(part => {
                if (!part) return;
                if (/^(\s+|[.,;:!?""\"()…—–]+)$/.test(part)) {
                    // Whitespace or punctuation (not hyphen/apostrophe) - leave as plain text
                    fragment.appendChild(document.createTextNode(part));
                } else {
                    const span = document.createElement('span');
                    span.className = 'word';
                    span.textContent = part;
                    fragment.appendChild(span);
                }
            });
            node.parentNode.replaceChild(fragment, node);
        });
    });
    
    // Build ordered list of words for range selection (moved up for hyphen linking)
    let wordsInOrder = [];
    document.querySelectorAll('.text-work .word, .text-page .word').forEach((w, i) => {
        w.dataset.idx = i;
        wordsInOrder.push(w);
    });
    
    // === HYPHENATED WORD LINKING ===
    // Link words that end with hyphen to the word on the next line
    let hyphenLinkId = 0;
    wordsInOrder.forEach((word, i) => {
        const text = word.textContent;
        // Check if this word ends with a hyphen (line-break hyphen)
        if (text.endsWith('-') && i < wordsInOrder.length - 1) {
            const nextWord = wordsInOrder[i + 1];
            const linkId = 'hyphen-' + (hyphenLinkId++);
            word.dataset.hyphenLink = linkId;
            nextWord.dataset.hyphenLink = linkId;
        }
    });
    
    // Add hover listeners for hyphen-linked words
    document.querySelectorAll('.word[data-hyphen-link]').forEach(word => {
        word.addEventListener('mouseenter', () => {
            const linkId = word.dataset.hyphenLink;
            document.querySelectorAll(`.word[data-hyphen-link="${linkId}"]`).forEach(w => {
                w.classList.add('hyphen-hover');
            });
        });
        word.addEventListener('mouseleave', () => {
            const linkId = word.dataset.hyphenLink;
            document.querySelectorAll(`.word[data-hyphen-link="${linkId}"]`).forEach(w => {
                w.classList.remove('hyphen-hover');
            });
        });
    });

    // Click and drag to select/deselect words
    let startWord = null;
    let dragMode = null;
    let isDragging = false;
    let currentPhraseId = null;
    let phraseCounter = 0;
    let phraseOverlays = {};
    
    // Get the text-body container for positioning overlays (parent of works/pages)
    const textBody = document.querySelector('.text-body');
    if (textBody) {
        textBody.style.position = 'relative';
    }
    
    // Create overlay boxes for a phrase
    function createPhraseOverlay(phraseId) {
        const words = document.querySelectorAll(`.word[data-phrase="${phraseId}"]`);
        if (words.length === 0 || !textBody) return;
        
        // Remove existing overlays for this phrase
        if (phraseOverlays[phraseId]) {
            phraseOverlays[phraseId].forEach(el => el.remove());
        }
        phraseOverlays[phraseId] = [];
        
        const bodyRect = textBody.getBoundingClientRect();
        
        // Group words by their line (based on top position)
        const lines = {};
        words.forEach(w => {
            const rect = w.getBoundingClientRect();
            const top = Math.round(rect.top - bodyRect.top);
            if (!lines[top]) lines[top] = [];
            lines[top].push({ el: w, rect });
        });
        
        // Create an overlay for each line
        Object.values(lines).forEach(lineWords => {
            const firstRect = lineWords[0].rect;
            const lastRect = lineWords[lineWords.length - 1].rect;
            
            const overlay = document.createElement('div');
            overlay.className = 'phrase-overlay';
            overlay.dataset.phrase = phraseId;
            
            const left = firstRect.left - bodyRect.left - 2;
            const top = firstRect.top - bodyRect.top - 2;
            const width = (lastRect.right - firstRect.left) + 4;
            const height = firstRect.height + 4;
            
            overlay.style.cssText = `left:${left}px; top:${top}px; width:${width}px; height:${height}px;`;
            textBody.appendChild(overlay);
            phraseOverlays[phraseId].push(overlay);
        });
    }
    
    // Remove a phrase by ID
    function removePhraseById(phraseId) {
        document.querySelectorAll(`.word[data-phrase="${phraseId}"]`).forEach(w => {
            w.classList.remove('phrase-word');
            delete w.dataset.phrase;
        });
        if (phraseOverlays[phraseId]) {
            phraseOverlays[phraseId].forEach(el => el.remove());
            delete phraseOverlays[phraseId];
        }
    }
    
    // Remove all phrases
    function clearAllPhrases() {
        document.querySelectorAll('.word.phrase-word').forEach(w => {
            w.classList.remove('phrase-word');
            delete w.dataset.phrase;
        });
        Object.values(phraseOverlays).forEach(overlays => {
            overlays.forEach(el => el.remove());
        });
        phraseOverlays = {};
    }
    
    document.addEventListener('mousedown', e => {
        if (e.target.classList.contains('word')) {
            wordInteractionActive = true;
            startWord = e.target;
            isDragging = false;
            dragMode = startWord.classList.contains('selected') ? 'deselect' : 'select';
        }
    });
    
    document.addEventListener('mousemove', e => {
        if (!startWord || e.buttons !== 1) return;
        
        const endWord = e.target.classList.contains('word') ? e.target : null;
        if (!endWord) return;
        
        const startIdx = parseInt(startWord.dataset.idx);
        const endIdx = parseInt(endWord.dataset.idx);
        
        // Only count as dragging if we've moved to a different word
        if (startIdx !== endIdx) {
            isDragging = true;
        }
        
        // Only create phrase selection when actually dragging
        if (!isDragging) return;
        
        const minIdx = Math.min(startIdx, endIdx);
        const maxIdx = Math.max(startIdx, endIdx);
        
        // Remove only the current in-progress phrase (not others)
        if (currentPhraseId !== null) {
            removePhraseById(currentPhraseId);
        }
        
        if (minIdx === maxIdx) return; // Single word, no phrase
        
        // Create new phrase ID
        currentPhraseId = ++phraseCounter;
        
        // Expand range to include hyphen-linked words at the edges
        let expandedMin = minIdx;
        let expandedMax = maxIdx;
        
        // Check if word at minIdx has a hyphen link and include its partner
        const minWord = wordsInOrder[minIdx];
        if (minWord && minWord.dataset.hyphenLink) {
            const linkedWords = document.querySelectorAll(`.word[data-hyphen-link="${minWord.dataset.hyphenLink}"]`);
            linkedWords.forEach(w => {
                const idx = parseInt(w.dataset.idx);
                if (idx < expandedMin) expandedMin = idx;
                if (idx > expandedMax) expandedMax = idx;
            });
        }
        
        // Check if word at maxIdx has a hyphen link and include its partner
        const maxWord = wordsInOrder[maxIdx];
        if (maxWord && maxWord.dataset.hyphenLink) {
            const linkedWords = document.querySelectorAll(`.word[data-hyphen-link="${maxWord.dataset.hyphenLink}"]`);
            linkedWords.forEach(w => {
                const idx = parseInt(w.dataset.idx);
                if (idx < expandedMin) expandedMin = idx;
                if (idx > expandedMax) expandedMax = idx;
            });
        }
        
        // Mark all words in expanded range as part of this phrase
        for (let i = expandedMin; i <= expandedMax; i++) {
            wordsInOrder[i].classList.add('phrase-word');
            wordsInOrder[i].dataset.phrase = currentPhraseId;
        }
        
        // Create the overlay box
        createPhraseOverlay(currentPhraseId);
    });
    
    document.addEventListener('mouseup', e => {
        if (startWord && !isDragging) {
            // Single click on word - check if it's part of a phrase first
            const phraseId = startWord.dataset.phrase;
            if (phraseId) {
                // Click on phrase word - remove that phrase
                removePhraseById(phraseId);
            } else {
                // Toggle red box on individual word (and any hyphen-linked words)
                const hyphenLink = startWord.dataset.hyphenLink;
                if (hyphenLink) {
                    // Toggle all linked parts together
                    const linkedWords = document.querySelectorAll(`.word[data-hyphen-link="${hyphenLink}"]`);
                    const shouldSelect = !startWord.classList.contains('selected');
                    linkedWords.forEach(w => {
                        if (shouldSelect) {
                            w.classList.add('selected');
                        } else {
                            w.classList.remove('selected');
                        }
                    });
                } else {
                    startWord.classList.toggle('selected');
                }
            }
        }
        if (!startWord && !wordInteractionActive && !e.target.classList.contains('word') && !e.target.closest('.text-work') && !e.target.closest('.text-page') && !e.target.closest('.dictionary-widget')) {
            // Click outside text area - clear all selections
            document.querySelectorAll('.word.selected').forEach(w => w.classList.remove('selected'));
            document.querySelectorAll('.text-page.selected').forEach(p => p.classList.remove('selected'));
            document.querySelectorAll('.text-work.selected').forEach(w => w.classList.remove('selected'));
            clearAllPhrases();
        }
        // Finalize the current phrase (it's now permanent until clicked)
        currentPhraseId = null;
        startWord = null;
        dragMode = null;
        isDragging = false;
        // Reset word interaction flag after a short delay to prevent click event from firing
        setTimeout(() => { wordInteractionActive = false; }, 10);
    });
    
    // === DICTIONARY WIDGET ===
    // Create the dictionary panel on the right side
    const dictWidget = document.createElement('div');
    dictWidget.className = 'dictionary-widget';
    dictWidget.innerHTML = `
        <div class="dict-header">
            <span class="dict-title">Dictionary</span>
            <button class="dict-close" title="Close">×</button>
        </div>
        <div class="dict-tabs"></div>
        <div class="dict-content">
            <div class="dict-placeholder">Select a word or phrase to look up</div>
        </div>
    `;
    document.body.appendChild(dictWidget);
    
    const dictTabs = dictWidget.querySelector('.dict-tabs');
    const dictContent = dictWidget.querySelector('.dict-content');
    const dictClose = dictWidget.querySelector('.dict-close');
    
    // Track active lookups: { id: { words: [...], element: tabElement } }
    let dictLookups = {};
    let activeLookupId = null;
    
    // Get language code from data.json (loaded elsewhere)
    // Try to get the ISO 639-3 code for Wiktionary
    function getTextLanguage() {
        // The page should have loaded data.json - check if window.textData exists
        // Otherwise try to extract from the page
        const langMeta = document.querySelector('meta[name="language"]');
        if (langMeta) return langMeta.content;
        // Default to English
        return 'en';
    }
    
    // Get the text's language names from the page (fallback)
    function getTextLanguageNames() {
        const langName = document.documentElement.dataset.languageName;
        if (langName) {
            // Split by comma and normalize
            return langName.split(',').map(l => l.trim().toLowerCase());
        }
        return ['english'];
    }
    
    // Get language(s) for a specific word element
    // Prioritizes work-specific language, falls back to text languages
    function getLanguagesForElement(wordElement) {
        if (!wordElement) return getTextLanguageNames();
        
        // Find the closest work container with a language
        const work = wordElement.closest('.text-work[data-language]');
        if (work) {
            const langIds = work.dataset.language;
            // Handle comma-separated language IDs (for multi-language works)
            const ids = langIds.split(',').map(id => id.trim());
            const names = [];
            
            for (const langId of ids) {
                // Lookup the language name from the search index
                if (typeof LANGUAGE_INDEX !== 'undefined') {
                    const entry = LANGUAGE_INDEX.find(e => e.id === langId);
                    if (entry) {
                        const name = entry.name.replace(/^† /, '').toLowerCase();
                        names.push(name);
                        continue;
                    }
                }
                // Fall back to using the ID as-is (might work for some)
                names.push(langId.toLowerCase());
            }
            
            return names.length > 0 ? names : getTextLanguageNames();
        }
        
        // No work-specific language, use text-level languages
        return getTextLanguageNames();
    }
    
    // Wiktionary Parse API lookup - returns full HTML with labels
    // Also fetches language subpages (e.g., "a/languages_M_to_Z") for large entries
    async function lookupWiktionary(word) {
        try {
            const url = `https://en.wiktionary.org/w/api.php?action=parse&page=${encodeURIComponent(word)}&prop=text&format=json&origin=*`;
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error('API error');
            }
            const data = await response.json();
            if (data.error) {
                return { error: 'not found' };
            }
            let html = data.parse?.text?.['*'] || '';
            if (!html) {
                return { error: 'not found' };
            }
            
            // Check for language subpages (large entries like "a" split across multiple pages)
            const subpagePattern = new RegExp(`/wiki/${encodeURIComponent(word)}/(languages_[^"#]+)`, 'g');
            const subpages = new Set();
            let match;
            while ((match = subpagePattern.exec(html)) !== null) {
                subpages.add(match[1]);
            }
            
            // Fetch each subpage and append its HTML
            for (const subpage of subpages) {
                try {
                    const subUrl = `https://en.wiktionary.org/w/api.php?action=parse&page=${encodeURIComponent(word + '/' + subpage)}&prop=text&format=json&origin=*`;
                    const subResponse = await fetch(subUrl);
                    if (subResponse.ok) {
                        const subData = await subResponse.json();
                        const subHtml = subData.parse?.text?.['*'] || '';
                        if (subHtml) {
                            html += subHtml;
                        }
                    }
                } catch (e) {
                    // Ignore subpage fetch errors
                }
            }
            
            return { html, title: data.parse?.title || word };
        } catch (err) {
            return { error: 'Failed to fetch definition' };
        }
    }
    
    // Remove diacritics/accents from a string
    function stripAccents(str) {
        return str.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    }
    
    // Common accent variants for single letters (for exhaustive lookup)
    const ACCENT_VARIANTS = {
        'a': ['a', 'á', 'à', 'â', 'ä', 'ã', 'å', 'ā', 'ă', 'ą'],
        'e': ['e', 'é', 'è', 'ê', 'ë', 'ē', 'ė', 'ę', 'ě'],
        'i': ['i', 'í', 'ì', 'î', 'ï', 'ī', 'į', 'ı'],
        'o': ['o', 'ó', 'ò', 'ô', 'ö', 'õ', 'ō', 'ø', 'ő'],
        'u': ['u', 'ú', 'ù', 'û', 'ü', 'ū', 'ů', 'ű', 'ų'],
        'c': ['c', 'ç', 'ć', 'č'],
        'n': ['n', 'ñ', 'ń', 'ň'],
        's': ['s', 'ś', 'š', 'ş'],
        'y': ['y', 'ý', 'ÿ'],
        'z': ['z', 'ź', 'ž', 'ż'],
        'l': ['l', 'ł', 'ľ'],
        'r': ['r', 'ř'],
        'd': ['d', 'ď', 'đ'],
        't': ['t', 'ť'],
        'g': ['g', 'ğ'],
    };
    
    // Generate accent variants for a word (only vary vowels to keep it manageable)
    // e.g., "glos" → ["glos", "glós", "glòs", "glôs", "glös", ...]
    function generateAccentVariants(word) {
        const vowels = ['a', 'e', 'i', 'o', 'u'];
        const variants = new Set([word]);
        
        // For each character position that's a vowel, try all accent variants
        for (let i = 0; i < word.length; i++) {
            const char = word[i].toLowerCase();
            if (vowels.includes(char) && ACCENT_VARIANTS[char]) {
                // Generate variants with this vowel changed
                for (const accentedChar of ACCENT_VARIANTS[char]) {
                    const variant = word.slice(0, i) + accentedChar + word.slice(i + 1);
                    variants.add(variant);
                }
            }
        }
        return [...variants];
    }
    
    // Search Wiktionary for similar words (uses full search API which handles accents properly)
    async function searchWiktionary(word) {
        try {
            const url = `https://en.wiktionary.org/w/api.php?action=query&list=search&srsearch=${encodeURIComponent(word)}&srlimit=10&format=json&origin=*`;
            const response = await fetch(url);
            if (!response.ok) return [];
            const data = await response.json();
            // Returns { query: { search: [{ title: "...", ... }, ...] } }
            const results = data.query?.search || [];
            return results.map(r => r.title);
        } catch (err) {
            return [];
        }
    }
    
    // Search Wiktionary for pages CONTAINING a word (quoted search)
    async function searchWiktionaryContent(word) {
        try {
            // Quoted search finds pages with the exact phrase in content
            // The quotes must be part of the search term, then the whole thing is URL-encoded
            const searchTerm = `"${word}"`;
            const url = `https://en.wiktionary.org/w/api.php?action=query&list=search&srsearch=${encodeURIComponent(searchTerm)}&srlimit=10&format=json&origin=*`;
            const response = await fetch(url);
            if (!response.ok) return [];
            const data = await response.json();
            const results = data.query?.search || [];
            return results.map(r => r.title);
        } catch (err) {
            return [];
        }
    }
    
    // Lookup word with both cases if different, and also try accent variations via search
    async function lookupWordWithCases(word) {
        const results = [];
        const seenWords = new Set();
        const lowerWord = word.toLowerCase();
        const capitalWord = lowerWord.charAt(0).toUpperCase() + lowerWord.slice(1);
        const isLowercase = word === lowerWord;
        const isCapitalized = word === capitalWord;
        
        // Also prepare accent-stripped versions
        const plainWord = stripAccents(lowerWord);
        const plainCapital = stripAccents(capitalWord);
        const hasAccents = plainWord !== lowerWord;
        
        // Also prepare apostrophe-free versions for contractions like "where's" -> "wheres"
        // This handles both internal apostrophes (there's) and leading apostrophes ('A)
        const noApostrophe = lowerWord.replace(/'/g, '');
        const noApostropheCapital = noApostrophe.charAt(0).toUpperCase() + noApostrophe.slice(1);
        const hasApostrophe = noApostrophe !== lowerWord;
        const startsWithApostrophe = lowerWord.startsWith("'");
        
        // Helper to try a word variant and add to results if found
        async function tryWord(variant) {
            if (seenWords.has(variant)) return;
            seenWords.add(variant);
            const result = await lookupWiktionary(variant);
            if (!result.error || result.error !== 'not found') {
                results.push({ word: variant, data: result });
            }
        }
        
        // Primary lookups based on case
        if (isLowercase) {
            await tryWord(lowerWord);
            await tryWord(capitalWord);
        } else if (isCapitalized) {
            await tryWord(capitalWord);
            await tryWord(lowerWord);
        } else {
            await tryWord(capitalWord);
            await tryWord(lowerWord);
        }
        
        // Also try without accents (to find both accented and unaccented forms)
        if (hasAccents) {
            console.log('Word has accents, trying plain versions:', plainWord, plainCapital);
            await tryWord(plainWord);
            await tryWord(plainCapital);
        }
        
        // Also try without apostrophes (for contractions like there's -> theres, or 'A -> A)
        if (hasApostrophe) {
            console.log('Word has apostrophe, trying without:', noApostrophe, noApostropheCapital);
            await tryWord(noApostrophe);
            await tryWord(noApostropheCapital);
            // For words starting with apostrophe like 'A, also try just stripping the leading apostrophe
            if (startsWithApostrophe) {
                const withoutLeading = lowerWord.slice(1);
                const withoutLeadingCapital = withoutLeading.charAt(0).toUpperCase() + withoutLeading.slice(1);
                await tryWord(withoutLeading);
                await tryWord(withoutLeadingCapital);
            }
        }
        
        // For single letters, try ALL accent variants (opensearch doesn't help here)
        if (plainWord.length === 1 && ACCENT_VARIANTS[plainWord]) {
            console.log('Single letter - trying all accent variants for:', plainWord);
            for (const variant of ACCENT_VARIANTS[plainWord]) {
                await tryWord(variant);
                await tryWord(variant.toUpperCase());
            }
        } else {
            // For longer words, use opensearch to find accent variants
            const baseWord = hasAccents ? plainWord : lowerWord;
            console.log('Searching for:', baseWord);
            const suggestions = await searchWiktionary(baseWord);
            console.log('Search suggestions:', suggestions);
            
            // Also search without apostrophe if word has one
            if (hasApostrophe) {
                const noApostropheSuggestions = await searchWiktionary(noApostrophe);
                console.log('Search suggestions (no apostrophe):', noApostropheSuggestions);
                suggestions.push(...noApostropheSuggestions);
            }
            
            // Try all suggestions that match our word when accents are stripped
            // Also accept prefix entries (word + hyphen) and abbreviations (word + period)
            for (const suggestion of suggestions) {
                const suggLower = suggestion.toLowerCase();
                const suggPlain = stripAccents(suggLower);
                const suggNoApostrophe = suggPlain.replace(/'/g, '');
                const baseNoApostrophe = baseWord.replace(/'/g, '');
                // Exact match (with possible accent differences)
                if (suggPlain === baseWord || suggNoApostrophe === baseNoApostrophe) {
                    console.log('Trying suggestion:', suggestion);
                    await tryWord(suggestion);
                }
                // Prefix entry (e.g., "uwch-" for "uwch")
                else if (suggPlain === baseWord + '-') {
                    console.log('Trying prefix entry:', suggestion);
                    await tryWord(suggestion);
                }
                // Abbreviation entry (e.g., "Sra." for "Sra")
                else if (suggPlain === baseWord + '.') {
                    console.log('Trying abbreviation entry:', suggestion);
                    await tryWord(suggestion);
                }
            }
        }
        
        // ALSO search for pages that mention this word in mutations/conjugations/etc.
        // This catches cases like "glôs" → "clòs" (which has "glòs" in its mutation table)
        // Don't do this for multi-word phrases
        if (!lowerWord.includes(' ')) {
            console.log('Searching for pages containing accent variants of:', plainWord);
            
            // Generate accent variants of the plain word
            // e.g., "glos" → ["glos", "glós", "glòs", "glôs", "glös", ...]
            const accentVariants = generateAccentVariants(plainWord);
            console.log('Generated accent variants:', accentVariants.slice(0, 15), '...');
            
            // For each accent variant, search for pages CONTAINING that word
            const candidatePages = new Set();
            // Limit to avoid too many API calls - prioritize common accents (grave, acute, circumflex)
            const priorityVariants = [lowerWord, plainWord, ...accentVariants.slice(0, 10)];
            const uniqueVariants = [...new Set(priorityVariants)];
            
            for (const variant of uniqueVariants) {
                // Content search: find pages that have this word in their text
                const containing = await searchWiktionaryContent(variant);
                console.log('Pages containing', variant, ':', containing);
                for (const page of containing) {
                    const pageLower = page.toLowerCase();
                    const pagePlain = stripAccents(pageLower);
                    // Skip if it's the same word (when stripped) or already in results
                    if (pagePlain === plainWord || pageLower.includes(' ')) continue;
                    if (seenWords.has(page)) continue;
                    // Skip if page has same consonants but DIFFERENT vowels (e.g., "glas" vs "glos")
                    // This filters out Wiktionary's fuzzy search false positives
                    const pageConsonants = pagePlain.replace(/[aeiouàáâãäåāăąæèéêëēėęěìíîïīįòóôõöøōőùúûüūůűýÿ]/gi, '');
                    const wordConsonants = plainWord.replace(/[aeiouàáâãäåāăąæèéêëēėęěìíîïīįòóôõöøōőùúûüūůűýÿ]/gi, '');
                    if (pageConsonants === wordConsonants && pagePlain !== plainWord) {
                        console.log('Skipping', page, '- same consonants but different vowels');
                        continue;
                    }
                    candidatePages.add(page);
                }
            }
            console.log('Candidate pages from content search:', [...candidatePages]);
            
            // Fetch candidate pages and verify word appears as a FORM in:
            // 1. Inflection TABLE cells (mutation/conjugation forms)
            // 2. Headword line (plural, comparative, superlative, etc.)
            for (const page of [...candidatePages].slice(0, 5)) {
                const result = await lookupWiktionary(page);
                if (!result.error && result.html) {
                    const tempDoc = new DOMParser().parseFromString(result.html, 'text/html');
                    
                    let foundAsForm = false;
                    
                    // Check inflection tables
                    const tables = tempDoc.querySelectorAll('table.inflection-table, table[class*="inflection"]');
                    for (const table of tables) {
                        const cells = table.querySelectorAll('td');
                        for (const cell of cells) {
                            const cellText = cell.textContent.trim();
                            const forms = cellText.split(/[,\/]+/).map(f => f.trim());
                            for (const form of forms) {
                                const formPlain = stripAccents(form.toLowerCase());
                                if (formPlain === plainWord && !form.includes(' ')) {
                                    foundAsForm = true;
                                    console.log('MATCH FOUND in table cell:', form);
                                    break;
                                }
                            }
                            if (foundAsForm) break;
                        }
                        if (foundAsForm) break;
                    }
                    
                    // Check headword lines for form-of (plural, comparative, etc.)
                    if (!foundAsForm) {
                        const headwordLines = tempDoc.querySelectorAll('.headword-line, p:has(.headword)');
                        for (const hwLine of headwordLines) {
                            // Look for form-of links (b.form-of or links with form-of class)
                            const formLinks = hwLine.querySelectorAll('b.form-of a, .form-of a, a.form-of');
                            for (const link of formLinks) {
                                const linkText = link.textContent.trim();
                                const linkPlain = stripAccents(linkText.toLowerCase());
                                if (linkPlain === plainWord) {
                                    foundAsForm = true;
                                    console.log('MATCH FOUND in headword line:', linkText);
                                    break;
                                }
                            }
                            if (foundAsForm) break;
                        }
                    }
                    
                    if (foundAsForm) {
                        console.log('Page', page, 'has', plainWord, 'as a form');
                        seenWords.add(page);
                        results.push({ word: page, data: result });
                    } else {
                        console.log('Page', page, 'does NOT have', plainWord, 'as a form');
                    }
                }
            }
        }
        
        console.log('Final results:', results.map(r => r.word));
        return results;
    }

    // Language name aliases: Glottolog name -> Wiktionary names (and vice versa)
    // This handles cases where Glottolog and Wiktionary use different names for the same language
    const languageAliases = {
        'tuvinian': ['tuvan'],
        'tuvan': ['tuvinian'],
        'modern greek': ['greek'],
        'greek': ['modern greek'],
        'mandarin chinese': ['chinese', 'mandarin'],
        'chinese': ['mandarin chinese', 'mandarin'],
        'standard arabic': ['arabic'],
        'arabic': ['standard arabic'],
        'persian': ['farsi'],
        'farsi': ['persian'],
        'old english (ca. 450-1100)': ['old english', 'anglo-saxon'],
        'old english': ['old english (ca. 450-1100)', 'anglo-saxon'],
        'anglo-saxon': ['old english', 'old english (ca. 450-1100)'],
    };
    
    // Expand a list of language names to include aliases
    function expandLanguageNames(names) {
        const expanded = new Set(names.map(n => n.toLowerCase()));
        for (const name of names) {
            const lower = name.toLowerCase();
            if (languageAliases[lower]) {
                for (const alias of languageAliases[lower]) {
                    expanded.add(alias);
                }
            }
        }
        return Array.from(expanded);
    }

    // === TUVAN TALKING DICTIONARY FALLBACK ===
    // Swarthmore's Tuvan Talking Dictionary: https://tuvan.swarthmore.edu/
    // Used as a fallback for Tuvan words when Wiktionary has no entry
    // Note: The dictionary doesn't support CORS, so we provide a direct search link
    
    // Check if language is Tuvan (various names)
    function isTuvanLanguage(languages) {
        const tuvanNames = ['tuvan', 'tuvinian', 'tyvan', 'tuvin'];
        return languages.some(lang => 
            tuvanNames.some(name => lang.toLowerCase().includes(name))
        );
    }
    
    // Create a link to Tuvan Talking Dictionary search
    // Since the dictionary doesn't support CORS, we can't fetch directly
    // Instead, provide a helpful link the user can click
    function createTuvanDictionaryLink(word) {
        const searchUrl = `https://tuvan.swarthmore.edu/?q=${encodeURIComponent(word)}&fields=lang`;
        
        let html = '<div class="dict-tuvan-fallback">';
        html += '<div class="dict-label">Not found in Wiktionary</div>';
        html += '<div class="dict-tuvan-link">';
        html += 'Try the <a href="' + searchUrl + '" target="_blank" rel="noopener">';
        html += 'Tuvan Talking Dictionary ↗</a>';
        html += '</div>';
        html += '<div class="dict-tuvan-note">(Swarthmore College - 8,300+ Tuvan-English entries)</div>';
        html += '</div>';
        
        return html;
    }

    // === OLD ENGLISH DICTIONARY FALLBACK ===
    // Bosworth-Toller Anglo-Saxon Dictionary: https://bosworthtoller.com/
    // Used as a fallback for Old English words when Wiktionary has no entry
    
    // Check if language is Old English (various names)
    function isOldEnglishLanguage(languages) {
        const oeNames = ['old english', 'anglo-saxon', 'anglosaxon', 'old-english'];
        return languages.some(lang => 
            oeNames.some(name => lang.toLowerCase().includes(name))
        );
    }
    
    // Create a link to Bosworth-Toller search
    function createOldEnglishDictionaryLink(word) {
        const searchUrl = `https://bosworthtoller.com/search?q=${encodeURIComponent(word)}`;
        
        let html = '<div class="dict-oe-fallback">';
        html += '<div class="dict-label">Not found in Wiktionary</div>';
        html += '<div class="dict-oe-link">';
        html += 'Try the <a href="' + searchUrl + '" target="_blank" rel="noopener">';
        html += 'Bosworth-Toller Anglo-Saxon Dictionary ↗</a>';
        html += '</div>';
        html += '<div class="dict-oe-note">(The standard Old English dictionary)</div>';
        html += '</div>';
        
        return html;
    }

    // Format Wiktionary Parse API response into readable HTML
    function formatDefinition(data, word, languages) {
        if (data.error) {
            return `<div class="dict-error">${data.error}</div>`;
        }
        
        // If languages is explicitly null, show ALL languages (no filtering)
        const showAllLanguages = languages === null;
        const textLanguages = showAllLanguages ? [] : (languages || getTextLanguageNames());
        const expandedLanguages = expandLanguageNames(textLanguages);
        const rawHtml = data.html || '';
        
        // Parse HTML
        const parser = new DOMParser();
        const doc = parser.parseFromString(rawHtml, 'text/html');
        
        // Sections to show as simple lists (mutations, conjugations, etc.)
        const formSections = ['alternative forms', 'mutation', 'declension', 'conjugation', 
            'inflection', 'derived terms', 'related terms', 'usage notes'];
        
        // Words that shouldn't be made into links (grammatical terms only)
        const skipLinkWords = new Set([
            'borrowed', 'derived', 'from', 'cognate', 'compare', 'see', 'also',
            'plural', 'singular', 'feminine', 'masculine', 'neuter',
            'comparative', 'superlative', 'equative', 'positive',
            'nominative', 'genitive', 'dative', 'accusative', 'ablative', 'vocative',
            'present', 'past', 'future', 'perfect', 'imperfect', 'infinitive',
            'participle', 'gerund', 'imperative', 'subjunctive', 'conditional',
            'first', 'second', 'third', 'person',
            'edit', 'note', 'literally', 'figuratively', 'by extension'
        ]);
        
        // Helper to make target-language links clickable (not English definitions or grammatical terms)
        function makeLinksClickable(element, targetLangs) {
            const clone = element.cloneNode(true);
            // Process all links
            clone.querySelectorAll('a').forEach(link => {
                const href = link.getAttribute('href') || '';
                const wordText = link.textContent.trim();
                const wordLower = wordText.toLowerCase();
                
                // Check if this is a redlink (page doesn't exist)
                const isRedlink = link.classList.contains('new') || href.includes('redlink=1');
                if (isRedlink) {
                    // Replace with grey non-clickable text
                    const span = document.createElement('span');
                    span.className = 'dict-missing';
                    span.textContent = wordText;
                    link.replaceWith(span);
                    return;
                }
                
                // Skip if not a wiki link or not a valid word (include combining marks for non-Latin scripts, periods for abbreviations)
                if (!href.startsWith('/wiki/') || !wordText || !/^[\p{L}\p{M}'. -]+$/u.test(wordText)) {
                    link.replaceWith(document.createTextNode(wordText));
                    return;
                }
                
                // Skip Appendix links, grammatical terms, and common English words
                if (href.includes('Appendix:') || href.includes('Reconstruction:')) {
                    link.replaceWith(document.createTextNode(wordText));
                    return;
                }
                if (skipLinkWords.has(wordLower)) {
                    link.replaceWith(document.createTextNode(wordText));
                    return;
                }
                
                // Skip links to English definitions
                // Wiktionary links to target language have #LanguageName, e.g. #Welsh, #Catalan
                // Links without # are usually English words in definitions
                // Also match variants like #Classical_Nahuatl when target is "nahuatl"
                const hashMatch = href.match(/#([^#]+)$/);
                const hashLang = hashMatch ? hashMatch[1].toLowerCase().replace(/_/g, ' ') : '';
                const hasLangHash = targetLangs.some(lang => {
                    const langLower = lang.toLowerCase();
                    // Exact match OR the hash contains the target language
                    // e.g., "classical nahuatl" contains "nahuatl"
                    return hashLang === langLower || hashLang.includes(langLower);
                });
                const isInLangSpan = link.closest('[lang]');
                const langAttr = isInLangSpan?.getAttribute('lang')?.toLowerCase() || '';
                // Check if it's a target language by ISO code (cy for Welsh, ca for Catalan, ang for Old English, etc.)
                const isTargetLangByCode = targetLangs.some(tl => {
                    const tlLower = tl.toLowerCase();
                    // Check 2-letter and 3-letter codes
                    const code2 = tlLower.substring(0, 2);
                    const code3 = tlLower.substring(0, 3);
                    // Also check specific mappings for languages with non-obvious codes
                    const langCodeMap = {
                        'old english': 'ang',
                        'old english (ca. 450-1100)': 'ang',
                        'anglo-saxon': 'ang',
                    };
                    const mappedCode = langCodeMap[tlLower];
                    return langAttr === code2 || langAttr.startsWith(code2 + '-') ||
                           langAttr === code3 || langAttr.startsWith(code3 + '-') ||
                           (mappedCode && (langAttr === mappedCode || langAttr.startsWith(mappedCode + '-')));
                });
                
                // Skip links to English definitions - convert to plain text
                // BUT only if English is not one of our target languages
                const targetEnglish = targetLangs.some(tl => tl.toLowerCase() === 'english');
                if (!targetEnglish && (href.includes('#English') || href.includes('#english'))) {
                    link.replaceWith(document.createTextNode(wordText));
                    return;
                }
                // Skip if has a hash to a non-target language - convert to plain text
                if (href.includes('#') && !hasLangHash) {
                    link.replaceWith(document.createTextNode(wordText));
                    return;
                }
                // Skip if no hash AND not in a target-language span (these are English words in definitions)
                // Unless English is our target language
                if (!href.includes('#') && !isTargetLangByCode && !targetEnglish) {
                    link.replaceWith(document.createTextNode(wordText));
                    return;
                }
                
                // If we get here, it's a valid clickable link
                const escapedWord = wordText.replace(/'/g, "\\'");
                const span = document.createElement('span');
                span.className = 'dict-word-link';
                span.dataset.word = escapedWord;
                span.textContent = wordText;
                
                // Extract language from hash if present (e.g., #Japanese) - reuse hashMatch from above
                if (hashMatch) {
                    span.dataset.lang = hashMatch[1].replace(/_/g, ' ');
                }
                
                link.replaceWith(span);
            });
            return clone;
        }
        
        // Helper to make ALL word links clickable (for etymology, descendants, etc.)
        // Preserves the language from the link hash so we look up the right entry
        function makeAllLinksClickable(element) {
            const clone = element.cloneNode(true);
            clone.querySelectorAll('a').forEach(link => {
                const href = link.getAttribute('href') || '';
                const displayText = link.textContent.trim();
                const displayLower = displayText.toLowerCase();
                
                // Check if this is a redlink (page doesn't exist at all)
                const isRedlink = link.classList.contains('new') || href.includes('redlink=1');
                if (isRedlink) {
                    const span = document.createElement('span');
                    span.className = 'dict-missing';
                    span.textContent = displayText;
                    link.replaceWith(span);
                    return;
                }
                
                // Handle self-links (same word, different language section)
                // e.g., href="#Breton" for Breton "holl" on the "holl" page
                const isSelfLink = link.classList.contains('mw-selflink-fragment') || 
                                   (href.startsWith('#') && !href.startsWith('#cite'));
                if (isSelfLink && href.startsWith('#')) {
                    const targetLang = href.slice(1).replace(/_/g, ' ');
                    const span = document.createElement('span');
                    span.className = 'dict-word-link';
                    span.dataset.word = displayText.replace(/'/g, "\\'");
                    span.dataset.lang = targetLang;
                    span.textContent = displayText;
                    link.replaceWith(span);
                    return;
                }
                
                // Skip if not a wiki link or not a valid word (allow asterisk for reconstructions, periods for abbreviations)
                if (!href.startsWith('/wiki/') || !displayText || !/^[\p{L}\p{M}*'. -]+$/u.test(displayText)) {
                    link.replaceWith(document.createTextNode(link.textContent));
                    return;
                }
                
                // Skip Appendix links but allow Reconstruction links
                if (href.includes('Appendix:')) {
                    link.replaceWith(document.createTextNode(link.textContent));
                    return;
                }
                
                // Skip grammatical terms
                if (skipLinkWords.has(displayLower)) {
                    link.replaceWith(document.createTextNode(link.textContent));
                    return;
                }
                
                // Extract the page name from the URL (this is the canonical form without diacritics)
                // e.g., /wiki/%D9%82%D9%87%D9%88%D8%A9#Arabic -> قهوة
                // Also convert underscores back to spaces (Wiktionary URLs use _ for spaces)
                const pageMatch = href.match(/\/wiki\/([^#]+)/);
                const pageName = pageMatch ? decodeURIComponent(pageMatch[1]).replace(/_/g, ' ') : displayText;
                
                const span = document.createElement('span');
                span.className = 'dict-word-link';
                span.dataset.word = pageName.replace(/'/g, "\\'");  // Use page name for lookup
                span.textContent = displayText;  // Display the vocalized form
                
                // Extract language from Reconstruction URL or hash
                if (href.includes('Reconstruction:')) {
                    const protoMatch = href.match(/Reconstruction:([^\/]+)/);
                    if (protoMatch) span.dataset.lang = protoMatch[1].replace(/_/g, ' ');
                    span.dataset.page = pageName;  // Use the full page path for Reconstruction
                } else {
                    const hashMatch = href.match(/#([A-Za-z_-]+)/);
                    if (hashMatch) span.dataset.lang = hashMatch[1].replace(/_/g, ' ');
                }
                
                link.replaceWith(span);
            });
            return clone;
        }
        
        // Process a definition <li> into clean HTML
        function processDefItem(li, targetLangs) {
            const clone = li.cloneNode(true);
            
            // Remove unwanted elements but keep dl (synonyms)
            clone.querySelectorAll('ul, .reference, .mw-editsection, style, .audiotable').forEach(el => el.remove());
            
            // Process synonyms (in dl > dd with class nyms)
            let synonymsHtml = '';
            clone.querySelectorAll('dl').forEach(dl => {
                const dd = dl.querySelector('dd');
                if (dd && dd.querySelector('.nyms')) {
                    const nyms = dd.querySelector('.nyms');
                    const label = nyms.querySelector('span[style*="smaller"]')?.textContent || 'Synonyms:';
                    const linksClone = makeLinksClickable(nyms, targetLangs);
                    linksClone.querySelectorAll('span[style*="smaller"]').forEach(e => e.remove());
                    const wordsText = linksClone.innerHTML;
                    synonymsHtml += `<div class="dict-synonyms"><span class="dict-syn-label">${label}</span> ${wordsText}</div>`;
                }
                dl.remove();
            });
            
            // Process nested ol (subdefinitions) BEFORE removing them
            let subdefs = '';
            clone.querySelectorAll(':scope > ol').forEach(nestedOl => {
                subdefs += '<ol class="dict-subdefs">';
                nestedOl.querySelectorAll(':scope > li').forEach(subLi => {
                    const subResult = processDefItem(subLi, targetLangs);
                    if (subResult) subdefs += `<li>${subResult}</li>`;
                });
                subdefs += '</ol>';
                nestedOl.remove();
            });
            
            // Extract usage labels
            const labels = [];
            clone.querySelectorAll('.ib-content.label-content, .ib-content.qualifier-content').forEach(lbl => {
                const text = lbl.textContent.trim();
                if (text) labels.push(text);
            });
            clone.querySelectorAll('.ib-brac, .ib-content.label-content, .ib-content.qualifier-content').forEach(el => el.remove());
            
            // Make links in the definition clickable
            const linkedClone = makeLinksClickable(clone, targetLangs);
            
            // Get text/HTML
            let text = linkedClone.innerHTML.replace(/\s+/g, ' ').trim();
            // Remove remaining tags except our span links
            text = text.replace(/<(?!\/?span)[^>]+>/g, '').trim();
            if (!text || text === '↑') return null;
            
            const labelHtml = labels.length ? `<span class="dict-label">(${labels.join(', ')})</span> ` : '';
            return labelHtml + text + synonymsHtml + subdefs;
        }
        
        let resultHtml = '';
        let currentLang = null;
        let currentPos = 'initial';  // Start with a valid value so content before first heading shows
        let inMatchingLang = false;
        
        // Walk through all elements in order
        const allElements = doc.body.querySelectorAll('*');
        
        for (const el of allElements) {
            // Check for language heading (h2)
            if (el.matches('.mw-heading2 h2')) {
                const langName = el.textContent.replace(/\[edit\]/g, '').trim();
                const langLower = langName.toLowerCase();
                // If showing all languages, match everything; otherwise filter by text languages
                inMatchingLang = showAllLanguages || expandedLanguages.some(tl => {
                    // Exact match, or the page language includes our target (e.g., "Welsh" matches when looking for "Welsh")
                    // But NOT the reverse - "Old Welsh" should NOT match a "Welsh" section
                    return langLower === tl || langLower.includes(tl);
                });
                
                if (inMatchingLang) {
                    currentLang = langName;
                    currentPos = 'initial';  // Reset for new language
                    resultHtml += `<div class="dict-language"><strong>${langName}</strong></div>`;
                } else {
                    currentPos = null;  // Not in matching language
                }
                continue;
            }
            
            if (!inMatchingLang) continue;
            
            // Check for POS/section heading (h3, h4, h5)
            if (el.matches('.mw-heading3 h3, .mw-heading4 h4, .mw-heading5 h5')) {
                const heading = el.textContent.replace(/\[edit\]/g, '').trim();
                const headingLower = heading.toLowerCase();
                
                // Skip references section
                if (headingLower === 'references' || headingLower === 'further reading' || headingLower === 'external links') {
                    currentPos = null;  // Signal to skip content until next heading
                    continue;
                }
                
                // Check if this is a forms/mutation section (show but handle differently)
                const isFormSection = formSections.some(s => headingLower.includes(s));
                
                currentPos = heading;
                const posClass = isFormSection ? 'dict-pos dict-forms-heading' : 'dict-pos';
                resultHtml += `<div class="${posClass}">${heading}</div>`;
                continue;
            }
            
            // Skip content if we're in a skipped section (references, etc.)
            if (currentPos === null) continue;
            
            // Check for translation tables (these are different from inflection tables)
            if (el.tagName === 'TABLE' && el.classList.contains('translations')) {
                // Extract translation items from the table
                const transItems = [];
                el.querySelectorAll('li').forEach(li => {
                    // Skip "please add translation" items
                    if (li.querySelector('.trreq')) return;
                    
                    // Get the language name (text before the colon)
                    const text = li.textContent;
                    const colonIdx = text.indexOf(':');
                    if (colonIdx === -1) return;
                    const langName = text.substring(0, colonIdx).trim();
                    
                    // Get the word link
                    const link = li.querySelector('a[href*="/wiki/"]');
                    if (!link) return;
                    
                    const href = link.getAttribute('href') || '';
                    const displayText = link.textContent.trim();  // Displayed word (may have diacritics)
                    
                    // Get the actual page name from href (decoded) - this is what we need for API lookup
                    // e.g., /wiki/%D8%AA%D8%B4%D9%86%D8%AC#Arabic -> تشنج
                    // Also convert underscores back to spaces (Wiktionary URLs use _ for spaces)
                    const pageMatch = href.match(/\/wiki\/([^#]+)/);
                    const pageName = pageMatch ? decodeURIComponent(pageMatch[1]).replace(/_/g, ' ') : displayText;
                    
                    // Skip redlinks
                    if (link.classList.contains('new') || href.includes('redlink=1')) return;
                    
                    // Extract the language from the anchor (e.g., /wiki/word#Arabic)
                    const hashMatch = href.match(/#(.+)$/);
                    const targetLang = hashMatch ? decodeURIComponent(hashMatch[1]) : langName;
                    
                    // Get transliteration if present
                    const translit = li.querySelector('.tr, .transliteration');
                    const translitText = translit ? translit.textContent.trim() : '';
                    
                    // Get gender if present
                    const gender = li.querySelector('.gender abbr');
                    const genderText = gender ? gender.textContent.trim() : '';
                    
                    transItems.push({ langName, displayText, pageName, targetLang, translitText, genderText });
                });
                
                if (transItems.length > 0) {
                    // Get the gloss from data attribute
                    const gloss = el.getAttribute('data-gloss') || '';
                    if (gloss) {
                        resultHtml += `<div class="dict-trans-gloss">${gloss}</div>`;
                    }
                    
                    resultHtml += '<ul class="dict-translations">';
                    transItems.forEach(item => {
                        // Properly escape for HTML attributes (handles non-Latin scripts, quotes, etc.)
                        const escapeAttr = s => s.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
                        // Use pageName for lookup (unvoweled/canonical form), displayText for display
                        const escapedPage = escapeAttr(item.pageName);
                        const escapedLang = escapeAttr(item.targetLang);
                        const wordSpan = `<span class="dict-word-link" data-word="${escapedPage}" data-lang="${escapedLang}">${item.displayText}</span>`;
                        const genderPart = item.genderText ? ` <span class="dict-gender">${item.genderText}</span>` : '';
                        const translitPart = item.translitText ? ` <span class="dict-translit">(${item.translitText})</span>` : '';
                        resultHtml += `<li><span class="dict-trans-lang">${item.langName}:</span> ${wordSpan}${genderPart}${translitPart}</li>`;
                    });
                    resultHtml += '</ul>';
                }
                continue;
            }
            
            // Check for mutation/inflection tables (but not translation tables)
            if (el.tagName === 'TABLE' && !el.classList.contains('translations') &&
                (el.classList.contains('inflection-table') || 
                el.closest('.NavFrame') || el.querySelector('th'))) {
                // Clone and clean up the table
                const tableClone = el.cloneNode(true);
                tableClone.querySelectorAll('.reference, sup, .mw-editsection, style, script').forEach(e => e.remove());
                // Remove any nested navframes/collapsible content labels
                tableClone.querySelectorAll('.NavHead, .NavContent > .NavHead').forEach(e => e.remove());
                // Remove template editing links (layout · text) - usually in small tags
                tableClone.querySelectorAll('small').forEach(small => {
                    const text = small.textContent;
                    if (text.includes('layout') || text.includes('text') || text.includes('edit')) {
                        small.remove();
                    }
                });
                // Remove images (suit symbols, flags, etc.) - replace with alt text if available
                tableClone.querySelectorAll('img').forEach(img => {
                    const alt = img.getAttribute('alt') || '';
                    if (alt && alt.length < 20) {
                        img.replaceWith(document.createTextNode(alt));
                    } else {
                        img.remove();
                    }
                });
                // Remove empty file links left behind
                tableClone.querySelectorAll('a.mw-file-description, span.wikt-sticker-2px').forEach(e => {
                    if (!e.textContent.trim()) e.remove();
                });
                
                // Remove links from table TITLES/CAPTIONS (keep text, remove link)
                // These are usually in the first row or caption
                tableClone.querySelectorAll('caption a, tr:first-child a, th[colspan] a').forEach(link => {
                    link.replaceWith(document.createTextNode(link.textContent));
                });
                
                // Make links in table cells clickable (these are word forms, not English translations)
                tableClone.querySelectorAll('td a, th a').forEach(link => {
                    const href = link.getAttribute('href') || '';
                    const wordText = link.textContent.trim();
                    
                    // Check if this is a redlink (page doesn't exist)
                    const isRedlink = link.classList.contains('new') || href.includes('redlink=1');
                    if (isRedlink) {
                        // Replace with grey non-clickable text
                        const span = document.createElement('span');
                        span.className = 'dict-missing';
                        span.textContent = wordText;
                        link.replaceWith(span);
                        return;
                    }
                    
                    // Skip non-wiki links or invalid words (include combining marks, periods for abbreviations)
                    if (!href.startsWith('/wiki/') || !wordText || !/^[\p{L}\p{M}'. -]+$/u.test(wordText)) {
                        link.replaceWith(document.createTextNode(wordText));
                        return;
                    }
                    // Skip appendix links
                    if (href.includes('Appendix:') || href.includes('Reconstruction:')) {
                        link.replaceWith(document.createTextNode(wordText));
                        return;
                    }
                    
                    const escapedWord = wordText.replace(/'/g, "\\'");
                    const span = document.createElement('span');
                    span.className = 'dict-word-link';
                    span.dataset.word = escapedWord;
                    span.textContent = wordText;
                    link.replaceWith(span);
                });
                
                // Add our styling class
                tableClone.classList.add('dict-table');
                tableClone.removeAttribute('style');
                tableClone.removeAttribute('width');
                
                // Clean up cells and make grammatical terms bold
                const gramTerms = ['singular', 'plural', 'dual', 'masculine', 'feminine', 'neuter', 'common',
                    'nominative', 'genitive', 'dative', 'accusative', 'ablative', 'vocative', 'locative', 'instrumental',
                    'positive', 'comparative', 'superlative', 'equative',
                    'present', 'past', 'future', 'perfect', 'imperfect', 'pluperfect', 'preterite', 'aorist',
                    'indicative', 'subjunctive', 'imperative', 'conditional', 'optative',
                    'infinitive', 'participle', 'gerund', 'gerundive',
                    'active', 'passive', 'middle',
                    'first', 'second', 'third', '1st', '2nd', '3rd',
                    'definite', 'indefinite', 'unmutated', 'radical', 'soft', 'nasal', 'aspirate', 'hard', 'mixed'];
                const gramTermsLower = new Set(gramTerms.map(t => t.toLowerCase()));
                
                tableClone.querySelectorAll('th, td').forEach(cell => {
                    cell.removeAttribute('style');
                    cell.removeAttribute('width');
                    cell.removeAttribute('bgcolor');
                    
                    // If the cell contains only grammatical terms, make it bold
                    const cellText = cell.textContent.trim().toLowerCase();
                    const words = cellText.split(/[\s\/,]+/);
                    const isGramLabel = words.length > 0 && words.every(w => 
                        gramTermsLower.has(w) || w === '' || /^\d+(st|nd|rd|th)?$/.test(w)
                    );
                    if (isGramLabel && cell.tagName === 'TD') {
                        cell.style.fontWeight = 'bold';
                        cell.style.color = '#ccc';
                    }
                });
                
                resultHtml += tableClone.outerHTML;
                continue;
            }
            
            // Check for simple lists (alternative forms, derived terms, descendants, pronunciation, etc.)
            if (el.tagName === 'UL' && !el.closest('li') && !el.closest('table')) {
                const items = el.querySelectorAll(':scope > li');
                if (items.length > 0) {
                    resultHtml += '<ul class="dict-forms-list">';
                    items.forEach(li => {
                        // Check if this is a pronunciation item (contains IPA directly, not in nested ul)
                        const directIPA = li.querySelector(':scope > .IPA, :scope > span > .IPA, :scope > a > .IPA');
                        const hasDirectIPA = directIPA || (li.childNodes[0]?.textContent?.includes('IPA') && li.querySelector('.IPA'));
                        
                        if (hasDirectIPA) {
                            // Special handling for pronunciation - extract from THIS li only (not nested)
                            // First, remove nested ul/li to avoid double counting
                            const clone = li.cloneNode(true);
                            clone.querySelectorAll(':scope > ul').forEach(e => e.remove());
                            
                            // Remove edit links, references, sup tags
                            clone.querySelectorAll('.reference, sup, .mw-editsection, style').forEach(e => e.remove());
                            // Remove audio elements
                            clone.querySelectorAll('.audiotable, audio').forEach(e => e.remove());
                            
                            // Get qualifier text (only direct children, not nested)
                            const qualifiers = [];
                            clone.querySelectorAll(':scope > .ib-content.qualifier-content, :scope > span > .usage-label-accent').forEach(q => {
                                let text = q.textContent.trim().replace(/[,\s]+$/, '');
                                if (text) qualifiers.push(text);
                            });
                            
                            // Get IPA text (only direct children)
                            const ipaSpan = clone.querySelector('.IPA');
                            const ipa = ipaSpan ? ipaSpan.textContent.trim() : '';
                            
                            // Check for "Rhymes:" prefix
                            const isRhymes = clone.textContent.includes('Rhymes:');
                            
                            // Build output
                            let itemHtml = '';
                            if (isRhymes) {
                                itemHtml = `Rhymes: <span class="dict-ipa">${ipa}</span>`;
                            } else {
                                if (qualifiers.length > 0) {
                                    itemHtml += `<span class="dict-label">(${qualifiers[0]})</span> `;
                                }
                                if (ipa) {
                                    itemHtml += `<span class="dict-ipa">${ipa}</span>`;
                                }
                            }
                            
                            if (itemHtml.trim()) {
                                resultHtml += `<li>${itemHtml.trim()}</li>`;
                            }
                            
                            // Now process any nested ul (dialect variations)
                            const nestedUl = li.querySelector(':scope > ul');
                            if (nestedUl) {
                                nestedUl.querySelectorAll(':scope > li').forEach(nestedLi => {
                                    const nestedClone = nestedLi.cloneNode(true);
                                    nestedClone.querySelectorAll('.reference, sup, .mw-editsection, style, .audiotable, audio').forEach(e => e.remove());
                                    
                                    const nestedQualifiers = [];
                                    nestedClone.querySelectorAll('.ib-content.qualifier-content, .usage-label-accent').forEach(q => {
                                        let text = q.textContent.trim().replace(/[,\s]+$/, '');
                                        if (text) nestedQualifiers.push(text);
                                    });
                                    
                                    const nestedIpaSpan = nestedClone.querySelector('.IPA');
                                    const nestedIpa = nestedIpaSpan ? nestedIpaSpan.textContent.trim() : '';
                                    
                                    if (nestedIpa) {
                                        let nestedHtml = '';
                                        if (nestedQualifiers.length > 0) {
                                            nestedHtml += `<span class="dict-label">(${nestedQualifiers[0]})</span> `;
                                        }
                                        nestedHtml += `<span class="dict-ipa">${nestedIpa}</span>`;
                                        resultHtml += `<li style="margin-left: 1em;">${nestedHtml}</li>`;
                                    }
                                });
                            }
                        } else {
                            // Regular list item - use makeAllLinksClickable
                            const clone = makeAllLinksClickable(li);
                            clone.querySelectorAll('.reference, sup, style, link').forEach(e => e.remove());
                            
                            // Get cleaned HTML (preserving our spans and nested lists)
                            let itemHtml = clone.innerHTML;
                            // Remove remaining unwanted tags but keep span, ul, li
                            itemHtml = itemHtml.replace(/<(?!\/?(span|ul|li)\b)[^>]+>/g, '').trim();
                            // Clean up excess whitespace
                            itemHtml = itemHtml.replace(/\s+/g, ' ').trim();
                            
                            // Allow longer items for descendants (which have nested language trees)
                            if (itemHtml && itemHtml.length < 5000) {
                                resultHtml += `<li>${itemHtml}</li>`;
                            }
                        }
                    });
                    resultHtml += '</ul>';
                }
                continue;
            }
            
            // Check for definition list (ol that's a direct child of body or main content)
            // Only process top-level ol, not nested ones
            if (el.tagName === 'OL' && !el.closest('li')) {
                resultHtml += '<ol class="dict-definitions">';
                el.querySelectorAll(':scope > li').forEach(li => {
                    const processed = processDefItem(li, expandedLanguages);
                    if (processed) {
                        resultHtml += `<li>${processed}</li>`;
                    }
                });
                resultHtml += '</ol>';
                continue;
            }
            
            // Check for paragraphs (etymology, headword/inflection line, notes, etc.)
            if (el.tagName === 'P' && !el.closest('li') && !el.closest('table')) {
                const clone = el.cloneNode(true);
                // Remove references and edit links
                clone.querySelectorAll('.reference, sup, .mw-editsection, style').forEach(e => e.remove());
                
                // Check if this is a headword line (contains inflection info)
                const isHeadword = clone.querySelector('.headword-line') !== null;
                
                // Check if we're in an etymology section
                const isEtymology = currentPos && currentPos.toLowerCase().includes('etymology');
                
                // Use makeAllLinksClickable for etymology (to link to source languages)
                // Use makeLinksClickable for definitions (to filter English)
                const linkedClone = isEtymology ? makeAllLinksClickable(clone) : makeLinksClickable(clone, expandedLanguages);
                
                // Get HTML content (preserving our link spans only)
                let html = linkedClone.innerHTML.replace(/\s+/g, ' ').trim();
                // Remove ALL tags except our span links
                html = html.replace(/<(?!\/?span)[^>]+>/g, '').trim();
                
                if (!html || html.length < 3) continue;
                
                // Skip reference-only paragraphs
                if (html.match(/^\[\d+\]$/) || html === '↑') continue;
                
                // Skip boilerplate notes about mutated forms
                if (html.includes('Certain mutated forms') || html.includes('All possible mutated forms')) continue;
                
                // For headword lines, bold grammatical terms and remove "mutated forms" links
                if (isHeadword) {
                    // Remove link from "mutated forms"
                    html = html.replace(/<span class="dict-word-link[^"]*" data-word="mutated forms">mutated forms<\/span>/gi, 'mutated forms');
                    
                    // Bold ONLY grammatical label terms (not the words that follow them)
                    // These appear as "feminine X" or "feminine:" so we look for term followed by space or colon
                    const gramTerms = ['feminine', 'masculine', 'neuter', 'common', 
                        'singular', 'plural', 'dual',
                        'positive', 'comparative', 'superlative', 'equative',
                        'nominative', 'genitive', 'dative', 'accusative', 'ablative', 'vocative',
                        'definite', 'indefinite'];
                    for (const term of gramTerms) {
                        // Only match the term itself when it's a label (followed by space, colon, or word)
                        const regex = new RegExp('\\b(' + term + ')(?=\\s|:|$)', 'gi');
                        html = html.replace(regex, '<b>$1</b>');
                    }
                    
                    resultHtml += `<p class="dict-headword">${html}</p>`;
                } else {
                    resultHtml += `<p class="dict-paragraph">${html}</p>`;
                }
                continue;
            }
        }
        
        return resultHtml || '<div class="dict-error">No definitions found for this language</div>';
    }
    
    // Add a lookup to the widget
    // wordElement is optional - used to determine work-specific language
    // overrideLanguages is optional - used when clicking links with specific language targets
    async function addDictLookup(words, id, wordElement, overrideLanguages = null) {
        // Check if all words are just numbers/punctuation (\p{L} matches any Unicode letter)
        const hasLetters = words.some(w => /\p{L}/u.test(w));
        if (!hasLetters) {
            // Don't create a tab for pure numbers
            return;
        }
        
        // Get languages for this word's context (work-specific or text-level)
        // Use override if provided (for links from etymology/descendants with specific language)
        const languages = overrideLanguages || getLanguagesForElement(wordElement);
        console.log('addDictLookup:', words, 'languages:', languages, 'override:', overrideLanguages);
        
        // Create tab - clean up display text for Reconstruction pages
        const displayWords = words.map(w => {
            if (w.startsWith('Reconstruction:')) {
                // Show just "*word" instead of full page path
                return '*' + w.split('/').pop();
            }
            return w;
        });
        
        const tab = document.createElement('div');
        tab.className = 'dict-tab active';
        tab.dataset.id = id;
        tab.innerHTML = `
            <span class="dict-tab-text">${displayWords.join(' ')}</span>
            <span class="dict-tab-close" title="Remove">×</span>
        `;
        
        // Deactivate other tabs
        dictTabs.querySelectorAll('.dict-tab').forEach(t => t.classList.remove('active'));
        dictTabs.appendChild(tab);
        
        // Store lookup with placeholder for cached content
        dictLookups[id] = { words, tab, cachedHtml: null };
        activeLookupId = id;
        
        // Show loading
        dictContent.innerHTML = '<div class="dict-loading">Looking up...</div>';
        dictWidget.classList.add('visible');
        
        // Pre-process words: join hyphenated line breaks (e.g., "con-" + "tinued" → "continued")
        const processedWords = [];
        for (let i = 0; i < words.length; i++) {
            let word = words[i];
            // Check if word ends with hyphen (line break hyphenation)
            if (word.endsWith('-') && i < words.length - 1) {
                // Join with next word, removing the hyphen
                word = word.slice(0, -1) + words[i + 1];
                i++;  // Skip next word since we consumed it
            }
            processedWords.push(word);
        }
        
        // Check if this is a phrase (multiple words) - try phrase lookup first
        const isPhrase = processedWords.length > 1;
        let resultsHtml = '';
        
        if (isPhrase) {
            // Build phrase variants to try
            const phraseVariants = [];
            const basePhrase = processedWords.join(' ')
                .replace(/[.,!?;:"()\[\]{}]/g, '')
                .replace(/ſ/g, 's')
                .trim();
            
            // Try various forms of the phrase
            phraseVariants.push(basePhrase);                           // "per signum crucis"
            phraseVariants.push(basePhrase.replace(/\s+/g, '-'));      // "per-signum-crucis"
            phraseVariants.push(basePhrase.replace(/\s+/g, ''));       // "persignumcrucis"
            phraseVariants.push(basePhrase.replace(/\s+/g, '_'));      // "per_signum_crucis"
            
            // Try each variant
            for (const phrase of phraseVariants) {
                if (!phrase) continue;
                
                const caseResults = await lookupWordWithCases(phrase);
                
                for (const result of caseResults) {
                    const defHtml = formatDefinition(result.data, result.word, languages);
                    if (defHtml.includes('dict-error')) continue;
                    resultsHtml += `<div class="dict-word-entry"><h3>${result.word}</h3>`;
                    resultsHtml += defHtml;
                    resultsHtml += '</div>';
                }
                
                // If we found results for this variant, don't try others
                if (resultsHtml) break;
            }
            
            // If phrase lookup found nothing, add a note and fall through to individual words
            if (!resultsHtml) {
                resultsHtml += `<div class="dict-phrase-note">No entry for "${basePhrase}" — showing individual words:</div>`;
            }
        }
        
        // Lookup each word individually (always for single words, or as fallback for phrases)
        for (const word of processedWords) {
            // Skip punctuation-only and numbers (\p{L} matches any Unicode letter)
            if (!/\p{L}/u.test(word)) continue;
            
            // Check if this is a Reconstruction: page (special page for proto-languages)
            if (word.startsWith('Reconstruction:')) {
                // Direct lookup without cleaning - these are page names, not words
                const result = await lookupWiktionary(word);
                if (!result.error) {
                    // Extract proto-language name for matching (e.g., "Proto-Brythonic" from "Reconstruction:Proto-Brythonic/llugad")
                    const protoLangMatch = word.match(/Reconstruction:([^\/]+)/);
                    const protoLang = protoLangMatch ? protoLangMatch[1].replace(/_/g, ' ') : null;
                    const protoLanguages = protoLang ? [protoLang] : languages;
                    
                    const defHtml = formatDefinition(result, word, protoLanguages);
                    if (!defHtml.includes('dict-error')) {
                        // Extract the actual reconstructed word for display (e.g., *llugad)
                        const displayWord = word.split('/').pop() || word;
                        resultsHtml += `<div class="dict-word-entry"><h3>*${displayWord}</h3>`;
                        resultsHtml += defHtml;
                        resultsHtml += '</div>';
                    }
                }
                continue;
            }
            
            // Clean the word: remove punctuation (but keep internal apostrophes) and normalize historical characters
            // Normalize curly apostrophes to straight ones so "there's" and "there's" match
            const cleanWord = word
                .replace(/[.,!?;:""\"()[\]{}·•‧∙]/g, '')  // Remove quotes, punctuation, and interpuncts
                .replace(/['']/g, "'")  // Normalize curly apostrophes to straight
                .replace(/ſ/g, 's')  // Long s → s
                .replace(/ƿ/g, 'w')  // Wynn → w (Old English)
                .replace(/Ƿ/g, 'W')  // Capital wynn → W
                .replace(/^'+|'+$/g, '')  // Strip leading/trailing apostrophes (they're quotes, not contractions)
                .trim();
            if (!cleanWord) continue;
            
            // Lookup with both cases, and also without apostrophes (there's → theres)
            const caseResults = await lookupWordWithCases(cleanWord);
            
            // Track if we found anything from Wiktionary
            let foundWiktionary = false;
            
            for (const result of caseResults) {
                // For the EXACT word selected (same case), show all languages
                // For case variants, apply language filtering
                const isExactMatch = result.word === cleanWord;
                const defHtml = formatDefinition(result.data, result.word, isExactMatch ? null : languages);
                // Skip if no definitions for this language (but never skip exact match)
                if (!isExactMatch && defHtml.includes('dict-error')) continue;
                resultsHtml += `<div class="dict-word-entry"><h3>${result.word}</h3>`;
                resultsHtml += defHtml;
                resultsHtml += '</div>';
                foundWiktionary = true;
            }
            
            // If no Wiktionary results and this is a Tuvan text, show Tuvan dictionary link
            if (!foundWiktionary && isTuvanLanguage(languages)) {
                console.log('No Wiktionary entry, showing Tuvan dictionary link for:', cleanWord);
                const tuvanHtml = createTuvanDictionaryLink(cleanWord);
                resultsHtml += `<div class="dict-word-entry"><h3>${cleanWord}</h3>`;
                resultsHtml += tuvanHtml;
                resultsHtml += '</div>';
            }
            
            // If no Wiktionary results and this is Old English, show Bosworth-Toller link
            if (!foundWiktionary && isOldEnglishLanguage(languages)) {
                console.log('No Wiktionary entry, showing Bosworth-Toller link for:', cleanWord);
                const oeHtml = createOldEnglishDictionaryLink(cleanWord);
                resultsHtml += `<div class="dict-word-entry"><h3>${cleanWord}</h3>`;
                resultsHtml += oeHtml;
                resultsHtml += '</div>';
            }
        }
        
        // If no results at all, remove the tab and deselect
        if (!resultsHtml) {
            deselectById(id);
            removeDictLookup(id);
            return;
        }
        
        // Cache the results
        if (dictLookups[id]) {
            dictLookups[id].cachedHtml = resultsHtml;
        }
        
        // Only update if this is still the active lookup
        if (activeLookupId === id) {
            dictContent.innerHTML = dictLookups[id].cachedHtml;
        }
        
        // Tab click to switch
        tab.addEventListener('click', (e) => {
            if (e.target.classList.contains('dict-tab-close')) return;
            dictTabs.querySelectorAll('.dict-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            activeLookupId = id;
            // Show cached content
            if (dictLookups[id] && dictLookups[id].cachedHtml) {
                dictContent.innerHTML = dictLookups[id].cachedHtml;
            }
        });
        
        // Tab close
        tab.querySelector('.dict-tab-close').addEventListener('click', (e) => {
            e.stopPropagation();
            // Also deselect the word/phrase in the text
            deselectById(id);
            removeDictLookup(id);
        });
    }
    
    // Clear all dictionary lookups (for external use like page-viewer click-outside)
    function clearAllDictLookups() {
        const ids = Object.keys(dictLookups);
        ids.forEach(id => {
            deselectById(id);
            removeDictLookup(id);
        });
    }
    
    // Export functions for page-viewer.js
    window.addDictLookup = addDictLookup;
    window.clearAllDictLookups = clearAllDictLookups;
    
    // Deselect word/phrase in text by lookup ID
    function deselectById(id) {
        if (id.startsWith('word-')) {
            // Single word - find by idx
            const idx = id.replace('word-', '');
            const word = document.querySelector(`.word[data-idx="${idx}"]`);
            if (word) word.classList.remove('selected');
        } else if (id.startsWith('hyphen-')) {
            // Hyphen-linked words
            const hyphenLink = id.replace('hyphen-', '');
            document.querySelectorAll(`.word[data-hyphen-link="${hyphenLink}"]`).forEach(w => {
                w.classList.remove('selected');
            });
        } else if (id.startsWith('phrase-')) {
            // Phrase - use the existing removePhraseById
            const phraseId = id.replace('phrase-', '');
            // Find and remove phrase styling
            document.querySelectorAll(`.word[data-phrase="${phraseId}"]`).forEach(w => {
                w.classList.remove('phrase-word');
                delete w.dataset.phrase;
            });
            // Remove overlays
            if (typeof phraseOverlays !== 'undefined' && phraseOverlays[phraseId]) {
                phraseOverlays[phraseId].forEach(el => el.remove());
                delete phraseOverlays[phraseId];
            }
        }
    }
    
    // Remove a lookup from the widget
    function removeDictLookup(id) {
        console.log('removeDictLookup called with id:', id, 'exists:', !!dictLookups[id]);
        if (dictLookups[id]) {
            dictLookups[id].tab.remove();
            delete dictLookups[id];
            
            // If this was active, switch to another or hide
            if (activeLookupId === id) {
                const remaining = Object.keys(dictLookups);
                if (remaining.length > 0) {
                    const nextId = remaining[remaining.length - 1];
                    const nextTab = dictTabs.querySelector(`.dict-tab[data-id="${nextId}"]`);
                    if (nextTab) nextTab.classList.add('active');
                    activeLookupId = nextId;
                    // Show cached content for the new active tab
                    if (dictLookups[nextId] && dictLookups[nextId].cachedHtml) {
                        dictContent.innerHTML = dictLookups[nextId].cachedHtml;
                    }
                } else {
                    activeLookupId = null;
                    dictContent.innerHTML = '<div class="dict-placeholder">Select a word or phrase to look up</div>';
                }
            }
        }
        
        // Hide widget if no lookups
        if (Object.keys(dictLookups).length === 0) {
            dictWidget.classList.remove('visible');
        }
    }
    
    // Close button hides widget
    dictClose.addEventListener('click', () => {
        dictWidget.classList.remove('visible');
    });
    
    // Handle clicks on dictionary word links (derived terms, alternate forms, etc.)
    dictContent.addEventListener('click', async (e) => {
        const wordLink = e.target.closest('.dict-word-link');
        if (wordLink) {
            const word = wordLink.dataset.word;
            const targetLang = wordLink.dataset.lang;  // Language from href hash (e.g., "Tagalog")
            const pageName = wordLink.dataset.page;    // Full page name for Reconstruction: pages
            console.log('Dict link clicked:', word, 'targetLang:', targetLang, 'pageName:', pageName);
            if (word) {
                // Look up this word in a new tab
                const id = 'dict-link-' + word + '-' + Date.now();
                // Pass the target language if specified, and page name for reconstructions
                addDictLookup([pageName || word], id, null, targetLang ? [targetLang] : null);
            }
        }
    });
    
    // Hook into word selection - watch for class changes
    // Use MutationObserver to detect when words get selected/deselected
    const wordObserver = new MutationObserver((mutations) => {
        mutations.forEach(mutation => {
            if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                const word = mutation.target;
                if (!word.classList.contains('word')) return;
                
                const text = word.textContent.trim();
                const wordId = 'word-' + (word.dataset.idx || text);
                
                if (word.classList.contains('selected')) {
                    // Word selected (red) - add to dictionary
                    // Check for hyphen-linked words
                    const hyphenLink = word.dataset.hyphenLink;
                    if (hyphenLink) {
                        const lookupId = 'hyphen-' + hyphenLink;
                        // Only add if not already added (prevents duplicates from multiple linked words)
                        if (!dictLookups[lookupId]) {
                            const linkedWords = Array.from(document.querySelectorAll(`.word[data-hyphen-link="${hyphenLink}"]`));
                            // Join words, removing trailing hyphens (line-break hyphenation)
                            const fullText = linkedWords.map(w => w.textContent.trim().replace(/-$/, '')).join('');
                            addDictLookup([fullText], lookupId, word);
                        }
                    } else {
                        addDictLookup([text], wordId, word);
                    }
                } else if (!word.classList.contains('phrase-word')) {
                    // Word deselected - remove from dictionary
                    const hyphenLink = word.dataset.hyphenLink;
                    if (hyphenLink) {
                        // Only remove if ALL linked words are deselected
                        const linkedWords = document.querySelectorAll(`.word[data-hyphen-link="${hyphenLink}"]`);
                        const anySelected = Array.from(linkedWords).some(w => w.classList.contains('selected'));
                        if (!anySelected) {
                            removeDictLookup('hyphen-' + hyphenLink);
                        }
                    } else {
                        removeDictLookup(wordId);
                    }
                }
                
                // Check for phrase selection
                const phraseId = word.dataset.phrase;
                if (word.classList.contains('phrase-word') && phraseId) {
                    // This is part of a phrase - check if we already have this phrase
                    const phraseLookupId = 'phrase-' + phraseId;
                    if (!dictLookups[phraseLookupId]) {
                        const phraseWords = Array.from(document.querySelectorAll(`.word[data-phrase="${phraseId}"]`))
                            .map(w => w.textContent.trim());
                        addDictLookup(phraseWords, phraseLookupId, word);
                    }
                }
            }
        });
    });
    
    // Observe all word elements for class changes
    document.querySelectorAll('.word').forEach(word => {
        wordObserver.observe(word, { attributes: true, attributeFilter: ['class'] });
    });
    
    // Also watch for phrase removal (when phrase class is removed)
    const phraseCheckInterval = setInterval(() => {
        // Check if any tracked phrases no longer exist
        Object.keys(dictLookups).forEach(id => {
            if (id.startsWith('phrase-')) {
                const phraseId = id.replace('phrase-', '');
                const stillExists = document.querySelector(`.word[data-phrase="${phraseId}"]`);
                if (!stillExists) {
                    removeDictLookup(id);
                }
            }
        });
    }, 500);

    // === SHEET MUSIC SUPPORT ===
    // Initialize OpenSheetMusicDisplay for any music containers
    // Look for both .work-music (inside gold box) and .text-music (standalone blue box)
    
    const musicContainers = document.querySelectorAll('.work-music[data-music-file], .text-music[data-music-file]');
    if (musicContainers.length > 0) {
        // Load OSMD from CDN
        const osmdScript = document.createElement('script');
        osmdScript.src = 'https://cdn.jsdelivr.net/npm/opensheetmusicdisplay@1.8.6/build/opensheetmusicdisplay.min.js';
        osmdScript.onload = () => initializeSheetMusic(musicContainers);
        document.head.appendChild(osmdScript);
    }
    
    function initializeSheetMusic(containers) {
        containers.forEach(async (container) => {
            const musicFile = container.dataset.musicFile;
            const renderId = container.id + '-render';
            
            // Create render target with explicit dimensions for OSMD
            const renderDiv = document.createElement('div');
            renderDiv.id = renderId;
            renderDiv.className = 'music-render';
            renderDiv.style.width = '550px';
            renderDiv.style.minHeight = '200px';
            
            // Create controls
            const controls = document.createElement('div');
            controls.className = 'music-controls';
            controls.innerHTML = `
                <button class="play-btn" title="Play">▶ Play</button>
                <button class="pause-btn" title="Pause" disabled>Pause</button>
                <button class="stop-btn" title="Stop" disabled>Stop</button>
                <span class="music-time"></span>
            `;
            
            // Clear container and add elements FIRST (OSMD needs the div in the DOM)
            container.innerHTML = '';
            container.appendChild(controls);
            container.appendChild(renderDiv);
            
            console.log('OSMD: Initializing for', musicFile);
            console.log('OSMD: Render div:', renderDiv, 'in DOM:', document.body.contains(renderDiv));
            console.log('OSMD: Container dimensions:', container.offsetWidth, container.offsetHeight);
            console.log('OSMD: RenderDiv dimensions:', renderDiv.offsetWidth, renderDiv.offsetHeight);
            console.log('OSMD: opensheetmusicdisplay object:', typeof opensheetmusicdisplay, Object.keys(opensheetmusicdisplay || {}));
            
            try {
                // Initialize OSMD (now the div exists in DOM)
                // OSMD exports OpenSheetMusicDisplay at opensheetmusicdisplay.OpenSheetMusicDisplay
                const OSMD = opensheetmusicdisplay.OpenSheetMusicDisplay || opensheetmusicdisplay;
                const osmd = new OSMD(renderDiv, {
                    autoResize: true,
                    backend: 'svg',
                    drawTitle: false,
                    drawComposer: false,
                    drawLyricist: false
                });
                
                console.log('OSMD: Created instance, loading', musicFile);
                
                // Load and render
                await osmd.load(musicFile);
                console.log('OSMD: Loaded, now rendering');
                await osmd.render();
                console.log('OSMD: Rendered');
                
                // Post-process lyrics to integrate with word selection system
                processSheetMusicLyrics(container, osmd);
                
                // Setup playback (optional - requires osmd-audio-player)
                setupMusicPlayback(container, osmd, controls);
                
            } catch (err) {
                console.error('Failed to load sheet music:', err);
                container.innerHTML = `<div class="music-error">Failed to load sheet music: ${err.message}</div>`;
            }
        });
    }
    
    function processSheetMusicLyrics(container, osmd) {
        // Find all lyric text elements in the SVG
        const svg = container.querySelector('svg');
        if (!svg) return;
        
        // OSMD wraps lyrics in text elements
        const textElements = svg.querySelectorAll('text');
        const lyricElements = [];
        
        textElements.forEach(text => {
            const textContent = text.textContent.trim();
            if (!textContent) return;
            
            // Skip if it looks like musical notation (dynamics, tempo, etc.)
            if (/^[pfms]+$|^\d+$|^[A-G]$|^(cresc|dim|rit|accel)/i.test(textContent)) return;
            
            // Check if this text is likely a lyric
            const classList = text.getAttribute('class') || '';
            const isLyric = classList.includes('lyric') || 
                           classList.includes('Lyric') ||
                           text.closest('[class*="lyric"]') ||
                           text.closest('[class*="Lyric"]');
            
            // Position heuristic: lyrics are typically lower
            const y = parseFloat(text.getAttribute('y') || '0');
            const likelyLyric = isLyric || y > 100;
            
            if (likelyLyric && /^[\p{L}\p{M}'-]+$/u.test(textContent)) {
                lyricElements.push(text);
            }
        });
        
        if (lyricElements.length === 0) return;
        
        console.log('Found lyric elements:', lyricElements.map(el => ({
            text: el.textContent,
            y: el.getAttribute('y'),
            class: el.getAttribute('class')
        })));
        
        // Get current max idx from wordsInOrder
        let maxIdx = wordsInOrder.length;
        
        // Process each lyric element
        lyricElements.forEach((text, i) => {
            const textContent = text.textContent.trim();
            
            // Add 'word' class so it works with existing selection system
            text.classList.add('word');
            text.classList.add('lyric-word');
            text.dataset.idx = maxIdx + i;
            text.style.cursor = 'pointer';
            
            // Add to wordsInOrder array
            wordsInOrder.push(text);
            
            // Check for hyphen continuation (syllable linking)
            if (textContent.endsWith('-')) {
                text.dataset.hyphenContinues = 'true';
            }
            
            // SVG elements need direct event handlers (document-level won't work reliably)
            text.addEventListener('mousedown', (e) => {
                console.log('Lyric mousedown:', textContent);
                e.stopPropagation();
                wordInteractionActive = true;
                startWord = text;
                isDragging = false;
                dragMode = text.classList.contains('selected') ? 'deselect' : 'select';
            });
            
            text.addEventListener('click', (e) => {
                console.log('Lyric click:', textContent, 'isDragging:', isDragging);
                e.stopPropagation();
                // Toggle selection on click (if not dragging)
                if (!isDragging) {
                    const hyphenLink = text.dataset.hyphenLink;
                    if (hyphenLink) {
                        const linkedWords = document.querySelectorAll(`[data-hyphen-link="${hyphenLink}"]`);
                        const shouldSelect = !text.classList.contains('selected');
                        console.log('Lyric toggle hyphen-linked:', hyphenLink, 'shouldSelect:', shouldSelect);
                        linkedWords.forEach(w => {
                            if (shouldSelect) {
                                w.classList.add('selected');
                            } else {
                                w.classList.remove('selected');
                            }
                        });
                    } else {
                        console.log('Lyric toggle single word');
                        text.classList.toggle('selected');
                    }
                }
            });
        });
        
        // Link hyphenated syllables (same logic as regular words)
        let hyphenLinkIdLocal = hyphenLinkId;
        for (let i = 0; i < lyricElements.length; i++) {
            const lyric = lyricElements[i];
            const text = lyric.textContent.trim();
            if (text.endsWith('-') && i < lyricElements.length - 1) {
                const nextLyric = lyricElements[i + 1];
                const linkId = 'hyphen-' + (hyphenLinkIdLocal++);
                lyric.dataset.hyphenLink = linkId;
                nextLyric.dataset.hyphenLink = linkId;
            }
        }
        hyphenLinkId = hyphenLinkIdLocal;
        
        // Add hover listeners for all lyrics (and special handling for hyphen-linked)
        lyricElements.forEach(lyric => {
            lyric.addEventListener('mouseenter', () => {
                const linkId = lyric.dataset.hyphenLink;
                if (linkId) {
                    document.querySelectorAll(`[data-hyphen-link="${linkId}"]`).forEach(w => {
                        w.classList.add('hyphen-hover');
                    });
                } else {
                    lyric.classList.add('hyphen-hover');
                }
            });
            lyric.addEventListener('mouseleave', () => {
                const linkId = lyric.dataset.hyphenLink;
                if (linkId) {
                    document.querySelectorAll(`[data-hyphen-link="${linkId}"]`).forEach(w => {
                        w.classList.remove('hyphen-hover');
                    });
                } else {
                    lyric.classList.remove('hyphen-hover');
                }
            });
        });
        
        // Observe lyrics for class changes (for dictionary widget)
        lyricElements.forEach(lyric => {
            wordObserver.observe(lyric, { attributes: true, attributeFilter: ['class'] });
        });
        
        console.log(`Processed ${lyricElements.length} lyric words for selection`);
    }
    
    function setupMusicPlayback(container, osmd, controls) {
        // Basic playback would require osmd-audio-player or similar
        // For now, just disable playback buttons if no audio engine
        const playBtn = controls.querySelector('.play-btn');
        const pauseBtn = controls.querySelector('.pause-btn');
        const stopBtn = controls.querySelector('.stop-btn');
        
        // Check if audio player is available
        const hasAudioPlayer = typeof AudioPlayer !== 'undefined' || 
                               typeof opensheetmusicdisplay.PlaybackEngine !== 'undefined';
        
        if (!hasAudioPlayer) {
            playBtn.title = 'Playback requires additional audio library';
            playBtn.disabled = true;
            playBtn.textContent = '▶ (no audio)';
            return;
        }
        
        // If audio player exists, set up handlers
        // (Implementation depends on which audio library is used)
    }

    // === AUTOMATIC FULLSCREEN TITLE UPDATE ===
    // Watches for fullscreen class on page-viewer and updates title automatically
    function setupFullscreenTitleUpdate() {
        const pageViewer = document.querySelector('.page-viewer');
        const pvTitle = document.getElementById('pv-title');
        const pageTitle = document.getElementById('page-title');
        
        if (!pageViewer || !pvTitle || !pageTitle) return;
        
        // Create a MutationObserver to watch for class changes
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.attributeName === 'class') {
                    const isFullscreen = pageViewer.classList.contains('fullscreen');
                    pvTitle.textContent = isFullscreen ? pageTitle.textContent : 'Page Viewer';
                }
            });
        });
        
        observer.observe(pageViewer, { attributes: true, attributeFilter: ['class'] });
    }
    
    // Run after DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', setupFullscreenTitleUpdate);
    } else {
        // Small delay to ensure page viewer is initialized
        setTimeout(setupFullscreenTitleUpdate, 100);
    }
}

// Auto-init if content is already present, otherwise wait for manual call
(function() {
    const textBody = document.querySelector('.text-body');
    if (textBody && textBody.querySelector('.text-work, .text-page')) {
        // Content already present (static HTML pages)
        window.initTextReader();
    } else if (textBody) {
        // Dynamic content - use MutationObserver to auto-init when content appears
        const observer = new MutationObserver((mutations, obs) => {
            if (textBody.querySelector('.text-work, .text-page')) {
                obs.disconnect();
                window.initTextReader();
            }
        });
        observer.observe(textBody, { childList: true, subtree: true });
    }
})();
