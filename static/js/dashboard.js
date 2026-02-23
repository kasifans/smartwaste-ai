let alertsCount = 0;

// ─── LOAD BINS ───
async function loadBins() {
    const res = await fetch('/api/bins');
    const bins = await res.json();

    let html = '';
    let critical = 0;
    let totalFill = 0;

    // Clear bin select options except first
    const select = document.getElementById('bin-select');
    select.innerHTML = '<option value="">Select Bin...</option>';

    bins.forEach(bin => {
        const fill = bin.fill_level;
        totalFill += fill;
        if (fill >= 80) critical++;

        const cardClass = fill >= 80 ? 'critical' : fill >= 60 ? 'high' : '';
        const barColor = getFillColor(fill);
        const status = fill >= 80 ? '🔴 CRITICAL' : fill >= 60 ? '🟡 HIGH' : '🟢 NORMAL';

        html += `
            <div class="bin-card ${cardClass}">
                <div class="bin-header">
                    <div>
                        <div class="bin-name">${bin.name}</div>
                        <div class="bin-location">📍 ${bin.location}</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:18px;font-weight:bold;color:${barColor}">${fill}%</div>
                        <div style="font-size:11px;">${status}</div>
                    </div>
                </div>
                <div class="fill-bar-bg">
                    <div class="fill-bar" style="width:${fill}%;background:${barColor};"></div>
                </div>
                <div class="fill-info">
                    <span>Last updated: ${bin.last_updated || 'N/A'}</span>
                    <span>Bin ID: ${bin.id}</span>
                </div>
            </div>`;

        // Populate bin select
        const opt = document.createElement('option');
        opt.value = bin.id;
        opt.text = `${bin.name} — ${bin.location}`;
        select.appendChild(opt);
    });

    document.getElementById('bin-list').innerHTML = html;
    document.getElementById('critical-bins').textContent = critical;
    document.getElementById('avg-fill').textContent = Math.round(totalFill / bins.length) + '%';
    document.getElementById('last-updated').textContent = 'Updated: ' + new Date().toLocaleTimeString();

    // Update map markers
    updateMapMarkers(bins);
}

// ─── IMAGE PREVIEW ───
function previewImage(input) {
    const preview = document.getElementById('preview');
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = e => {
            preview.src = e.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// ─── DETECT FILL ───
async function detectFill() {
    const binId = document.getElementById('bin-select').value;
    const imageFile = document.getElementById('image-upload').files[0];

    if (!binId) { alert('Please select a bin'); return; }
    if (!imageFile) { alert('Please upload an image'); return; }

    const formData = new FormData();
    formData.append('bin_id', binId);
    formData.append('image', imageFile);

    const resultBox = document.getElementById('detect-result');
    resultBox.style.display = 'block';
    resultBox.innerHTML = '⏳ Analyzing image...';

    const res = await fetch('/api/detect', { method: 'POST', body: formData });
    const data = await res.json();

    resultBox.innerHTML = `
        <div style="color:${data.color}">● ${data.status}</div>
        <div style="font-size:18px;font-weight:bold;margin:5px 0;">${data.fill_level}% Full</div>
        <div style="color:#9ca3af;">${data.action}</div>
    `;

    loadBins();
}

// ─── SEND ALERT ───
async function sendAlert() {
    const res = await fetch('/api/alert', { method: 'POST' });
    const data = await res.json();
    alertsCount += data.alerts_sent;
    document.getElementById('alerts-sent').textContent = alertsCount;
    alert(`✅ ${data.alerts_sent} WhatsApp alert(s) sent to driver!`);
}

// ─── OPTIMIZE ROUTE ───
async function optimizeRoute() {
    document.getElementById('route-list').innerHTML = '<p style="color:#6b7280;font-size:13px;padding:10px;">⏳ Calculating optimal route...</p>';

    const res = await fetch('/api/optimize');
    const data = await res.json();

    if (data.status === 'NO_COLLECTION_NEEDED') {
        document.getElementById('route-list').innerHTML = '<p style="color:#10b981;font-size:13px;padding:10px;">✅ All bins below threshold — no collection needed.</p>';
        return;
    }

    // Draw route on map
    drawRoute(data.route);

    // Show route stops
    let html = '';
    data.route.forEach((stop, i) => {
        html += `
            <div class="route-stop">
                <div class="stop-number">${i + 1}</div>
                <div class="stop-info">
                    <div class="stop-name">${stop.name}</div>
                    <div class="stop-fill">${stop.fill_level ? `Fill: ${stop.fill_level}%` : 'Depot'}</div>
                </div>
            </div>`;
    });

    document.getElementById('route-list').innerHTML = html;

    const summary = document.getElementById('route-summary');
    summary.style.display = 'block';
    summary.innerHTML = `✅ ${data.total_bins_in_route} bins | Total distance: ${data.total_distance_km} km`;
}

// ─── AUTO REFRESH EVERY 30 SECONDS ───
loadBins();
setInterval(loadBins, 30000);