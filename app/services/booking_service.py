from datetime import datetime, timezone
from app.models.booking import (
    create_booking, find_booking_by_id, get_user_bookings,
    get_vendor_bookings, cancel_booking, confirm_booking,
    complete_booking, get_vendor_stats, calculate_total_amount
)
from app.models.package import find_package_by_id
from app.utils.validators import safe_int


def create_new_booking(user_id, data):
    """Create a booking. Returns (booking, error)."""
    package = find_package_by_id(data.get('packageId'))
    if not package:
        return None, 'Package not found.'
    if package.status != 'published':
        return None, 'Package is not available for booking.'

    traveler_count = safe_int(data.get('travelers'), default=1, min_val=1)
    avail = package.availability or {}
    min_group = avail.get('minGroupSize', 1)
    max_group = avail.get('maxGroupSize', 100)

    if traveler_count < min_group or traveler_count > max_group:
        return None, f'Traveler count must be between {min_group} and {max_group}.'

    start_date = data.get('startDate')
    total = calculate_total_amount(package, traveler_count, start_date)

    # Build travelers list
    travelers = []
    for i in range(traveler_count):
        travelers.append({
            'name': data.get(f'travelerName_{i}', f'Traveler {i+1}'),
            'age': safe_int(data.get(f'travelerAge_{i}'), default=30, min_val=1, max_val=120),
            'gender': data.get(f'travelerGender_{i}', 'other'),
        })

    # If simple form (no individual traveler details), fill with placeholder
    if not data.get('travelerName_0'):
        travelers = [{'name': f'Traveler {i+1}', 'age': 30, 'gender': 'other'} for i in range(traveler_count)]

    # Calculate end date
    duration_days = (package.duration or {}).get('days', 1)

    booking_data = {
        'packageId': str(package.id),
        'userId': user_id,
        'vendorId': str(package.vendor_id),
        'travelers': travelers,
        'travelDates': {
            'start': start_date,
            'end': data.get('endDate', start_date),
        },
        'totalAmount': total,
        'currency': (package.pricing or {}).get('currency', 'USD'),
        'specialRequests': data.get('specialRequests', ''),
    }

    booking = create_booking(booking_data)
    return booking, None


def get_booking_detail(booking_id, user_id, role='traveler'):
    """Get booking with authorization check."""
    booking = find_booking_by_id(booking_id)
    if not booking:
        return None, 'Booking not found.'
    if role == 'vendor':
        if str(booking.vendor_id) != str(user_id):
            return None, 'Access denied.'
    else:
        if str(booking.user_id) != str(user_id):
            return None, 'Access denied.'
    return booking, None


def cancel_user_booking(booking_id, user_id, reason=''):
    """Cancel a booking. Returns (booking, error)."""
    booking = find_booking_by_id(booking_id)
    if not booking:
        return None, 'Booking not found.'
    if str(booking.user_id) != str(user_id):
        return None, 'Access denied.'
    if booking.status in ('cancelled', 'completed'):
        return None, f'Cannot cancel a {booking.status} booking.'
    return cancel_booking(booking_id, reason), None


def confirm_vendor_booking(booking_id, vendor_id):
    booking = find_booking_by_id(booking_id)
    if not booking:
        return None, 'Booking not found.'
    if str(booking.vendor_id) != str(vendor_id):
        return None, 'Access denied.'
    if booking.status != 'pending':
        return None, 'Only pending bookings can be confirmed.'
    return confirm_booking(booking_id), None


def complete_vendor_booking(booking_id, vendor_id):
    booking = find_booking_by_id(booking_id)
    if not booking:
        return None, 'Booking not found.'
    if str(booking.vendor_id) != str(vendor_id):
        return None, 'Access denied.'
    if booking.status != 'confirmed':
        return None, 'Only confirmed bookings can be completed.'
    return complete_booking(booking_id), None
