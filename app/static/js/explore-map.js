// Leaflet map for Explore page
let map, markers = [];

document.addEventListener('DOMContentLoaded', function() {
    map = L.map('explore-map').setView([20, 0], 2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
        maxZoom: 18,
    }).addTo(map);

    // Search on Enter key
    document.getElementById('search-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') searchPlaces();
    });
});

async function searchPlaces() {
    const query = document.getElementById('search-input').value.trim();
    const category = document.getElementById('category-select').value;
    if (!query) return;

    const loading = document.getElementById('results-loading');
    const resultsList = document.getElementById('results-list');
    const title = document.getElementById('results-title');

    loading.classList.remove('hidden');
    resultsList.innerHTML = '';
    title.textContent = `Places in "${query}"`;

    try {
        const res = await apiRequest(`/api/maps/famous-places?location=${encodeURIComponent(query)}&category=${category}`);
        const places = res.results || [];

        // Clear markers
        markers.forEach(m => map.removeLayer(m));
        markers = [];

        if (places.length === 0) {
            resultsList.innerHTML = '<p class="text-gray-500 text-sm py-4 text-center">No places found</p>';
            loading.classList.add('hidden');
            return;
        }

        // Add markers and cards
        const bounds = [];
        places.forEach(function(place, i) {
            if (place.location) {
                const lat = place.location.lat;
                const lng = place.location.lng;
                const marker = L.marker([lat, lng]).addTo(map);
                marker.bindPopup(`<b>${place.name}</b><br>${place.address || ''}<br>Rating: ${place.rating || 'N/A'}`);
                markers.push(marker);
                bounds.push([lat, lng]);
            }

            const card = document.createElement('div');
            card.className = 'p-3 border border-gray-100 rounded-lg hover:bg-gray-50 cursor-pointer transition';
            card.innerHTML = `
                <div class="flex items-start space-x-3">
                    ${place.photo ? `<img src="${place.photo}" class="w-16 h-16 rounded-lg object-cover shrink-0">` : '<div class="w-16 h-16 rounded-lg bg-gray-100 shrink-0 flex items-center justify-center"><i data-lucide="map-pin" class="w-6 h-6 text-gray-300"></i></div>'}
                    <div class="min-w-0">
                        <h4 class="font-medium text-gray-900 text-sm truncate">${place.name}</h4>
                        <p class="text-xs text-gray-500 truncate">${place.address || ''}</p>
                        ${place.rating ? `<div class="flex items-center mt-1"><i data-lucide="star" class="w-3 h-3 text-yellow-400 fill-yellow-400"></i><span class="text-xs ml-1">${place.rating} (${place.totalRatings || 0})</span></div>` : ''}
                    </div>
                </div>
            `;
            card.addEventListener('click', function() {
                if (place.location) {
                    map.setView([place.location.lat, place.location.lng], 15);
                    markers[i]?.openPopup();
                }
            });
            resultsList.appendChild(card);
        });

        // Fit bounds
        if (bounds.length > 0) {
            map.fitBounds(bounds, { padding: [50, 50] });
        }

        // Refresh Lucide icons for new elements
        lucide.createIcons();
    } catch (err) {
        resultsList.innerHTML = `<p class="text-red-500 text-sm py-4 text-center">${err.message || 'Search failed'}</p>`;
    }

    loading.classList.add('hidden');
}
