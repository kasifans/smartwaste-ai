// ─── MAP SETUP ───
const map = L.map('map').setView([28.5850, 77.3150], 13);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap'
}).addTo(map);

let markers = {};
let routeLayer = null;

function getFillColor(fill) {
    if (fill >= 80) return '#ef4444';
    if (fill >= 60) return '#f59e0b';
    return '#10b981';
}

function createBinIcon(fill) {
    const color = getFillColor(fill);
    return L.divIcon({
        html: `<div style="background:${color};width:20px;height:20px;border-radius:50%;border:3px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.5);"></div>`,
        iconSize: [20, 20],
        className: ''
    });
}

function updateMapMarkers(bins) {
    // Clear old markers
    Object.values(markers).forEach(m => map.removeLayer(m));
    markers = {};

    bins.forEach(bin => {
        const fill = bin.fill_level;
        const status = fill >= 80 ? '🔴 CRITICAL' : fill >= 60 ? '🟡 HIGH' : '🟢 NORMAL';

        const marker = L.marker([bin.latitude, bin.longitude], {
            icon: createBinIcon(fill)
        })
        .addTo(map)
        .bindPopup(`
            <b>${bin.name}</b><br>
            ${bin.location}<br>
            Fill: <b>${fill}%</b><br>
            Status: ${status}
        `);

        markers[bin.id] = marker;
    });
}

function drawRoute(route) {
    if (routeLayer) map.removeLayer(routeLayer);
    const coords = route.map(stop => [stop.latitude, stop.longitude]);
    routeLayer = L.polyline(coords, {
        color: '#3b82f6',
        weight: 3,
        dashArray: '8,4'
    }).addTo(map);
    map.fitBounds(routeLayer.getBounds());
}