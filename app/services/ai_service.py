"""AI service — Groq-powered itinerary generation and travel suggestions."""

import os
import json
import requests
from groq import Groq
from app.models.ai_itinerary import create_ai_itinerary


def _groq_client():
    key = os.getenv("OPENAI_API_KEY", "")
    if not key:
        return None
    return Groq(api_key=key)


def _ask_groq(prompt, max_tokens=3000):
    """Call Groq AI and return the response text."""
    client = _groq_client()
    if not client:
        return None
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert travel planner. Always respond with valid JSON only, no markdown, no extra text."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=max_tokens,
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


def _get_place_image(place_name):
    """Fetch a thumbnail image URL from Wikipedia for a place."""
    search_terms = [place_name.strip(), f"{place_name.strip()} landmark"]
    for term in search_terms:
        slug = term.replace(' ', '_')
        try:
            resp = requests.get(
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{slug}",
                headers={"User-Agent": "TripPlanner/1.0"},
                timeout=5,
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
    encoded = requests.utils.quote(place_name)
    return f"https://placehold.co/400x300/e2e8f0/64748b?text={encoded}"


def _add_images_to_itinerary(generated):
    """Add image URLs to each activity in the itinerary."""
    if not generated or 'days' not in generated:
        return generated
    for day in generated.get('days', []):
        for activity in day.get('activities', []):
            name = activity.get('activity', '')
            if name and 'image_url' not in activity:
                activity['image_url'] = _get_place_image(name)
    return generated


def generate_itinerary(user_id, data):
    """Generate a complete travel itinerary using Groq AI."""
    destinations = data.get('destinations', ['Paris'])
    duration = int(data.get('duration', 3))
    budget = float(data.get('budget', 1000))
    travelers = int(data.get('travelers', 1))
    preferences = data.get('preferences', [])
    start_date = data.get('startDate', '')

    dest_str = ', '.join(destinations) if isinstance(destinations, list) else destinations
    pref_str = ', '.join(preferences) if preferences else 'general sightseeing'

    prompt = f"""Create a {duration}-day travel itinerary for {dest_str}.
Budget: ${budget} total for {travelers} traveler(s).
Preferences: {pref_str}
Start date: {start_date or 'flexible'}

Return JSON in this exact format:
{{
    "title": "{duration}-Day Adventure in {dest_str}",
    "days": [
        {{
            "day": 1,
            "activities": [
                {{"time": "09:00 AM", "activity": "Place name", "location": "Full address", "lat": 48.8584, "lng": 2.2945, "cost": 50}},
                {{"time": "12:00 PM", "activity": "Restaurant name", "location": "Full address", "lat": 48.86, "lng": 2.33, "cost": 30}},
                {{"time": "02:00 PM", "activity": "Afternoon spot", "location": "Full address", "lat": 48.87, "lng": 2.29, "cost": 40}},
                {{"time": "06:00 PM", "activity": "Evening activity", "location": "Full address", "lat": 48.85, "lng": 2.35, "cost": 60}}
            ],
            "totalCost": 180,
            "tips": ["Tip 1", "Tip 2", "Tip 3"]
        }}
    ],
    "totalBudget": {budget},
    "recommendations": ["Rec 1", "Rec 2", "Rec 3", "Rec 4", "Rec 5"]
}}

Include real place names, real coordinates, and realistic costs. Generate all {duration} days.
Return ONLY the JSON."""

    raw = _ask_groq(prompt, max_tokens=4000)
    generated = _parse_json(raw)

    # Add images to all activities
    if generated:
        generated = _add_images_to_itinerary(generated)

    if not generated:
        # Fallback: basic structure
        generated = {
            'title': f'{duration}-Day Adventure in {dest_str}',
            'days': [{
                'day': d,
                'activities': [
                    {'time': '09:00 AM', 'activity': f'Explore {dest_str} - Day {d}', 'location': f'{dest_str}', 'cost': round(budget * 0.05)},
                    {'time': '12:00 PM', 'activity': 'Local cuisine lunch', 'location': f'{dest_str}', 'cost': round(budget * 0.03)},
                    {'time': '02:00 PM', 'activity': f'Visit landmarks - Day {d}', 'location': f'{dest_str}', 'cost': round(budget * 0.04)},
                    {'time': '06:00 PM', 'activity': 'Evening experience', 'location': f'{dest_str}', 'cost': round(budget * 0.06)},
                ],
                'totalCost': round(budget / duration),
                'tips': ['Book tickets in advance.', 'Try local street food.', 'Use public transport.'],
            } for d in range(1, duration + 1)],
            'totalBudget': budget,
            'recommendations': [
                f'Best time to visit {dest_str} is during shoulder season.',
                'Consider purchasing a city pass for discounted entry.',
                'Learn basic phrases in the local language.',
                'Carry local currency for small vendors.',
                'Book accommodations near public transport.',
            ],
        }

    itinerary_data = {
        'userId': user_id,
        'input': {
            'destinations': destinations,
            'duration': duration,
            'budget': budget,
            'travelers': travelers,
            'preferences': preferences,
            'startDate': start_date,
        },
        'generatedItinerary': generated,
    }
    saved = create_ai_itinerary(itinerary_data)
    return saved, None


def plan_trip_itinerary(data):
    """
    Generate a day-by-day trip plan based on user inputs.
    Does NOT require login, does NOT save to DB.
    Returns (result_dict, None) or (None, error_string).
    """
    destination = data.get('destination', '').strip()
    places = data.get('places', [])
    days = int(data.get('days', 3))
    budget = float(data.get('budget', 10000))
    members = int(data.get('members', 2))
    start_date = data.get('start_date', '')
    currency = 'INR'

    if days < 1 or days > 15:
        days = min(max(days, 1), 15)
    if members < 1:
        members = 1

    places_str = ', '.join(places) if places else f'popular attractions in {destination}'
    per_person = round(budget / members)

    prompt = f"""Create a detailed {days}-day trip itinerary for {destination}.
Group size: {members} travelers.
Total budget: {budget} {currency} (approx {per_person} {currency} per person).
Start date: {start_date or 'flexible'}
Must-visit places: {places_str}

Return JSON in this EXACT format:
{{
    "title": "...",
    "summary": "One-line trip summary",
    "total_cost": {budget},
    "per_person_cost": {per_person},
    "days": [
        {{
            "day": 1,
            "date": "{start_date or 'Day 1'}",
            "theme": "Short theme like Beach Day, Temple Tour",
            "activities": [
                {{"time": "09:00 AM", "activity": "Place name", "description": "What to do here", "duration": "2 hours", "cost": 200, "type": "sightseeing"}},
                {{"time": "12:00 PM", "activity": "Restaurant name", "description": "Lunch at local restaurant", "duration": "1 hour", "cost": 500, "type": "food"}},
                {{"time": "02:00 PM", "activity": "Afternoon spot", "description": "Activity details", "duration": "3 hours", "cost": 300, "type": "activity"}},
                {{"time": "06:00 PM", "activity": "Evening activity", "description": "Details", "duration": "2 hours", "cost": 400, "type": "entertainment"}}
            ],
            "day_cost": 1400,
            "tips": ["Tip 1", "Tip 2"]
        }}
    ],
    "packing_tips": ["item 1", "item 2", "item 3"],
    "recommendations": ["Rec 1", "Rec 2", "Rec 3"]
}}

Activity types: sightseeing, food, activity, entertainment, shopping, transport, rest.
Use REAL place names and realistic costs in {currency}. Distribute the must-visit places across the days.
Generate ALL {days} days with 4-6 activities each.
Return ONLY the JSON."""

    raw = _ask_groq(prompt, max_tokens=4000)
    result = _parse_json(raw)

    if not result:
        return None, 'AI could not generate the itinerary. Please try again.'

    # Fill in dates if start_date provided
    if start_date and result.get('days'):
        from datetime import datetime, timedelta
        try:
            base = datetime.strptime(start_date, '%Y-%m-%d')
            for i, day in enumerate(result['days']):
                day['date'] = (base + timedelta(days=i)).strftime('%a, %d %b %Y')
        except ValueError:
            pass

    # Add metadata
    result['destination'] = destination
    result['members'] = members
    result['budget'] = budget
    result['num_days'] = days
    result['start_date'] = start_date
    result['places_requested'] = places

    return result, None


def get_suggestions(data):
    """Get AI-powered travel suggestions from Groq."""
    prompt = """Suggest 5 trending travel destinations with this JSON format:
[
    {
        "destination": "City Name",
        "country": "Country",
        "description": "2-3 sentence description",
        "estimatedCost": 1500,
        "bestTimeToVisit": "Month - Month"
    }
]
Include a mix of budget-friendly and premium destinations worldwide.
Return ONLY the JSON array."""

    raw = _ask_groq(prompt, max_tokens=1500)
    suggestions = _parse_json(raw)

    if not suggestions:
        suggestions = [
            {'destination': 'Bali', 'country': 'Indonesia', 'description': 'Tropical paradise with stunning temples and rice terraces.', 'estimatedCost': 1200, 'bestTimeToVisit': 'April - October'},
            {'destination': 'Kyoto', 'country': 'Japan', 'description': 'Ancient capital with thousands of temples and traditional gardens.', 'estimatedCost': 2000, 'bestTimeToVisit': 'March - May'},
            {'destination': 'Santorini', 'country': 'Greece', 'description': 'Iconic white-washed buildings and stunning sunsets.', 'estimatedCost': 1800, 'bestTimeToVisit': 'May - October'},
            {'destination': 'Marrakech', 'country': 'Morocco', 'description': 'Exotic markets, palaces, and gateway to the Sahara.', 'estimatedCost': 800, 'bestTimeToVisit': 'March - May'},
            {'destination': 'Reykjavik', 'country': 'Iceland', 'description': 'Northern lights, geysers, and dramatic volcanic landscapes.', 'estimatedCost': 2500, 'bestTimeToVisit': 'June - August'},
        ]

    # Add images to suggestions
    for s in suggestions:
        if 'image_url' not in s:
            s['image_url'] = _get_place_image(s.get('destination', ''))

    return suggestions, None
