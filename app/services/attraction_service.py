"""Attraction service — Overpass API search + ranking."""

import requests
import math
from .route_service import haversine

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
OVERPASS_TIMEOUT = 20
SEARCH_RADIUS_M = 15000  # 15 km from route midpoint


# ---------------------------------------------------------------------------
# Overpass query builder
# ---------------------------------------------------------------------------

def _build_overpass_query(lat, lng, radius_m):
    """Build Overpass QL to fetch attractions near a point."""
    return f"""
    [out:json][timeout:20];
    (
      node["tourism"="attraction"](around:{radius_m},{lat},{lng});
      node["tourism"="viewpoint"](around:{radius_m},{lat},{lng});
      node["natural"="waterfall"](around:{radius_m},{lat},{lng});
      node["historic"](around:{radius_m},{lat},{lng});
      node["leisure"="park"](around:{radius_m},{lat},{lng});
    );
    out body 40;
    """


# ---------------------------------------------------------------------------
# Fetch raw attractions from Overpass
# ---------------------------------------------------------------------------

def fetch_attractions_near(lat, lng, radius_m=SEARCH_RADIUS_M):
    """
    Query Overpass for attractions near (lat, lng).
    Returns list of dicts with name, lat, lng, type, tags.
    """
    query = _build_overpass_query(lat, lng, radius_m)
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
    seen_names = set()
    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name", "").strip()
        if not name or name.lower() in seen_names:
            continue
        seen_names.add(name.lower())

        # Determine attraction type
        atype = "attraction"
        if tags.get("natural") == "waterfall":
            atype = "waterfall"
        elif tags.get("tourism") == "viewpoint":
            atype = "viewpoint"
        elif "historic" in tags:
            atype = "historic"
        elif tags.get("leisure") == "park":
            atype = "park"

        results.append({
            "name": name,
            "lat": el.get("lat"),
            "lng": el.get("lon"),
            "type": atype,
            "tags": tags,
        })

    return results


# ---------------------------------------------------------------------------
# Ranking
# ---------------------------------------------------------------------------

TYPE_WEIGHTS = {
    "attraction": 10,
    "historic": 9,
    "waterfall": 8,
    "viewpoint": 7,
    "park": 6,
}

BUDGET_TYPE_BONUS = {
    "low": {"park": 3, "viewpoint": 3, "waterfall": 2},
    "medium": {"attraction": 2, "historic": 2, "waterfall": 2},
    "high": {"attraction": 3, "historic": 3},
}


def rank_attractions(attractions, route_midpoint, budget="medium"):
    """
    Score and rank attractions.

    Score = type_weight + budget_bonus - proximity_penalty
    proximity_penalty = distance_km * 0.5 (capped at 5)
    """
    mid_lat, mid_lng = route_midpoint
    budget_bonuses = BUDGET_TYPE_BONUS.get(budget, {})

    scored = []
    for att in attractions:
        dist = haversine(mid_lat, mid_lng, att["lat"], att["lng"])
        type_w = TYPE_WEIGHTS.get(att["type"], 5)
        budget_b = budget_bonuses.get(att["type"], 0)
        proximity_penalty = min(dist * 0.5, 5)
        score = type_w + budget_b - proximity_penalty
        scored.append({**att, "score": round(score, 2), "distance_km": round(dist, 2)})

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored


# ---------------------------------------------------------------------------
# Fetch + rank attractions for a route segment
# ---------------------------------------------------------------------------

def get_segment_attractions(segment, budget="medium", limit=5):
    """
    Fetch and rank attractions for a single route segment.
    Returns top *limit* attractions.
    """
    mid = segment["midpoint"]
    raw = fetch_attractions_near(mid[0], mid[1], SEARCH_RADIUS_M)
    if not raw:
        # Try with wider radius
        raw = fetch_attractions_near(mid[0], mid[1], SEARCH_RADIUS_M * 2)
    ranked = rank_attractions(raw, (mid[0], mid[1]), budget)
    return ranked[:limit]
