import hmac
import hashlib
from flask import Blueprint, request, jsonify, session, current_app
from app.models.booking import find_booking_by_id
from app.services.payment_service import process_payment
from app.utils.decorators import login_required

payments_bp = Blueprint('payments', __name__)


def verify_stripe_signature(payload, sig_header, secret):
    """Verify Stripe webhook signature."""
    if not secret:
        return False, 'Stripe webhook secret is not configured.'
    if not sig_header:
        return False, 'Missing Stripe-Signature header.'

    try:
        elements = dict(pair.split('=', 1) for pair in sig_header.split(','))
        timestamp = elements.get('t', '')
        expected_sig = elements.get('v1', '')
    except (ValueError, AttributeError):
        return False, 'Malformed Stripe-Signature header.'

    signed_payload = f'{timestamp}.{payload}'.encode()
    computed = hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(computed, expected_sig):
        return False, 'Signature verification failed.'
    return True, None


def verify_razorpay_signature(payload, sig_header, secret):
    """Verify Razorpay webhook signature."""
    if not secret:
        return False, 'Razorpay webhook secret is not configured.'
    if not sig_header:
        return False, 'Missing X-Razorpay-Signature header.'

    computed = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(computed, sig_header):
        return False, 'Signature verification failed.'
    return True, None


@payments_bp.route('/create-intent', methods=['POST'])
@login_required
def create_intent():
    data = request.get_json()
    if not data or not data.get('bookingId'):
        return jsonify({'error': 'bookingId is required'}), 400

    booking = find_booking_by_id(data['bookingId'])
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404

    # Demo mode: return a mock payment intent
    return jsonify({
        'demo': True,
        'message': 'Payment processing is a demo feature.',
        'bookingId': data['bookingId'],
        'amount': booking.total_amount,
    })


@payments_bp.route('/process', methods=['POST'])
@login_required
def process():
    """Process a demo payment for a booking."""
    data = request.get_json()
    if not data or not data.get('bookingId'):
        return jsonify({'error': 'bookingId is required'}), 400

    user_id = session['user_id']
    booking_id = data['bookingId']
    payment_method = data.get('method', 'card')
    card_info = data.get('cardInfo')

    result, error = process_payment(booking_id, user_id, payment_method, card_info)
    if error:
        return jsonify({'error': error}), 400

    return jsonify(result)


@payments_bp.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    secret = current_app.config['STRIPE_WEBHOOK_SECRET']
    ok, error = verify_stripe_signature(
        request.get_data(as_text=True),
        request.headers.get('Stripe-Signature', ''),
        secret,
    )
    if not ok:
        current_app.logger.warning('Stripe webhook rejected: %s', error)
        return jsonify({'error': error}), 400

    # TODO: process the verified event
    return jsonify({'received': True})


@payments_bp.route('/webhook/razorpay', methods=['POST'])
def razorpay_webhook():
    secret = current_app.config['RAZORPAY_WEBHOOK_SECRET']
    ok, error = verify_razorpay_signature(
        request.get_data(as_text=True),
        request.headers.get('X-Razorpay-Signature', ''),
        secret,
    )
    if not ok:
        current_app.logger.warning('Razorpay webhook rejected: %s', error)
        return jsonify({'error': error}), 400

    # TODO: process the verified event
    return jsonify({'received': True})


@payments_bp.route('/<booking_id>', methods=['GET'])
@login_required
def payment_status(booking_id):
    booking = find_booking_by_id(booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    return jsonify({
        'bookingId': booking.booking_id,
        'payment': booking.payment,
        'totalAmount': booking.total_amount,
    })
