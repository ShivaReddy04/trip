from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.services.booking_service import (
    create_new_booking, get_booking_detail,
    cancel_user_booking
)
from app.models.booking import get_user_bookings
from app.models.package import find_package_by_id
from app.utils.decorators import login_required
from app.utils.helpers import paginate_args

bookings_bp = Blueprint('bookings', __name__, template_folder='../templates')


@bookings_bp.route('/')
@login_required
def my_bookings():
    user_id = session['user_id']
    page, limit = paginate_args(request)
    status = request.args.get('status', '')

    bookings, total = get_user_bookings(user_id, status=status or None, page=page, limit=limit)
    total_pages = (total + limit - 1) // limit

    # Fetch package info for each booking
    booking_packages = {}
    for b in bookings:
        pid = str(b.package_id)
        if pid not in booking_packages:
            booking_packages[pid] = find_package_by_id(pid)

    return render_template('pages/bookings.html',
        bookings=bookings, booking_packages=booking_packages,
        page=page, total=total, total_pages=total_pages,
        current_status=status,
        endpoint='bookings.my_bookings',
        kwargs={'status': status} if status else {})


@bookings_bp.route('/create', methods=['POST'])
@login_required
def create():
    user_id = session['user_id']
    data = {
        'packageId': request.form.get('packageId'),
        'travelers': request.form.get('travelers', 1),
        'startDate': request.form.get('startDate'),
        'endDate': request.form.get('endDate', request.form.get('startDate')),
        'specialRequests': request.form.get('specialRequests', ''),
    }

    booking, error = create_new_booking(user_id, data)
    if error:
        flash(error, 'danger')
        return redirect(request.referrer or url_for('packages.browse'))

    flash(f'Booking {booking.booking_id} created! Please complete payment.', 'success')
    return redirect(url_for('bookings.checkout', booking_id=str(booking.id)))


@bookings_bp.route('/<booking_id>')
@login_required
def detail(booking_id):
    user_id = session['user_id']
    booking, error = get_booking_detail(booking_id, user_id)
    if error:
        flash(error, 'danger')
        return redirect(url_for('bookings.my_bookings'))

    package = find_package_by_id(booking.package_id)
    return render_template('pages/booking_detail.html', booking=booking, package=package)


@bookings_bp.route('/<booking_id>/checkout')
@login_required
def checkout(booking_id):
    user_id = session['user_id']
    booking, error = get_booking_detail(booking_id, user_id)
    if error:
        flash(error, 'danger')
        return redirect(url_for('bookings.my_bookings'))

    # If already paid, redirect to detail
    if booking.payment and booking.payment.get('status') == 'completed':
        flash('Payment already completed for this booking.', 'info')
        return redirect(url_for('bookings.detail', booking_id=booking_id))

    # If cancelled, redirect to detail
    if booking.status == 'cancelled':
        flash('This booking has been cancelled.', 'danger')
        return redirect(url_for('bookings.detail', booking_id=booking_id))

    package = find_package_by_id(booking.package_id)
    return render_template('pages/checkout.html', booking=booking, package=package)


@bookings_bp.route('/<booking_id>/payment-success')
@login_required
def payment_success(booking_id):
    user_id = session['user_id']
    booking, error = get_booking_detail(booking_id, user_id)
    if error:
        flash(error, 'danger')
        return redirect(url_for('bookings.my_bookings'))

    package = find_package_by_id(booking.package_id)
    return render_template('pages/payment_success.html', booking=booking, package=package)


@bookings_bp.route('/<booking_id>/cancel', methods=['POST'])
@login_required
def cancel(booking_id):
    user_id = session['user_id']
    reason = request.form.get('reason', '')
    booking, error = cancel_user_booking(booking_id, user_id, reason)
    if error:
        flash(error, 'danger')
    else:
        flash('Booking cancelled successfully.', 'success')
    return redirect(url_for('bookings.detail', booking_id=booking_id))
