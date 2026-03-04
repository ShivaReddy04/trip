// Global JS - Flash dismiss, mobile menu, AJAX helpers

document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss flash messages after 5 seconds
    document.querySelectorAll('.flash-msg').forEach(function(msg) {
        setTimeout(function() { msg.remove(); }, 5000);
    });

    // Mobile menu toggle
    const menuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    if (menuBtn && mobileMenu) {
        menuBtn.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
    }

    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('[x-data]')) {
            document.querySelectorAll('[x-data] > div:last-child').forEach(function(el) {
                if (!el.classList.contains('hidden')) {
                    el.classList.add('hidden');
                }
            });
        }
    });
});

// CSRF token helper
function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.content : '';
}

// Generic AJAX helper
async function apiRequest(url, options = {}) {
    const defaults = {
        headers: {},
        credentials: 'same-origin',
    };
    const config = { ...defaults, ...options };
    config.headers = { ...defaults.headers, ...options.headers };

    // Add CSRF header to all mutating requests
    const csrfToken = getCsrfToken();
    if (csrfToken) {
        config.headers['X-CSRFToken'] = csrfToken;
    }

    // Auto-set Content-Type and stringify body for JSON requests
    const isFormData = config.body instanceof FormData;
    if (!isFormData && !config.headers['Content-Type']) {
        config.headers['Content-Type'] = 'application/json';
    }
    if (config.headers['Content-Type'] === 'application/json' && config.body && typeof config.body !== 'string') {
        config.body = JSON.stringify(config.body);
    }

    // Allow long-running requests (e.g. itinerary generation) up to 3 minutes
    const timeoutMs = config.timeout || 180000;
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    config.signal = controller.signal;

    try {
        const response = await fetch(url, config);
        clearTimeout(timer);
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Request failed');
        }
        return data;
    } catch (error) {
        clearTimeout(timer);
        if (error.name === 'AbortError') {
            console.error('API Error: Request timed out');
            throw new Error('Request timed out. Please try again.');
        }
        console.error('API Error:', error);
        throw error;
    }
}

// Show toast notification
function showToast(message, type = 'info') {
    const colors = {
        success: 'bg-green-500',
        error: 'bg-red-500',
        warning: 'bg-yellow-500',
        info: 'bg-blue-500',
    };
    const toast = document.createElement('div');
    toast.className = `fixed bottom-4 right-4 ${colors[type]} text-white px-6 py-3 rounded-lg shadow-lg z-50 transition-all transform translate-y-0 opacity-100`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(function() {
        toast.classList.add('opacity-0', 'translate-y-2');
        setTimeout(function() { toast.remove(); }, 300);
    }, 3000);
}
