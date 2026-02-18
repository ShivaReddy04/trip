from flask import Blueprint, request, jsonify, session
from app.services.review_service import create_new_review, reply_to_review
from app.models.review import get_package_reviews, mark_helpful, get_rating_summary
from app.utils.helpers import serialize_doc
from app.utils.decorators import login_required

reviews_bp = Blueprint('reviews', __name__, template_folder='../templates')


@reviews_bp.route('/package/<package_id>', methods=['GET'])
def package_reviews(package_id):
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    reviews, total = get_package_reviews(package_id, page, limit)
    return jsonify({
        'reviews': [serialize_doc(r) for r in reviews],
        'total': total,
        'page': page,
    })


@reviews_bp.route('/package/<package_id>/summary', methods=['GET'])
def review_summary(package_id):
    summary = get_rating_summary(package_id)
    return jsonify(summary)


@reviews_bp.route('/', methods=['POST'])
@login_required
def create():
    user_id = session['user_id']
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid data'}), 400

    review, error = create_new_review(user_id, data)
    if error:
        return jsonify({'error': error}), 400

    return jsonify(serialize_doc(review)), 201


@reviews_bp.route('/<review_id>/reply', methods=['POST'])
@login_required
def reply(review_id):
    user_id = session['user_id']
    data = request.get_json()
    if not data or not data.get('content'):
        return jsonify({'error': 'Reply content required'}), 400

    review, error = reply_to_review(review_id, user_id, data['content'])
    if error:
        return jsonify({'error': error}), 400

    return jsonify(serialize_doc(review))


@reviews_bp.route('/<review_id>/helpful', methods=['POST'])
@login_required
def helpful(review_id):
    user_id = session['user_id']
    review, error = mark_helpful(review_id, user_id)
    if error:
        return jsonify({'error': error}), 400
    return jsonify({'helpfulCount': review.helpful_count})
