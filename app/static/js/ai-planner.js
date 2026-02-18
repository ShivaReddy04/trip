// AI Planner AJAX + Leaflet Map

let itineraryMap = null;
let mapMarkers = [];
let mapPolylines = [];

const DAY_COLORS = ['#667eea', '#e53e3e', '#38a169', '#d69e2e', '#9f7aea', '#ed8936', '#3182ce', '#e53e3e'];

function getMarkerIcon(color) {
    return L.divIcon({
        className: 'custom-marker',
        html: `<div style="background:${color};width:14px;height:14px;border-radius:50%;border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,0.3);"></div>`,
        iconSize: [14, 14],
        iconAnchor: [7, 7],
        popupAnchor: [0, -10],
    });
}

function clearMap() {
    mapMarkers.forEach(m => m.remove());
    mapPolylines.forEach(p => p.remove());
    mapMarkers = [];
    mapPolylines = [];
    if (itineraryMap) {
        itineraryMap.remove();
        itineraryMap = null;
    }
}

function renderMap(itinerary) {
    const mapDiv = document.getElementById('itinerary-map');
    clearMap();

    // Collect all locations with coordinates
    const allCoords = [];
    const dayData = [];

    if (!itinerary.days) return;

    itinerary.days.forEach(day => {
        const dayCoords = [];
        if (day.activities) {
            day.activities.forEach(act => {
                if (act.lat != null && act.lng != null) {
                    dayCoords.push({ lat: act.lat, lng: act.lng, activity: act.activity, time: act.time, location: act.location });
                    allCoords.push([act.lat, act.lng]);
                }
            });
        }
        dayData.push({ day: day.day, coords: dayCoords });
    });

    if (allCoords.length === 0) {
        mapDiv.classList.add('hidden');
        return;
    }

    mapDiv.classList.remove('hidden');

    itineraryMap = L.map('itinerary-map', { scrollWheelZoom: true });
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
        maxZoom: 18,
    }).addTo(itineraryMap);

    // Add markers and polylines per day
    dayData.forEach(({ day, coords }) => {
        if (coords.length === 0) return;
        const color = DAY_COLORS[(day - 1) % DAY_COLORS.length];
        const icon = getMarkerIcon(color);

        const linePoints = [];
        coords.forEach(c => {
            const marker = L.marker([c.lat, c.lng], { icon })
                .bindPopup(`<strong>Day ${day}: ${c.activity}</strong><br><span style="color:#666">${c.time}</span><br><small>${c.location}</small>`)
                .addTo(itineraryMap);
            marker._dayNum = day;
            mapMarkers.push(marker);
            linePoints.push([c.lat, c.lng]);
        });

        if (linePoints.length > 1) {
            const polyline = L.polyline(linePoints, { color, weight: 2, opacity: 0.6, dashArray: '6 4' }).addTo(itineraryMap);
            polyline._dayNum = day;
            mapPolylines.push(polyline);
        }
    });

    // Fit bounds
    if (allCoords.length > 0) {
        itineraryMap.fitBounds(allCoords, { padding: [30, 30] });
    }
}

function highlightDay(dayNum) {
    if (!itineraryMap) return;
    const dayCoords = [];

    mapMarkers.forEach(m => {
        if (m._dayNum === dayNum) {
            m.setOpacity(1);
            dayCoords.push(m.getLatLng());
        } else {
            m.setOpacity(0.3);
        }
    });
    mapPolylines.forEach(p => {
        p.setStyle({ opacity: p._dayNum === dayNum ? 0.8 : 0.15 });
    });

    if (dayCoords.length > 0) {
        itineraryMap.fitBounds(dayCoords.map(c => [c.lat, c.lng]), { padding: [40, 40], maxZoom: 15 });
    }
}

function resetMapHighlight() {
    mapMarkers.forEach(m => m.setOpacity(1));
    mapPolylines.forEach(p => p.setStyle({ opacity: 0.6 }));
    if (mapMarkers.length > 0) {
        const allCoords = mapMarkers.map(m => [m.getLatLng().lat, m.getLatLng().lng]);
        itineraryMap.fitBounds(allCoords, { padding: [30, 30] });
    }
}

async function generateItinerary() {
    const destinations = document.getElementById('ai-destinations').value.split(',').map(s => s.trim()).filter(Boolean);
    const duration = parseInt(document.getElementById('ai-duration').value) || 5;
    const travelers = parseInt(document.getElementById('ai-travelers').value) || 2;
    const budget = parseFloat(document.getElementById('ai-budget').value) || 2000;
    const startDate = document.getElementById('ai-start-date').value;
    const preferences = Array.from(document.querySelectorAll('.pref-check:checked')).map(c => c.value);

    if (destinations.length === 0) {
        showToast('Please enter at least one destination', 'error');
        return;
    }

    const btn = document.getElementById('generate-btn');
    const loading = document.getElementById('ai-loading');
    const error = document.getElementById('ai-error');
    const result = document.getElementById('ai-result');
    const empty = document.getElementById('ai-empty');

    btn.disabled = true;
    btn.innerHTML = '<div class="spinner mx-auto"></div>';
    loading.classList.remove('hidden');
    error.classList.add('hidden');
    result.classList.add('hidden');
    empty.classList.add('hidden');
    document.getElementById('itinerary-map').classList.add('hidden');

    try {
        const data = await apiRequest('/ai/generate', {
            method: 'POST',
            body: { destinations, duration, travelers, budget, startDate, preferences },
        });

        const itinerary = data.generatedItinerary;
        if (!itinerary) throw new Error('No itinerary generated');

        // Render title and budget
        document.getElementById('itinerary-title').textContent = itinerary.title || 'Your Trip Itinerary';
        document.getElementById('itinerary-budget').innerHTML = `<i data-lucide="wallet" class="w-4 h-4 mr-1"></i>Estimated: $${itinerary.totalBudget || budget}`;

        // Render recommendations
        const recsDiv = document.getElementById('itinerary-recommendations');
        recsDiv.innerHTML = '';
        if (itinerary.recommendations) {
            itinerary.recommendations.forEach(rec => {
                const p = document.createElement('p');
                p.className = 'text-sm text-gray-600 flex items-start';
                p.innerHTML = `<i data-lucide="lightbulb" class="w-4 h-4 text-yellow-500 mr-2 shrink-0 mt-0.5"></i>${rec}`;
                recsDiv.appendChild(p);
            });
        }

        // Render days
        const daysDiv = document.getElementById('itinerary-days');
        daysDiv.innerHTML = '';
        if (itinerary.days) {
            itinerary.days.forEach(day => {
                const dayCard = document.createElement('div');
                dayCard.className = 'bg-white rounded-xl shadow-sm border border-gray-100 p-6 cursor-pointer hover:border-primary-300 transition';
                dayCard.dataset.day = day.day;

                dayCard.addEventListener('click', () => highlightDay(day.day));
                dayCard.addEventListener('dblclick', () => resetMapHighlight());

                let activitiesHtml = '';
                if (day.activities) {
                    day.activities.forEach(act => {
                        const coordBadge = (act.lat != null && act.lng != null)
                            ? `<span class="inline-block w-2 h-2 rounded-full ml-1" style="background:${DAY_COLORS[(day.day - 1) % DAY_COLORS.length]}"></span>`
                            : '';
                        activitiesHtml += `
                            <div class="flex items-start py-2 border-b border-gray-50 last:border-0">
                                <span class="text-xs font-mono text-primary-600 w-20 shrink-0 pt-0.5">${act.time || ''}</span>
                                <div class="flex-1">
                                    <p class="text-sm font-medium text-gray-900">${act.activity}${coordBadge}</p>
                                    ${act.location ? `<p class="text-xs text-gray-500">${act.location}</p>` : ''}
                                </div>
                                ${act.cost ? `<span class="text-xs font-medium text-gray-500">$${act.cost}</span>` : ''}
                            </div>`;
                    });
                }
                let tipsHtml = '';
                if (day.tips && day.tips.length) {
                    tipsHtml = `<div class="mt-3 pt-3 border-t border-gray-100">
                        ${day.tips.map(t => `<p class="text-xs text-primary-600"><i data-lucide="info" class="w-3 h-3 inline mr-1"></i>${t}</p>`).join('')}
                    </div>`;
                }
                dayCard.innerHTML = `
                    <div class="flex items-center justify-between mb-4">
                        <h3 class="font-semibold text-gray-900">
                            <span class="inline-block w-3 h-3 rounded-full mr-2" style="background:${DAY_COLORS[(day.day - 1) % DAY_COLORS.length]}"></span>Day ${day.day}
                        </h3>
                        ${day.totalCost ? `<span class="text-sm text-gray-500">Day total: $${day.totalCost}</span>` : ''}
                    </div>
                    <div class="space-y-0">${activitiesHtml}</div>
                    ${tipsHtml}`;
                daysDiv.appendChild(dayCard);
            });
        }

        result.classList.remove('hidden');
        lucide.createIcons();

        // Render map after DOM is visible
        setTimeout(() => renderMap(itinerary), 100);
    } catch (err) {
        error.classList.remove('hidden');
        document.getElementById('ai-error-msg').textContent = err.message || 'Failed to generate itinerary. Please try again.';
    }

    loading.classList.add('hidden');
    btn.disabled = false;
    btn.innerHTML = '<i data-lucide="sparkles" class="w-5 h-5 mr-2"></i>Generate Itinerary';
    lucide.createIcons();
}
