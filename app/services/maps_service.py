# Maps service - Demo mode (no Google Maps API)

MOCK_PLACES = [
    {
        'placeId': 'place_1',
        'name': 'Eiffel Tower',
        'address': 'Champ de Mars, 5 Av. Anatole France, 75007 Paris, France',
        'location': {'lat': 48.8584, 'lng': 2.2945},
        'rating': 4.7,
        'totalRatings': 234567,
        'photo': 'https://images.unsplash.com/photo-1511739001486-6bfe10ce65f4?w=400',
        'types': ['tourist_attraction', 'landmark'],
    },
    {
        'placeId': 'place_2',
        'name': 'Taj Mahal',
        'address': 'Dharmapuri, Forest Colony, Tajganj, Agra, Uttar Pradesh 282001, India',
        'location': {'lat': 27.1751, 'lng': 78.0421},
        'rating': 4.8,
        'totalRatings': 198234,
        'photo': 'https://images.unsplash.com/photo-1564507592333-c60657eea523?w=400',
        'types': ['tourist_attraction', 'landmark'],
    },
    {
        'placeId': 'place_3',
        'name': 'Colosseum',
        'address': 'Piazza del Colosseo, 1, 00184 Roma RM, Italy',
        'location': {'lat': 41.8902, 'lng': 12.4922},
        'rating': 4.7,
        'totalRatings': 312456,
        'photo': 'https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=400',
        'types': ['tourist_attraction', 'landmark'],
    },
    {
        'placeId': 'place_4',
        'name': 'Machu Picchu',
        'address': '08680, Peru',
        'location': {'lat': -13.1631, 'lng': -72.5450},
        'rating': 4.9,
        'totalRatings': 87654,
        'photo': 'https://images.unsplash.com/photo-1587595431973-160d0d163406?w=400',
        'types': ['tourist_attraction', 'landmark'],
    },
    {
        'placeId': 'place_5',
        'name': 'Great Wall of China',
        'address': 'Huairou District, China',
        'location': {'lat': 40.4319, 'lng': 116.5704},
        'rating': 4.6,
        'totalRatings': 156789,
        'photo': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=400',
        'types': ['tourist_attraction', 'landmark'],
    },
    {
        'placeId': 'place_6',
        'name': 'Santorini',
        'address': 'Santorini, Greece',
        'location': {'lat': 36.3932, 'lng': 25.4615},
        'rating': 4.8,
        'totalRatings': 145678,
        'photo': 'https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=400',
        'types': ['tourist_attraction', 'natural_feature'],
    },
]


def search_places(query, location=None):
    """Demo: return mock places matching the query."""
    query_lower = query.lower()
    results = [p for p in MOCK_PLACES if query_lower in p['name'].lower() or query_lower in p['address'].lower()]
    if not results:
        results = MOCK_PLACES[:3]
    return {'results': results}


def get_place_details(place_id):
    """Demo: return mock place details."""
    for p in MOCK_PLACES:
        if p['placeId'] == place_id:
            return {
                **p,
                'phone': '+1 (555) 123-4567',
                'website': '#',
                'openingHours': ['Monday: 9:00 AM - 6:00 PM', 'Tuesday: 9:00 AM - 6:00 PM'],
                'photos': [p['photo']],
            }
    return {'error': 'Place not found'}


def get_famous_places(location, category='tourist_attraction'):
    """Demo: return mock famous places."""
    return {'results': MOCK_PLACES}


def get_distance(origins, destinations, mode='driving'):
    """Demo: return mock distance data."""
    return {
        'rows': [{
            'elements': [{
                'distance': {'text': '15.2 km', 'value': 15200},
                'duration': {'text': '25 mins', 'value': 1500},
                'status': 'OK',
            }]
        }],
        'status': 'OK',
        'demo': True,
    }


def geocode(address):
    """Demo: return mock geocode result."""
    return {
        'lat': 48.8566,
        'lng': 2.3522,
        'address': address or 'Paris, France',
        'demo': True,
    }
