/**
 * Career Prep Agent — minimal client-side JS.
 *
 * Responsibilities:
 * 1. Inject the CSRF token into every HTMX request.
 * 2. Utility helpers for flash messages.
 */

// --- CSRF token injection ---
function getCookie(name) {
    const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? match[2] : '';
}

document.addEventListener('htmx:configRequest', function (event) {
    const token = getCookie('csrf_token');
    if (token) {
        event.detail.headers['X-CSRF-Token'] = token;
    }
});

// --- Auto-dismiss flash messages after 5s ---
document.addEventListener('htmx:afterSettle', function () {
    document.querySelectorAll('.flash[data-auto-dismiss]').forEach(function (el) {
        setTimeout(function () {
            el.style.transition = 'opacity 0.3s';
            el.style.opacity = '0';
            setTimeout(function () { el.remove(); }, 300);
        }, 5000);
    });
});
