"""Route service — OpenRouteService directions + route splitting."""

import os
import math
import requests

ORS_BASE = "https://api.openrouteservice.org"
REQUEST_TIMEOUT = 15


def _ors_key():
    """Read ORS key at call time so .env is already loaded."""
    return os.getenv("OPENROUTE_API_KEY", "")


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
    key = _ors_key()
    if not key:
        return None

    # Try with country hint first, fetching multiple results to pick the best
    search_texts = [f"{city_name}, India", city_name]

    for text in search_texts:
        try:
            resp = requests.get(
                f"{ORS_BASE}/geocode/search",
                params={
                    "api_key": key,
                    "text": text,
                    "size": 5,
                    "boundary.country": "IN",
                },
                timeout=REQUEST_TIMEOUT,
            )
            resp.raise_for_status()
            features = resp.json().get("features", [])
            best = _pick_best_feature(features, city_name)
            if best:
                coords = best["geometry"]["coordinates"]  # [lng, lat]
                return (coords[1], coords[0])
        except (requests.RequestException, KeyError, IndexError):
            continue

    # Final attempt without country filter
    try:
        resp = requests.get(
            f"{ORS_BASE}/geocode/search",
            params={"api_key": key, "text": city_name, "size": 5},
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        features = resp.json().get("features", [])
        best = _pick_best_feature(features, city_name)
        if best:
            coords = best["geometry"]["coordinates"]  # [lng, lat]
            return (coords[1], coords[0])
    except (requests.RequestException, KeyError, IndexError):
        pass
    return None


# Layers that count as a "city" or "town" in ORS/Pelias results
_CITY_LAYERS = {"locality", "localadmin", "county", "macrocounty", "region"}


def _pick_best_feature(features, query):
    """Pick the best geocode result, preferring cities/towns over villages."""
    if not features:
        return None
    if len(features) == 1:
        return features[0]

    query_lower = query.strip().lower()

    # Score each feature: higher = better match
    scored = []
    for f in features:
        props = f.get("properties", {})
        score = props.get("confidence", 0) * 10
        layer = props.get("layer", "")
        name = (props.get("name", "") or "").lower()

        # Boost city/town-level results over hamlets/villages
        if layer in _CITY_LAYERS:
            score += 5
        elif layer in ("neighbourhood", "borough"):
            score += 1

        # Boost exact or close name match
        if name == query_lower:
            score += 10
        elif query_lower in name or name in query_lower:
            score += 4

        # Boost larger population places (higher confidence usually = bigger city)
        pop = props.get("population", 0)
        if pop and pop > 100000:
            score += 3
        elif pop and pop > 10000:
            score += 1

        scored.append((score, f))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0][1]


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
    Fetch route from ORS with turn-by-turn steps.

    Parameters
    ----------
    start_coords : tuple  (lat, lng)
    end_coords   : tuple  (lat, lng)
    travel_mode  : str    "driving" | "cycling" | "walking"

    Returns
    -------
    (dict, None) on success — keys: distance_km, duration_hours, geometry,
    bbox, steps (turn-by-turn directions).
    (None, error_string) on failure.
    """
    key = _ors_key()
    if not key:
        return None, "OPENROUTE_API_KEY is not set"

    profile = PROFILE_MAP.get(travel_mode, "driving-car")
    # ORS expects [lng, lat]
    body = {
        "coordinates": [
            [start_coords[1], start_coords[0]],
            [end_coords[1], end_coords[0]],
        ],
        "radiuses": [5000, 5000],  # snap to nearest road within 5 km
    }
    headers = {
        "Authorization": key,
        "Content-Type": "application/json; charset=utf-8",
    }

    try:
        # --- GeoJSON request (geometry + summary) ---
        resp = requests.post(
            f"{ORS_BASE}/v2/directions/{profile}/geojson",
            json=body,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )
        if not resp.ok:
            try:
                detail = resp.json().get("error", {})
                msg = detail.get("message", resp.text) if isinstance(detail, dict) else str(detail)
            except Exception:
                msg = resp.text
            return None, f"ORS directions API error ({resp.status_code}): {msg}"
        data = resp.json()
        feature = data["features"][0]
        props = feature["properties"]["summary"]
        raw_coords = feature["geometry"]["coordinates"]
        geometry = [[c[1], c[0]] for c in raw_coords]

        # --- JSON request (turn-by-turn steps) ---
        steps = _fetch_steps(profile, body, headers)

        return {
            "distance_km": round(props["distance"] / 1000, 2),
            "duration_hours": round(props["duration"] / 3600, 2),
            "geometry": geometry,
            "bbox": feature.get("bbox"),
            "steps": steps,
        }, None
    except requests.RequestException as exc:
        return None, f"ORS request failed: {exc}"
    except (KeyError, IndexError) as exc:
        return None, f"Unexpected ORS response format: {exc}"


# ORS instruction type → human-readable icon hint
_STEP_TYPE_MAP = {
    0: "depart", 1: "turn-right", 2: "turn-sharp-right", 3: "turn-slight-right",
    4: "straight", 5: "turn-slight-left", 6: "turn-left", 7: "turn-sharp-left",
    8: "u-turn", 9: "u-turn", 10: "arrive", 11: "roundabout", 12: "roundabout-exit",
}


def _fetch_steps(profile, body, headers):
    """Fetch turn-by-turn steps from ORS JSON endpoint."""
    try:
        resp = requests.post(
            f"{ORS_BASE}/v2/directions/{profile}/json",
            json=body,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )
        if not resp.ok:
            return []
        data = resp.json()
        raw_steps = data["routes"][0]["segments"][0]["steps"]
        steps = []
        for s in raw_steps:
            steps.append({
                "instruction": s.get("instruction", ""),
                "distance_km": round(s.get("distance", 0) / 1000, 2),
                "duration_min": round(s.get("duration", 0) / 60, 1),
                "type": _STEP_TYPE_MAP.get(s.get("type", 4), "straight"),
                "name": s.get("name", ""),
            })
        return steps
    except Exception:
        return []


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
        is_last = (day == num_days - 1)

        if is_last:
            # Last segment takes everything remaining — avoids rounding gaps
            seg_end_idx = len(geometry) - 1
        else:
            target = seg_len * (day + 1)
            seg_end_idx = seg_start_idx
            for j in range(seg_start_idx, len(cum_dist)):
                if cum_dist[j] >= target or j == len(cum_dist) - 1:
                    seg_end_idx = j
                    break

        # Ensure at least 2 points per segment
        if seg_end_idx <= seg_start_idx:
            seg_end_idx = min(seg_start_idx + 1, len(geometry) - 1)

        pts = geometry[seg_start_idx: seg_end_idx + 1]
        if len(pts) < 2 and seg_start_idx > 0:
            pts = geometry[seg_start_idx - 1: seg_end_idx + 1]

        mid_idx = len(pts) // 2
        seg_dist = cum_dist[min(seg_end_idx, len(cum_dist) - 1)] - cum_dist[seg_start_idx]

        segments.append({
            "start": pts[0],
            "end": pts[-1],
            "midpoint": pts[mid_idx] if pts else geometry[0],
            "points": pts,
            "segment_distance_km": round(seg_dist, 2),
        })
        seg_start_idx = seg_end_idx

    return segments
