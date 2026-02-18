# Payment service - Demo mode (no external payment providers)

import uuid
from datetime import datetime, timezone
from sqlalchemy.orm.attributes import flag_modified
from app.extensions import db
from app.models.booking import find_booking_by_id


def process_payment(booking_id, user_id, payment_method='card', card_info=None):
    """Demo: simulate payment processing and update booking."""
    booking = find_booking_by_id(booking_id)
    if not booking:
        return None, 'Booking not found.'

    if str(booking.user_id) != str(user_id):
        return None, 'Access denied.'

    if booking.status == 'cancelled':
        return None, 'Cannot pay for a cancelled booking.'

    if booking.payment and booking.payment.get('status') == 'completed':
        return None, 'Payment already completed.'

    # Generate a demo transaction ID
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

    # Move booking status to confirmed after payment
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


def create_payment_intent(booking_id, method='stripe', amount=None):
    """Demo: return mock payment intent."""
    return {
        'demo': True,
        'message': 'Payment processing is a demo feature.',
        'bookingId': booking_id,
        'method': method,
    }, None
