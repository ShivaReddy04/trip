from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.services.package_service import search_all_packages, get_package_detail
from app.models.review import get_package_reviews, get_rating_summary
from app.models.user import find_user_by_id
from app.utils.helpers import paginate_args

packages_bp = Blueprint('packages', __name__, template_folder='../templates')

CATEGORIES = ['adventure', 'beach', 'cultural', 'wildlife', 'honeymoon', 'family', 'pilgrimage']


@packages_bp.route('/')
def browse():
    page, limit = paginate_args(request)
    filters = {
        'query': request.args.get('q', ''),
        'category': request.args.get('category', ''),
        'minPrice': request.args.get('minPrice', ''),
        'maxPrice': request.args.get('maxPrice', ''),
        'duration': request.args.get('duration', ''),
        'difficulty': request.args.get('difficulty', ''),
        'destination': request.args.get('destination', ''),
        'rating': request.args.get('rating', ''),
        'featured': request.args.get('featured', ''),
    }
    sort_by = request.args.get('sortBy', 'createdAt')
    sort_order = request.args.get('sortOrder', 'desc')

    packages, total = search_all_packages(filters, page, limit, sort_by, sort_order)
    total_pages = (total + limit - 1) // limit

    return render_template('pages/packages.html',
        packages=packages, page=page, total=total,
        total_pages=total_pages, filters=filters,
        sort_by=sort_by, sort_order=sort_order,
        categories=CATEGORIES,
        endpoint='packages.browse',
        kwargs={k: v for k, v in request.args.items() if k != 'page'})


@packages_bp.route('/<slug>')
def detail(slug):
    package = get_package_detail(slug)
    if not package:
        flash('Package not found.', 'danger')
        return redirect(url_for('packages.browse'))

    # Get vendor info
    vendor = find_user_by_id(package.vendor_id)

    # Get reviews
    reviews, review_total = get_package_reviews(str(package.id), page=1, limit=5)
    rating_summary = get_rating_summary(str(package.id))

    # Get reviewer info for each review
    review_users = {}
    for review in reviews:
        uid = str(review.user_id)
        if uid not in review_users:
            review_users[uid] = find_user_by_id(uid)

    # Check if current user is logged in
    current_user_id = session.get('user_id')

    return render_template('pages/package_detail.html',
        package=package, vendor=vendor,
        reviews=reviews, review_users=review_users,
        rating_summary=rating_summary,
        current_user_id=current_user_id)
