"""Accommodation service — Overpass-based hotel/hostel search."""

import requests
from .route_service import haversine

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
OVERPASS_TIMEOUT = 15
SEARCH_RADIUS_M = 10000  # 10 km

# Estimated nightly cost by budget tier (INR)
NIGHTLY_COST = {
    "low": {"hotel": 1200, "hostel": 600, "guest_house": 800},
    "medium": {"hotel": 3000, "hostel": 1200, "guest_house": 1800},
    "high": {"hotel": 7000, "hostel": 2500, "guest_house": 4000},
}


def _build_accommodation_query(lat, lng, radius_m):
    return f"""
    [out:json][timeout:15];
    (
      node["tourism"="hotel"](around:{radius_m},{lat},{lng});
      node["tourism"="hostel"](around:{radius_m},{lat},{lng});
      node["tourism"="guest_house"](around:{radius_m},{lat},{lng});
    );
    out body 30;
    """


def fetch_accommodations_near(lat, lng, radius_m=SEARCH_RADIUS_M):
    """
    Query Overpass for accommodation near (lat, lng).
    Returns list of dicts.
    """
    query = _build_accommodation_query(lat, lng, radius_m)
    try:
        resp = requests.post(
            OVERPASS_URL,
            data={"data": query},
            timeout=OVERPASS_TIMEOUT,
        )
        resp.raise_for_status()
        elements = resp.json().get("elements", [])
    except (requests.RequestException, ValueError):
        return []

    results = []
    seen = set()
    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name", "").strip()
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())

        accom_type = tags.get("tourism", "hotel")
        results.append({
            "name": name,
            "lat": el.get("lat"),
            "lng": el.get("lon"),
            "type": accom_type,
            "stars": tags.get("stars", ""),
            "phone": tags.get("phone", ""),
            "website": tags.get("website", ""),
            "address": tags.get("addr:full", tags.get("addr:street", "")),
        })

    return results


def suggest_accommodation(segment_end, budget="medium"):
    """
    Find the best accommodation near *segment_end* [lat, lng].
    Returns a single accommodation dict with estimated cost, or a fallback.
    """
    lat, lng = segment_end
    results = fetch_accommodations_near(lat, lng)
    if not results:
        results = fetch_accommodations_near(lat, lng, SEARCH_RADIUS_M * 2)

    cost_map = NIGHTLY_COST.get(budget, NIGHTLY_COST["medium"])

    if results:
        # Pick the closest one
        for r in results:
            r["distance_km"] = round(haversine(lat, lng, r["lat"], r["lng"]), 2)
        results.sort(key=lambda x: x["distance_km"])
        best = results[0]
        best["estimated_cost"] = cost_map.get(best["type"], cost_map["hotel"])
        return best

    # Fallback when Overpass returns nothing
    return {
        "name": "Accommodation near route",
        "lat": lat,
        "lng": lng,
        "type": "hotel",
        "stars": "",
        "phone": "",
        "website": "",
        "address": "",
        "distance_km": 0,
        "estimated_cost": cost_map["hotel"],
    }
