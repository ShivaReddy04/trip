"""Destination guide service — free APIs: ORS geocoding + Groq AI + Wikipedia images."""

import os
import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

from groq import Groq

from app.services.route_service import geocode_city, haversine, get_route

ORS_BASE = "https://api.openrouteservice.org"
REQUEST_TIMEOUT = 10


def _smart_geocode(city_name, state=None, ai_lat=None, ai_lng=None):
    """
    Geocode a city using ORS, fetching multiple results and picking the one
    closest to AI-provided approximate coordinates (if available).
    Falls back to standard geocode_city if no AI coords.
    """
    key = os.getenv("OPENROUTE_API_KEY", "")
    if not key:
        return geocode_city(city_name)

    # Build search queries — with state context first
    queries = []
    if state:
        queries.append(f"{city_name}, {state}, India")
        queries.append(f"{city_name}, {state}")
    queries.append(f"{city_name}, India")
    queries.append(city_name)

    all_candidates = []
    for text in queries:
        try:
            resp = requests.get(
                f"{ORS_BASE}/geocode/search",
                params={"api_key": key, "text": text, "size": 5, "boundary.country": "IN"},
                timeout=REQUEST_TIMEOUT,
            )
            resp.raise_for_status()
            features = resp.json().get("features", [])
            for f in features:
                coords = f["geometry"]["coordinates"]  # [lng, lat]
                lat, lng = coords[1], coords[0]
                props = f.get("properties", {})
                all_candidates.append({
                    "lat": lat, "lng": lng,
                    "name": props.get("name", ""),
                    "layer": props.get("layer", ""),
                    "region": props.get("region", ""),
                    "confidence": props.get("confidence", 0),
                })
            if features:
                break  # first query with results is usually best
        except Exception:
            continue

    if not all_candidates:
        return geocode_city(city_name)

    # If we have AI approximate coords, pick the candidate closest to them
    if ai_lat and ai_lng:
        try:
            ai_lat_f, ai_lng_f = float(ai_lat), float(ai_lng)
            for c in all_candidates:
                c["ai_dist"] = haversine(c["lat"], c["lng"], ai_lat_f, ai_lng_f)
            all_candidates.sort(key=lambda x: x["ai_dist"])
            best = all_candidates[0]
            # Only use if within 100km of AI coords (sanity check)
            if best["ai_dist"] < 100:
                return (best["lat"], best["lng"])
        except (ValueError, TypeError):
            pass

    # Fallback: pick the first locality-layer result, or first overall
    for c in all_candidates:
        if c["layer"] in ("locality", "localadmin"):
            return (c["lat"], c["lng"])
    return (all_candidates[0]["lat"], all_candidates[0]["lng"])


def _pick_best_coords(baseline, smart, ai_lat, ai_lng):
    """Pick the most accurate coordinates from baseline and smart geocode results.
    Uses AI approximate coords as the tiebreaker when available."""
    candidates = [c for c in [smart, baseline] if c is not None]
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]

    # Both baseline and smart are available
    # If AI coords available, pick whichever is closer to AI's estimate
    if ai_lat and ai_lng:
        try:
            ai_lat_f, ai_lng_f = float(ai_lat), float(ai_lng)
            base_dist = haversine(baseline[0], baseline[1], ai_lat_f, ai_lng_f)
            smart_dist = haversine(smart[0], smart[1], ai_lat_f, ai_lng_f)

            if smart_dist < base_dist and smart_dist < 150:
                return smart
            elif base_dist < smart_dist and base_dist < 150:
                return baseline
            # Both are far from AI coords — prefer baseline (more conservative)
            return baseline if base_dist <= smart_dist else smart
        except (ValueError, TypeError):
            pass

    # No AI coords — prefer smart if within 200km of baseline, else baseline
    drift = haversine(baseline[0], baseline[1], smart[0], smart[1])
    if drift < 200:
        return smart  # smart has state context, so prefer it
    return baseline


# ---------------------------------------------------------------------------
# Groq AI
# ---------------------------------------------------------------------------

def _groq_client():
    key = os.getenv("OPENAI_API_KEY", "")
    if not key:
        return None
    return Groq(api_key=key)


def _ask_groq(prompt, temperature=0.7, model=None):
    """Call Groq AI and return the response text."""
    client = _groq_client()
    if not client:
        return None
    try:
        response = client.chat.completions.create(
            model=model or "llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful travel guide assistant. Always respond with valid JSON only, no extra text, no markdown fences."},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_tokens=2000,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return None


def _parse_json(raw):
    """Parse JSON from AI response, handling markdown fences."""
    if not raw:
        return None
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
    try:
        return json.loads(raw.strip())
    except (json.JSONDecodeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Wikipedia image helper (free, no key needed)
# ---------------------------------------------------------------------------

def _wiki_image(name):
    """Fetch a thumbnail image URL from Wikipedia for a place name."""
    search_terms = [name.strip(), f"{name.strip()} India"]
    for term in search_terms:
        slug = term.replace(' ', '_')
        try:
            resp = requests.get(
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{slug}",
                headers={"User-Agent": "TripPlanner/1.0"},
                timeout=3,
            )
            if resp.ok:
                data = resp.json()
                thumb = data.get("thumbnail", {}).get("source")
                if thumb:
                    return thumb.replace("/220px-", "/600px-").replace("/330px-", "/600px-")
                og = data.get("originalimage", {}).get("source")
                if og:
                    return og
        except Exception:
            continue
    encoded = requests.utils.quote(name)
    return f"https://placehold.co/600x400/e2e8f0/64748b?text={encoded}"


# ---------------------------------------------------------------------------
# Groq AI — destination guide info
# ---------------------------------------------------------------------------

def _get_ai_destination_info(destination_name):
    """Use Groq to generate rich destination info."""
    prompt = f"""Give me a detailed travel guide for "{destination_name}" (in India) in this exact JSON format:
{{
    "corrected_name": "official English name of the city (e.g. Tirupathi becomes Tirupati, Banglore becomes Bangalore)",
    "approx_lat": 15.49,
    "approx_lng": 73.82,
    "state": "Indian state name only (e.g. Goa, Rajasthan, Kerala, Andhra Pradesh — NOT India)",
    "region": "region name (e.g. South India, North India, Western Ghats)",
    "popularity_score": 8,
    "best_seasons": ["March-May", "October-November"],
    "avoid_seasons": ["June-August"],
    "peak_tourist_season": "October to March",
    "off_season": "June to August",
    "ideal_days": 4,
    "minimum_days": 2,
    "maximum_days": 7,
    "suggested_itinerary": "Day 1: ..., Day 2: ...",
    "food_scene": "Description of food culture",
    "local_cuisine_must_try": ["dish1", "dish2", "dish3"],
    "safety_rating": 8,
    "safety_notes": "Safety info",
    "local_culture": "Cultural highlights",
    "festivals_events": "Major festivals",
    "activities": ["activity1", "activity2"],
    "unique_experiences": "Unique things to do",
    "hidden_gems": ["gem1", "gem2"],
    "trip_types": ["family", "adventure", "cultural"],
    "accommodation_types": ["hotels", "hostels", "resorts"],
    "special_considerations": "Any special notes",
    "primary_attractions": ["attraction1", "attraction2", "attraction3"]
}}
Return ONLY the JSON."""

    raw = _ask_groq(prompt, temperature=0.3)
    return _parse_json(raw) or {}


# ---------------------------------------------------------------------------
# Main: get destination guide
# ---------------------------------------------------------------------------

def get_destination_guide(destination_name):
    """
    Fetch a comprehensive destination guide using ORS + Groq AI + Wikipedia.
    Returns (dest_dict, None) on success or (None, error_string).
    """
    query = destination_name.strip()
    if not query:
        return None, "Destination name is required"

    # 1. Get AI info FIRST — it returns the corrected name + state
    #    which helps us geocode accurately
    ai_info = _get_ai_destination_info(query)

    # Use AI-corrected name if available
    ai_name = ai_info.get('corrected_name', '').strip()
    ai_state = ai_info.get('state', '').strip()
    ai_lat = ai_info.get('approx_lat')
    ai_lng = ai_info.get('approx_lng')
    if ai_name and ai_name.lower() != query.lower():
        print(f"[INFO] City name corrected: '{query}' -> '{ai_name}'")
        query = ai_name

    # 2. Geocode — collect candidates and pick the best
    baseline = geocode_city(query)
    if not baseline and query != destination_name.strip():
        baseline = geocode_city(destination_name.strip())

    smart = None
    if ai_state and ai_state.lower() not in ('india', query.lower()):
        smart = _smart_geocode(query, ai_state, ai_lat, ai_lng)

    # Pick the best candidate using AI coords as ground truth
    coords = _pick_best_coords(baseline, smart, ai_lat, ai_lng)

    if not coords:
        # Last resort: use AI approximate coords
        if ai_lat and ai_lng:
            try:
                coords = (float(ai_lat), float(ai_lng))
            except (ValueError, TypeError):
                pass
    if not coords:
        return None, f"Could not find location for '{destination_name}'"

    lat, lng = coords

    # 3. Get image from Wikipedia (free)
    image_url = _wiki_image(query)

    dest = {
        'name': query.title(),
        'state': ai_info.get('state', ''),
        'region': ai_info.get('region', ''),
        'lat': lat,
        'lng': lng,
        'popularity_score': ai_info.get('popularity_score', 7),
        'best_seasons': ai_info.get('best_seasons', []),
        'avoid_seasons': ai_info.get('avoid_seasons', []),
        'peak_tourist_season': ai_info.get('peak_tourist_season', ''),
        'off_season': ai_info.get('off_season', ''),
        'ideal_days': ai_info.get('ideal_days', 3),
        'minimum_days': ai_info.get('minimum_days', 1),
        'maximum_days': ai_info.get('maximum_days', 7),
        'suggested_itinerary': ai_info.get('suggested_itinerary', ''),
        'food_scene': ai_info.get('food_scene', ''),
        'local_cuisine_must_try': ai_info.get('local_cuisine_must_try', []),
        'safety_rating': ai_info.get('safety_rating', 7),
        'safety_notes': ai_info.get('safety_notes', ''),
        'local_culture': ai_info.get('local_culture', ''),
        'festivals_events': ai_info.get('festivals_events', ''),
        'activities': ai_info.get('activities', []),
        'unique_experiences': ai_info.get('unique_experiences', ''),
        'hidden_gems': ai_info.get('hidden_gems', []),
        'trip_types': ai_info.get('trip_types', []),
        'accommodation_types': ai_info.get('accommodation_types', []),
        'special_considerations': ai_info.get('special_considerations', ''),
        'primary_attractions': ai_info.get('primary_attractions', []),
        'accessibility': '',
        'nearest_airport': {},
        'nearest_railway_station': {},
        'road_connectivity': '',
        'image_url': image_url,
    }

    return dest, None


# ---------------------------------------------------------------------------
# Famous places near a destination — Groq AI + Wikipedia images
# ---------------------------------------------------------------------------

def _geocode_place(place_name, near_lat, near_lng, state_hint=""):
    """Geocode a specific place name using ORS, picking result closest to (near_lat, near_lng)."""
    key = os.getenv("OPENROUTE_API_KEY", "")
    if not key:
        return None, None

    queries = []
    if state_hint:
        queries.append(f"{place_name}, {state_hint}, India")
    queries.append(f"{place_name}, India")
    queries.append(place_name)

    for text in queries:
        try:
            resp = requests.get(
                f"{ORS_BASE}/geocode/search",
                params={"api_key": key, "text": text, "size": 3, "boundary.country": "IN"},
                timeout=5,
            )
            resp.raise_for_status()
            features = resp.json().get("features", [])
            if not features:
                continue

            # Pick the result closest to the destination center
            best = None
            best_dist = float("inf")
            for f in features:
                c = f["geometry"]["coordinates"]  # [lng, lat]
                d = haversine(near_lat, near_lng, c[1], c[0])
                if d < best_dist:
                    best_dist = d
                    best = (c[1], c[0])

            # Only accept if within a reasonable radius (80km)
            if best and best_dist < 80:
                return best
        except Exception:
            continue
    return None, None


def _process_single_place(item, lat, lng):
    """Geocode and fetch image for a single famous place (runs in thread)."""
    name = item.get("name", "")
    if not name:
        return None

    plat, plng = _geocode_place(name, lat, lng)
    if plat is None or plng is None:
        return None

    dist = round(haversine(lat, lng, plat, plng), 1)

    return {
        'name': name,
        'lat': plat,
        'lng': plng,
        'type': item.get('type', 'attraction'),
        'description': item.get('description', ''),
        'city': '',
        'image_url': _wiki_image(name),
        'distance_km': dist,
        'rating': item.get('rating', 4.0),
    }


def get_famous_places_at_destination(lat, lng, radius_km=40):
    """Fetch tourist attractions near (lat, lng) using Groq AI + ORS geocoding for accurate coords."""
    prompt = f"""List 12 famous tourist attractions near coordinates ({lat}, {lng}) within {radius_km}km.
Return a JSON array:
[
    {{"name": "Place Name", "type": "temple", "description": "Short 1-line description", "rating": 4.5}}
]
Types: temple, monument, museum, beach, park, historic, nature, waterfall, attraction.
Use REAL well-known place names. Return ONLY the JSON array."""

    raw = _ask_groq(prompt, model="llama-3.1-8b-instant")
    items = _parse_json(raw) or []

    # Deduplicate
    unique_items = []
    seen = set()
    for item in items:
        name = item.get("name", "")
        if name and name.lower() not in seen:
            seen.add(name.lower())
            unique_items.append(item)

    # Geocode + fetch images in parallel (up to 6 threads)
    places = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {
            executor.submit(_process_single_place, item, lat, lng): item
            for item in unique_items
        }
        for future in as_completed(futures):
            try:
                result = future.result()
                if result:
                    places.append(result)
            except Exception:
                continue

    places.sort(key=lambda x: (-x.get('rating', 0), x['distance_km']))
    return places[:20]


# ---------------------------------------------------------------------------
# Nearby destinations — Groq AI + Wikipedia images
# ---------------------------------------------------------------------------

def get_nearby_destinations(lat, lng, current_name, radius_km=200):
    """Find nearby tourist destinations using Groq AI."""
    prompt = f"""Suggest 6 popular tourist destinations near {current_name} (coordinates: {lat}, {lng}) within {radius_km}km.
Do NOT include {current_name} itself.
Return a JSON array:
[
    {{"name": "City Name", "state": "State", "distance_km": 120, "key_attractions": ["Attraction 1", "Attraction 2"], "popularity_score": 8, "ideal_days": 3}}
]
Use REAL distances. Return ONLY the JSON array."""

    raw = _ask_groq(prompt, model="llama-3.1-8b-instant")
    items = _parse_json(raw) or []

    unique_items = []
    seen = set()
    seen.add(current_name.lower())

    for item in items:
        name = item.get("name", "")
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        unique_items.append(item)

    # Fetch Wikipedia images in parallel
    def _build_destination(item):
        name = item.get("name", "")
        return {
            'name': name,
            'state': item.get('state', ''),
            'distance_km': item.get('distance_km', 0),
            'key_attractions': item.get('key_attractions', [])[:4],
            'popularity_score': item.get('popularity_score', 7),
            'ideal_days': item.get('ideal_days', 3),
            'image_url': _wiki_image(name),
        }

    destinations = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(_build_destination, item) for item in unique_items]
        for future in as_completed(futures):
            try:
                destinations.append(future.result())
            except Exception:
                continue

    destinations.sort(key=lambda x: x['distance_km'])
    return destinations[:8]


# ---------------------------------------------------------------------------
# Price & time estimation helpers
# ---------------------------------------------------------------------------

def _estimate_prices(distance_km):
    d = distance_km
    prices = {
        'train': {'low': round(d * 0.5), 'high': round(d * 1.5), 'label': 'Sleeper to AC First'},
        'bus':   {'low': round(d * 1.0), 'high': round(d * 2.0), 'label': 'Non-AC to Volvo AC'},
        'car':   {'low': round(d * 8),   'high': round(d * 12),  'label': 'Fuel cost (self-drive)'},
    }
    if d > 300:
        prices['flight'] = {'low': round(2500 + d * 3), 'high': round(2500 + d * 5), 'label': 'Economy'}
    else:
        prices['flight'] = None
    return prices


def _estimate_travel_times(distance_km, car_duration_hours=None):
    d = distance_km
    return {
        'train': round(d / 55, 1),
        'bus':   round(d / 45, 1),
        'flight': round(d / 700 + 1.5, 1) if d > 300 else None,
        'car':   round(car_duration_hours, 1) if car_duration_hours else round(d / 50, 1),
    }


# ---------------------------------------------------------------------------
# Travel info from origin
# ---------------------------------------------------------------------------

def get_travel_info(from_city, dest_data, travel_mode='train'):
    """Compute travel info using ORS routing (free)."""
    result = {
        'from_city': from_city or '',
        'travel_mode': travel_mode,
        'distance_km': None,
        'road_distance_km': None,
        'duration_hours': None,
        'origin_coords': None,
        'route_geometry': None,
        'price_estimates': None,
        'travel_times': None,
        'nearest_airport': dest_data.get('nearest_airport', {}),
        'nearest_railway': dest_data.get('nearest_railway_station', {}),
        'road_info': dest_data.get('road_connectivity', ''),
    }

    if not from_city:
        return result

    # Use smart geocode for accurate origin coordinates
    origin_coords = _smart_geocode(from_city)
    if not origin_coords or not dest_data.get('lat') or not dest_data.get('lng'):
        return result

    result['origin_coords'] = list(origin_coords)

    straight_dist = haversine(origin_coords[0], origin_coords[1],
                              dest_data['lat'], dest_data['lng'])
    result['distance_km'] = round(straight_dist, 1)

    car_duration = None
    dest_coords = (dest_data['lat'], dest_data['lng'])
    route_data, route_err = get_route(origin_coords, dest_coords, 'driving')
    if route_data:
        result['road_distance_km'] = route_data['distance_km']
        result['duration_hours'] = route_data['duration_hours']
        result['route_geometry'] = route_data['geometry']
        car_duration = route_data['duration_hours']
    else:
        result['road_distance_km'] = round(straight_dist * 1.3, 1)

    road_dist = result['road_distance_km'] or straight_dist
    result['price_estimates'] = _estimate_prices(road_dist)
    result['travel_times'] = _estimate_travel_times(road_dist, car_duration)

    return result
