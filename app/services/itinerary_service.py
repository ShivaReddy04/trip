"""Itinerary service — orchestrates route, attractions, accommodation, cost."""

import math
from .route_service import geocode_city, get_route, split_route_into_segments, haversine
from .attraction_service import get_segment_attractions
from .accommodation_service import suggest_accommodation, NIGHTLY_COST


# ---------------------------------------------------------------------------
# Cost estimation constants
# ---------------------------------------------------------------------------

FOOD_COST_PER_DAY = {"low": 400, "medium": 800, "high": 1500}          # INR
FUEL_PRICE_PER_LITRE = 105    # INR
VEHICLE_MILEAGE_KMPL = 15     # km per litre (average car)
COST_BUFFER_PERCENT = 0.10    # 10 %


# ---------------------------------------------------------------------------
# AI refinement — reorder stops to minimise total travel within a day
# ---------------------------------------------------------------------------

def _refine_stop_order(stops, day_start):
    """
    Nearest-neighbour reordering of *stops* starting from *day_start* [lat, lng].
    Returns reordered list (new list, originals untouched).
    """
    if len(stops) <= 1:
        return list(stops)

    remaining = list(stops)
    ordered = []
    current = day_start

    while remaining:
        nearest = min(
            remaining,
            key=lambda s: haversine(current[0], current[1], s["lat"], s["lng"]),
        )
        ordered.append(nearest)
        current = [nearest["lat"], nearest["lng"]]
        remaining.remove(nearest)

    return ordered


# ---------------------------------------------------------------------------
# Estimate daily + total costs
# ---------------------------------------------------------------------------

def _estimate_costs(total_distance_km, days, budget, accommodation_costs):
    """
    Return dict with per-day and total cost estimates (INR).
    """
    food_day = FOOD_COST_PER_DAY.get(budget, FOOD_COST_PER_DAY["medium"])
    fuel_total = (total_distance_km / VEHICLE_MILEAGE_KMPL) * FUEL_PRICE_PER_LITRE
    fuel_per_day = fuel_total / max(days, 1)

    total_accom = sum(accommodation_costs)
    total_food = food_day * days
    subtotal = fuel_total + total_accom + total_food
    buffer = subtotal * COST_BUFFER_PERCENT
    total = subtotal + buffer

    return {
        "fuel_total": round(fuel_total),
        "fuel_per_day": round(fuel_per_day),
        "food_per_day": food_day,
        "food_total": round(total_food),
        "accommodation_total": round(total_accom),
        "buffer": round(buffer),
        "estimated_total": round(total),
    }


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def generate_smart_itinerary(data):
    """
    Build a complete multi-day itinerary.

    Parameters
    ----------
    data : dict  {start_city, destination_city, days, budget, travel_mode}

    Returns
    -------
    (result_dict, error_string_or_None)
    """
    start_city = data.get("start_city", "").strip()
    dest_city = data.get("destination_city", "").strip()
    days = int(data.get("days", 3))
    budget = data.get("budget", "medium").lower()
    travel_mode = data.get("travel_mode", "driving").lower()

    if not start_city or not dest_city:
        return None, "start_city and destination_city are required"
    if days < 1 or days > 14:
        return None, "days must be between 1 and 14"
    if budget not in ("low", "medium", "high"):
        return None, "budget must be low, medium, or high"

    # 1. Geocode cities
    start_coords = geocode_city(start_city)
    if not start_coords:
        return None, f"Could not geocode start city: {start_city}"

    dest_coords = geocode_city(dest_city)
    if not dest_coords:
        return None, f"Could not geocode destination city: {dest_city}"

    # 2. Fetch route
    route = get_route(start_coords, dest_coords, travel_mode)
    if not route:
        return None, "Could not fetch route from OpenRouteService"

    total_distance = route["distance_km"]
    total_duration = route["duration_hours"]

    # 3. Split route into daily segments
    segments = split_route_into_segments(route["geometry"], days)

    # 4. Build each day
    day_results = []
    accommodation_costs = []

    for idx, seg in enumerate(segments):
        day_num = idx + 1
        is_last_day = (day_num == days)

        # 4a. Fetch & rank attractions for this segment
        attractions = get_segment_attractions(seg, budget=budget, limit=5)

        # 4b. AI refinement: reorder stops
        stops = _refine_stop_order(attractions, seg["start"])

        # Clean stop output
        clean_stops = []
        for s in stops:
            clean_stops.append({
                "name": s["name"],
                "lat": s["lat"],
                "lng": s["lng"],
                "type": s["type"],
                "score": s.get("score", 0),
                "distance_from_route_km": s.get("distance_km", 0),
            })

        # 4c. Accommodation (skip last day — you arrive at destination)
        stay = None
        accom_cost = 0
        if not is_last_day:
            stay = suggest_accommodation(seg["end"], budget=budget)
            accom_cost = stay.get("estimated_cost", 0)
            accommodation_costs.append(accom_cost)

        # 4d. Daily cost
        food_day = FOOD_COST_PER_DAY.get(budget, FOOD_COST_PER_DAY["medium"])
        fuel_day = ((seg["segment_distance_km"] / VEHICLE_MILEAGE_KMPL)
                     * FUEL_PRICE_PER_LITRE)
        daily_cost = round(fuel_day + food_day + accom_cost)

        day_results.append({
            "day": day_num,
            "segment_distance_km": seg["segment_distance_km"],
            "start_point": seg["start"],
            "end_point": seg["end"],
            "stops": clean_stops,
            "stay": stay,
            "daily_cost": daily_cost,
        })

    # 5. Cost summary
    costs = _estimate_costs(total_distance, days, budget, accommodation_costs)

    result = {
        "summary": {
            "start_city": start_city,
            "destination_city": dest_city,
            "travel_mode": travel_mode,
            "budget_tier": budget,
            "total_distance_km": total_distance,
            "total_duration_hours": total_duration,
            "total_days": days,
            "estimated_total_cost": costs["estimated_total"],
            "cost_breakdown": costs,
        },
        "days": day_results,
    }

    return result, None
