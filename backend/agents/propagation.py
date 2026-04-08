# ---------------------------------------
# PROPAGATION ENGINE (REAL-TIME SPREAD)
# ---------------------------------------

import math
from backend.utils.data_loader import get_coords, get_traffic_flow, get_incidents
from backend.utils.weather_api import get_weather


# ---------------------------------------
# HELPER: GENERATE NEARBY COORDS (GRID)
# ---------------------------------------
def generate_nearby_points(lat, lon, radius=0.02):
    """
    Generate nearby grid points (~2km radius)
    """
    offsets = [-radius, 0, radius]
    points = []

    for dlat in offsets:
        for dlon in offsets:
            points.append((lat + dlat, lon + dlon))

    return points


# ---------------------------------------
# HELPER: CALCULATE DISTANCE
# ---------------------------------------
def distance(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)


# ---------------------------------------
# MAIN PROPAGATION LOGIC
# ---------------------------------------
async def compute_propagation(location: str):

    coords = await get_coords(location)
    if not coords:
        return {"error": f"Location not found: {location}"}

    lat, lon = coords["lat"], coords["lon"]

    # Step 1: Get base traffic + weather
    flow = await get_traffic_flow(lat, lon)
    incidents = await get_incidents(lat, lon)
    weather = get_weather(location)

    base_flow = flow.get("flowSegmentData", {})
    base_speed = float(base_flow.get("currentSpeed", 30))
    free_speed = float(base_flow.get("freeFlowSpeed", 60))

    congestion_ratio = 1 - (base_speed / free_speed if free_speed else 1)

    # Step 2: Generate nearby regions
    nearby_points = generate_nearby_points(lat, lon)

    affected_areas = []

    # Step 3: Evaluate spread for each nearby point
    for nlat, nlon in nearby_points:

        try:
            flow_data = await get_traffic_flow(nlat, nlon)
            seg = flow_data.get("flowSegmentData", {})

            speed = float(seg.get("currentSpeed", 30))
            free = float(seg.get("freeFlowSpeed", 60))

            ratio = 1 - (speed / free if free else 1)

            # Spread condition
            if ratio > 0.4:
                affected_areas.append({
                    "lat": round(nlat, 4),
                    "lon": round(nlon, 4),
                    "congestion": round(ratio * 100, 2)
                })

        except Exception:
            continue

    # Step 4: Determine spread level
    incident_count = len(incidents.get("incidents", []))

    if congestion_ratio > 0.6 or incident_count > 3:
        spread = "high"
    elif congestion_ratio > 0.3:
        spread = "medium"
    else:
        spread = "low"

    # Step 5: Weather impact
    if weather in ["rain", "storm"]:
        spread = "high"
    elif weather in ["fog", "mist"] and spread != "high":
        spread = "medium"

    return {
        "location": location,
        "spread_level": spread,
        "affected_zones": affected_areas,
        "incident_count": incident_count,
        "weather": weather
    }


# ---------------------------------------
# WRAPPER (SYNC CALL)
# ---------------------------------------
import asyncio

def run(input_data: dict):
    location = input_data.get("location", "bengaluru")
    return asyncio.run(compute_propagation(location))