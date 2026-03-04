"""Attraction service — Overpass API (free) + Groq AI fallback for route attractions."""

import os
import json
import requests
from .route_service import haversine

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
OVERPASS_TIMEOUT = 25
CORRIDOR_RADIUS_M = 15000


# ---------------------------------------------------------------------------
# Overpass query (free, no API key)
# ---------------------------------------------------------------------------

def _build_overpass_query(lat, lng, radius_m):
    return f"""
    [out:json][timeout:25];
    (
      nwr["tourism"="attraction"](around:{radius_m},{lat},{lng});
      nwr["tourism"="viewpoint"](around:{radius_m},{lat},{lng});
      nwr["tourism"="museum"](around:{radius_m},{lat},{lng});
      nwr["natural"="waterfall"](around:{radius_m},{lat},{lng});
      nwr["natural"="beach"](around:{radius_m},{lat},{lng});
      nwr["natural"="peak"](around:{radius_m},{lat},{lng});
      nwr["historic"](around:{radius_m},{lat},{lng});
      nwr["leisure"="park"]["name"](around:{radius_m},{lat},{lng});
      nwr["amenity"="place_of_worship"]["name"](around:{radius_m},{lat},{lng});
      nwr["man_made"="monument"](around:{radius_m},{lat},{lng});
    );
    out center 50;
    """


def _extract_coords(el):
    if el["type"] == "node":
        return el.get("lat"), el.get("lon")
    center = el.get("center", {})
    return center.get("lat"), center.get("lon")


def fetch_attractions_near(lat, lng, radius_m=CORRIDOR_RADIUS_M):
    """Query Overpass for attractions near (lat, lng)."""
    query = _build_overpass_query(lat, lng, radius_m)
    try:
        resp = requests.post(OVERPASS_URL, data={"data": query}, timeout=OVERPASS_TIMEOUT)
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

        elat, elng = _extract_coords(el)
        if elat is None or elng is None:
            continue

        atype = _classify_type(tags)
        notable = bool(tags.get("wikipedia") or tags.get("wikidata"))

        results.append({
            "name": name,
            "lat": elat,
            "lng": elng,
            "type": atype,
            "notable": notable,
            "tags": tags,
        })

    return results


def _classify_type(tags):
    if tags.get("natural") == "waterfall": return "waterfall"
    if tags.get("natural") == "beach": return "beach"
    if tags.get("natural") == "peak": return "peak"
    if tags.get("tourism") == "viewpoint": return "viewpoint"
    if tags.get("tourism") == "museum": return "museum"
    if tags.get("amenity") == "place_of_worship":
        religion = tags.get("religion", "").lower()
        if "hindu" in religion: return "temple"
        if "christian" in religion: return "church"
        if "islam" in religion or "muslim" in religion: return "mosque"
        if "sikh" in religion: return "gurudwara"
        if "buddhis" in religion: return "monastery"
        return "temple"
    if "historic" in tags: return "historic"
    if tags.get("leisure") == "park": return "park"
    if tags.get("man_made") == "monument": return "monument"
    return "attraction"


# ---------------------------------------------------------------------------
# Ranking
# ---------------------------------------------------------------------------

TYPE_WEIGHTS = {
    "attraction": 10, "historic": 9, "museum": 9, "waterfall": 8,
    "national park": 8, "temple": 8, "church": 7, "mosque": 7,
    "gurudwara": 7, "monastery": 7, "monument": 7, "viewpoint": 7,
    "beach": 7, "peak": 6, "nature reserve": 6, "park": 5,
}

BUDGET_TYPE_BONUS = {
    "low": {"park": 3, "viewpoint": 3, "waterfall": 3, "beach": 3, "peak": 2, "temple": 2},
    "medium": {"attraction": 2, "historic": 2, "waterfall": 2, "museum": 2, "temple": 2},
    "high": {"attraction": 3, "historic": 3, "museum": 3, "monument": 2},
}

NOTABLE_BONUS = 5


def _min_distance_to_route(att_lat, att_lng, route_points):
    min_d = float("inf")
    step = max(1, len(route_points) // 60)
    for i in range(0, len(route_points), step):
        d = haversine(att_lat, att_lng, route_points[i][0], route_points[i][1])
        if d < min_d:
            min_d = d
    return min_d


def rank_attractions(attractions, route_points, budget="medium"):
    budget_bonuses = BUDGET_TYPE_BONUS.get(budget, {})
    scored = []
    for att in attractions:
        dist = _min_distance_to_route(att["lat"], att["lng"], route_points)
        type_w = TYPE_WEIGHTS.get(att["type"], 5)
        budget_b = budget_bonuses.get(att["type"], 0)
        notable_b = NOTABLE_BONUS if att.get("notable") else 0

        if dist <= 5:
            proximity_penalty = dist * 0.5
        else:
            proximity_penalty = 2.5 + (dist - 5) * 1.2

        score = type_w + budget_b + notable_b - proximity_penalty
        scored.append({**att, "score": round(score, 2), "distance_km": round(dist, 2)})

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored


# ---------------------------------------------------------------------------
# Multi-point search along segment
# ---------------------------------------------------------------------------

def get_segment_attractions(segment, budget="medium", limit=5):
    pts = segment["points"]
    if not pts:
        return []

    seg_dist = segment.get("segment_distance_km", 0)

    if seg_dist < 50:
        sample_indices = [len(pts) // 2]
    elif seg_dist < 150:
        sample_indices = [len(pts) // 4, len(pts) // 2, 3 * len(pts) // 4]
    else:
        sample_indices = [len(pts) // 5, 2 * len(pts) // 5, 3 * len(pts) // 5, 4 * len(pts) // 5]

    all_raw = []
    seen_names = set()
    for idx in sample_indices:
        idx = min(idx, len(pts) - 1)
        lat, lng = pts[idx][0], pts[idx][1]
        raw = fetch_attractions_near(lat, lng, CORRIDOR_RADIUS_M)
        for att in raw:
            key = att["name"].lower()
            if key not in seen_names:
                seen_names.add(key)
                all_raw.append(att)

    if not all_raw:
        mid = pts[len(pts) // 2]
        all_raw = fetch_attractions_near(mid[0], mid[1], CORRIDOR_RADIUS_M * 2)

    ranked = rank_attractions(all_raw, pts, budget)
    return ranked[:limit]


# ---------------------------------------------------------------------------
# Famous places along route — Overpass + Groq AI fallback
# ---------------------------------------------------------------------------

def _sample_route_points(geometry, max_points=20):
    if len(geometry) <= max_points:
        return list(geometry)
    step = max(1, len(geometry) // max_points)
    pts = geometry[::step]
    if pts[-1] != geometry[-1]:
        pts.append(geometry[-1])
    return pts


def _build_famous_polyline_query(sample_points, radius_m=25000):
    coord_str = ",".join(f"{p[0]},{p[1]}" for p in sample_points)
    return f"""
    [out:json][timeout:30];
    (
      node["tourism"="attraction"]["wikipedia"](around:{radius_m},{coord_str});
      node["tourism"="attraction"]["wikidata"](around:{radius_m},{coord_str});
      node["historic"]["wikipedia"](around:{radius_m},{coord_str});
      node["tourism"="museum"]["name"](around:{radius_m},{coord_str});
      node["amenity"="place_of_worship"]["wikipedia"](around:{radius_m},{coord_str});
      node["natural"="waterfall"]["name"](around:{radius_m},{coord_str});
      node["natural"="beach"]["name"](around:{radius_m},{coord_str});
    );
    out 80;
    """


def get_famous_places_along_route(geometry, limit=20):
    """Fetch notable places along a route using Overpass (free)."""
    if not geometry or len(geometry) < 2:
        return []

    sample_pts = _sample_route_points(geometry, max_points=20)
    query = _build_famous_polyline_query(sample_pts)

    try:
        resp = requests.post(OVERPASS_URL, data={"data": query}, timeout=30)
        resp.raise_for_status()
        elements = resp.json().get("elements", [])
    except (requests.RequestException, ValueError):
        elements = []

    route_sample = geometry[::max(1, len(geometry) // 60)]
    places = []
    seen_names = set()

    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name", "").strip()
        if not name or name.lower() in seen_names:
            continue

        elat, elng = _extract_coords(el)
        if elat is None or elng is None:
            continue

        min_dist = min(haversine(elat, elng, rp[0], rp[1]) for rp in route_sample)
        if min_dist > 30:
            continue

        seen_names.add(name.lower())
        atype = _classify_type(tags)

        wiki = tags.get("wikipedia", "")
        wiki_url = ""
        if wiki:
            parts = wiki.split(":", 1)
            if len(parts) == 2:
                lang, title = parts
                wiki_url = f"https://{lang}.wikipedia.org/wiki/{title.replace(' ', '_')}"

        places.append({
            "name": name,
            "lat": elat,
            "lng": elng,
            "type": atype,
            "wikipedia_url": wiki_url,
            "description": tags.get("description", tags.get("note", "")),
        })

    # Sort by proximity to route start → end
    if geometry and places:
        for p in places:
            best_idx = 0
            best_d = float("inf")
            for i, rp in enumerate(route_sample):
                d = haversine(p["lat"], p["lng"], rp[0], rp[1])
                if d < best_d:
                    best_d = d
                    best_idx = i
            p["_sort_idx"] = best_idx
        places.sort(key=lambda p: p["_sort_idx"])
        for p in places:
            p.pop("_sort_idx", None)

    return places[:limit]
