// Review AJAX interactions
async function markHelpful(reviewId) {
    try {
        const res = await apiRequest('/api/reviews/' + reviewId + '/helpful', { method: 'POST' });
        const el = document.getElementById('helpful-' + reviewId);
        if (el) el.textContent = res.helpfulCount;
        showToast('Marked as helpful', 'success');
    } catch (err) {
        showToast(err.message || 'Failed to mark as helpful', 'error');
    }
}

async function submitVendorReply(reviewId) {
    const input = document.getElementById('reply-input-' + reviewId);
    if (!input || !input.value.trim()) return;

    try {
        await apiRequest('/api/reviews/' + reviewId + '/reply', {
            method: 'POST',
            body: { content: input.value.trim() }
        });
        showToast('Reply posted', 'success');
        location.reload();
    } catch (err) {
        showToast(err.message || 'Failed to post reply', 'error');
    }
}
