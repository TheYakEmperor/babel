// Page viewer initialization - scans images/ directory automatically
// Backblaze B2 configuration for image hosting
const B2_BASE_URL = 'https://babel-images.s3.us-east-005.backblazeb2.com';

function initPageViewer(pagesData) {
    const viewer = document.getElementById('page-viewer');
    const mainContainer = document.getElementById('pv-main');
    const spread = document.getElementById('pv-spread');
    const container1 = document.getElementById('pv-container-1');
    const container2 = document.getElementById('pv-container-2');
    const mainImage = document.getElementById('pv-image');
    const mainImage2 = document.getElementById('pv-image-2');
    const thumbContainer = document.getElementById('pv-thumbnails');
    const countDisplay = document.getElementById('pv-count');
    const prevBtn = document.getElementById('pv-prev');
    const nextBtn = document.getElementById('pv-next');
    const dualToggle = document.getElementById('pv-dual-toggle');
    const fullscreenToggle = document.getElementById('pv-fullscreen-toggle');
    const zoomInBtn = document.getElementById('pv-zoom-in');
    const zoomOutBtn = document.getElementById('pv-zoom-out');
    const zoomResetBtn = document.getElementById('pv-zoom-reset');
    const zoomLevelDisplay = document.getElementById('pv-zoom-level');
    
    // Get current text path for B2 URL construction
    const pathMatch = window.location.pathname.match(/\/texts\/(.+?)\/(?:index\.html)?$/);
    const textPath = pathMatch ? pathMatch[1] : '';
    
    // Queue for early calls before images are loaded
    let pendingLabelNavigations = [];
    let isReady = false;
    
    // Placeholder function that queues calls until ready
    window.goToViewerPageByLabel = function(label) {
        console.log('goToViewerPageByLabel called (pending):', label);
        pendingLabelNavigations.push(label);
    };
    
    window.goToViewerPage = function(pageIndex) {
        console.log('goToViewerPage called (pending):', pageIndex);
    };
    
    let images = [];
    let currentIndex = 0;
    let isDualMode = false;
    let isFullscreen = false;
    let isTranscriptionMode = false;
    let transcriptionPanel = null;
    let refreshTranscriptionPanel = null;  // Function reference set later
    
    // Zoom and pan state
    let zoomLevel = 1;
    const minZoom = 1;
    const maxZoom = 5;
    const zoomStep = 0.25;
    let panX = 0, panY = 0;
    let isDragging = false, startX = 0, startY = 0;
    
    function updateZoomDisplay() {
        zoomLevelDisplay.textContent = Math.round(zoomLevel * 100) + '%';
    }
    
    function applyZoom() {
        spread.style.transform = `scale(${zoomLevel}) translate(${panX}px, ${panY}px)`;
        mainContainer.classList.toggle('zoomed', zoomLevel > 1);
        updateZoomDisplay();
    }
    
    function zoomIn() {
        zoomLevel = Math.min(maxZoom, zoomLevel + zoomStep);
        applyZoom();
    }
    
    function zoomOut() {
        zoomLevel = Math.max(minZoom, zoomLevel - zoomStep);
        if (zoomLevel === 1) resetPan();
        applyZoom();
    }
    
    function resetZoom() {
        zoomLevel = 1;
        resetPan();
        applyZoom();
    }
    
    function resetPan() {
        panX = 0;
        panY = 0;
        applyZoom();
    }
    
    function setupPanHandlers() {
        // Pan handler - transform the spread as a single unit
        mainContainer.addEventListener('mousedown', (e) => {
            if (zoomLevel <= 1) return;
            if (e.target.closest('.page-viewer-zoom-controls')) return;
            e.preventDefault();
            
            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            mainContainer.classList.add('dragging');
        });
        
        mainContainer.addEventListener('mousemove', (e) => {
            if (zoomLevel <= 1 || !isDragging) return;
            e.preventDefault();
            
            const deltaX = (e.clientX - startX) / zoomLevel;
            const deltaY = (e.clientY - startY) / zoomLevel;
            
            panX += deltaX;
            panY += deltaY;
            
            // Calculate limits based on spread size
            const spreadRect = spread.getBoundingClientRect();
            const containerRect = mainContainer.getBoundingClientRect();
            const scaledWidth = spreadRect.width;
            const scaledHeight = spreadRect.height;
            
            const maxPanX = Math.max(0, (scaledWidth - containerRect.width) / (2 * zoomLevel));
            const maxPanY = Math.max(0, (scaledHeight - containerRect.height) / (2 * zoomLevel));
            panX = Math.max(-maxPanX, Math.min(maxPanX, panX));
            panY = Math.max(-maxPanY, Math.min(maxPanY, panY));
            
            applyZoom();
            
            startX = e.clientX;
            startY = e.clientY;
        });
        
        mainContainer.addEventListener('mouseup', () => {
            isDragging = false;
            mainContainer.classList.remove('dragging');
        });
        
        mainContainer.addEventListener('mouseleave', () => {
            isDragging = false;
            mainContainer.classList.remove('dragging');
        });
        
        // Mouse wheel zoom
        mainContainer.addEventListener('wheel', (e) => {
            e.preventDefault();
            if (e.deltaY < 0) {
                zoomIn();
            } else {
                zoomOut();
            }
        }, { passive: false });
    }
    
    // Get images from pagesData, manifest, or scan images/ directory
    async function detectImages() {
        // First check if pagesData has image properties
        if (pagesData && pagesData.length > 0) {
            const fromData = pagesData
                .filter(p => p.image)
                .map(p => ({ url: p.image, label: p.label || '' }));
            
            if (fromData.length > 0) {
                return fromData;
            }
        }
        
        // Check for images.json manifest (for B2-hosted images)
        try {
            const manifestResp = await fetch('images.json');
            if (manifestResp.ok) {
                const manifest = await manifestResp.json();
                if (manifest.images && manifest.images.length > 0) {
                    return manifest.images;
                }
            }
        } catch (e) {}
        
        // Scan images/ directory listing
        try {
            const resp = await fetch('images/');
            if (resp.ok) {
                const html = await resp.text();
                const imageExts = /\.(jpg|jpeg|png|webp|gif)$/i;
                const matches = html.match(/href="([^"]+)"/g) || [];
                const found = matches
                    .map(m => decodeURIComponent(m.replace(/href="|"/g, '')))
                    .filter(f => imageExts.test(f) && !f.startsWith('/'))
                    .sort((a, b) => a.localeCompare(b, undefined, { numeric: true, sensitivity: 'base' }))
                    .map(f => ({
                        url: 'images/' + encodeURIComponent(f),
                        label: f.replace(/\.[^.]+$/, '').replace(/_/g, ' ')
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
    }
    
    // Extract page name - uses label if item is an object, otherwise filename
    function getPageName(item) {
        if (typeof item === 'object' && item.label) {
            return item.label;
        }
        const url = typeof item === 'object' ? item.url : item;
        const filename = url.split('/').pop();
        return filename.replace(/\.[^.]+$/, '');
    }
    
    function getPageUrl(item) {
        const url = typeof item === 'object' ? item.url : item;
        // If already absolute URL, return as-is
        if (url.startsWith('http://') || url.startsWith('https://')) {
            return url;
        }
        // Construct B2 URL: base + /texts/path/to/text/ + images/filename
        if (textPath && url.startsWith('images/')) {
            return `${B2_BASE_URL}/texts/${textPath}/${url}`;
        }
        return url;
    }
    
    function getSpreads() {
        if (images.length === 0) return [];
        const spreads = [];
        spreads.push([0]);
        for (let i = 1; i < images.length; i += 2) {
            if (i + 1 < images.length) {
                spreads.push([i, i + 1]);
            } else {
                spreads.push([i]);
            }
        }
        return spreads;
    }
    
    function showSingle(index) {
        if (index < 0 || index >= images.length) return;
        currentIndex = index;
        resetZoom();
        
        mainContainer.classList.remove('dual-page');
        mainImage.classList.remove('solo');
        mainImage.src = getPageUrl(images[index]);
        mainImage.alt = getPageName(images[index]);
        container1.style.display = '';
        container2.style.display = 'none';
        
        countDisplay.textContent = getPageName(images[index]);
        prevBtn.disabled = index === 0;
        nextBtn.disabled = index === images.length - 1;
        
        thumbContainer.querySelectorAll('.page-viewer-thumb-wrapper').forEach((wrapper, i) => {
            wrapper.classList.toggle('active', i === index);
            if (i === index) {
                wrapper.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
            }
        });
    }
    
    function showSpread(spreadIndex) {
        const spreads = getSpreads();
        if (spreadIndex < 0 || spreadIndex >= spreads.length) return;
        currentIndex = spreadIndex;
        resetZoom();
        
        const spread = spreads[spreadIndex];
        mainContainer.classList.add('dual-page');
        
        if (spread.length === 1) {
            mainImage.src = getPageUrl(images[spread[0]]);
            mainImage.alt = getPageName(images[spread[0]]);
            mainImage.classList.add('solo');
            container1.classList.add('solo');
            container1.style.display = '';
            container2.style.display = 'none';
            countDisplay.textContent = getPageName(images[spread[0]]);
        } else {
            mainImage.src = getPageUrl(images[spread[0]]);
            mainImage.alt = getPageName(images[spread[0]]);
            mainImage.classList.remove('solo');
            container1.classList.remove('solo');
            container1.style.display = '';
            
            mainImage2.src = getPageUrl(images[spread[1]]);
            mainImage2.alt = getPageName(images[spread[1]]);
            container2.style.display = '';
            
            countDisplay.textContent = `${getPageName(images[spread[0]])} – ${getPageName(images[spread[1]])}`;
        }
        
        prevBtn.disabled = spreadIndex === 0;
        nextBtn.disabled = spreadIndex === spreads.length - 1;
        
        const thumbs = thumbContainer.querySelectorAll('.page-viewer-thumb-wrapper');
        thumbs.forEach((wrapper, i) => {
            wrapper.classList.toggle('active', spread.includes(i));
        });
        // Scroll to show both spread thumbnails - use the second one if dual, first if single
        const scrollToIdx = spread.length === 2 ? spread[1] : spread[0];
        if (thumbs[scrollToIdx]) {
            thumbs[scrollToIdx].scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
        }
    }
    
    function showImage(index) {
        if (isDualMode) {
            showSpread(index);
        } else {
            showSingle(index);
        }
        
        // Update transcription panel if in transcription mode
        if (isTranscriptionMode && transcriptionPanel && refreshTranscriptionPanel) {
            refreshTranscriptionPanel();
        }
    }
    
    function navigate(delta) {
        showImage(currentIndex + delta);
    }
    
    function toggleDualMode() {
        isDualMode = !isDualMode;
        dualToggle.classList.toggle('active', isDualMode);
        dualToggle.textContent = isDualMode ? 'Single' : 'Dual';
        
        if (isDualMode) {
            const spreads = getSpreads();
            let spreadIdx = 0;
            for (let i = 0; i < spreads.length; i++) {
                if (spreads[i].includes(currentIndex)) {
                    spreadIdx = i;
                    break;
                }
            }
            showSpread(spreadIdx);
        } else {
            const spreads = getSpreads();
            const pageIdx = spreads[currentIndex] ? spreads[currentIndex][0] : 0;
            showSingle(pageIdx);
        }
    }
    
    function toggleFullscreen() {
        isFullscreen = !isFullscreen;
        viewer.classList.toggle('fullscreen', isFullscreen);
        document.body.classList.toggle('viewer-fullscreen', isFullscreen);
        fullscreenToggle.classList.toggle('active', isFullscreen);
        fullscreenToggle.textContent = isFullscreen ? 'Exit' : 'Fullscreen';
        resetZoom();
    }
    
    // Start detection
    detectImages().then(found => {
        if (found.length === 0) return;
        
        images = found;
        viewer.style.display = 'block';
        
        // Set title if in fullscreen title element exists
        const pvTitle = document.getElementById('pv-title');
        if (pvTitle && window.textData && window.textData.title) {
            pvTitle.textContent = window.textData.title;
        }
        
        // Create thumbnails
        images.forEach((url, i) => {
            const wrapper = document.createElement('div');
            wrapper.className = 'page-viewer-thumb-wrapper';
            
            const thumb = document.createElement('img');
            thumb.className = 'page-viewer-thumb';
            thumb.src = getPageUrl(url);
            thumb.alt = getPageName(url);
            
            const label = document.createElement('span');
            label.className = 'page-viewer-thumb-label';
            label.textContent = getPageName(url);
            
            wrapper.appendChild(thumb);
            wrapper.appendChild(label);
            wrapper.addEventListener('click', () => {
                if (isDualMode) {
                    const spreads = getSpreads();
                    for (let s = 0; s < spreads.length; s++) {
                        if (spreads[s].includes(i)) {
                            showSpread(s);
                            break;
                        }
                    }
                } else {
                    showSingle(i);
                }
            });
            thumbContainer.appendChild(wrapper);
        });
        
        // Set up pan handlers
        setupPanHandlers();
        
        // Set up controls
        prevBtn.addEventListener('click', () => navigate(-1));
        nextBtn.addEventListener('click', () => navigate(1));
        dualToggle.addEventListener('click', toggleDualMode);
        fullscreenToggle.addEventListener('click', toggleFullscreen);
        zoomInBtn.addEventListener('click', zoomIn);
        zoomOutBtn.addEventListener('click', zoomOut);
        zoomResetBtn.addEventListener('click', resetZoom);
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') navigate(-1);
            if (e.key === 'ArrowRight') navigate(1);
            if (e.key === '+' || e.key === '=') zoomIn();
            if (e.key === '-') zoomOut();
            if (e.key === '0') resetZoom();
            if (e.key === 'Escape' && isFullscreen) toggleFullscreen();
        });
        
        // Internal navigation by label
        function navigateToLabel(label) {
            console.log('navigateToLabel called with:', label);
            console.log('Available images:', images.map(img => getPageName(img)));
            
            // Try exact match first
            let idx = images.findIndex(img => getPageName(img) === label);
            
            // If no exact match, try with underscore/space normalization
            if (idx < 0) {
                const normalizedLabel = label.replace(/_/g, ' ');
                idx = images.findIndex(img => {
                    const name = getPageName(img);
                    return name === normalizedLabel || name.replace(/_/g, ' ') === normalizedLabel;
                });
            }
            
            // If still no match, try partial match
            if (idx < 0) {
                const normalizedLabel = label.replace(/_/g, ' ');
                idx = images.findIndex(img => {
                    const name = getPageName(img);
                    const normalizedName = name.replace(/_/g, ' ');
                    return normalizedName.includes(normalizedLabel) || name.includes(label);
                });
            }
            
            console.log('Found index:', idx);
            if (idx >= 0) {
                if (isDualMode) {
                    const spreads = getSpreads();
                    for (let s = 0; s < spreads.length; s++) {
                        if (spreads[s].includes(idx)) {
                            showSpread(s);
                            break;
                        }
                    }
                } else {
                    showSingle(idx);
                }
                return true;
            }
            return false;
        }
        
        // Expose goToPage globally for work linking
        window.goToViewerPage = function(pageIndex) {
            if (pageIndex < 0 || pageIndex >= images.length) return;
            if (isDualMode) {
                const spreads = getSpreads();
                for (let s = 0; s < spreads.length; s++) {
                    if (spreads[s].includes(pageIndex)) {
                        showSpread(s);
                        break;
                    }
                }
            } else {
                showSingle(pageIndex);
            }
        };
        
        // Override placeholder with real implementation
        window.goToViewerPageByLabel = function(label) {
            return navigateToLabel(label);
        };
        
        // Mark as ready and process any pending calls
        isReady = true;
        console.log('Page viewer ready, processing', pendingLabelNavigations.length, 'pending navigations');
        pendingLabelNavigations.forEach(label => navigateToLabel(label));
        pendingLabelNavigations = [];
        
        // =============================================
        // TEXT REGION SELECTION FEATURE
        // =============================================
        
        let isTextSelectMode = false;
        let selectionCanvas1 = null;
        let selectionCanvas2 = null;
        let hoveredRegion = null;
        let selectedRegions = [];  // Track multiple selected regions
        let selectedCanvases = []; // Track canvases for each selected region
        
        // Get regions for current page(s) from pagesData
        function getRegionsForPage(pageLabel) {
            if (!pagesData) return [];
            const page = pagesData.find(p => p.label === pageLabel || p.id === pageLabel);
            return page?.regions || [];
        }
        
        // Canvas resize functions (stored for external calls)
        let resizeCanvas1 = null;
        let resizeCanvas2 = null;
        
        // Create selection canvas overlay for an image container
        function createSelectionCanvas(container, imageElement, canvasId, resizeFnSetter) {
            let canvas = document.getElementById(canvasId);
            if (!canvas) {
                canvas = document.createElement('canvas');
                canvas.id = canvasId;
                canvas.className = 'pv-selection-canvas';
                container.style.position = 'relative';
                container.appendChild(canvas);
            }
            
            // Size and position canvas to match image exactly
            function resizeCanvas() {
                if (!imageElement.complete || imageElement.naturalWidth === 0) return;
                
                // Get image's actual rendered size (accounting for object-fit: contain)
                const naturalWidth = imageElement.naturalWidth;
                const naturalHeight = imageElement.naturalHeight;
                const elementWidth = imageElement.offsetWidth;
                const elementHeight = imageElement.offsetHeight;
                
                // Check if object-fit: contain is applied
                const computedStyle = window.getComputedStyle(imageElement);
                const objectFit = computedStyle.objectFit;
                
                let imgWidth, imgHeight, offsetX = 0, offsetY = 0;
                
                if (objectFit === 'contain') {
                    // Calculate actual rendered image dimensions
                    const naturalRatio = naturalWidth / naturalHeight;
                    const elementRatio = elementWidth / elementHeight;
                    
                    if (naturalRatio > elementRatio) {
                        // Image is wider - constrained by width
                        imgWidth = elementWidth;
                        imgHeight = elementWidth / naturalRatio;
                        offsetY = (elementHeight - imgHeight) / 2;
                    } else {
                        // Image is taller - constrained by height
                        imgHeight = elementHeight;
                        imgWidth = elementHeight * naturalRatio;
                        offsetX = (elementWidth - imgWidth) / 2;
                    }
                } else {
                    // No object-fit or object-fit: fill - use element dimensions
                    imgWidth = elementWidth;
                    imgHeight = elementHeight;
                }
                
                // Set canvas drawing buffer size
                canvas.width = imgWidth;
                canvas.height = imgHeight;
                
                // Set canvas display size
                canvas.style.width = imgWidth + 'px';
                canvas.style.height = imgHeight + 'px';
                
                // Position canvas exactly over image using offset properties
                // Account for any object-fit centering offset
                canvas.style.position = 'absolute';
                canvas.style.left = (imageElement.offsetLeft + offsetX) + 'px';
                canvas.style.top = (imageElement.offsetTop + offsetY) + 'px';
            }
            
            // Store resize function externally
            if (resizeFnSetter) resizeFnSetter(resizeCanvas);
            
            imageElement.addEventListener('load', () => {
                setTimeout(resizeCanvas, 10);
            });
            window.addEventListener('resize', resizeCanvas);
            setTimeout(resizeCanvas, 100);
            setTimeout(resizeCanvas, 500); // Extra delay for slow layouts
            
            return canvas;
        }
        
        // Resize all canvases (call when layout changes)
        function resizeAllCanvases() {
            setTimeout(() => {
                if (resizeCanvas1) resizeCanvas1();
                if (resizeCanvas2) resizeCanvas2();
            }, 50);
        }
        
        // Draw a single region (for hover effect)
        function drawHoveredRegion(canvas, region, skipClear = false) {
            const ctx = canvas.getContext('2d');
            if (!skipClear) {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
            }
            
            if (!isTextSelectMode || !region) return;
            
            const x = region.x * canvas.width;
            const y = region.y * canvas.height;
            const w = region.width * canvas.width;
            const h = region.height * canvas.height;
            
            ctx.strokeStyle = 'rgba(59, 130, 246, 0.8)';
            ctx.lineWidth = 2;
            ctx.strokeRect(x, y, w, h);
            
            ctx.fillStyle = 'rgba(59, 130, 246, 0.15)';
            ctx.fillRect(x, y, w, h);
        }
        
        // Find which region the mouse is over
        function findRegionAtPoint(pageLabel, normX, normY) {
            const regions = getRegionsForPage(pageLabel);
            return regions.find(region => {
                return normX >= region.x && normX <= region.x + region.width &&
                       normY >= region.y && normY <= region.y + region.height;
            });
        }
        
        // Cache for actual work titles from work.json
        const workTitleCache = {};
        
        // Fetch actual work title from work.json
        async function fetchWorkTitle(workId) {
            if (!workId) return null;
            if (workTitleCache[workId]) return workTitleCache[workId];
            
            try {
                const response = await fetch(`../../../../works/${workId}/work.json`);
                if (response.ok) {
                    const data = await response.json();
                    workTitleCache[workId] = data.title || workId;
                    return workTitleCache[workId];
                }
            } catch (e) {
                // Fall back to workId
            }
            workTitleCache[workId] = workId;
            return workId;
        }
        
        // Find work title by workId from pagesData (localized, used as fallback)
        function findWorkTitle(workId) {
            if (!pagesData || !workId) return null;
            for (const page of pagesData) {
                if (page.works) {
                    for (const work of page.works) {
                        if (work.id === workId) return work.title;
                        if (work.subworks) {
                            for (const sub of work.subworks) {
                                if (sub.id === workId) return sub.title;
                            }
                        }
                    }
                }
            }
            return null;
        }
        
        // Get all regions for a specific workId, sorted by page then region order
        function getAllRegionsForWork(workId) {
            if (!pagesData || !workId) return [];
            const result = [];
            for (const page of pagesData) {
                if (page.regions) {
                    for (const region of page.regions) {
                        if (region.workId === workId) {
                            result.push({
                                ...region,
                                pageLabel: page.label || page.id
                            });
                        }
                    }
                }
            }
            return result;
        }
        
        // Show full work popup with all regions concatenated - simulates clicking all regions
        async function showFullWorkPopup(workId) {
            // Clear current selection
            closeTranscriptionPopup();
            selectedRegions.length = 0;
            selectedCanvases.length = 0;
            
            // Find all regions for this work with their canvases
            if (!pagesData || !workId) return;
            
            for (const page of pagesData) {
                if (page.regions) {
                    const pageLabel = page.label || page.id;
                    page.regions.forEach((region, regionIndex) => {
                        if (region.workId === workId) {
                            // Find the canvas for this page by checking the two selection canvases
                            let canvas = null;
                            if (selectionCanvas1 && selectionCanvas1.dataset.pageLabel === pageLabel) {
                                canvas = selectionCanvas1;
                            } else if (selectionCanvas2 && selectionCanvas2.dataset.pageLabel === pageLabel) {
                                canvas = selectionCanvas2;
                            }
                            selectedRegions.push({ region, canvas, pageLabel, index: regionIndex });
                            if (canvas && !selectedCanvases.includes(canvas)) selectedCanvases.push(canvas);
                        }
                    });
                }
            }
            
            if (selectedRegions.length === 0) return;
            
            // Sort by page label then region index
            selectedRegions.sort((a, b) => {
                if (a.pageLabel !== b.pageLabel) return a.pageLabel.localeCompare(b.pageLabel);
                return a.index - b.index;
            });
            
            // Use the normal popup code
            updateTranscriptionPopup();
            drawAllSelectedRegions();
        }
        
        // Get region index within its page
        function getRegionIndex(pageLabel, region) {
            const regions = getRegionsForPage(pageLabel);
            return regions.indexOf(region);
        }
        
        // Make popup draggable
        let popupDragState = { isDragging: false, startX: 0, startY: 0, initialX: 0, initialY: 0, popup: null };
        
        // Global drag handlers (added once)
        document.addEventListener('mousemove', (e) => {
            if (!popupDragState.isDragging || !popupDragState.popup) return;
            const dx = e.clientX - popupDragState.startX;
            const dy = e.clientY - popupDragState.startY;
            popupDragState.popup.style.left = (popupDragState.initialX + dx) + 'px';
            popupDragState.popup.style.top = (popupDragState.initialY + dy) + 'px';
        });
        
        document.addEventListener('mouseup', () => {
            popupDragState.isDragging = false;
        });
        
        function makePopupDraggable(popup) {
            const header = popup.querySelector('.pv-popup-header');
            if (!header) return;
            
            header.style.cursor = 'move';
            
            header.addEventListener('mousedown', (e) => {
                if (e.target.classList.contains('pv-popup-close')) return;
                popupDragState.isDragging = true;
                popupDragState.popup = popup;
                popupDragState.startX = e.clientX;
                popupDragState.startY = e.clientY;
                const rect = popup.getBoundingClientRect();
                popupDragState.initialX = rect.left;
                popupDragState.initialY = rect.top;
                popup.style.transform = 'none';
                popup.style.left = popupDragState.initialX + 'px';
                popup.style.top = popupDragState.initialY + 'px';
            });
        }
        
        // Show transcription popup (or add to existing)
        function showTranscriptionPopup(region, canvas, pageLabel) {
            if (!region) return;
            
            // Check if this region is already selected
            const existingIndex = selectedRegions.findIndex(r => 
                r.region === region || (r.region.x === region.x && r.region.y === region.y && r.pageLabel === pageLabel)
            );
            
            if (existingIndex !== -1) {
                // Deselect this region
                selectedRegions.splice(existingIndex, 1);
                selectedCanvases.splice(existingIndex, 1);
                
                if (selectedRegions.length === 0) {
                    // No more regions - close popup
                    closeTranscriptionPopup();
                } else {
                    // Update popup and redraw
                    updateTranscriptionPopup();
                    drawAllSelectedRegions();
                }
                return;
            }
            
            // Add to selected regions
            const regionIndex = getRegionIndex(pageLabel, region);
            selectedRegions.push({ region, canvas, pageLabel, index: regionIndex });
            selectedCanvases.push(canvas);
            
            // Sort by page label then region index (work grouping is incidental)
            selectedRegions.sort((a, b) => {
                if (a.pageLabel !== b.pageLabel) return a.pageLabel.localeCompare(b.pageLabel);
                return a.index - b.index;
            });
            
            // Rebuild popup content
            updateTranscriptionPopup();
            
            // Draw blue boxes on all selected regions
            drawAllSelectedRegions();
        }
        
        // Draw blue boxes for all selected regions
        function drawAllSelectedRegions() {
            // Clear all canvases first
            [selectionCanvas1, selectionCanvas2].forEach(canvas => {
                if (canvas) {
                    const ctx = canvas.getContext('2d');
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                }
            });
            
            // Draw each selected region on its current canvas (by matching pageLabel)
            selectedRegions.forEach(({ region, pageLabel }) => {
                // Find the canvas currently showing this page
                let canvas = null;
                if (selectionCanvas1 && selectionCanvas1.dataset.pageLabel === pageLabel) {
                    canvas = selectionCanvas1;
                } else if (selectionCanvas2 && selectionCanvas2.dataset.pageLabel === pageLabel) {
                    canvas = selectionCanvas2;
                }
                
                if (!canvas) return; // Page not currently visible
                const ctx = canvas.getContext('2d');
                
                const x = region.x * canvas.width;
                const y = region.y * canvas.height;
                const w = region.width * canvas.width;
                const h = region.height * canvas.height;
                
                ctx.strokeStyle = 'rgba(59, 130, 246, 0.8)';
                ctx.lineWidth = 2;
                ctx.strokeRect(x, y, w, h);
                ctx.fillStyle = 'rgba(59, 130, 246, 0.15)';
                ctx.fillRect(x, y, w, h);
            });
        }
        
        // Update or create popup with all selected regions
        async function updateTranscriptionPopup() {
            let popup = document.getElementById('pv-transcription-popup');
            const isNew = !popup;
            
            if (isNew) {
                popup = document.createElement('div');
                popup.id = 'pv-transcription-popup';
                popup.className = 'pv-transcription-popup';
                document.body.appendChild(popup);
            }
            
            // Collect all unique workIds and fetch their titles
            const workIds = [...new Set(selectedRegions.map(r => r.region.workId).filter(Boolean))];
            await Promise.all(workIds.map(id => fetchWorkTitle(id)));
            
            // Build header
            let headerTitle = 'Transcription';
            if (selectedRegions.length === 1) {
                const { region } = selectedRegions[0];
                if (region.workId) {
                    const localizedTitle = findWorkTitle(region.workId) || region.workId;
                    const actualTitle = workTitleCache[region.workId] || region.workId;
                    const workLinkUrl = `../../../../works/${region.workId}/`;
                    headerTitle = `${escapeHtmlPV(localizedTitle)} (<a href="${workLinkUrl}" target="_blank" class="pv-header-link">${escapeHtmlPV(actualTitle)}</a>)`;
                    if (region.title) {
                        headerTitle += ` <span class="pv-region-subtitle">· ${escapeHtmlPV(region.title)}</span>`;
                    }
                } else if (region.title) {
                    headerTitle = escapeHtmlPV(region.title);
                }
            } else {
                headerTitle = `${selectedRegions.length} Regions`;
            }
            
            // Build regions content - group by work if multiple works
            let regionsHtml = '';
            
            if (selectedRegions.length > 1) {
                // Check if there are multiple different works
                const hasMultipleWorks = workIds.length > 1 || (workIds.length === 1);
                
                if (hasMultipleWorks) {
                    // Group by work
                    let currentWorkId = null;
                    let isFirstOfWork = false;
                    selectedRegions.forEach(({ region }) => {
                        const workId = region.workId || '';
                        let workCaptionHtml = '';
                        if (workId !== currentWorkId) {
                            currentWorkId = workId;
                            isFirstOfWork = true;
                            const workTitle = workId ? (workTitleCache[workId] || workId) : 'Unassigned';
                            const workLinkUrl = workId ? `../../../../works/${workId}/` : '';
                            const captionContent = workLinkUrl 
                                ? `<a href="${workLinkUrl}" target="_blank">${escapeHtmlPV(workTitle)}</a>`
                                : escapeHtmlPV(workTitle);
                            workCaptionHtml = `<span class="pv-work-caption">${captionContent}</span>`;
                        } else {
                            isFirstOfWork = false;
                        }
                        const titleHtml = region.title ? `<span class="pv-region-title-corner">${escapeHtmlPV(region.title)}</span>` : '';
                        regionsHtml += `<div class="pv-popup-region">${workCaptionHtml}${titleHtml}<div class="pv-region-content">${region.text || region.content || '<em>No transcription</em>'}</div></div>`;
                    });
                } else {
                    // No works - just show regions with titles
                    regionsHtml = selectedRegions.map(({ region }) => {
                        const titleHtml = region.title ? `<span class="pv-region-title-corner">${escapeHtmlPV(region.title)}</span>` : '';
                        return `<div class="pv-popup-region">${titleHtml}<div class="pv-region-content">${region.text || region.content || '<em>No transcription</em>'}</div></div>`;
                    }).join('');
                }
            } else {
                // Single region - show with title if present
                const { region } = selectedRegions[0];
                const titleHtml = region.title ? `<span class="pv-region-title-corner">${escapeHtmlPV(region.title)}</span>` : '';
                regionsHtml = `<div class="pv-popup-region">${titleHtml}<div class="pv-region-content">${region.text || region.content || '<em>No transcription</em>'}</div></div>`;
            }
            
            // Build work link if single region with work
            let workLink = '';
            if (selectedRegions.length === 1) {
                const { region } = selectedRegions[0];
                if (region.workId) {
                    const allRegions = getAllRegionsForWork(region.workId);
                    if (allRegions.length > 1) {
                        workLink = `<button class="pv-view-fullwork" onclick="window.pvShowFullWork('${region.workId}')">View full work (${allRegions.length} regions)</button>`;
                    }
                }
            }
            
            popup.innerHTML = `
                <div class="pv-popup-header">
                    <h4>${headerTitle}</h4>
                    <button class="pv-popup-close" onclick="window.pvClosePopup && window.pvClosePopup()">&times;</button>
                </div>
                <div class="pv-popup-content">
                    ${regionsHtml}
                    ${workLink}
                </div>
            `;
            
            // Always reattach drag handlers after innerHTML update
            makePopupDraggable(popup);
            
            // Process text for dictionary feature
            pvProcessTextForDictionary(popup);
        }
        
        // Expose full work view globally
        window.pvShowFullWork = showFullWorkPopup;
        
        function closeTranscriptionPopup() {
            const existing = document.getElementById('pv-transcription-popup');
            if (existing) existing.remove();
            
            // Clear all selection highlights
            [selectionCanvas1, selectionCanvas2].forEach(canvas => {
                if (canvas) {
                    const ctx = canvas.getContext('2d');
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                }
            });
            selectedRegions = [];
            selectedCanvases = [];
        }
        
        // Expose close function globally for the close button
        window.pvClosePopup = closeTranscriptionPopup;
        
        function escapeHtmlPV(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        // Setup hover and click handlers for a canvas
        function setupSelectionHandlers(canvas, imageElement) {
            canvas.addEventListener('mousemove', (e) => {
                if (!isTextSelectMode) {
                    canvas.style.cursor = 'default';
                    return;
                }
                
                const rect = canvas.getBoundingClientRect();
                const normX = (e.clientX - rect.left) / rect.width;
                const normY = (e.clientY - rect.top) / rect.height;
                
                const pageLabel = canvas.dataset.pageLabel;
                const region = findRegionAtPoint(pageLabel, normX, normY);
                
                // If we have selected regions, keep them highlighted but still show hover
                if (selectedRegions.length > 0) {
                    const isSelected = selectedRegions.some(r => r.region === region);
                    if (region && !isSelected && region !== hoveredRegion) {
                        hoveredRegion = region;
                        // Redraw selected + add hover on top
                        drawAllSelectedRegions();
                        drawHoveredRegion(canvas, region, true);
                    } else if (!region || isSelected) {
                        if (hoveredRegion) {
                            hoveredRegion = null;
                            drawAllSelectedRegions();
                        }
                    }
                    canvas.style.cursor = region ? 'pointer' : 'default';
                    return;
                }
                
                if (region !== hoveredRegion) {
                    hoveredRegion = region;
                    drawHoveredRegion(canvas, region);
                }
                
                canvas.style.cursor = region ? 'pointer' : 'default';
            });
            
            canvas.addEventListener('click', (e) => {
                if (!isTextSelectMode) return;
                e.preventDefault();
                e.stopPropagation();
                
                const rect = canvas.getBoundingClientRect();
                const normX = (e.clientX - rect.left) / rect.width;
                const normY = (e.clientY - rect.top) / rect.height;
                
                const pageLabel = canvas.dataset.pageLabel;
                const region = findRegionAtPoint(pageLabel, normX, normY);
                
                if (region) {
                    showTranscriptionPopup(region, canvas, pageLabel);
                }
            });
            
            canvas.addEventListener('mouseleave', () => {
                // Don't clear if popup is open
                if (selectedRegion) return;
                
                hoveredRegion = null;
                const ctx = canvas.getContext('2d');
                ctx.clearRect(0, 0, canvas.width, canvas.height);
            });
        }
        
        // Toggle text selection mode
        function toggleTextSelectMode() {
            isTextSelectMode = !isTextSelectMode;
            
            const btn = document.getElementById('pv-text-select-toggle');
            if (btn) {
                btn.classList.toggle('active', isTextSelectMode);
                btn.textContent = isTextSelectMode ? 'Text Select (On)' : 'Text Select';
            }
            
            // Update canvas visibility
            if (selectionCanvas1) {
                selectionCanvas1.style.display = isTextSelectMode ? 'block' : 'none';
                selectionCanvas1.style.pointerEvents = isTextSelectMode ? 'auto' : 'none';
                const ctx = selectionCanvas1.getContext('2d');
                ctx.clearRect(0, 0, selectionCanvas1.width, selectionCanvas1.height);
            }
            if (selectionCanvas2) {
                selectionCanvas2.style.display = isTextSelectMode ? 'block' : 'none';
                selectionCanvas2.style.pointerEvents = isTextSelectMode ? 'auto' : 'none';
                const ctx = selectionCanvas2.getContext('2d');
                ctx.clearRect(0, 0, selectionCanvas2.width, selectionCanvas2.height);
            }
            
            // Close any open popup when disabling
            if (!isTextSelectMode) {
                closeTranscriptionPopup();
            } else {
                // Resize canvases when enabling text select mode
                resizeAllCanvases();
            }
        }
        
        // Check if any pages have regions
        function hasAnyRegions() {
            if (!pagesData) return false;
            return pagesData.some(p => p.regions && p.regions.length > 0);
        }
        
        // Always add text select button (shows regions if any exist)
        const textSelectBtn = document.createElement('button');
        textSelectBtn.id = 'pv-text-select-toggle';
        textSelectBtn.className = 'pv-view-toggle';
        textSelectBtn.textContent = 'Text Select';
        textSelectBtn.title = 'Toggle text selection mode';
        textSelectBtn.addEventListener('click', toggleTextSelectMode);
        
        // Insert before dual toggle
        dualToggle.parentNode.insertBefore(textSelectBtn, dualToggle);
        
        // =============================================
        // TRANSCRIPTION MODE - Shows all text without images
        // =============================================
        
        // Create transcription panel
        function createTranscriptionPanel() {
            const panel = document.createElement('div');
            panel.id = 'pv-transcription-panel';
            panel.className = 'pv-transcription-panel';
            panel.style.display = 'none';
            
            // Insert after the main container
            mainContainer.parentNode.insertBefore(panel, mainContainer.nextSibling);
            
            return panel;
        }
        
        // Get regions for the current page(s) only
        function getCurrentPageRegions() {
            if (!pagesData) return [];
            const result = [];
            
            // Get actual page indices based on mode
            let pageIndices = [];
            if (isDualMode) {
                // In dual mode, currentIndex is the spread index, not the page index
                const spreads = getSpreads();
                if (currentIndex >= 0 && currentIndex < spreads.length) {
                    pageIndices = spreads[currentIndex];  // Array of 1 or 2 page indices
                }
            } else {
                // In single mode, currentIndex is the actual page index
                pageIndices = [currentIndex];
            }
            
            // For each visible page index, find the matching pagesData entry by label
            for (const idx of pageIndices) {
                if (idx < 0 || idx >= images.length) continue;
                
                // Get the label of the currently displayed image
                const currentImage = images[idx];
                const currentLabel = typeof currentImage === 'object' ? currentImage.label : getPageName(currentImage);
                
                // Find the pagesData entry with matching label
                const page = pagesData.find(p => {
                    const pageLabel = p.label || p.id || '';
                    return pageLabel === currentLabel;
                });
                
                if (page && page.regions && page.regions.length > 0) {
                    for (const region of page.regions) {
                        result.push({
                            ...region,
                            pageLabel: page.label || page.id
                        });
                    }
                }
            }
            return result;
        }
        
        // Populate transcription panel with text from current page(s)
        async function populateTranscriptionPanel() {
            if (!transcriptionPanel) return;
            
            const allRegions = getCurrentPageRegions();
            
            if (allRegions.length === 0) {
                transcriptionPanel.innerHTML = `
                    <div class="pv-transcription-empty">
                        <p>No transcription regions available for this text.</p>
                    </div>
                `;
                return;
            }
            
            // Collect all unique workIds and fetch their titles
            const workIds = [...new Set(allRegions.map(r => r.workId).filter(Boolean))];
            await Promise.all(workIds.map(id => fetchWorkTitle(id)));
            
            // Build content grouped by work
            let html = '<div class="pv-transcription-content">';
            
            if (workIds.length > 0) {
                // Group by work
                let currentWorkId = null;
                allRegions.forEach((region) => {
                    const workId = region.workId || '';
                    let workCaptionHtml = '';
                    if (workId !== currentWorkId) {
                        currentWorkId = workId;
                        const workTitle = workId ? (workTitleCache[workId] || workId) : 'Unassigned';
                        const workLinkUrl = workId ? `../../../../works/${workId}/` : '';
                        const captionContent = workLinkUrl 
                            ? `<a href="${workLinkUrl}" target="_blank">${escapeHtmlPV(workTitle)}</a>`
                            : escapeHtmlPV(workTitle);
                        workCaptionHtml = `<span class="pv-work-caption">${captionContent}</span>`;
                    }
                    const titleHtml = region.title ? `<span class="pv-region-title-corner">${escapeHtmlPV(region.title)}</span>` : '';
                    html += `<div class="pv-popup-region">${workCaptionHtml}${titleHtml}<div class="pv-region-content">${region.text || region.content || '<em>No transcription</em>'}</div></div>`;
                });
            } else {
                // No works - just show regions with titles
                allRegions.forEach((region) => {
                    const titleHtml = region.title ? `<span class="pv-region-title-corner">${escapeHtmlPV(region.title)}</span>` : '';
                    html += `<div class="pv-popup-region">${titleHtml}<div class="pv-region-content">${region.text || region.content || '<em>No transcription</em>'}</div></div>`;
                });
            }
            
            html += '</div>';
            transcriptionPanel.innerHTML = html;
            
            // Process text for dictionary feature
            pvProcessTextForDictionary(transcriptionPanel);
        }
        
        // Make populateTranscriptionPanel accessible for page navigation
        refreshTranscriptionPanel = populateTranscriptionPanel;
        
        // Toggle transcription mode
        function toggleTranscriptionMode() {
            isTranscriptionMode = !isTranscriptionMode;
            
            const btn = document.getElementById('pv-transcription-toggle');
            if (btn) {
                btn.classList.toggle('active', isTranscriptionMode);
            }
            
            if (isTranscriptionMode) {
                // Hide image viewer components but keep thumbnails for navigation
                mainContainer.style.display = 'none';
                
                // Show transcription panel
                if (!transcriptionPanel) {
                    transcriptionPanel = createTranscriptionPanel();
                }
                transcriptionPanel.style.display = 'block';
                populateTranscriptionPanel();
                
                // Disable controls that don't apply (but keep nav buttons and thumbnails enabled)
                dualToggle.disabled = true;
                textSelectBtn.disabled = true;
                zoomInBtn.disabled = true;
                zoomOutBtn.disabled = true;
                zoomResetBtn.disabled = true;
            } else {
                // Show image viewer components
                mainContainer.style.display = '';
                thumbContainer.style.display = '';
                
                // Hide transcription panel
                if (transcriptionPanel) {
                    transcriptionPanel.style.display = 'none';
                }
                
                // Re-enable controls
                dualToggle.disabled = false;
                textSelectBtn.disabled = false;
                zoomInBtn.disabled = false;
                zoomOutBtn.disabled = false;
                zoomResetBtn.disabled = false;
                // Update nav buttons based on current state
                showImage(currentIndex);
            }
        }
        
        // Add transcription mode button
        const transcriptionBtn = document.createElement('button');
        transcriptionBtn.id = 'pv-transcription-toggle';
        transcriptionBtn.className = 'pv-view-toggle';
        transcriptionBtn.textContent = 'Transcription';
        transcriptionBtn.title = 'View full transcription';
        transcriptionBtn.addEventListener('click', toggleTranscriptionMode);
        
        // Insert after text select button
        textSelectBtn.parentNode.insertBefore(transcriptionBtn, textSelectBtn.nextSibling);
        
        // Create selection canvases for both image containers
        selectionCanvas1 = createSelectionCanvas(container1, mainImage, 'pv-selection-canvas-1', fn => resizeCanvas1 = fn);
        setupSelectionHandlers(selectionCanvas1, mainImage);
        selectionCanvas1.style.display = 'none';
        
        selectionCanvas2 = createSelectionCanvas(container2, mainImage2, 'pv-selection-canvas-2', fn => resizeCanvas2 = fn);
        setupSelectionHandlers(selectionCanvas2, mainImage2);
        selectionCanvas2.style.display = 'none';
        
        // Update canvas page labels when image changes
        const originalShowSingle = showSingle;
        showSingle = function(index) {
            originalShowSingle(index);
            if (selectionCanvas1) {
                selectionCanvas1.dataset.pageLabel = getPageName(images[index]);
            }
            resizeAllCanvases();
            // Redraw any selected regions on this page
            setTimeout(drawAllSelectedRegions, 50);
        };
        
        const originalShowSpread = showSpread;
        showSpread = function(spreadIndex) {
            originalShowSpread(spreadIndex);
            const spreads = getSpreads();
            const spread = spreads[spreadIndex];
            if (selectionCanvas1 && spread[0] !== undefined) {
                selectionCanvas1.dataset.pageLabel = getPageName(images[spread[0]]);
            }
            if (selectionCanvas2 && spread[1] !== undefined) {
                selectionCanvas2.dataset.pageLabel = getPageName(images[spread[1]]);
            }
            resizeAllCanvases();
            // Redraw any selected regions on these pages
            setTimeout(drawAllSelectedRegions, 50);
        };
        
        // Resize canvases when fullscreen or dual mode toggles
        fullscreenToggle.addEventListener('click', () => {
            setTimeout(resizeAllCanvases, 100);
            setTimeout(resizeAllCanvases, 300);
        });
        dualToggle.addEventListener('click', () => {
            setTimeout(resizeAllCanvases, 100);
            setTimeout(resizeAllCanvases, 300);
        });
        
        // =============================================
        // DICTIONARY FEATURE FOR POPUPS
        // Uses the existing dictionary-widget from text-reader.js
        // =============================================
        
        let pvPhraseCounter = 0;
        let pvPhraseOverlays = {};
        let pvDictInitialized = false;
        
        // Try to initialize the dictionary system
        function pvEnsureDictionary() {
            if (pvDictInitialized) return typeof window.addDictLookup === 'function';
            pvDictInitialized = true;
            
            // Try to initialize text-reader if not already done
            if (typeof window.addDictLookup !== 'function' && typeof window.initTextReader === 'function') {
                try {
                    window.initTextReader();
                } catch (e) {
                    console.warn('Failed to initialize text-reader:', e);
                }
            }
            
            return typeof window.addDictLookup === 'function';
        }
        
        // Process popup text to wrap words in clickable spans
        function pvProcessTextForDictionary(container) {
            if (!container) return;
            
            const regions = container.querySelectorAll('.pv-popup-region');
            let wordIndex = 0;
            
            regions.forEach(region => {
                // Don't process if already processed
                if (region.dataset.dictProcessed) return;
                region.dataset.dictProcessed = 'true';
                
                // Set position relative for phrase overlays
                region.style.position = 'relative';
                
                // Get all text nodes and wrap words
                const walker = document.createTreeWalker(region, NodeFilter.SHOW_TEXT, null, false);
                const textNodes = [];
                while (walker.nextNode()) {
                    textNodes.push(walker.currentNode);
                }
                
                textNodes.forEach(node => {
                    const text = node.textContent;
                    if (!text.trim()) return;
                    
                    // Skip if inside title corner or work caption (check ancestors, not just parent)
                    if (node.parentElement.closest('.pv-region-title-corner')) return;
                    if (node.parentElement.closest('.pv-work-caption')) return;
                    
                    // Match words (letters with optional internal apostrophes) vs everything else
                    const fragment = document.createDocumentFragment();
                    let lastIndex = 0;
                    
                    const wordRegex = /[\p{L}]+(?:[''][\p{L}]+)*/gu;
                    let match;
                    
                    while ((match = wordRegex.exec(text)) !== null) {
                        if (match.index > lastIndex) {
                            fragment.appendChild(document.createTextNode(text.slice(lastIndex, match.index)));
                        }
                        
                        const span = document.createElement('span');
                        span.className = 'pv-word';
                        span.textContent = match[0];
                        span.dataset.idx = wordIndex++;
                        fragment.appendChild(span);
                        
                        lastIndex = match.index + match[0].length;
                    }
                    
                    if (lastIndex < text.length) {
                        fragment.appendChild(document.createTextNode(text.slice(lastIndex)));
                    }
                    
                    node.parentNode.replaceChild(fragment, node);
                });
            });
            
            // Add word interaction handlers (only once per container)
            if (!container.pvHandlersAttached) {
                container.pvHandlersAttached = true;
                pvSetupWordHandlers(container);
            }
        }
        
        // Setup word click/drag handlers that trigger the existing dictionary widget
        function pvSetupWordHandlers(container) {
            let startWord = null;
            let isDragging = false;
            let dragPhraseId = null; // Phrase being created during current drag
            let wordInteractionActive = false; // Flag to prevent click-outside from firing during drag
            
            // Track all active selections for this container
            if (!container.pvSelectedWords) container.pvSelectedWords = new Set();
            if (!container.pvActivePhrases) container.pvActivePhrases = new Set();
            
            container.addEventListener('mousedown', e => {
                if (e.target.classList.contains('pv-word')) {
                    wordInteractionActive = true;
                    startWord = e.target;
                    isDragging = false;
                    dragPhraseId = null;
                    e.stopPropagation();
                }
            });
            
            container.addEventListener('mousemove', e => {
                if (!startWord || e.buttons !== 1) return;
                
                const endWord = e.target.classList.contains('pv-word') ? e.target : null;
                if (!endWord) return;
                
                const startIdx = parseInt(startWord.dataset.idx);
                const endIdx = parseInt(endWord.dataset.idx);
                
                if (startIdx !== endIdx) isDragging = true;
                if (!isDragging) return;
                
                const minIdx = Math.min(startIdx, endIdx);
                const maxIdx = Math.max(startIdx, endIdx);
                
                // Remove temporary drag phrase if exists (but not committed phrases)
                if (dragPhraseId !== null) {
                    pvRemovePhraseById(dragPhraseId, container);
                    container.pvActivePhrases.delete(dragPhraseId);
                }
                
                if (minIdx === maxIdx) {
                    dragPhraseId = null;
                    return;
                }
                
                // Create new temporary phrase for drag preview
                dragPhraseId = ++pvPhraseCounter;
                
                const words = container.querySelectorAll('.pv-word');
                for (let i = minIdx; i <= maxIdx; i++) {
                    if (words[i]) {
                        words[i].classList.add('phrase-word');
                        words[i].dataset.phrase = dragPhraseId;
                    }
                }
                
                pvCreatePhraseOverlay(dragPhraseId, container);
            });
            
            container.addEventListener('mouseup', e => {
                if (startWord && !isDragging) {
                    // Single click on a word
                    const existingPhraseId = startWord.dataset.phrase;
                    if (existingPhraseId) {
                        // Click on phrase word - remove that phrase
                        pvRemovePhraseById(existingPhraseId, container);
                        container.pvActivePhrases.delete(parseInt(existingPhraseId));
                    } else {
                        // Toggle individual word selection
                        const wasSelected = startWord.classList.contains('selected');
                        if (wasSelected) {
                            startWord.classList.remove('selected');
                            container.pvSelectedWords.delete(startWord);
                        } else {
                            startWord.classList.add('selected');
                            container.pvSelectedWords.add(startWord);
                            pvTriggerDictLookup(startWord.textContent.trim());
                        }
                    }
                } else if (isDragging && dragPhraseId !== null) {
                    // Phrase drag complete - commit this phrase and trigger lookup
                    container.pvActivePhrases.add(dragPhraseId);
                    
                    const phraseWords = Array.from(container.querySelectorAll(`.pv-word[data-phrase="${dragPhraseId}"]`))
                        .map(w => w.textContent.trim());
                    if (phraseWords.length > 0) {
                        pvTriggerDictLookup(phraseWords.join(' '));
                    }
                }
                
                startWord = null;
                isDragging = false;
                dragPhraseId = null;
                // Reset word interaction flag after a short delay to prevent click handler from clearing
                setTimeout(() => { wordInteractionActive = false; }, 50);
            });
            
            // Click outside words clears all selections and dictionary
            container.addEventListener('click', e => {
                // Don't clear during word interaction (flag set during drag)
                if (wordInteractionActive) return;
                // If clicking on a word, pv-phrase-overlay, or dictionary widget - don't clear
                if (e.target.classList.contains('pv-word')) return;
                if (e.target.classList.contains('pv-phrase-overlay')) return;
                if (e.target.closest('.dictionary-widget')) return;
                
                // Clear all word selections
                container.querySelectorAll('.pv-word.selected').forEach(w => {
                    w.classList.remove('selected');
                });
                container.pvSelectedWords.clear();
                
                // Clear all phrases
                container.pvActivePhrases.forEach(phraseId => {
                    pvRemovePhraseById(phraseId, container);
                });
                container.pvActivePhrases.clear();
                
                // Clear dictionary widget
                if (typeof window.clearAllDictLookups === 'function') {
                    window.clearAllDictLookups();
                }
            });
        }
        
        // Clean word for dictionary lookup
        function pvCleanWord(word) {
            // Small caps Unicode → regular lowercase
            const smallCapsMap = {
                'ᴀ': 'a', 'ʙ': 'b', 'ᴄ': 'c', 'ᴅ': 'd', 'ᴇ': 'e', 'ꜰ': 'f',
                'ɢ': 'g', 'ʜ': 'h', 'ɪ': 'i', 'ᴊ': 'j', 'ᴋ': 'k', 'ʟ': 'l',
                'ᴍ': 'm', 'ɴ': 'n', 'ᴏ': 'o', 'ᴘ': 'p', 'ʀ': 'r', 'ꜱ': 's',
                'ᴛ': 't', 'ᴜ': 'u', 'ᴠ': 'v', 'ᴡ': 'w', 'ʏ': 'y', 'ᴢ': 'z'
            };
            let result = word;
            for (const [sc, reg] of Object.entries(smallCapsMap)) {
                result = result.replace(new RegExp(sc, 'g'), reg);
            }
            return result
                .replace(/[.,!?;:""\"()[\]{}·•‧∙«»‹›„"‟'‚]/g, '')
                .replace(/['']/g, "'")
                .replace(/ſ/g, 's')
                .replace(/ƿ/g, 'w')
                .replace(/Ƿ/g, 'W')
                .replace(/^'+|'+$/g, '')
                .trim();
        }
        
        // Trigger dictionary lookup using the existing text-reader.js dictionary widget
        function pvTriggerDictLookup(text) {
            const cleanText = pvCleanWord(text);
            if (!cleanText || !/[\p{L}]/u.test(cleanText)) return;
            
            // Ensure dictionary is available
            const dictAvailable = pvEnsureDictionary();
            
            if (dictAvailable) {
                // Use text-reader's dictionary
                const id = 'pv-' + cleanText.toLowerCase().replace(/\s+/g, '-');
                window.addDictLookup([cleanText], id, null);
            } else {
                // Dictionary not available - show inline definition popup as fallback
                pvShowInlineDictionary(cleanText);
            }
        }
        
        // Fallback inline dictionary when text-reader's widget isn't available
        async function pvShowInlineDictionary(word) {
            // Check if we already have a popup dictionary
            let dictPopup = document.querySelector('.pv-dict-popup');
            if (!dictPopup) {
                dictPopup = document.createElement('div');
                dictPopup.className = 'pv-dict-popup';
                dictPopup.innerHTML = `
                    <div class="pv-dict-popup-header">
                        <span class="pv-dict-popup-title">Dictionary</span>
                        <button class="pv-dict-popup-close">×</button>
                    </div>
                    <div class="pv-dict-popup-tabs"></div>
                    <div class="pv-dict-popup-content">Loading...</div>
                `;
                document.body.appendChild(dictPopup);
                
                // Close button handler
                dictPopup.querySelector('.pv-dict-popup-close').addEventListener('click', () => {
                    dictPopup.classList.remove('visible');
                });
                
                // Add styles if not present
                if (!document.querySelector('#pv-dict-popup-styles')) {
                    const style = document.createElement('style');
                    style.id = 'pv-dict-popup-styles';
                    style.textContent = `
                        .pv-dict-popup {
                            display: none;
                            position: fixed;
                            top: 50%;
                            right: 20px;
                            transform: translateY(-50%);
                            width: 350px;
                            max-height: 70vh;
                            background: white;
                            border: 1px solid #ddd;
                            border-radius: 0;
                            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
                            z-index: 100000;
                            overflow: hidden;
                            font-family: system-ui, sans-serif;
                        }
                        .pv-dict-popup.visible { display: block; }
                        .pv-dict-popup-header {
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            padding: 10px 15px;
                            background: #f5f5f5;
                            border-bottom: 1px solid #ddd;
                        }
                        .pv-dict-popup-title { font-weight: 600; }
                        .pv-dict-popup-close {
                            background: none;
                            border: none;
                            font-size: 20px;
                            cursor: pointer;
                            color: #666;
                        }
                        .pv-dict-popup-tabs {
                            display: flex;
                            flex-wrap: wrap;
                            gap: 5px;
                            padding: 8px;
                            border-bottom: 1px solid #eee;
                            background: #fafafa;
                        }
                        .pv-dict-popup-tab {
                            padding: 4px 10px;
                            background: #e5e5e5;
                            border: none;
                            border-radius: 0;
                            cursor: pointer;
                            font-size: 13px;
                        }
                        .pv-dict-popup-tab.active { background: #3b82f6; color: white; }
                        .pv-dict-popup-content {
                            padding: 15px;
                            overflow-y: auto;
                            max-height: calc(70vh - 100px);
                            font-size: 14px;
                            line-height: 1.5;
                        }
                        .pv-dict-popup-content .pv-dict-lang { 
                            font-weight: 600; 
                            margin-top: 10px; 
                            padding-bottom: 5px;
                            border-bottom: 1px solid #eee;
                        }
                        .pv-dict-popup-content .pv-dict-pos { 
                            font-style: italic; 
                            color: #666; 
                            margin: 8px 0 4px;
                        }
                        .pv-dict-popup-content .pv-dict-def { margin: 4px 0 4px 15px; }
                        .pv-dict-popup-content .pv-dict-error { color: #e53e3e; }
                    `;
                    document.head.appendChild(style);
                }
            }
            
            // Show popup
            dictPopup.classList.add('visible');
            const tabsEl = dictPopup.querySelector('.pv-dict-popup-tabs');
            const contentEl = dictPopup.querySelector('.pv-dict-popup-content');
            
            // Add tab for this word
            const existingTab = tabsEl.querySelector(`[data-word="${word.toLowerCase()}"]`);
            if (!existingTab) {
                tabsEl.querySelectorAll('.pv-dict-popup-tab').forEach(t => t.classList.remove('active'));
                const tab = document.createElement('button');
                tab.className = 'pv-dict-popup-tab active';
                tab.dataset.word = word.toLowerCase();
                tab.textContent = word;
                tab.addEventListener('click', () => {
                    tabsEl.querySelectorAll('.pv-dict-popup-tab').forEach(t => t.classList.remove('active'));
                    tab.classList.add('active');
                    pvFetchDefinition(word, contentEl);
                });
                tabsEl.appendChild(tab);
            } else {
                tabsEl.querySelectorAll('.pv-dict-popup-tab').forEach(t => t.classList.remove('active'));
                existingTab.classList.add('active');
            }
            
            // Fetch definition
            pvFetchDefinition(word, contentEl);
        }
        
        // Remove accents for dictionary lookup
        function pvStripAccents(str) {
            return str.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
        }
        
        // Fetch and display a Wiktionary definition
        async function pvFetchDefinition(word, contentEl) {
            contentEl.innerHTML = '<div>Loading...</div>';
            
            const lowerWord = word.toLowerCase();
            const plainWord = pvStripAccents(lowerWord);
            const capitalWord = lowerWord.charAt(0).toUpperCase() + lowerWord.slice(1);
            
            // Try variations
            const variations = [word, lowerWord, capitalWord];
            if (plainWord !== lowerWord) {
                variations.push(plainWord);
                variations.push(pvStripAccents(capitalWord));
            }
            
            for (const variant of variations) {
                try {
                    const url = `https://en.wiktionary.org/w/api.php?action=parse&page=${encodeURIComponent(variant)}&prop=text&format=json&origin=*`;
                    const resp = await fetch(url);
                    const data = await resp.json();
                    
                    if (data.parse && data.parse.text) {
                        const html = data.parse.text['*'];
                        const formatted = pvParseWiktionaryHtml(html, variant);
                        if (formatted && !formatted.includes('pv-dict-error')) {
                            contentEl.innerHTML = `<h3 style="margin:0 0 10px">${variant}</h3>${formatted}`;
                            return;
                        }
                    }
                } catch (e) {
                    console.warn('Wiktionary fetch error:', e);
                }
            }
            
            contentEl.innerHTML = `<div class="pv-dict-error">No definition found for "${word}"</div>`;
        }
        
        // Parse Wiktionary HTML to extract definitions
        function pvParseWiktionaryHtml(rawHtml, word) {
            const parser = new DOMParser();
            const doc = parser.parseFromString(rawHtml, 'text/html');
            
            // Find all h2 language headers
            const allH2s = doc.querySelectorAll('h2');
            let resultHtml = '';
            
            for (const h2 of allH2s) {
                const headline = h2.querySelector('.mw-headline');
                const langName = headline ? headline.textContent.trim() : h2.textContent.trim();
                
                if (!langName || ['Contents', 'See also', 'External links', 'Navigation menu'].includes(langName)) continue;
                
                let currentEl = h2.nextElementSibling;
                let sectionHtml = '';
                let hasDefinitions = false;
                
                while (currentEl && currentEl.tagName !== 'H2') {
                    if (currentEl.tagName === 'H3') {
                        const posHeadline = currentEl.querySelector('.mw-headline');
                        const pos = posHeadline ? posHeadline.textContent.trim() : currentEl.textContent.trim();
                        if (pos && !['Etymology', 'Pronunciation', 'References', 'Further reading'].includes(pos)) {
                            sectionHtml += `<div class="pv-dict-pos">${pos}</div>`;
                        }
                    }
                    
                    if (currentEl.tagName === 'OL') {
                        const items = currentEl.querySelectorAll(':scope > li');
                        items.forEach((li, idx) => {
                            const clone = li.cloneNode(true);
                            clone.querySelectorAll('ul, ol, dl, .h-usage-example').forEach(el => el.remove());
                            let text = clone.textContent.trim().replace(/\[\d+\]/g, '').replace(/\s+/g, ' ');
                            if (text && text.length > 1 && text.length < 500) {
                                hasDefinitions = true;
                                sectionHtml += `<div class="pv-dict-def">${idx + 1}. ${text}</div>`;
                            }
                        });
                    }
                    
                    currentEl = currentEl.nextElementSibling;
                }
                
                if (hasDefinitions) {
                    resultHtml += `<div class="pv-dict-lang">${langName}</div>${sectionHtml}`;
                }
            }
            
            return resultHtml || '<div class="pv-dict-error">No definitions found</div>';
        }
        
        // Create phrase overlay box
        function pvCreatePhraseOverlay(phraseId, container) {
            const words = container.querySelectorAll(`.pv-word[data-phrase="${phraseId}"]`);
            if (words.length === 0) return;
            
            pvPhraseOverlays[phraseId] = [];
            
            const firstWord = words[0];
            const region = firstWord.closest('.pv-popup-region');
            if (!region) return;
            
            // Helper to get offset relative to region
            function getOffsetToRegion(el) {
                let top = 0, left = 0;
                let current = el;
                while (current && current !== region) {
                    top += current.offsetTop;
                    left += current.offsetLeft;
                    current = current.offsetParent;
                }
                return { top, left };
            }
            
            // Group words by line (same offsetTop relative to region)
            const lines = {};
            words.forEach(w => {
                const offset = getOffsetToRegion(w);
                const lineKey = Math.round(offset.top);
                if (!lines[lineKey]) lines[lineKey] = [];
                lines[lineKey].push({ el: w, offset, width: w.offsetWidth, height: w.offsetHeight });
            });
            
            Object.values(lines).forEach(lineWords => {
                // Sort by left position
                lineWords.sort((a, b) => a.offset.left - b.offset.left);
                
                const first = lineWords[0];
                const last = lineWords[lineWords.length - 1];
                
                const overlay = document.createElement('div');
                overlay.className = 'pv-phrase-overlay';
                overlay.dataset.phrase = phraseId;
                
                const left = first.offset.left - 2;
                const top = first.offset.top - 2;
                const width = (last.offset.left + last.width) - first.offset.left + 4;
                const height = first.height + 4;
                
                overlay.style.cssText = `left:${left}px; top:${top}px; width:${width}px; height:${height}px;`;
                
                region.appendChild(overlay);
                pvPhraseOverlays[phraseId].push(overlay);
            });
        }
        
        // Remove phrase by ID
        function pvRemovePhraseById(phraseId, container) {
            container.querySelectorAll(`.pv-word[data-phrase="${phraseId}"]`).forEach(w => {
                w.classList.remove('phrase-word');
                delete w.dataset.phrase;
            });
            if (pvPhraseOverlays[phraseId]) {
                pvPhraseOverlays[phraseId].forEach(el => el.remove());
                delete pvPhraseOverlays[phraseId];
            }
        }
        
        // Expose dictionary text processing
        window.pvProcessTextForDictionary = pvProcessTextForDictionary;
        
        showImage(0);
    });
}
