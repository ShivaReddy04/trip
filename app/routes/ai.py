from flask import Blueprint, render_template, request, jsonify, session
from app.services.ai_service import generate_itinerary, get_suggestions
from app.services.itinerary_service import generate_smart_itinerary
from app.models.ai_itinerary import get_user_itineraries
from app.utils.helpers import serialize_doc
from app.utils.decorators import login_required

ai_bp = Blueprint('ai', __name__, template_folder='../templates')


@ai_bp.route('/planner')
def planner():
    return render_template('pages/ai_planner.html')


@ai_bp.route('/generate', methods=['POST'])
@login_required
def generate():
    user_id = session['user_id']
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid data'}), 400

    if not data.get('destinations'):
        return jsonify({'error': 'At least one destination is required'}), 400

    itinerary, error = generate_itinerary(user_id, data)
    if error:
        return jsonify({'error': error}), 400

    return jsonify(serialize_doc(itinerary)), 201


@ai_bp.route('/suggestions', methods=['POST'])
@login_required
def suggestions():
    data = request.get_json()
    result, error = get_suggestions(data or {})
    if error:
        return jsonify({'error': error}), 400
    return jsonify(result)


@ai_bp.route('/my-itineraries')
@login_required
def my_itineraries():
    user_id = session['user_id']
    page = request.args.get('page', 1, type=int)
    itineraries, total = get_user_itineraries(user_id, page=page)
    return jsonify({
        'itineraries': [serialize_doc(i) for i in itineraries],
        'total': total,
        'page': page,
    })


# -----------------------------------------------------------------------
# Smart itinerary — route-based multi-day planner
# -----------------------------------------------------------------------

@ai_bp.route('/smart-itinerary', methods=['POST'])
@login_required
def smart_itinerary():
    """
    Generate an intelligent multi-day road-trip itinerary.

    Expects JSON body:
    {
        "start_city": "Hyderabad",
        "destination_city": "Tirupati",
        "days": 3,
        "budget": "medium",
        "travel_mode": "driving"
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    required = ('start_city', 'destination_city')
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400

    result, error = generate_smart_itinerary(data)
    if error:
        return jsonify({'error': error}), 400

    return jsonify(result), 200
