import hmac
import hashlib
import json
import stripe
from flask import Blueprint, request, jsonify, session, current_app, url_for
from app.models.booking import find_booking_by_id
from app.services.payment_service import (
    create_checkout_session,
    handle_checkout_completed,
    process_payment,
)
from app.utils.decorators import login_required

payments_bp = Blueprint('payments', __name__)


@payments_bp.route('/create-checkout-session', methods=['POST'])
@login_required
def create_stripe_session():
    """Create a Stripe Checkout Session and return the URL."""
    data = request.get_json()
    if not data or not data.get('bookingId'):
        return jsonify({'error': 'bookingId is required'}), 400

    booking_id = data['bookingId']
    user_id = session['user_id']

    success_url = request.host_url.rstrip('/') + url_for(
        'bookings.payment_success', booking_id=booking_id
    )
    cancel_url = request.host_url.rstrip('/') + url_for(
        'bookings.checkout', booking_id=booking_id
    )

    result, error = create_checkout_session(
        booking_id, user_id, success_url, cancel_url
    )
    if error:
        return jsonify({'error': error}), 400

    return jsonify(result)


@payments_bp.route('/process', methods=['POST'])
@login_required
def process():
    """Fallback demo payment when Stripe is not configured."""
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
    """Handle Stripe webhook events."""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature', '')
    webhook_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET', '')

    if not webhook_secret:
        current_app.logger.warning('Stripe webhook secret not configured')
        return jsonify({'error': 'Webhook secret not configured'}), 400

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Invalid signature'}), 400

    if event['type'] == 'checkout.session.completed':
        session_obj = event['data']['object']
        handle_checkout_completed(session_obj)

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
