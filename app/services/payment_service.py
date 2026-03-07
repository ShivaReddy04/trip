import uuid
import stripe
from datetime import datetime, timezone
from flask import current_app
from sqlalchemy.orm.attributes import flag_modified
from app.extensions import db
from app.models.booking import find_booking_by_id


def _init_stripe():
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']


def create_checkout_session(booking_id, user_id, success_url, cancel_url):
    """Create a Stripe Checkout Session for a booking."""
    _init_stripe()

    booking = find_booking_by_id(booking_id)
    if not booking:
        return None, 'Booking not found.'

    if str(booking.user_id) != str(user_id):
        return None, 'Access denied.'

    if booking.status == 'cancelled':
        return None, 'Cannot pay for a cancelled booking.'

    if booking.payment and booking.payment.get('status') == 'completed':
        return None, 'Payment already completed.'

    # Get package info for the line item description
    from app.models.package import find_package_by_id
    package = find_package_by_id(booking.package_id)
    package_name = package.title if package else f'Booking {booking.booking_id}'

    # Amount in cents for Stripe
    amount_cents = int(round(booking.total_amount * 100))

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': (booking.currency or 'usd').lower(),
                    'product_data': {
                        'name': package_name,
                        'description': f'Booking ID: {booking.booking_id} | {booking.travelers.__len__() if booking.travelers else 1} traveler(s)',
                    },
                    'unit_amount': amount_cents,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'booking_id': str(booking.id),
                'booking_code': booking.booking_id,
            },
        )
        return {'sessionId': session.id, 'url': session.url}, None
    except stripe.error.StripeError as e:
        return None, str(e)


def handle_checkout_completed(session_obj):
    """Handle successful Stripe checkout.completed event."""
    booking_db_id = session_obj.get('metadata', {}).get('booking_id')
    if not booking_db_id:
        return

    booking = find_booking_by_id(booking_db_id)
    if not booking:
        return

    # Already processed
    if booking.payment and booking.payment.get('status') == 'completed':
        return

    payment_intent_id = session_obj.get('payment_intent', '')
    amount_total = session_obj.get('amount_total', 0) / 100.0

    now = datetime.now(timezone.utc).isoformat()
    history = booking.payment.get('history', []) if booking.payment else []
    history.append({
        'action': 'payment_completed',
        'amount': amount_total,
        'method': 'stripe',
        'transactionId': payment_intent_id,
        'timestamp': now,
    })

    booking.payment = {
        'status': 'completed',
        'method': 'stripe',
        'transactionId': payment_intent_id,
        'paidAmount': amount_total,
        'refundAmount': 0,
        'history': history,
    }
    flag_modified(booking, 'payment')

    if booking.status == 'pending':
        booking.status = 'confirmed'

    booking.updated_at = datetime.now(timezone.utc)
    db.session.commit()


def process_payment(booking_id, user_id, payment_method='card', card_info=None):
    """Fallback demo payment (used when Stripe keys are not configured)."""
    booking = find_booking_by_id(booking_id)
    if not booking:
        return None, 'Booking not found.'

    if str(booking.user_id) != str(user_id):
        return None, 'Access denied.'

    if booking.status == 'cancelled':
        return None, 'Cannot pay for a cancelled booking.'

    if booking.payment and booking.payment.get('status') == 'completed':
        return None, 'Payment already completed.'

    txn_id = f'TXN-{uuid.uuid4().hex[:12].upper()}'
    now = datetime.now(timezone.utc).isoformat()
    history = booking.payment.get('history', []) if booking.payment else []
    history.append({
        'action': 'payment_completed',
        'amount': booking.total_amount,
        'method': payment_method,
        'transactionId': txn_id,
        'timestamp': now,
    })

    booking.payment = {
        'status': 'completed',
        'method': payment_method,
        'transactionId': txn_id,
        'paidAmount': booking.total_amount,
        'refundAmount': 0,
        'history': history,
    }
    flag_modified(booking, 'payment')

    if booking.status == 'pending':
        booking.status = 'confirmed'

    booking.updated_at = datetime.now(timezone.utc)
    db.session.commit()

    return {
        'success': True,
        'transactionId': txn_id,
        'amount': booking.total_amount,
        'method': payment_method,
        'bookingId': booking.booking_id,
        'bookingDbId': booking.id,
    }, None
