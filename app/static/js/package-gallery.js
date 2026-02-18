// Image gallery for package detail page
document.addEventListener('DOMContentLoaded', function() {
    const thumbs = document.querySelectorAll('.gallery-thumb');
    const mainImg = document.getElementById('main-image');

    if (!mainImg || thumbs.length === 0) return;

    thumbs.forEach(function(thumb) {
        thumb.addEventListener('click', function() {
            mainImg.src = this.src;
            thumbs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
        });
    });
});
