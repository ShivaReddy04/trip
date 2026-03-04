from flask import Blueprint, render_template, request, jsonify, session
from app.services.ai_service import generate_itinerary, get_suggestions
from app.services.itinerary_service import generate_smart_itinerary
from app.services.destination_service import (
    get_destination_guide,
    get_famous_places_at_destination,
    get_nearby_destinations,
    get_travel_info,
)
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
# Destination guide — explore a destination
# -----------------------------------------------------------------------

@ai_bp.route('/destination-guide', methods=['POST'])
def destination_guide():
    """
    Get a comprehensive destination guide.

    Expects JSON body:
    {
        "destination": "Goa",
        "from_city": "Hyderabad"   (optional)
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    destination = data.get('destination', '').strip()
    if not destination:
        return jsonify({'error': 'Destination is required'}), 400

    from_city = data.get('from_city', '').strip() or None
    travel_mode = data.get('travel_mode', 'train').strip().lower()
    if travel_mode not in ('train', 'bus', 'flight', 'car'):
        travel_mode = 'train'

    try:
        # 1. Get destination info
        dest, error = get_destination_guide(destination)
        if error:
            return jsonify({'error': error}), 404

        # 2. Famous places near the destination
        famous = []
        if dest.get('lat') and dest.get('lng'):
            try:
                famous = get_famous_places_at_destination(dest['lat'], dest['lng'], radius_km=40)
            except Exception as e:
                print(f"[WARN] Famous places fetch failed: {e}")

        # 3. Nearby destinations
        nearby = []
        if dest.get('lat') and dest.get('lng'):
            try:
                nearby = get_nearby_destinations(dest['lat'], dest['lng'], dest['name'], radius_km=200)
            except Exception as e:
                print(f"[WARN] Nearby destinations fetch failed: {e}")

        # 4. Travel info from origin city
        travel = get_travel_info(from_city, dest, travel_mode)

        return jsonify({
            'destination': dest,
            'travel_info': travel,
            'famous_places': famous,
            'nearby_destinations': nearby,
        }), 200

    except Exception as e:
        print(f"[ERROR] Destination guide failed: {e}")
        return jsonify({'error': f'Failed to generate destination guide: {str(e)}'}), 500


# -----------------------------------------------------------------------
# Plan My Trip — generate itinerary (no login required)
# -----------------------------------------------------------------------

@ai_bp.route('/plan-trip', methods=['POST'])
def plan_trip():
    """
    Generate a day-by-day trip itinerary.
    Does NOT require login, does NOT save to database.

    Expects JSON body:
    {
        "destination": "Goa",
        "places": ["Baga Beach", "Fort Aguada"],
        "days": 3,
        "budget": 15000,
        "members": 2,
        "start_date": "2026-03-15"
    }
    """
    from app.services.ai_service import plan_trip_itinerary

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    destination = data.get('destination', '').strip()
    if not destination:
        return jsonify({'error': 'Destination is required'}), 400

    try:
        result, error = plan_trip_itinerary(data)
        if error:
            return jsonify({'error': error}), 400
        return jsonify(result), 200
    except Exception as e:
        print(f"[ERROR] Plan trip failed: {e}")
        return jsonify({'error': f'Failed to plan trip: {str(e)}'}), 500


# -----------------------------------------------------------------------
# Sarvam AI — Translation & Text-to-Speech
# -----------------------------------------------------------------------

@ai_bp.route('/languages', methods=['GET'])
def languages():
    """Return supported Indian languages."""
    from app.services.sarvam_service import get_supported_languages
    return jsonify(get_supported_languages()), 200


@ai_bp.route('/translate', methods=['POST'])
def translate():
    """
    Translate text to an Indian language.
    Body: { "text": "...", "target_lang": "hi-IN", "source_lang": "en-IN" }
    """
    from app.services.sarvam_service import translate_text

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    text = data.get('text', '').strip()
    target = data.get('target_lang', 'hi-IN').strip()
    source = data.get('source_lang', 'en-IN').strip()

    if not text:
        return jsonify({'error': 'Text is required'}), 400

    result, error = translate_text(text, target, source)
    if error:
        return jsonify({'error': error}), 400
    return jsonify({'translated_text': result, 'target_lang': target}), 200


@ai_bp.route('/speak', methods=['POST'])
def speak():
    """
    Convert text to speech audio (base64 mp3).
    Body: { "text": "...", "lang": "hi-IN", "speaker": "anushka" }
    """
    from app.services.sarvam_service import text_to_speech

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    text = data.get('text', '').strip()
    lang = data.get('lang', 'hi-IN').strip()
    speaker = data.get('speaker', 'anushka').strip().lower()

    if not text:
        return jsonify({'error': 'Text is required'}), 400

    audio_b64, error = text_to_speech(text, lang, speaker)
    if error:
        return jsonify({'error': error}), 400
    return jsonify({'audio': audio_b64, 'format': 'wav'}), 200
