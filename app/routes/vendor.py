from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.decorators import vendor_required
from app.models.package import get_vendor_packages, find_package_by_id
from app.models.booking import get_vendor_bookings, get_vendor_stats
from app.services.package_service import (
    create_new_package, update_existing_package,
    update_package_status, delete_vendor_package
)
from app.services.booking_service import confirm_vendor_booking, complete_vendor_booking
from app.utils.helpers import paginate_args
from app.utils.validators import safe_int, safe_float

vendor_bp = Blueprint('vendor', __name__, template_folder='../templates')

CATEGORIES = ['adventure', 'beach', 'cultural', 'wildlife', 'honeymoon', 'family', 'pilgrimage']


@vendor_bp.route('/dashboard')
@vendor_required
def dashboard():
    user_id = session['user_id']
    stats = get_vendor_stats(user_id)
    recent_bookings, _ = get_vendor_bookings(user_id, page=1, limit=5)
    packages, pkg_total = get_vendor_packages(user_id, page=1, limit=5)

    # Enrich bookings with package info
    for b in recent_bookings:
        b._package = find_package_by_id(b.package_id)

    return render_template('vendor/dashboard.html',
        stats=stats, recent_bookings=recent_bookings,
        packages=packages, pkg_total=pkg_total)


@vendor_bp.route('/packages')
@vendor_required
def packages():
    user_id = session['user_id']
    page, limit = paginate_args(request)
    packages, total = get_vendor_packages(user_id, page, limit)
    total_pages = (total + limit - 1) // limit
    return render_template('vendor/packages.html',
        packages=packages, page=page, total=total,
        total_pages=total_pages,
        endpoint='vendor.packages', kwargs={})


@vendor_bp.route('/packages/new', methods=['GET', 'POST'])
@vendor_required
def new_package():
    if request.method == 'GET':
        return render_template('vendor/package_form.html', package=None, categories=CATEGORIES)

    user_id = session['user_id']
    data = _parse_package_form(request.form)

    package, error = create_new_package(user_id, data)
    if error:
        flash(error, 'danger')
        return render_template('vendor/package_form.html', package=data, categories=CATEGORIES), 400

    flash('Package created successfully!', 'success')
    return redirect(url_for('vendor.packages'))


@vendor_bp.route('/packages/<package_id>/edit', methods=['GET', 'POST'])
@vendor_required
def edit_package(package_id):
    user_id = session['user_id']
    package = find_package_by_id(package_id)
    if not package:
        flash('Package not found.', 'danger')
        return redirect(url_for('vendor.packages'))
    if str(package.vendor_id) != str(user_id):
        flash('Access denied.', 'danger')
        return redirect(url_for('vendor.packages'))

    if request.method == 'GET':
        return render_template('vendor/package_form.html', package=package, categories=CATEGORIES)

    data = _parse_package_form(request.form)
    updated, error = update_existing_package(package_id, user_id, data)
    if error:
        flash(error, 'danger')
        return render_template('vendor/package_form.html', package=package, categories=CATEGORIES), 400

    flash('Package updated successfully!', 'success')
    return redirect(url_for('vendor.packages'))


@vendor_bp.route('/packages/<package_id>/status', methods=['POST'])
@vendor_required
def change_status(package_id):
    user_id = session['user_id']
    status = request.form.get('status', 'draft')
    _, error = update_package_status(package_id, user_id, status)
    if error:
        flash(error, 'danger')
    else:
        flash(f'Package status changed to {status}.', 'success')
    return redirect(url_for('vendor.packages'))


@vendor_bp.route('/packages/<package_id>/delete', methods=['POST'])
@vendor_required
def remove_package(package_id):
    user_id = session['user_id']
    error = delete_vendor_package(package_id, user_id)
    if error:
        flash(error, 'danger')
    else:
        flash('Package deleted.', 'success')
    return redirect(url_for('vendor.packages'))


@vendor_bp.route('/bookings')
@vendor_required
def bookings():
    user_id = session['user_id']
    page, limit = paginate_args(request)
    status = request.args.get('status', '')
    booking_list, total = get_vendor_bookings(user_id, status=status or None, page=page, limit=limit)
    total_pages = (total + limit - 1) // limit

    from app.models.user import find_user_by_id
    for b in booking_list:
        b._package = find_package_by_id(b.package_id)
        b._user = find_user_by_id(b.user_id)

    return render_template('vendor/bookings.html',
        bookings=booking_list, page=page, total=total,
        total_pages=total_pages, current_status=status,
        endpoint='vendor.bookings',
        kwargs={'status': status} if status else {})


@vendor_bp.route('/bookings/<booking_id>/confirm', methods=['POST'])
@vendor_required
def confirm(booking_id):
    user_id = session['user_id']
    _, error = confirm_vendor_booking(booking_id, user_id)
    if error:
        flash(error, 'danger')
    else:
        flash('Booking confirmed.', 'success')
    return redirect(url_for('vendor.bookings'))


@vendor_bp.route('/bookings/<booking_id>/complete', methods=['POST'])
@vendor_required
def complete(booking_id):
    user_id = session['user_id']
    _, error = complete_vendor_booking(booking_id, user_id)
    if error:
        flash(error, 'danger')
    else:
        flash('Booking marked as completed.', 'success')
    return redirect(url_for('vendor.bookings'))


def _parse_package_form(form):
    """Parse package form data into dict."""
    highlights = [h.strip() for h in form.get('highlights', '').split(',') if h.strip()]
    inclusions = [i.strip() for i in form.get('inclusions', '').split(',') if i.strip()]
    exclusions = [e.strip() for e in form.get('exclusions', '').split(',') if e.strip()]
    tags = [t.strip() for t in form.get('tags', '').split(',') if t.strip()]

    # Parse destinations
    dest_names = form.getlist('dest_name')
    dest_durations = form.getlist('dest_duration')
    destinations = []
    for i, name in enumerate(dest_names):
        if name.strip():
            raw_dur = dest_durations[i] if i < len(dest_durations) else ''
            destinations.append({
                'name': name.strip(),
                'duration': safe_int(raw_dur, default=1, min_val=1),
            })

    # Parse itinerary
    itinerary = []
    day_num = 1
    while form.get(f'day_{day_num}_title'):
        activities = [a.strip() for a in form.get(f'day_{day_num}_activities', '').split(',') if a.strip()]
        itinerary.append({
            'day': day_num,
            'title': form.get(f'day_{day_num}_title', ''),
            'description': form.get(f'day_{day_num}_description', ''),
            'activities': activities,
            'meals': {
                'breakfast': form.get(f'day_{day_num}_breakfast') == 'on',
                'lunch': form.get(f'day_{day_num}_lunch') == 'on',
                'dinner': form.get(f'day_{day_num}_dinner') == 'on',
            },
            'accommodation': form.get(f'day_{day_num}_accommodation', ''),
        })
        day_num += 1

    # Parse images (JSON from upload widget)
    import json
    images = []
    images_json = form.get('images_json', '[]')
    try:
        images = json.loads(images_json)
    except Exception:
        pass

    return {
        'title': form.get('title', ''),
        'description': form.get('description', ''),
        'highlights': highlights,
        'category': form.get('category', ''),
        'destinations': destinations,
        'itinerary': itinerary,
        'pricing': {
            'basePrice': safe_float(form.get('basePrice'), default=0, min_val=0),
            'currency': form.get('currency', 'USD'),
            'perPersonPrice': form.get('perPersonPrice') == 'on',
        },
        'inclusions': inclusions,
        'exclusions': exclusions,
        'images': images,
        'availability': {
            'startDate': form.get('startDate', ''),
            'endDate': form.get('endDate', ''),
            'maxGroupSize': safe_int(form.get('maxGroupSize'), default=10, min_val=1),
            'minGroupSize': safe_int(form.get('minGroupSize'), default=1, min_val=1),
        },
        'duration': {
            'days': safe_int(form.get('days'), default=1, min_val=1),
            'nights': safe_int(form.get('nights'), default=0, min_val=0),
        },
        'difficulty': form.get('difficulty', 'moderate'),
        'status': form.get('status', 'draft'),
        'tags': tags,
    }
