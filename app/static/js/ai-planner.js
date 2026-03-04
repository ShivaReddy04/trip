// Destination Guide — split-screen famous places with numbered map markers
let destMap = null;
let placeMarkers = [];       // numbered markers for famous places
let lastData = null;
let selectedTravelMode = 'train';
let routePolyline = null;
let originMarker = null;
let destMarkerObj = null;
let activeIndex = -1;        // currently highlighted place index
let scrollObserver = null;   // IntersectionObserver for scroll tracking

// ---------------------------------------------------------------------------
// Travel mode selector
// ---------------------------------------------------------------------------
function selectTravelMode(btn) {
    document.querySelectorAll('.travel-mode-btn').forEach(b => {
        b.classList.remove('selected', 'border-primary-500', 'bg-primary-50');
        b.classList.add('border-gray-200');
    });
    btn.classList.add('selected', 'border-primary-500', 'bg-primary-50');
    btn.classList.remove('border-gray-200');
    selectedTravelMode = btn.dataset.mode;
}

// ---------------------------------------------------------------------------
// Main explore function
// ---------------------------------------------------------------------------
async function exploreDest() {
    const destination = document.getElementById('dest-input').value.trim();
    const fromCity = document.getElementById('from-input').value.trim();

    if (!destination) {
        showToast('Please enter a destination', 'error');
        return;
    }

    const btn = document.getElementById('explore-btn');
    const loading = document.getElementById('ai-loading');
    const errorDiv = document.getElementById('ai-error');
    const result = document.getElementById('ai-result');
    const empty = document.getElementById('ai-empty');

    btn.disabled = true;
    btn.innerHTML = '<div class="spinner mx-auto"></div>';
    loading.classList.remove('hidden');
    errorDiv.classList.add('hidden');
    result.classList.add('hidden');
    empty.classList.add('hidden');

    try {
        const data = await apiRequest('/ai/destination-guide', {
            method: 'POST',
            body: {
                destination: destination,
                from_city: fromCity || null,
                travel_mode: selectedTravelMode,
            },
        });

        if (data.error) throw new Error(data.error);

        lastData = data;

        renderHero(data.destination);
        renderTravelInfo(data.travel_info, data.destination);
        renderThingsToDo(data.destination);
        renderTravelTips(data.destination);
        renderNearbyPlaces(data.nearby_destinations);

        result.classList.remove('hidden');
        lucide.createIcons();

        // Render famous places split-screen (includes map)
        setTimeout(() => {
            try {
                renderFamousPlacesSplit(data);
            } catch (mapErr) {
                console.error('Map/places render error:', mapErr);
            }
        }, 150);

        // Initialize language bar for translation + speech
        setTimeout(() => initLanguageBar(), 300);

    } catch (err) {
        console.error('Explore error:', err);
        errorDiv.classList.remove('hidden');
        let msg = err.message || 'Failed to load destination guide.';
        if (msg.includes('timed out')) {
            msg = 'Request timed out. The AI service may be slow — please try again.';
        } else if (msg.includes('Failed to fetch') || msg.includes('NetworkError')) {
            msg = 'Network error. Please check your internet connection and try again.';
        }
        document.getElementById('ai-error-msg').textContent = msg;
    }

    loading.classList.add('hidden');
    btn.disabled = false;
    btn.innerHTML = '<i data-lucide="compass" class="w-5 h-5 mr-2"></i>Explore Destination';
    lucide.createIcons();
}

// ---------------------------------------------------------------------------
// Hero section
// ---------------------------------------------------------------------------
function renderHero(dest) {
    const section = document.getElementById('hero-section');
    const stars = '&#9733;'.repeat(Math.min(Math.round(dest.popularity_score / 2), 5));
    const seasons = (dest.best_seasons || []).join(', ') || 'Year-round';

    section.innerHTML = `
        <div class="relative rounded-xl overflow-hidden shadow-sm border border-gray-100">
            <img src="${dest.image_url}" alt="${dest.name}"
                class="w-full h-56 object-cover" onerror="this.src='https://placehold.co/600x400/e2e8f0/64748b?text=No+Image'">
            <div class="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent"></div>
            <div class="absolute bottom-0 left-0 right-0 p-6 text-white">
                <h2 class="text-2xl font-bold">${dest.name}</h2>
                <p class="text-sm opacity-90">${dest.state} &middot; ${dest.region}</p>
                <div class="flex flex-wrap items-center gap-3 mt-2 text-sm">
                    <span class="text-yellow-300">${stars}</span>
                    <span class="bg-white/20 px-2 py-0.5 rounded-full text-xs">${dest.ideal_days} days ideal</span>
                    <span class="bg-white/20 px-2 py-0.5 rounded-full text-xs">Best: ${seasons}</span>
                    ${dest.accessibility ? `<span class="bg-white/20 px-2 py-0.5 rounded-full text-xs">${dest.accessibility} access</span>` : ''}
                </div>
            </div>
        </div>`;
}

// ---------------------------------------------------------------------------
// How to Reach
// ---------------------------------------------------------------------------
function _formatHours(h) {
    if (!h) return '—';
    if (h < 1) return `${Math.round(h * 60)} min`;
    const hrs = Math.floor(h);
    const mins = Math.round((h - hrs) * 60);
    return mins > 0 ? `${hrs}h ${mins}m` : `${hrs}h`;
}

function _formatPrice(p) {
    if (!p) return '—';
    return `₹${p.low.toLocaleString('en-IN')} – ₹${p.high.toLocaleString('en-IN')}`;
}

function _bookingUrl(mode, from, to) {
    switch (mode) {
        case 'train':  return 'https://www.irctc.co.in/nget/train-search';
        case 'bus':    return `https://www.redbus.in/bus-tickets/${(from||'').toLowerCase().replace(/\s+/g,'-')}-to-${(to||'').toLowerCase().replace(/\s+/g,'-')}`;
        case 'flight': return `https://www.makemytrip.com/flight/search?fromCity=${encodeURIComponent(from||'')}&toCity=${encodeURIComponent(to||'')}`;
        default:       return null;
    }
}

function renderTravelInfo(travel, dest) {
    const section = document.getElementById('travel-info-section');
    const airport = travel.nearest_airport || {};
    const railway = travel.nearest_railway || {};
    const prices = travel.price_estimates || {};
    const times = travel.travel_times || {};
    const mode = travel.travel_mode || selectedTravelMode;

    let summaryHtml = '';
    if (travel.from_city && travel.road_distance_km) {
        const dist = travel.road_distance_km;
        const dur = times[mode];
        summaryHtml = `
            <div class="flex items-center gap-3 p-4 bg-gradient-to-r from-primary-50 to-blue-50 rounded-xl mb-4">
                <i data-lucide="navigation" class="w-6 h-6 text-primary-600 shrink-0"></i>
                <div>
                    <p class="font-semibold text-gray-900">${travel.from_city} → ${dest.name}</p>
                    <p class="text-sm text-gray-600">${dist} km${dur ? ` · ~${_formatHours(dur)} by ${mode}` : ''}</p>
                </div>
            </div>`;
    }

    const modeConfig = {
        train:  { icon: 'train-front', color: 'green',  label: 'Train' },
        bus:    { icon: 'bus',          color: 'orange', label: 'Bus' },
        flight: { icon: 'plane',        color: 'indigo', label: 'Flight' },
        car:    { icon: 'car',          color: 'red',    label: 'Car' },
    };

    let priceCardsHtml = '';
    if (travel.from_city && travel.price_estimates) {
        const cards = Object.entries(modeConfig).map(([m, cfg]) => {
            const p = prices[m];
            const t = times[m];
            const isSelected = m === mode;
            const borderClass = isSelected ? `border-${cfg.color}-400 ring-2 ring-${cfg.color}-200` : 'border-gray-100';
            const bgClass = isSelected ? `bg-${cfg.color}-50` : 'bg-white';
            const unavailable = !p || !t;

            return `
                <div class="rounded-xl border ${borderClass} ${bgClass} p-4 ${unavailable ? 'opacity-50' : ''}">
                    <div class="flex items-center gap-2 mb-2">
                        <i data-lucide="${cfg.icon}" class="w-4 h-4 text-${cfg.color}-500"></i>
                        <span class="text-sm font-semibold text-gray-900">${cfg.label}</span>
                        ${isSelected ? '<span class="ml-auto text-xs bg-primary-100 text-primary-700 px-2 py-0.5 rounded-full">Selected</span>' : ''}
                    </div>
                    ${unavailable
                        ? '<p class="text-xs text-gray-400">Not available for this distance</p>'
                        : `<p class="text-base font-bold text-gray-900">${_formatPrice(p)}</p>
                           <p class="text-xs text-gray-500 mt-1">${p.label} · ${_formatHours(t)}</p>`
                    }
                </div>`;
        }).join('');

        const bookUrl = _bookingUrl(mode, travel.from_city, dest.name);
        const bookLabel = { train: 'Book on IRCTC', bus: 'Book on RedBus', flight: 'Book on MakeMyTrip', car: null };
        const bookBtnHtml = bookLabel[mode]
            ? `<a href="${bookUrl}" target="_blank" rel="noopener noreferrer"
                  class="inline-flex items-center gap-2 mt-4 px-5 py-2.5 bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium rounded-lg transition">
                  <i data-lucide="external-link" class="w-4 h-4"></i>
                  ${bookLabel[mode]}
               </a>`
            : `<span class="inline-flex items-center gap-2 mt-4 px-5 py-2.5 bg-gray-100 text-gray-600 text-sm font-medium rounded-lg">
                  <i data-lucide="car" class="w-4 h-4"></i>
                  Self-drive
               </span>`;

        priceCardsHtml = `
            <div class="mb-4">
                <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Estimated Prices</p>
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">${cards}</div>
                <div class="flex items-center justify-between mt-3">
                    ${bookBtnHtml}
                    <p class="text-xs text-gray-400 italic">Prices are approximate</p>
                </div>
            </div>`;
    }

    let infoCards = '';
    if (airport.name) {
        infoCards += `
            <div class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <i data-lucide="plane" class="w-5 h-5 text-indigo-500 shrink-0"></i>
                <div>
                    <p class="text-sm font-medium text-gray-900">${airport.name}</p>
                    <p class="text-xs text-gray-500">${airport.distance_km} km away</p>
                </div>
            </div>`;
    }
    if (railway.name) {
        infoCards += `
            <div class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <i data-lucide="train-front" class="w-5 h-5 text-green-600 shrink-0"></i>
                <div>
                    <p class="text-sm font-medium text-gray-900">${railway.name}</p>
                    <p class="text-xs text-gray-500">${railway.distance_km} km away</p>
                </div>
            </div>`;
    }
    if (travel.road_info) {
        infoCards += `
            <div class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <i data-lucide="car" class="w-5 h-5 text-orange-500 shrink-0"></i>
                <div>
                    <p class="text-sm font-medium text-gray-900">Road Connectivity</p>
                    <p class="text-xs text-gray-500">${travel.road_info}</p>
                </div>
            </div>`;
    }

    section.innerHTML = `
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 class="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <i data-lucide="route" class="w-5 h-5 text-primary-600"></i>
                How to Reach
            </h3>
            ${summaryHtml}
            ${priceCardsHtml}
            ${infoCards ? `<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">${infoCards}</div>` : ''}
        </div>`;
}

// ---------------------------------------------------------------------------
// Famous Places — SPLIT SCREEN (list + map)
// ---------------------------------------------------------------------------
function renderFamousPlacesSplit(data) {
    const section = document.getElementById('famous-places-section');
    const places = data.famous_places || [];
    const dest = data.destination;
    const travel = data.travel_info || {};

    if (!places.length || !dest || !dest.lat || !dest.lng) {
        section.innerHTML = '';
        return;
    }
    if (typeof L === 'undefined') {
        console.error('Leaflet library not loaded');
        return;
    }

    // Cleanup previous
    clearMap();

    // Build the split layout HTML
    const listCards = places.map((p, i) => `
        <div class="place-card" data-index="${i}"
             onmouseenter="highlightPlace(${i}, true)"
             onmouseleave="highlightPlace(${i}, false)"
             onclick="focusPlace(${i})">
            <div class="place-card-num">${i + 1}</div>
            <img class="place-card-img" src="${p.image_url || ''}" alt="${p.name}"
                 onerror="this.onerror=null;this.src='https://placehold.co/64x64/e2e8f0/64748b?text=${i + 1}'">
            <div class="flex-1 min-w-0">
                <h4 class="text-sm font-semibold text-gray-900 truncate">${p.name}</h4>
                <div class="flex items-center gap-2 mt-0.5">
                    <span class="px-1.5 py-0.5 rounded text-[10px] bg-pink-50 text-pink-700">${p.type || 'attraction'}</span>
                    <span class="text-[11px] text-gray-400">${p.distance_km || 0} km</span>
                    ${p.rating ? `<span class="text-[11px] text-yellow-500 font-medium">${p.rating}</span>` : ''}
                </div>
                ${p.description ? `<p class="text-[11px] text-gray-500 mt-1 line-clamp-2">${p.description}</p>` : ''}
            </div>
        </div>`).join('');

    section.innerHTML = `
        <div>
            <h3 class="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <span class="text-pink-500 text-lg">&#9733;</span>
                Famous Places Nearby
                <span class="text-xs text-gray-400 font-normal">${places.length} found</span>
            </h3>
            <div class="places-split">
                <div class="places-list" id="places-list">
                    ${listCards}
                </div>
                <div class="places-map" id="places-map-container"></div>
            </div>
        </div>`;

    // --- Initialize Leaflet map inside the right pane ---
    const mapContainer = document.getElementById('places-map-container');
    destMap = L.map(mapContainer, { zoomControl: true, scrollWheelZoom: true })
        .setView([dest.lat, dest.lng], 12);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OSM',
        maxZoom: 18,
    }).addTo(destMap);

    const bounds = L.latLngBounds([[dest.lat, dest.lng]]);

    // Destination center marker
    destMarkerObj = L.marker([dest.lat, dest.lng], {
        icon: L.divIcon({ className: 'dest-marker', iconSize: [20, 20], iconAnchor: [10, 10] }),
        zIndexOffset: 1000,
    }).addTo(destMap).bindPopup(`<strong>${dest.name}</strong><br><small>${dest.state || ''}</small>`);

    // --- Route polyline + origin marker ---
    const mode = travel.travel_mode || selectedTravelMode;
    if (travel.origin_coords) {
        const oLat = travel.origin_coords[0];
        const oLng = travel.origin_coords[1];

        originMarker = L.marker([oLat, oLng], {
            icon: L.divIcon({ className: 'origin-marker', iconSize: [18, 18], iconAnchor: [9, 9] }),
            zIndexOffset: 900,
        }).addTo(destMap).bindPopup(`<strong>${travel.from_city || 'Origin'}</strong><br><small>Starting point</small>`);
        bounds.extend([oLat, oLng]);

        const modeColors = { car: '#ef4444', bus: '#f97316', train: '#22c55e', flight: '#6366f1' };
        const lineColor = modeColors[mode] || '#667eea';

        if (travel.route_geometry && travel.route_geometry.length > 0) {
            const path = travel.route_geometry.map(p => [p[0], p[1]]);
            routePolyline = L.polyline(path, { color: lineColor, weight: 4, opacity: 0.8 }).addTo(destMap);
        } else {
            routePolyline = L.polyline([[oLat, oLng], [dest.lat, dest.lng]], {
                color: lineColor, weight: 3, opacity: 0.7, dashArray: mode === 'flight' ? null : '8 6',
            }).addTo(destMap);
        }
    }

    // --- Numbered place markers ---
    placeMarkers = [];
    places.forEach((place, i) => {
        const icon = _makeNumberedIcon(i + 1, false);
        const m = L.marker([place.lat, place.lng], { icon: icon, zIndexOffset: 500 })
            .addTo(destMap)
            .bindPopup(`<strong>${i + 1}. ${place.name}</strong><br><small>${place.type || 'attraction'}</small>${place.description ? `<br><small style="color:#6b7280">${place.description}</small>` : ''}`);
        m._placeIdx = i;

        // Clicking a marker on the map scrolls the list
        m.on('click', () => {
            _scrollToCard(i);
            _setActive(i);
        });

        placeMarkers.push(m);
        bounds.extend([place.lat, place.lng]);
    });

    if (bounds.isValid()) {
        destMap.fitBounds(bounds, { padding: [30, 30] });
    }

    // Invalidate map size after DOM reflow
    setTimeout(() => destMap.invalidateSize(), 200);

    // --- Set up IntersectionObserver for scroll-driven highlighting ---
    _setupScrollObserver();

    // Activate first place
    if (places.length > 0) {
        _setActive(0);
    }
}

// ---------------------------------------------------------------------------
// Numbered marker icon helper
// ---------------------------------------------------------------------------
function _makeNumberedIcon(num, isActive) {
    const size = isActive ? 36 : 28;
    const cls = isActive ? 'num-marker active' : 'num-marker';
    return L.divIcon({
        className: '',
        html: `<div class="${cls}">${num}</div>`,
        iconSize: [size, size],
        iconAnchor: [size / 2, size / 2],
    });
}

// ---------------------------------------------------------------------------
// Set active place (update marker + card)
// ---------------------------------------------------------------------------
function _setActive(index) {
    if (index === activeIndex) return;
    const prevIndex = activeIndex;
    activeIndex = index;

    // Deactivate previous marker
    if (prevIndex >= 0 && prevIndex < placeMarkers.length) {
        placeMarkers[prevIndex].setIcon(_makeNumberedIcon(prevIndex + 1, false));
        placeMarkers[prevIndex].setZIndexOffset(500);
    }

    // Activate new marker
    if (index >= 0 && index < placeMarkers.length) {
        placeMarkers[index].setIcon(_makeNumberedIcon(index + 1, true));
        placeMarkers[index].setZIndexOffset(2000);
    }

    // Update card styling
    document.querySelectorAll('#places-list .place-card').forEach((card, i) => {
        card.classList.toggle('active', i === index);
    });
}

// ---------------------------------------------------------------------------
// Highlight on hover (temporary — doesn't change activeIndex)
// ---------------------------------------------------------------------------
function highlightPlace(index, entering) {
    if (index < 0 || index >= placeMarkers.length) return;

    if (entering) {
        // Make hovered marker active style
        placeMarkers[index].setIcon(_makeNumberedIcon(index + 1, true));
        placeMarkers[index].setZIndexOffset(2000);

        // Pan map smoothly to this place
        const place = lastData.famous_places[index];
        if (place && destMap) {
            destMap.panTo([place.lat, place.lng], { animate: true, duration: 0.4 });
        }
    } else {
        // Restore: if this was the active one keep it active, else deactivate
        if (index !== activeIndex) {
            placeMarkers[index].setIcon(_makeNumberedIcon(index + 1, false));
            placeMarkers[index].setZIndexOffset(500);
        }
    }
}

// ---------------------------------------------------------------------------
// Focus place (click) — pan map + open popup
// ---------------------------------------------------------------------------
function focusPlace(index) {
    if (!destMap || !lastData || !lastData.famous_places) return;
    const place = lastData.famous_places[index];
    if (!place) return;

    _setActive(index);
    destMap.setView([place.lat, place.lng], 15, { animate: true });

    if (placeMarkers[index]) {
        placeMarkers[index].openPopup();
    }
}

// ---------------------------------------------------------------------------
// Scroll to a card in the list (when marker is clicked on map)
// ---------------------------------------------------------------------------
function _scrollToCard(index) {
    const list = document.getElementById('places-list');
    const card = list?.querySelectorAll('.place-card')[index];
    if (card && list) {
        card.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

// ---------------------------------------------------------------------------
// IntersectionObserver — track which card is visible in the scroll area
// ---------------------------------------------------------------------------
function _setupScrollObserver() {
    if (scrollObserver) {
        scrollObserver.disconnect();
        scrollObserver = null;
    }

    const list = document.getElementById('places-list');
    if (!list) return;

    const cards = list.querySelectorAll('.place-card');
    if (!cards.length) return;

    // Observe which card intersects the middle of the list viewport
    scrollObserver = new IntersectionObserver((entries) => {
        let bestEntry = null;
        let bestRatio = 0;

        entries.forEach(entry => {
            if (entry.isIntersecting && entry.intersectionRatio > bestRatio) {
                bestRatio = entry.intersectionRatio;
                bestEntry = entry;
            }
        });

        if (bestEntry) {
            const idx = parseInt(bestEntry.target.dataset.index, 10);
            if (!isNaN(idx) && idx !== activeIndex) {
                _setActive(idx);

                // Gently pan map to show this place
                const place = lastData?.famous_places?.[idx];
                if (place && destMap) {
                    destMap.panTo([place.lat, place.lng], { animate: true, duration: 0.5 });
                }
            }
        }
    }, {
        root: list,
        rootMargin: '-35% 0px -35% 0px',   // "center zone" of the list
        threshold: [0, 0.25, 0.5, 0.75, 1],
    });

    cards.forEach(card => scrollObserver.observe(card));
}

// ---------------------------------------------------------------------------
// Cleanup
// ---------------------------------------------------------------------------
function clearMap() {
    if (scrollObserver) {
        scrollObserver.disconnect();
        scrollObserver = null;
    }
    if (destMap) {
        destMap.remove();
        destMap = null;
    }
    placeMarkers = [];
    routePolyline = null;
    originMarker = null;
    destMarkerObj = null;
    activeIndex = -1;
}

// ---------------------------------------------------------------------------
// Things to Do
// ---------------------------------------------------------------------------
function renderThingsToDo(dest) {
    const section = document.getElementById('things-to-do-section');

    const activities = dest.activities || [];
    const experiences = dest.unique_experiences || '';
    const gems = dest.hidden_gems || [];
    const attractions = dest.primary_attractions || [];

    if (activities.length === 0 && !experiences && gems.length === 0 && attractions.length === 0) {
        section.innerHTML = '';
        return;
    }

    const chipList = (items, color) => items.map(item =>
        `<span class="inline-block px-3 py-1 rounded-full text-xs font-medium bg-${color}-50 text-${color}-700 border border-${color}-100">${item}</span>`
    ).join('');

    let html = `<div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 class="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <i data-lucide="sparkles" class="w-5 h-5 text-amber-500"></i>
            Things to Do
        </h3>`;

    if (attractions.length > 0) {
        html += `<div class="mb-4">
            <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Top Attractions</p>
            <div class="flex flex-wrap gap-2">${chipList(attractions, 'blue')}</div>
        </div>`;
    }

    if (activities.length > 0) {
        html += `<div class="mb-4">
            <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Activities</p>
            <div class="flex flex-wrap gap-2">${chipList(activities, 'green')}</div>
        </div>`;
    }

    if (experiences) {
        html += `<div class="mb-4">
            <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Unique Experiences</p>
            <p class="text-sm text-gray-700">${experiences}</p>
        </div>`;
    }

    if (gems.length > 0) {
        html += `<div class="mb-5">
            <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Hidden Gems</p>
            <div class="flex flex-wrap gap-2">${chipList(gems, 'purple')}</div>
        </div>`;
    }

    // --- Plan My Trip CTA ---
    html += `
        <div class="mt-2 pt-4 border-t border-gray-100">
            <button onclick="openTripModal()" class="w-full bg-gradient-to-r from-orange-500 to-pink-500 text-white py-3.5 rounded-xl font-semibold hover:opacity-90 transition flex items-center justify-center gap-2 shadow-md shadow-orange-200/50">
                <i data-lucide="route" class="w-5 h-5"></i>
                Plan My Trip
            </button>
        </div>`;

    html += `</div>`;
    section.innerHTML = html;
    lucide.createIcons();
}

// ---------------------------------------------------------------------------
// Travel Tips
// ---------------------------------------------------------------------------
function renderTravelTips(dest) {
    const section = document.getElementById('travel-tips-section');

    const items = [];
    if (dest.best_seasons && dest.best_seasons.length > 0) {
        items.push({ icon: 'sun', label: 'Best Seasons', value: dest.best_seasons.join(', ') });
    }
    if (dest.avoid_seasons && dest.avoid_seasons.length > 0) {
        items.push({ icon: 'cloud-rain', label: 'Avoid', value: dest.avoid_seasons.join(', ') });
    }
    if (dest.food_scene) {
        items.push({ icon: 'utensils', label: 'Food Scene', value: dest.food_scene });
    }
    if (dest.local_cuisine_must_try && dest.local_cuisine_must_try.length > 0) {
        items.push({ icon: 'chef-hat', label: 'Must Try', value: dest.local_cuisine_must_try.join(', ') });
    }
    if (dest.safety_notes) {
        items.push({ icon: 'shield', label: 'Safety', value: `${dest.safety_rating}/10 — ${dest.safety_notes}` });
    }
    if (dest.local_culture) {
        items.push({ icon: 'heart', label: 'Culture', value: dest.local_culture });
    }
    if (dest.festivals_events) {
        items.push({ icon: 'party-popper', label: 'Festivals', value: dest.festivals_events });
    }
    if (dest.special_considerations) {
        items.push({ icon: 'info', label: 'Tips', value: dest.special_considerations });
    }
    if (dest.suggested_itinerary) {
        items.push({ icon: 'calendar-days', label: 'Suggested Plan', value: dest.suggested_itinerary });
    }

    if (items.length === 0) {
        section.innerHTML = '';
        return;
    }

    const rows = items.map(item => `
        <div class="flex items-start gap-3 py-3 border-b border-gray-50 last:border-0">
            <i data-lucide="${item.icon}" class="w-4 h-4 text-primary-500 mt-0.5 shrink-0"></i>
            <div>
                <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide">${item.label}</p>
                <p class="text-sm text-gray-700 mt-0.5">${item.value}</p>
            </div>
        </div>`).join('');

    section.innerHTML = `
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 class="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                <i data-lucide="lightbulb" class="w-5 h-5 text-yellow-500"></i>
                Travel Tips
            </h3>
            ${rows}
        </div>`;
}

// ---------------------------------------------------------------------------
// Nearby Destinations
// ---------------------------------------------------------------------------
function renderNearbyPlaces(nearby) {
    const section = document.getElementById('nearby-section');

    if (!nearby || nearby.length === 0) {
        section.innerHTML = '';
        return;
    }

    const cards = nearby.map(p => {
        const attrs = (p.key_attractions || []).slice(0, 3).join(', ');
        return `
        <div class="bg-white rounded-lg border border-gray-100 overflow-hidden hover:shadow-md transition">
            <img src="${p.image_url}" alt="${p.name}"
                class="w-full h-28 object-cover"
                onerror="this.onerror=null;this.src='https://placehold.co/300x200/e2e8f0/64748b?text=${encodeURIComponent(p.name)}'">
            <div class="p-3">
                <h4 class="text-sm font-semibold text-gray-900">${p.name}</h4>
                <p class="text-xs text-gray-500">${p.state} &middot; ${p.distance_km} km away</p>
                ${attrs ? `<p class="text-xs text-gray-400 mt-1 truncate">${attrs}</p>` : ''}
                <div class="flex items-center gap-1 mt-1">
                    <span class="text-yellow-400 text-xs">${'&#9733;'.repeat(Math.min(Math.round(p.popularity_score / 2), 5))}</span>
                    <span class="text-xs text-gray-400">${p.ideal_days}d ideal</span>
                </div>
            </div>
        </div>`;
    }).join('');

    section.innerHTML = `
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 class="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <i data-lucide="map" class="w-5 h-5 text-teal-500"></i>
                Nearby Destinations
                <span class="text-xs text-gray-400 font-normal">If you have time</span>
            </h3>
            <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">${cards}</div>
        </div>`;
}


// ===========================================================================
// PLAN MY TRIP — Modal, Form, Generation, Itinerary Rendering
// ===========================================================================

// ---------------------------------------------------------------------------
// Open / Close modal
// ---------------------------------------------------------------------------
function openTripModal() {
    if (!lastData || !lastData.destination) {
        showToast('Please explore a destination first', 'error');
        return;
    }

    const dest = lastData.destination;
    const places = lastData.famous_places || [];

    // Update modal header
    document.getElementById('trip-modal-title').textContent = 'Plan My Trip';
    document.getElementById('trip-modal-subtitle').textContent = `to ${dest.name}`;

    // Pre-fill days from AI suggestion
    const daysInput = document.getElementById('trip-days');
    daysInput.value = dest.ideal_days || 3;

    // Set min date to today
    const dateInput = document.getElementById('trip-start-date');
    const today = new Date().toISOString().split('T')[0];
    dateInput.min = today;
    if (!dateInput.value) dateInput.value = today;

    // Build place pills from famous places + primary attractions
    const placesList = document.getElementById('trip-places-list');
    const allPlaces = new Set();

    // Add famous places
    places.forEach(p => allPlaces.add(p.name));

    // Add primary attractions from destination info
    (dest.primary_attractions || []).forEach(a => allPlaces.add(a));

    const pills = Array.from(allPlaces).map((name, i) => `
        <label class="place-pill">
            <input type="checkbox" value="${name}" ${i < 6 ? 'checked' : ''}>
            <span>${name}</span>
        </label>`).join('');

    placesList.innerHTML = pills || '<p class="text-xs text-gray-400">No places found — the AI will suggest spots!</p>';

    // Update per-person display
    _updatePerPerson();

    // Wire up budget/members change for live per-person update
    document.getElementById('trip-budget').oninput = _updatePerPerson;
    document.getElementById('trip-members').oninput = _updatePerPerson;

    // Reset states
    document.getElementById('trip-form-section').classList.remove('hidden');
    document.getElementById('trip-loading').classList.add('hidden');
    document.getElementById('trip-error').classList.add('hidden');
    document.getElementById('trip-result').classList.add('hidden');
    document.getElementById('trip-result').innerHTML = '';

    // Open modal
    document.getElementById('trip-modal-overlay').classList.add('open');
    document.body.style.overflow = 'hidden';
    lucide.createIcons();
}

function closeTripModal() {
    document.getElementById('trip-modal-overlay').classList.remove('open');
    document.body.style.overflow = '';
}

function _updatePerPerson() {
    const budget = parseFloat(document.getElementById('trip-budget').value) || 0;
    const members = parseInt(document.getElementById('trip-members').value) || 1;
    const pp = Math.round(budget / members);
    document.getElementById('trip-per-person').textContent = `Per person: ~₹${pp.toLocaleString('en-IN')}`;
}

// ---------------------------------------------------------------------------
// Generate trip plan
// ---------------------------------------------------------------------------
async function generateTripPlan() {
    const dest = lastData?.destination;
    if (!dest) return;

    const members = parseInt(document.getElementById('trip-members').value) || 2;
    const days = parseInt(document.getElementById('trip-days').value) || 3;
    const budget = parseFloat(document.getElementById('trip-budget').value) || 15000;
    const startDate = document.getElementById('trip-start-date').value || '';

    // Gather selected places
    const selectedPlaces = [];
    document.querySelectorAll('#trip-places-list input[type=checkbox]:checked').forEach(cb => {
        selectedPlaces.push(cb.value);
    });

    const btn = document.getElementById('trip-generate-btn');
    const formSection = document.getElementById('trip-form-section');
    const loadingDiv = document.getElementById('trip-loading');
    const errorDiv = document.getElementById('trip-error');
    const resultDiv = document.getElementById('trip-result');

    btn.disabled = true;
    formSection.classList.add('hidden');
    loadingDiv.classList.remove('hidden');
    errorDiv.classList.add('hidden');
    resultDiv.classList.add('hidden');

    try {
        const data = await apiRequest('/ai/plan-trip', {
            method: 'POST',
            body: {
                destination: dest.name,
                places: selectedPlaces,
                days: days,
                budget: budget,
                members: members,
                start_date: startDate,
            },
        });

        if (data.error) throw new Error(data.error);

        loadingDiv.classList.add('hidden');
        renderTripItinerary(data, resultDiv);
        resultDiv.classList.remove('hidden');

    } catch (err) {
        console.error('Trip plan error:', err);
        loadingDiv.classList.add('hidden');
        errorDiv.classList.remove('hidden');
        document.getElementById('trip-error-msg').textContent = err.message || 'Failed to generate trip plan.';
        formSection.classList.remove('hidden');
    }

    btn.disabled = false;
}

// ---------------------------------------------------------------------------
// Render the generated itinerary inside the modal
// ---------------------------------------------------------------------------
const _typeColors = {
    sightseeing: '#6366f1', food: '#f97316', activity: '#22c55e',
    entertainment: '#ec4899', shopping: '#a855f7', transport: '#64748b', rest: '#06b6d4',
};

function renderTripItinerary(data, container) {
    const days = data.days || [];
    const members = data.members || 1;
    const totalCost = data.total_cost || data.budget || 0;

    // --- Summary header ---
    let html = `
        <div class="mb-5">
            <div class="flex items-center justify-between mb-3">
                <h3 class="font-bold text-gray-900 text-lg">${data.title || 'Your Trip Plan'}</h3>
                <button onclick="_backToTripForm()" class="text-xs text-orange-600 hover:text-orange-700 font-medium flex items-center gap-1">
                    <i data-lucide="pencil" class="w-3 h-3"></i> Edit
                </button>
            </div>
            ${data.summary ? `<p class="text-sm text-gray-600 mb-3">${data.summary}</p>` : ''}
            <div class="grid grid-cols-3 gap-3 text-center">
                <div class="bg-orange-50 rounded-xl py-3 px-2">
                    <p class="text-lg font-bold text-orange-600">${days.length}</p>
                    <p class="text-[10px] text-gray-500 uppercase font-medium">Days</p>
                </div>
                <div class="bg-green-50 rounded-xl py-3 px-2">
                    <p class="text-lg font-bold text-green-600">₹${Math.round(totalCost).toLocaleString('en-IN')}</p>
                    <p class="text-[10px] text-gray-500 uppercase font-medium">Total</p>
                </div>
                <div class="bg-blue-50 rounded-xl py-3 px-2">
                    <p class="text-lg font-bold text-blue-600">₹${Math.round(totalCost / members).toLocaleString('en-IN')}</p>
                    <p class="text-[10px] text-gray-500 uppercase font-medium">Per Person</p>
                </div>
            </div>
        </div>`;

    // --- Day-by-day cards ---
    days.forEach(day => {
        const activities = day.activities || [];
        const dayCost = day.day_cost || activities.reduce((s, a) => s + (a.cost || 0), 0);

        html += `
            <div class="itin-day-card">
                <div class="flex items-center justify-between mb-2">
                    <div>
                        <h4 class="font-bold text-gray-900 text-sm">Day ${day.day}${day.theme ? ` — ${day.theme}` : ''}</h4>
                        ${day.date ? `<p class="text-[11px] text-gray-400">${day.date}</p>` : ''}
                    </div>
                    <span class="text-xs font-semibold text-orange-600 bg-orange-50 px-2.5 py-1 rounded-full">₹${Math.round(dayCost).toLocaleString('en-IN')}</span>
                </div>`;

        activities.forEach(act => {
            const typeColor = _typeColors[act.type] || '#94a3b8';
            const cost = act.cost ? `₹${act.cost.toLocaleString('en-IN')}` : '';
            html += `
                <div class="itin-activity">
                    <div class="itin-time">${act.time || ''}</div>
                    <div class="itin-type-dot" style="background:${typeColor}"></div>
                    <div class="flex-1 min-w-0">
                        <p class="text-sm font-medium text-gray-900">${act.activity || ''}</p>
                        ${act.description ? `<p class="text-[11px] text-gray-500 mt-0.5">${act.description}</p>` : ''}
                        <div class="flex items-center gap-3 mt-1 text-[10px] text-gray-400">
                            ${act.duration ? `<span>${act.duration}</span>` : ''}
                            ${cost ? `<span class="font-medium text-gray-600">${cost}</span>` : ''}
                        </div>
                    </div>
                </div>`;
        });

        // Day tips
        if (day.tips && day.tips.length > 0) {
            html += `<div class="mt-2 pt-2 border-t border-gray-50">
                ${day.tips.map(t => `<p class="text-[11px] text-gray-400 flex items-start gap-1.5 mb-0.5">
                    <span class="text-yellow-400 mt-0.5">&#9679;</span>${t}
                </p>`).join('')}
            </div>`;
        }

        html += `</div>`;
    });

    // --- Packing tips & Recommendations ---
    if (data.packing_tips && data.packing_tips.length > 0) {
        html += `
            <div class="bg-blue-50 rounded-xl p-4 mb-4">
                <p class="text-xs font-semibold text-blue-700 uppercase mb-2">Packing Tips</p>
                <div class="flex flex-wrap gap-1.5">
                    ${data.packing_tips.map(t => `<span class="text-[11px] bg-white text-blue-700 px-2.5 py-1 rounded-full border border-blue-100">${t}</span>`).join('')}
                </div>
            </div>`;
    }

    if (data.recommendations && data.recommendations.length > 0) {
        html += `
            <div class="bg-amber-50 rounded-xl p-4">
                <p class="text-xs font-semibold text-amber-700 uppercase mb-2">Recommendations</p>
                ${data.recommendations.map(r => `<p class="text-[11px] text-gray-600 mb-1 flex items-start gap-1.5">
                    <span class="text-amber-400 mt-0.5">&#9733;</span>${r}
                </p>`).join('')}
            </div>`;
    }

    container.innerHTML = html;
    lucide.createIcons();
}

// ---------------------------------------------------------------------------
// Back to form (Edit button in result header)
// ---------------------------------------------------------------------------
function _backToTripForm() {
    document.getElementById('trip-form-section').classList.remove('hidden');
    document.getElementById('trip-result').classList.add('hidden');
    document.getElementById('trip-error').classList.add('hidden');
}


// ===========================================================================
// SARVAM AI — Language Translation & Text-to-Speech
// ===========================================================================

let currentLang = 'en-IN';
let originalTexts = {};    // section -> original English text
let translatedCache = {};  // "section:lang" -> translated text
let currentAudio = null;   // HTMLAudioElement currently playing

const LANGUAGES = {
    'en-IN': 'English', 'hi-IN': 'हिन्दी', 'te-IN': 'తెలుగు',
    'ta-IN': 'தமிழ்', 'kn-IN': 'ಕನ್ನಡ', 'ml-IN': 'മലയാളം',
    'mr-IN': 'मराठी', 'bn-IN': 'বাংলা', 'gu-IN': 'ગુજરાતી',
    'pa-IN': 'ਪੰਜਾਬੀ', 'od-IN': 'ଓଡ଼ିଆ',
};

// Translatable sections — we store their original English content
const TRANSLATABLE_SECTIONS = [
    'things-to-do-section',
    'travel-tips-section',
    'travel-info-section',
];

// ---------------------------------------------------------------------------
// Initialize language bar after results are rendered
// ---------------------------------------------------------------------------
function initLanguageBar() {
    const barSection = document.getElementById('lang-bar-section');
    const pillsContainer = document.getElementById('lang-pills');
    if (!barSection || !pillsContainer) return;

    // Build language pills
    let pillsHtml = '';
    for (const [code, name] of Object.entries(LANGUAGES)) {
        const active = code === 'en-IN' ? ' active' : '';
        pillsHtml += `<button class="lang-pill${active}" data-lang="${code}" onclick="switchLanguage('${code}')">${name}</button>`;
    }
    pillsContainer.innerHTML = pillsHtml;

    // Store original English text from each section
    originalTexts = {};
    TRANSLATABLE_SECTIONS.forEach(id => {
        const el = document.getElementById(id);
        if (el && el.innerHTML.trim()) {
            originalTexts[id] = el.innerHTML;
        }
    });

    currentLang = 'en-IN';
    translatedCache = {};
    barSection.classList.remove('hidden');
    document.getElementById('speak-btn').disabled = false;
    document.getElementById('lang-status').textContent = '';
    lucide.createIcons();
}

// ---------------------------------------------------------------------------
// Switch language
// ---------------------------------------------------------------------------
async function switchLanguage(lang) {
    if (lang === currentLang) return;

    // Update pills
    document.querySelectorAll('.lang-pill').forEach(p => {
        p.classList.toggle('active', p.dataset.lang === lang);
    });

    const status = document.getElementById('lang-status');

    // If switching back to English, restore originals
    if (lang === 'en-IN') {
        TRANSLATABLE_SECTIONS.forEach(id => {
            const el = document.getElementById(id);
            if (el && originalTexts[id]) {
                el.innerHTML = originalTexts[id];
            }
        });
        currentLang = lang;
        status.textContent = '';
        lucide.createIcons();
        return;
    }

    // Translate each section
    status.textContent = `Translating to ${LANGUAGES[lang]}...`;

    // Add shimmer effect
    TRANSLATABLE_SECTIONS.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.classList.add('translating-shimmer');
    });

    for (const sectionId of TRANSLATABLE_SECTIONS) {
        const el = document.getElementById(sectionId);
        if (!el || !originalTexts[sectionId]) continue;

        const cacheKey = `${sectionId}:${lang}`;

        if (translatedCache[cacheKey]) {
            el.innerHTML = translatedCache[cacheKey];
            continue;
        }

        // Extract only visible text content (not HTML) for translation
        const textContent = _extractVisibleText(el);
        if (!textContent.trim()) continue;

        try {
            const data = await apiRequest('/ai/translate', {
                method: 'POST',
                body: { text: textContent, target_lang: lang, source_lang: 'en-IN' },
            });

            if (data.translated_text) {
                // Replace text content in the section while keeping HTML structure
                const translatedHtml = _replaceTextInHtml(originalTexts[sectionId], textContent, data.translated_text);
                translatedCache[cacheKey] = translatedHtml;
                el.innerHTML = translatedHtml;
            }
        } catch (err) {
            console.error(`Translation failed for ${sectionId}:`, err);
            status.textContent = `Translation failed: ${err.message}`;
        }
    }

    // Remove shimmer
    TRANSLATABLE_SECTIONS.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.classList.remove('translating-shimmer');
    });

    currentLang = lang;
    status.textContent = `Showing in ${LANGUAGES[lang]}`;
    lucide.createIcons();
}

// ---------------------------------------------------------------------------
// Extract visible text from HTML element
// ---------------------------------------------------------------------------
function _extractVisibleText(el) {
    // Get all text nodes, joining with spaces
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null);
    const parts = [];
    let node;
    while (node = walker.nextNode()) {
        const t = node.textContent.trim();
        if (t && t.length > 1) parts.push(t);
    }
    return parts.join('. ');
}

// ---------------------------------------------------------------------------
// Replace text in HTML while preserving structure
// ---------------------------------------------------------------------------
function _replaceTextInHtml(originalHtml, originalText, translatedText) {
    // Simple approach: create a temp div, walk text nodes, replace with translated segments
    const div = document.createElement('div');
    div.innerHTML = originalHtml;

    const origParts = originalText.split('. ').filter(p => p.trim());
    const transParts = translatedText.split('. ').filter(p => p.trim());

    // Build a lookup map: original text → translated text
    const textMap = new Map();
    for (let i = 0; i < origParts.length && i < transParts.length; i++) {
        textMap.set(origParts[i].trim(), transParts[i].trim());
    }

    // Walk all text nodes and replace
    const walker = document.createTreeWalker(div, NodeFilter.SHOW_TEXT, null);
    let textNode;
    while (textNode = walker.nextNode()) {
        const t = textNode.textContent.trim();
        if (t.length <= 1) continue;

        // Try exact match first
        if (textMap.has(t)) {
            textNode.textContent = textMap.get(t);
            continue;
        }

        // Try partial match for longer texts
        for (const [orig, trans] of textMap.entries()) {
            if (t.includes(orig) && orig.length > 5) {
                textNode.textContent = textNode.textContent.replace(orig, trans);
            }
        }
    }

    return div.innerHTML;
}

// ---------------------------------------------------------------------------
// Speak current section
// ---------------------------------------------------------------------------
async function speakCurrentSection() {
    const btn = document.getElementById('speak-btn');
    const btnText = document.getElementById('speak-btn-text');

    // If already playing, stop
    if (currentAudio && !currentAudio.paused) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
        currentAudio = null;
        btn.classList.remove('playing');
        btnText.textContent = 'Listen';
        return;
    }

    // Gather text from all visible sections
    let speakText = '';
    TRANSLATABLE_SECTIONS.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            const text = _extractVisibleText(el);
            if (text) speakText += text + '. ';
        }
    });

    if (!speakText.trim()) {
        showToast('No content to speak', 'error');
        return;
    }

    // Trim to 1500 chars (Sarvam Bulbul v2 limit)
    speakText = speakText.substring(0, 1500);

    btn.disabled = true;
    btnText.textContent = 'Generating audio...';

    try {
        const data = await apiRequest('/ai/speak', {
            method: 'POST',
            body: {
                text: speakText,
                lang: currentLang || 'hi-IN',
                speaker: 'anushka',
            },
        });

        if (data.audio) {
            // Convert base64 to Blob for reliable playback
            const byteChars = atob(data.audio);
            const byteArray = new Uint8Array(byteChars.length);
            for (let i = 0; i < byteChars.length; i++) {
                byteArray[i] = byteChars.charCodeAt(i);
            }
            const blob = new Blob([byteArray], { type: 'audio/wav' });
            const blobUrl = URL.createObjectURL(blob);

            currentAudio = new Audio(blobUrl);

            currentAudio.oncanplaythrough = async () => {
                try {
                    await currentAudio.play();
                    btn.classList.add('playing');
                    btn.disabled = false;
                    btnText.textContent = 'Stop';
                } catch (playErr) {
                    console.error('Audio play failed:', playErr);
                    showToast('Browser blocked audio playback. Click again.', 'error');
                    btn.disabled = false;
                    btnText.textContent = 'Listen';
                    URL.revokeObjectURL(blobUrl);
                    currentAudio = null;
                }
            };

            currentAudio.onended = () => {
                btn.classList.remove('playing');
                btnText.textContent = 'Listen';
                URL.revokeObjectURL(blobUrl);
                currentAudio = null;
            };

            currentAudio.onerror = (e) => {
                console.error('Audio error:', e);
                btn.classList.remove('playing');
                btn.disabled = false;
                btnText.textContent = 'Listen';
                showToast('Audio playback failed', 'error');
                URL.revokeObjectURL(blobUrl);
                currentAudio = null;
            };

            // Start loading
            currentAudio.load();
        } else {
            showToast('No audio generated', 'error');
            btn.disabled = false;
            btnText.textContent = 'Listen';
        }
    } catch (err) {
        console.error('Speak error:', err);
        showToast(err.message || 'Speech generation failed', 'error');
        btn.disabled = false;
        btnText.textContent = 'Listen';
    }
}
