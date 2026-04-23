const state = {
    layerMode: "lst",
    showQuantile: false,
    geojson: null,
    pointLayer: null,
    quantileLayer: null,
    selectedId: null,
    map: null
};

// --- Color Scales (Academic) ---
const scales = {
    lst: {
        colors: ['#4575b4', '#91bfdb', '#e0f3f8', '#fee090', '#fc8d59', '#d73027'], // Cool to Warm
        title: "Observed LST",
        unit: "°C",
        dataKey: "LST"
    },
    predicted: {
        colors: ['#4575b4', '#91bfdb', '#e0f3f8', '#fee090', '#fc8d59', '#d73027'],
        title: "Predicted LST",
        unit: "°C",
        dataKey: "pred_LST"
    },
    residual: {
        colors: ['#0571b0', '#92c5de', '#f7f7f7', '#f4a582', '#ca0020'], // Diverging: Blue to Red
        title: "Residual (True - Pred)",
        unit: "°C",
        fixed: [-3, 3], // Academic range from report
        dataKey: "residual"
    },
    poi_density: {
        colors: ['#edf8fb', '#b2e2e2', '#66c2a4', '#2ca25f', '#006d2c'], // Greens
        title: "POI Density",
        unit: "pts/ha",
        dataKey: "poi_density"
    }
};

const getColor = (val, mode, ranges) => {
    const config = scales[mode];
    const colors = config.colors;
    let min, max;

    if (config.fixed) {
        [min, max] = config.fixed;
    } else {
        min = ranges[config.dataKey].min;
        max = ranges[config.dataKey].max;
    }

    if (val <= min) return colors[0];
    if (val >= max) return colors[colors.length - 1];

    const ratio = (val - min) / (max - min);
    const idx = Math.min(Math.floor(ratio * colors.length), colors.length - 1);
    return colors[idx];
};

const getProp = (f, p) => f.properties ? f.properties[p] : f[p];

const styleForFeature = (feature, ranges) => {
    const config = scales[state.layerMode];
    const val = getProp(feature, config.dataKey);
    const isSelected = String(getProp(feature, "id")) === String(state.selectedId);

    return {
        radius: isSelected ? 8 : 5,
        fillColor: getColor(val, state.layerMode, ranges),
        color: isSelected ? "#fff" : "#000",
        weight: isSelected ? 3 : 0.5,
        opacity: 1,
        fillOpacity: 0.85
    };
};

const updateLegend = (mode, ranges) => {
    const container = document.getElementById("legend");
    const config = scales[mode];
    let min, max;

    if (config.fixed) {
        [min, max] = config.fixed;
    } else {
        min = ranges[config.dataKey].min;
        max = ranges[config.dataKey].max;
    }

    let html = `<div class="legend-title">${config.title} (${config.unit})</div><div class="legend-scale">`;
    const steps = config.colors.length;
    for (let i = 0; i < steps; i++) {
        const val = min + (i / (steps - 1)) * (max - min);
        html += `
            <div class="legend-row">
                <div class="legend-color" style="background:${config.colors[i]}"></div>
                <span>${val.toFixed(1)}</span>
            </div>
        `;
    }
    html += `</div>`;
    container.innerHTML = html;
};

const selectFeature = (feature, ranges) => {
    const p = feature.properties || {};
    state.selectedId = p.id;

    // Show overlays
    const overlay = document.getElementById("indicators-overlay");
    if (overlay) overlay.classList.remove("hidden");
    const svOverlay = document.getElementById("street-view-overlay");
    if (svOverlay) svOverlay.classList.remove("hidden");

    // 1. Info Card (Right Panel)
    const locInfo = document.getElementById("loc-info");
    if (locInfo) {
        locInfo.innerHTML = `
            <div class="loc-item"><span class="loc-k">Point ID:</span><span class="loc-v">${p.id || "—"}</span></div>
            <div class="loc-item"><span class="loc-k">Coord:</span><span class="loc-v">${Number(p.lat || 0).toFixed(4)}, ${Number(p.lon || 0).toFixed(4)}</span></div>
            <div class="loc-item"><span class="loc-k">Status:</span><span class="loc-v" style="color:${p.quantile_class === 'hot' ? 'var(--accent-warm)' : p.quantile_class === 'cold' ? 'var(--accent-cool)' : 'var(--muted)'}">${(p.quantile_class || "normal").toUpperCase()}</span></div>
        `;
    }

    // 2. Indicators (Floating Overlay on Map)
    const metrics = [
        { k: "Observed LST", v: p.LST, m: 40, u: "°C" },
        { k: "Residual (T-P)", v: p.residual, m: 5, u: "°C", center: true },
        { k: "POI Density", v: p.poi_density, m: 100, u: "" },
        { k: "Sky View", v: (p.sky || 0) * 100, m: 100, u: "%" },
        { k: "Vegetation", v: (p.vegetation || 0) * 100, m: 100, u: "%" },
        { k: "Building", v: (p.building || 0) * 100, m: 100, u: "%" }
    ];

    const indicatorsList = document.getElementById("indicators-list");
    if (indicatorsList) {
        indicatorsList.innerHTML = metrics.map(m => {
            const val = (m.v !== null && m.v !== undefined && !isNaN(m.v)) ? Number(m.v) : 0;
            let pct = (val / m.m) * 100;
            if (m.center) pct = 50 + (val / m.m) * 50; // Center 0 at 50%
            pct = Math.max(0, Math.min(100, pct));

            const barColor = m.center ? (val > 0 ? 'var(--accent-warm)' : 'var(--accent-cool)') : 'var(--accent)';

            return `
                <div class="indicator-item">
                    <div class="indicator-head">
                        <span>${m.k}</span>
                        <strong>${val.toFixed(2)}${m.u}</strong>
                    </div>
                    <div class="bar-bg">
                        <div class="bar-fill" style="width:${pct}%; background:${barColor}"></div>
                    </div>
                </div>
            `;
        }).join("");
    }

    // 3. Interpretation (Right Panel)
    const interpBox = document.getElementById("model-interpretation");
    if (interpBox) {
        let text = `This location shows <b>${p.quantile_class || "normal"}</b> thermal exposure. `;
        if (p.poi_density > 40) text += `The high LST is strongly associated with <b>high POI density</b> (${Number(p.poi_density || 0).toFixed(0)}), indicating intense human activity. `;
        if (p.sky > 0.4) text += `Open sky exposure (${(Number(p.sky || 0) * 100).toFixed(0)}%) contributes to radiative trapping during day hours. `;
        if (p.vegetation < 0.05) text += `Extremely limited vegetation reduces local cooling capacity. `;
        interpBox.innerHTML = text;
    }

    // 4. Street View (Floating Overlay on Map)
    const img = document.getElementById("sv-image");
    const idLabel = document.getElementById("sv-id-label");

    // Support custom base URL for images (e.g. for Streamlit deployment)
    const imgBase = window.IMAGE_BASE_URL || "../data/svi_images/";

    if (img) {
        img.src = p.street_image ? p.street_image.replace("../data/svi_images/", imgBase) : 'https://placehold.co/400x300?text=No+Street+View+Available';
    }
    if (idLabel) {
        idLabel.textContent = `ID: ${p.id}`;
    }

    // Refresh styles
    if (state.pointLayer) {
        state.pointLayer.setStyle(f => styleForFeature(f, ranges));
    }
};

async function init() {
    const map = L.map('map', {
        center: [22.31, 114.17],
        zoom: 14,
        zoomControl: false
    });
    state.map = map;
    L.control.zoom({ position: 'bottomright' }).addTo(map);

    const baseLayers = {
        none: L.tileLayer('', { attribution: 'DeepStreetHeat' }),
        osm: L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap'
        })
    };
    baseLayers.none.addTo(map);

    // Load Data
    let data;
    if (window.pointsData) {
        data = window.pointsData;
    } else {
        const res = await fetch('./data/points.geojson');
        data = await res.json();
    }
    state.geojson = data;

    // Calculate ranges
    const ranges = {};
    const features = data.features || [];

    // Define all keys we need to compute ranges for
    const rangeKeys = ["LST", "pred_LST", "residual", "poi_density", "sky", "vegetation", "building"];

    rangeKeys.forEach(key => {
        const vals = features.map(f => Number(getProp(f, key))).filter(v => !isNaN(v));
        if (vals.length > 0) {
            ranges[key] = { min: Math.min(...vals), max: Math.max(...vals) };
        } else {
            ranges[key] = { min: 0, max: 1 };
        }
    });

    // Layers
    const pointLayer = L.geoJSON(data, {
        pointToLayer: (f, latlng) => L.circleMarker(latlng),
        style: (f) => styleForFeature(f, ranges)
    }).addTo(map);

    pointLayer.on('click', (e) => {
        selectFeature(e.layer.feature, ranges);
    });

    state.pointLayer = pointLayer;

    const quantileLayer = L.geoJSON(data, {
        filter: (f) => f.properties.quantile_class !== 'normal',
        pointToLayer: (f, latlng) => L.circleMarker(latlng, {
            radius: 12,
            fillColor: f.properties.quantile_class === 'hot' ? '#ef4444' : '#3b82f6',
            color: '#fff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.3
        })
    });
    state.quantileLayer = quantileLayer;

    // Controls
    document.getElementById("layerSelect").onchange = (e) => {
        state.layerMode = e.target.value;
        pointLayer.setStyle(f => styleForFeature(f, ranges));
        updateLegend(state.layerMode, ranges);
    };

    document.getElementById("quantileToggle").onchange = (e) => {
        if (e.target.checked) quantileLayer.addTo(map);
        else map.removeLayer(quantileLayer);
    };

    document.querySelectorAll(".base-btn").forEach(btn => {
        btn.onclick = () => {
            document.querySelectorAll(".base-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            Object.values(baseLayers).forEach(l => map.removeLayer(l));
            baseLayers[btn.dataset.base].addTo(map);
        };
    });

    // Nav
    document.querySelectorAll(".nav-btn").forEach(btn => {
        btn.onclick = () => {
            document.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            const target = btn.dataset.view + "-section";
            const el = document.getElementById(target);
            if (el) el.scrollIntoView({ behavior: 'smooth' });
        };
    });

    // Modal
    const modal = document.getElementById("methodModal");
    document.getElementById("helpBtn").onclick = () => modal.style.display = "block";
    document.querySelector(".close").onclick = () => modal.style.display = "none";
    window.onclick = (e) => { if (e.target == modal) modal.style.display = "none"; };

    updateLegend(state.layerMode, ranges);

    // Select first point by default
    if (features.length) {
        selectFeature(features[0], ranges);
    }
}

init();
