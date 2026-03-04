"""Accommodation service — Overpass API (free) hotel/hostel search with budget-aware ranking."""

import requests
from .route_service import haversine

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
OVERPASS_TIMEOUT = 15
SEARCH_RADIUS_M = 15000

NIGHTLY_COST = {
    "low": {"hotel": 1200, "hostel": 600, "guest_house": 800, "motel": 900},
    "medium": {"hotel": 3000, "hostel": 1200, "guest_house": 1800, "motel": 1500},
    "high": {"hotel": 7000, "hostel": 2500, "guest_house": 4000, "motel": 3000},
}

BUDGET_TYPE_PREFERENCE = {
    "low": ["hostel", "guest_house", "motel", "hotel"],
    "medium": ["hotel", "guest_house", "motel", "hostel"],
    "high": ["hotel", "guest_house", "motel", "hostel"],
}


def _build_accommodation_query(lat, lng, radius_m):
    return f"""
    [out:json][timeout:15];
    (
      nwr["tourism"="hotel"](around:{radius_m},{lat},{lng});
      nwr["tourism"="hostel"](around:{radius_m},{lat},{lng});
      nwr["tourism"="guest_house"](around:{radius_m},{lat},{lng});
      nwr["tourism"="motel"](around:{radius_m},{lat},{lng});
    );
    out center 40;
    """


def _extract_coords(el):
    if el["type"] == "node":
        return el.get("lat"), el.get("lon")
    center = el.get("center", {})
    return center.get("lat"), center.get("lon")


def fetch_accommodations_near(lat, lng, radius_m=SEARCH_RADIUS_M):
    query = _build_accommodation_query(lat, lng, radius_m)
    try:
        resp = requests.post(OVERPASS_URL, data={"data": query}, timeout=OVERPASS_TIMEOUT)
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

        elat, elng = _extract_coords(el)
        if elat is None or elng is None:
            continue

        results.append({
            "name": name,
            "lat": elat,
            "lng": elng,
            "type": tags.get("tourism", "hotel"),
            "stars": tags.get("stars", ""),
            "phone": tags.get("phone", ""),
            "website": tags.get("website", ""),
            "address": tags.get("addr:full", tags.get("addr:street", "")),
        })

    return results


def suggest_accommodation(segment_end, budget="medium"):
    lat, lng = segment_end
    results = fetch_accommodations_near(lat, lng)
    if not results:
        results = fetch_accommodations_near(lat, lng, SEARCH_RADIUS_M * 2)

    cost_map = NIGHTLY_COST.get(budget, NIGHTLY_COST["medium"])
    type_prefs = BUDGET_TYPE_PREFERENCE.get(budget, BUDGET_TYPE_PREFERENCE["medium"])

    if results:
        for r in results:
            r["distance_km"] = round(haversine(lat, lng, r["lat"], r["lng"]), 2)

        def _score(r):
            try:
                type_rank = type_prefs.index(r["type"])
            except ValueError:
                type_rank = len(type_prefs)
            stars_bonus = 0
            if budget == "high" and r.get("stars"):
                try:
                    stars_bonus = -int(r["stars"])
                except (ValueError, TypeError):
                    pass
            return (type_rank + stars_bonus, r["distance_km"])

        results.sort(key=_score)
        best = results[0]
        best["estimated_cost"] = cost_map.get(best["type"], cost_map["hotel"])
        return best

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
