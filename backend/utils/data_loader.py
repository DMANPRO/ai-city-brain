import httpx
import os
from dotenv import load_dotenv

load_dotenv()
TOMTOM_API_KEY = os.getenv("TOMTOM_API_KEY")

LOCATION_COORDS = {
    "whitefield":   {"lat": 12.9698,  "lon": 77.7499},
    "indiranagar":  {"lat": 12.9784,  "lon": 77.6408},
    "koramangala":  {"lat": 12.9352,  "lon": 77.6245},
    "hebbal":       {"lat": 13.0354,  "lon": 77.5970},
    "marathahalli": {"lat": 12.9591,  "lon": 77.6972},
    "mg road":      {"lat": 12.9757,  "lon": 77.6011},
    "electronic city": {"lat": 12.8399, "lon": 77.6770},
    "jayanagar":    {"lat": 12.9308,  "lon": 77.5838},
    "rajajinagar":  {"lat": 12.9907,  "lon": 77.5530},
    "yeshwanthpur": {"lat": 13.0280,  "lon": 77.5478},
}

async def get_coords_dynamic(location: str):
    url = f"https://api.tomtom.com/search/2/geocode/{location}.json"
    params = {"key": TOMTOM_API_KEY}

    async with httpx.AsyncClient(timeout=5) as client:
        try:
            res = await client.get(url, params=params)
            res.raise_for_status()
            data = res.json()

            results = data.get("results", [])
            if not results:
                return None

            position = results[0]["position"]

            return {
                "lat": position["lat"],
                "lon": position["lon"]
            }

        except Exception as e:
            print('Geocoding error:',e)
            return None

async def get_coords(location: str):
    location = location.lower().strip()

    # First check predefined
    if location in LOCATION_COORDS:
        return LOCATION_COORDS[location]
    return await get_coords_dynamic(location)


async def get_traffic_flow(lat: float, lon: float) -> dict:
    url = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"

    params = {
        "point": f"{lat},{lon}",
        "key": TOMTOM_API_KEY,
        "unit": "KMPH",
    }

    async with httpx.AsyncClient(timeout=5) as client:
        try:
            res = await client.get(url, params=params)
            res.raise_for_status()
            data = res.json()

            flow = data.get("flowSegmentData", {})

            return {
                "current_speed": flow.get("currentSpeed"),
                "free_flow_speed": flow.get("freeFlowSpeed"),
                "confidence": flow.get("confidence", 0.8)
            }

        except Exception as e:
            return {"error": str(e)}
            
async def get_incidents(lat: float, lon: float) -> dict:
    bbox = f"{lon-0.02},{lat-0.02},{lon+0.02},{lat+0.02}"
    url = "https://api.tomtom.com/traffic/services/5/incidentDetails"
    params = {
        "bbox": bbox,
        "key": TOMTOM_API_KEY,
        "language": "en-GB",
    }
    async with httpx.AsyncClient(timeout=5) as client:
        try:
            res = await client.get(url, params=params)
            res.raise_for_status()
            data = res.json()

            incidents = data.get("incidents", [])

            return {
                "incident_count": len(incidents),
                "has_incident": len(incidents) > 0
            }

        except Exception:
            return {
                "incident_count": 0,
                "has_incident": False
            }

CACHE = {}
async def get_live_data(location: str):
    location = location.lower().strip()
    if location in CACHE:
        return CACHE[location]
    coords = await get_coords(location)
    if not coords:
        return {"error": "invalid location"}
    lat, lon = coords["lat"], coords["lon"]
    flow = await get_traffic_flow(lat, lon)
    incidents = await get_incidents(lat, lon)
    result = {
        "location": location,
        "coordinates": coords,
        "flow": flow,
        "incidents": incidents
    }
    CACHE[location] = result
    return result
