"""Route service — OpenRouteService directions + route splitting."""

import os
import math
import requests

ORS_BASE = "https://api.openrouteservice.org"
ORS_KEY = os.getenv("OPENROUTE_API_KEY", "")
REQUEST_TIMEOUT = 15


# ---------------------------------------------------------------------------
# Haversine
# ---------------------------------------------------------------------------

def haversine(lat1, lon1, lat2, lon2):
    """Return distance in km between two lat/lng points."""
    R = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2
         + math.cos(math.radians(lat1))
         * math.cos(math.radians(lat2))
         * math.sin(d_lon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ---------------------------------------------------------------------------
# Geocode a city name → (lat, lng)
# ---------------------------------------------------------------------------

def geocode_city(city_name):
    """Return (lat, lng) for *city_name* using ORS geocoding, or None."""
    if not ORS_KEY:
        return None
    try:
        resp = requests.get(
            f"{ORS_BASE}/geocode/search",
            params={"api_key": ORS_KEY, "text": city_name, "size": 1},
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        features = resp.json().get("features", [])
        if features:
            coords = features[0]["geometry"]["coordinates"]  # [lng, lat]
            return (coords[1], coords[0])
    except (requests.RequestException, KeyError, IndexError):
        pass
    return None


# ---------------------------------------------------------------------------
# Get driving/cycling/walking route between two points
# ---------------------------------------------------------------------------

PROFILE_MAP = {
    "driving": "driving-car",
    "cycling": "cycling-regular",
    "walking": "foot-walking",
}


def get_route(start_coords, end_coords, travel_mode="driving"):
    """
    Fetch route from ORS.

    Parameters
    ----------
    start_coords : tuple  (lat, lng)
    end_coords   : tuple  (lat, lng)
    travel_mode  : str    "driving" | "cycling" | "walking"

    Returns
    -------
    dict with keys: distance_km, duration_hours, geometry (list of [lat, lng]),
    bbox, or None on failure.
    """
    profile = PROFILE_MAP.get(travel_mode, "driving-car")
    # ORS expects [lng, lat]
    body = {
        "coordinates": [
            [start_coords[1], start_coords[0]],
            [end_coords[1], end_coords[0]],
        ]
    }
    headers = {
        "Authorization": ORS_KEY,
        "Content-Type": "application/json; charset=utf-8",
    }
    try:
        resp = requests.post(
            f"{ORS_BASE}/v2/directions/{profile}/geojson",
            json=body,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        feature = data["features"][0]
        props = feature["properties"]["summary"]
        # geometry coordinates are [lng, lat] — convert to [lat, lng]
        raw_coords = feature["geometry"]["coordinates"]
        geometry = [[c[1], c[0]] for c in raw_coords]
        return {
            "distance_km": round(props["distance"] / 1000, 2),
            "duration_hours": round(props["duration"] / 3600, 2),
            "geometry": geometry,
            "bbox": feature.get("bbox"),
        }
    except (requests.RequestException, KeyError, IndexError):
        return None


# ---------------------------------------------------------------------------
# Split route geometry into N equal-distance segments
# ---------------------------------------------------------------------------

def split_route_into_segments(geometry, num_days):
    """
    Divide a list of [lat, lng] points into *num_days* segments of roughly
    equal cumulative distance.

    Returns list of dicts: {start, end, midpoint, points, segment_distance_km}
    """
    if not geometry or num_days < 1:
        return []

    # Compute cumulative distance along geometry
    cum_dist = [0.0]
    for i in range(1, len(geometry)):
        d = haversine(geometry[i - 1][0], geometry[i - 1][1],
                      geometry[i][0], geometry[i][1])
        cum_dist.append(cum_dist[-1] + d)
    total = cum_dist[-1]
    if total == 0:
        return []

    seg_len = total / num_days
    segments = []
    seg_start_idx = 0

    for day in range(num_days):
        target = seg_len * (day + 1)
        # Find the index where cumulative distance crosses target
        seg_end_idx = seg_start_idx
        for j in range(seg_start_idx, len(cum_dist)):
            if cum_dist[j] >= target or j == len(cum_dist) - 1:
                seg_end_idx = j
                break

        pts = geometry[seg_start_idx: seg_end_idx + 1]
        if len(pts) < 2:
            pts = geometry[max(0, seg_end_idx - 1): seg_end_idx + 1]

        mid_idx = len(pts) // 2
        seg_dist = cum_dist[seg_end_idx] - cum_dist[seg_start_idx]

        segments.append({
            "start": pts[0],
            "end": pts[-1],
            "midpoint": pts[mid_idx] if pts else geometry[0],
            "points": pts,
            "segment_distance_km": round(seg_dist, 2),
        })
        seg_start_idx = seg_end_idx

    return segments
