# backend/agents/propagation.py

import math
import asyncio
from backend.utils.data_loader import get_coords, get_traffic_flow, get_incidents
from backend.utils.weather_api import get_weather


def generate_nearby_points(lat, lon, radius=0.02):
    return [(lat, lon)]


def distance(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)


async def compute_propagation(location: str):

    coords = await get_coords(location)
    if not coords:
        return {"error": f"Location not found: {location}"}

    lat, lon = coords["lat"], coords["lon"]

    flow      = await get_traffic_flow(lat, lon)
    incidents = await get_incidents(lat, lon)
    weather   = get_weather(location)

    base_speed = float(flow.get("current_speed")  or 30)
    free_speed = float(flow.get("free_flow_speed") or 60)

    congestion_ratio = 1 - (base_speed / free_speed if free_speed else 1)

    # Always include center point regardless of threshold
    affected_areas = [{
        "lat":        round(lat, 4),
        "lon":        round(lon, 4),
        "congestion": round(max(congestion_ratio, 0.01) * 100, 2)
    }]

    # Spread level
    incident_count = incidents.get("incident_count", 0)

    if congestion_ratio > 0.6 or incident_count > 3:
        spread = "high"
    elif congestion_ratio > 0.3:
        spread = "medium"
    else:
        spread = "low"

    # Weather impact
    if weather in ["rain", "storm"]:
        spread = "high"
    elif weather in ["fog", "mist"] and spread != "high":
        spread = "medium"

    return {
        "location":       location,
        "spread_level":   spread,
        "affected_zones": affected_areas,
        "incident_count": incident_count,
        "weather":        weather
    }


def run(input_data: dict):
    location = input_data.get("location", "bengaluru")
    return asyncio.run(compute_propagation(location))
