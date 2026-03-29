/**
 * Map initialization script for language pages
 * Uses Leaflet.js for interactive maps
 */

function initMap(elementId, latitude, longitude) {
    const container = document.getElementById(elementId);
    if (!container) return;
    
    // Create map centered on language location
    const map = L.map(elementId).setView([latitude, longitude], 6);
    
    // Add OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19,
        minZoom: 2
    }).addTo(map);
    
    // Add a marker at the language location
    L.circleMarker([latitude, longitude], {
        radius: 8,
        fillColor: '#B85A4F',
        color: '#8B4530',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.8
    }).addTo(map).bindPopup(`Location: ${latitude.toFixed(4)}°, ${longitude.toFixed(4)}°`);
    
    // Adjust map container height after content loads
    setTimeout(() => {
        map.invalidateSize();
    }, 100);
}
