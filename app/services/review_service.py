from app.models.review import (
    create_review, get_package_reviews, get_user_reviews,
    add_vendor_reply, mark_helpful, get_rating_summary,
    check_existing_review
)
from app.models.booking import find_booking_by_id
from app.models.package import find_package_by_id, update_package_rating


def create_new_review(user_id, data):
    """Create review. Returns (review, error)."""
    booking = find_booking_by_id(data.get('bookingId'))
    if not booking:
        return None, 'Booking not found.'
    if str(booking.user_id) != str(user_id):
        return None, 'You can only review your own bookings.'
    if booking.status != 'completed':
        return None, 'You can only review completed bookings.'

    existing = check_existing_review(user_id, data['bookingId'])
    if existing:
        return None, 'You have already reviewed this booking.'

    rating = int(data.get('rating', 0))
    if rating < 1 or rating > 5:
        return None, 'Rating must be between 1 and 5.'

    review_data = {
        'packageId': data['packageId'],
        'userId': user_id,
        'bookingId': data['bookingId'],
        'rating': rating,
        'title': data.get('title', ''),
        'content': data.get('content', ''),
        'images': data.get('images', []),
    }
    review = create_review(review_data)

    # Update package rating
    update_package_rating(data['packageId'])

    return review, None


def reply_to_review(review_id, vendor_id, content):
    """Vendor reply. Returns (review, error)."""
    from app.models.review import find_review_by_id
    review = find_review_by_id(review_id)
    if not review:
        return None, 'Review not found.'

    package = find_package_by_id(review.package_id)
    if not package or str(package.vendor_id) != str(vendor_id):
        return None, 'You can only reply to reviews on your packages.'

    return add_vendor_reply(review_id, content), None
