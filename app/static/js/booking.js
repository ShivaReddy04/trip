// Price calculation for package booking
function initBookingCalc(basePrice, perPerson) {
    const countInput = document.getElementById('traveler-count');
    const countDisplay = document.getElementById('count-display');
    const subtotal = document.getElementById('subtotal');
    const totalPrice = document.getElementById('total-price');

    if (!countInput) return;

    countInput.addEventListener('input', function() {
        const count = parseInt(this.value) || 1;
        countDisplay.textContent = count;
        const total = perPerson ? basePrice * count : basePrice;
        subtotal.textContent = '$' + total.toFixed(2);
        totalPrice.textContent = '$' + total.toFixed(2);
    });
}
