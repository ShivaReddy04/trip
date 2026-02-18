// Checkout page - payment method switching and form submission

let selectedMethod = 'card';

// Payment method switching
document.querySelectorAll('.payment-method-btn').forEach(btn => {
    btn.addEventListener('click', function () {
        const method = this.dataset.method;
        selectedMethod = method;

        // Update button styles
        document.querySelectorAll('.payment-method-btn').forEach(b => {
            b.classList.remove('active', 'border-primary-500', 'bg-primary-50');
            b.classList.add('border-gray-200');
            const icon = b.querySelector('svg') || b.querySelector('i');
            if (icon) { icon.classList.remove('text-primary-600'); icon.classList.add('text-gray-500'); }
            const label = b.querySelector('span');
            if (label) { label.classList.remove('text-primary-700'); label.classList.add('text-gray-600'); }
        });
        this.classList.add('active', 'border-primary-500', 'bg-primary-50');
        this.classList.remove('border-gray-200');
        const activeIcon = this.querySelector('svg') || this.querySelector('i');
        if (activeIcon) { activeIcon.classList.remove('text-gray-500'); activeIcon.classList.add('text-primary-600'); }
        const activeLabel = this.querySelector('span');
        if (activeLabel) { activeLabel.classList.remove('text-gray-600'); activeLabel.classList.add('text-primary-700'); }

        // Show/hide forms
        document.getElementById('card-form').classList.toggle('hidden', method !== 'card');
        document.getElementById('upi-form').classList.toggle('hidden', method !== 'upi');
        document.getElementById('netbanking-form').classList.toggle('hidden', method !== 'netbanking');
    });
});

// Card number formatting (add spaces every 4 digits)
const cardNumberInput = document.getElementById('card-number');
if (cardNumberInput) {
    cardNumberInput.addEventListener('input', function () {
        let v = this.value.replace(/\s/g, '').replace(/\D/g, '');
        let formatted = '';
        for (let i = 0; i < v.length && i < 16; i++) {
            if (i > 0 && i % 4 === 0) formatted += ' ';
            formatted += v[i];
        }
        this.value = formatted;
    });
}

// Expiry date formatting (MM/YY)
const expiryInput = document.getElementById('card-expiry');
if (expiryInput) {
    expiryInput.addEventListener('input', function () {
        let v = this.value.replace(/\D/g, '');
        if (v.length >= 2) {
            v = v.substring(0, 2) + '/' + v.substring(2, 4);
        }
        this.value = v;
    });
}

// CVV - only digits
const cvvInput = document.getElementById('card-cvv');
if (cvvInput) {
    cvvInput.addEventListener('input', function () {
        this.value = this.value.replace(/\D/g, '').substring(0, 4);
    });
}

function validateForm() {
    if (selectedMethod === 'card') {
        const name = document.getElementById('card-name').value.trim();
        const number = document.getElementById('card-number').value.replace(/\s/g, '');
        const expiry = document.getElementById('card-expiry').value;
        const cvv = document.getElementById('card-cvv').value;

        if (!name) return 'Please enter the cardholder name.';
        if (number.length < 13) return 'Please enter a valid card number.';
        if (!/^\d{2}\/\d{2}$/.test(expiry)) return 'Please enter a valid expiry date (MM/YY).';
        if (cvv.length < 3) return 'Please enter a valid CVV.';
    } else if (selectedMethod === 'upi') {
        const upiId = document.getElementById('upi-id').value.trim();
        if (!upiId || !upiId.includes('@')) return 'Please enter a valid UPI ID.';
    } else if (selectedMethod === 'netbanking') {
        const bank = document.getElementById('bank-select').value;
        if (!bank) return 'Please select a bank.';
    }
    return null;
}

function showPaymentError(msg) {
    const el = document.getElementById('payment-error');
    document.getElementById('payment-error-msg').textContent = msg;
    el.classList.remove('hidden');
    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function hidePaymentError() {
    document.getElementById('payment-error').classList.add('hidden');
}

async function submitPayment() {
    hidePaymentError();

    const error = validateForm();
    if (error) {
        showPaymentError(error);
        return;
    }

    const btn = document.getElementById('pay-btn');
    const originalHtml = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<div class="spinner mx-auto"></div><span class="ml-2">Processing payment...</span>';

    try {
        // Simulate a short delay for realism
        await new Promise(resolve => setTimeout(resolve, 1500));

        const result = await apiRequest('/api/payments/process', {
            method: 'POST',
            body: {
                bookingId: BOOKING_ID,
                method: selectedMethod,
            },
        });

        if (result.success) {
            // Show brief success toast before redirecting
            showToast('Payment successful!', 'success');
            setTimeout(() => {
                window.location.href = SUCCESS_URL;
            }, 500);
        } else {
            throw new Error(result.error || 'Payment failed');
        }
    } catch (err) {
        showPaymentError(err.message || 'Payment failed. Please try again.');
        btn.disabled = false;
        btn.innerHTML = originalHtml;
        lucide.createIcons();
    }
}
