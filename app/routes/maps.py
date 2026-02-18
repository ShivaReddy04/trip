from flask import Blueprint, render_template, request, jsonify
from app.services.maps_service import (
    search_places, get_place_details, get_famous_places,
    get_distance, geocode
)

maps_bp = Blueprint('maps', __name__, template_folder='../templates')


@maps_bp.route('/explore')
def explore():
    return render_template('pages/explore.html')


@maps_bp.route('/places/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    result = search_places(query)
    return jsonify(result)


@maps_bp.route('/places/<place_id>', methods=['GET'])
def place_details(place_id):
    result = get_place_details(place_id)
    return jsonify(result)


@maps_bp.route('/famous-places', methods=['GET'])
def famous_places():
    location = request.args.get('location', '')
    category = request.args.get('category', 'tourist_attraction')
    if not location:
        return jsonify({'error': 'Location is required'}), 400
    result = get_famous_places(location, category)
    return jsonify(result)


@maps_bp.route('/distance', methods=['GET'])
def distance():
    origins = request.args.get('origins', '')
    destinations = request.args.get('destinations', '')
    mode = request.args.get('mode', 'driving')
    if not origins or not destinations:
        return jsonify({'error': 'Origins and destinations are required'}), 400
    result = get_distance(origins, destinations, mode)
    return jsonify(result)


@maps_bp.route('/geocode', methods=['GET'])
def geocode_route():
    address = request.args.get('address', '')
    if not address:
        return jsonify({'error': 'Address is required'}), 400
    result = geocode(address)
    return jsonify(result)
