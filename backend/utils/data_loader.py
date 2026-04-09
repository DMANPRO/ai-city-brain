import httpx
import os
import time as time_module
from dotenv import load_dotenv

load_dotenv()
TOMTOM_API_KEY = os.getenv("TOMTOM_API_KEY")

LOCATION_COORDS = {
    "whitefield":      {"lat": 12.9698, "lon": 77.7499},
    "indiranagar":     {"lat": 12.9784, "lon": 77.6408},
    "koramangala":     {"lat": 12.9352, "lon": 77.6245},
    "hebbal":          {"lat": 13.0354, "lon": 77.5970},
    "marathahalli":    {"lat": 12.9591, "lon": 77.6972},
    "mg road":         {"lat": 12.9757, "lon": 77.6011},
    "electronic city": {"lat": 12.8399, "lon": 77.6770},
    "jayanagar":       {"lat": 12.9308, "lon": 77.5838},
    "rajajinagar":     {"lat": 12.9907, "lon": 77.5530},
    "yeshwanthpur":    {"lat": 13.0280, "lon": 77.5478},
}

# Cache with expiry (5 minutes)
CACHE = {}
CACHE_TTL = 300

def get_cached(key):
    if key in CACHE:
        data, ts = CACHE[key]
        if time_module.time() - ts < CACHE_TTL:
            return data
    return None

def set_cache(key, value):
    CACHE[key] = (value, time_module.time())


# --- Geocoding API ---
async def get_coords_dynamic(location: str):
    url = f"https://api.tomtom.com/search/2/geocode/{location},Bangalore.json"
    params = {"key": TOMTOM_API_KEY}
    async with httpx.AsyncClient(timeout=5) as client:
        try:
            res = await client.get(url, params=params)
            res.raise_for_status()
            results = res.json().get("results", [])
            if not results:
                return None
            position = results[0]["position"]
            return {"lat": position["lat"], "lon": position["lon"]}
        except Exception as e:
            print("Geocoding error:", e)
            return None

async def get_coords(location: str):
    location = location.lower().strip()
    if location in LOCATION_COORDS:
        return LOCATION_COORDS[location]
    return await get_coords_dynamic(location)


# --- Reverse Geocoding API ---
async def reverse_geocode(lat: float, lon: float) -> str:
    url = f"https://api.tomtom.com/search/2/reverseGeocode/{lat},{lon}.json"
    params = {"key": TOMTOM_API_KEY}
    async with httpx.AsyncClient(timeout=5) as client:
        try:
            res = await client.get(url, params=params)
            res.raise_for_status()
            addresses = res.json().get("addresses", [])
            if not addresses:
                return "Unknown Location"
            addr = addresses[0].get("address", {})
            # Return neighbourhood or municipality
            return (
                addr.get("neighbourhood") or
                addr.get("municipalitySubdivision") or
                addr.get("municipality") or
                "Unknown Location"
            )
        except Exception as e:
            print("Reverse geocoding error:", e)
            return "Unknown Location"

async def search_locations(query: str, limit: int = 5) -> list:
    url = f"https://api.tomtom.com/search/2/search/{query}.json"
    params = {
        "key":          TOMTOM_API_KEY,
        "countrySet":   "IN",
        "lat":          12.9716,   # Bangalore center bias
        "lon":          77.5946,
        "radius":       30000,     # 30km radius around Bangalore
        "limit":        limit,
        "typeahead":    True,
    }
    async with httpx.AsyncClient(timeout=5) as client:
        try:
            res = await client.get(url, params=params)
            res.raise_for_status()
            results = res.json().get("results", [])
            suggestions = []
            for r in results:
                addr = r.get("address", {})
                suggestions.append({
                    "name":    r.get("poi", {}).get("name") or addr.get("freeformAddress", ""),
                    "area":    addr.get("municipalitySubdivision") or addr.get("municipality", ""),
                    "lat":     r["position"]["lat"],
                    "lon":     r["position"]["lon"],
                })
            return suggestions
        except Exception as e:
            print("Search error:", e)
            return []

async def get_traffic_flow(lat: float, lon: float) -> dict:
    url = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"
    params = {"point": f"{lat},{lon}", "key": TOMTOM_API_KEY, "unit": "KMPH"}
    async with httpx.AsyncClient(timeout=5) as client:
        try:
            res = await client.get(url, params=params)
            res.raise_for_status()
            flow = res.json().get("flowSegmentData", {})
            return {
                "current_speed":   flow.get("currentSpeed"),
                "free_flow_speed": flow.get("freeFlowSpeed"),
                "confidence":      flow.get("confidence", 0.8),
            }
        except Exception as e:
            return {"error": str(e)}

INCIDENT_TYPES = {
    0:  "Unknown",
    1:  "Accident",
    2:  "Fog",
    3:  "Dangerous Conditions",
    4:  "Rain",
    5:  "Ice",
    6:  "Jam",
    7:  "Lane Closed",
    8:  "Road Closed",
    9:  "Road Works",
    10: "Wind",
    11: "Flooding",
    14: "Broken Down Vehicle",
}

async def get_incidents(lat: float, lon: float) -> dict:
    bbox = f"{lon-0.02},{lat-0.02},{lon+0.02},{lat+0.02}"
    url = "https://api.tomtom.com/traffic/services/5/incidentDetails"
    params = {"bbox": bbox, "key": TOMTOM_API_KEY, "language": "en-GB"}
    async with httpx.AsyncClient(timeout=5) as client:
        try:
            res = await client.get(url, params=params)
            res.raise_for_status()
            incidents = res.json().get("incidents", [])
            parsed = []
            for i in incidents:
                props = i.get("properties", {})
                type_id = props.get("iconCategory", 0)
                parsed.append({
                    "type":        INCIDENT_TYPES.get(type_id, "Unknown"),
                    "type_id":     type_id,
                    "description": props.get("description", ""),
                })
            return {
                "incident_count": len(parsed),
                "has_incident":   len(parsed) > 0,
                "incidents":      parsed,
            }
        except Exception:
            return {"incident_count": 0, "has_incident": False, "incidents": []}

async def get_matrix_travel_times(origin: dict, destinations: list) -> list:
    """
    origin       = {"lat": 12.93, "lon": 77.62}
    destinations = [{"lat": ..., "lon": ...}, ...]
    Returns list of travel times in seconds per destination
    """
    url = "https://api.tomtom.com/routing/1/matrix/sync/json"
    params = {"key": TOMTOM_API_KEY}

    body = {
        "origins": [
            {"point": {"latitude": origin["lat"], "longitude": origin["lon"]}}
        ],
        "destinations": [
            {"point": {"latitude": d["lat"], "longitude": d["lon"]}}
            for d in destinations
        ],
    }

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            res = await client.post(url, params=params, json=body)
            res.raise_for_status()
            matrix = res.json().get("matrix", [[]])
            results = []
            for i, dest in enumerate(destinations):
                try:
                    travel_time = matrix[0][i]["response"]["routeSummary"]["travelTimeInSeconds"]
                    results.append({
                        "destination": dest.get("name", f"dest_{i}"),
                        "travel_time_seconds": travel_time,
                        "travel_time_minutes": round(travel_time / 60, 1),
                    })
                except Exception:
                    results.append({
                        "destination": dest.get("name", f"dest_{i}"),
                        "travel_time_seconds": None,
                        "travel_time_minutes": None,
                    })
            return results
        except Exception as e:
            print("Matrix routing error:", e)
            return []

async def get_live_data(location: str) -> dict:
    location = location.lower().strip()

    # 🔥 FIX 1: Extract clean area name (remove ", bangalore, india")
    clean_location = location.split(",")[0].strip()

    print("📍 INPUT LOCATION:", location)
    print("📍 CLEAN LOCATION:", clean_location)

    # ---------------------------------------
    # CACHE CHECK
    # ---------------------------------------
    cached = get_cached(clean_location)
    if cached:
        return cached

    # ---------------------------------------
    # GET COORDS (USE CLEAN NAME FIRST)
    # ---------------------------------------
    coords = await get_coords(clean_location)

    # 🔥 FIX 2: If dynamic fails, fallback to known locations manually
    if not coords:
        print("⚠️ Dynamic geocode failed, trying known locations...")

        if clean_location in LOCATION_COORDS:
            coords = LOCATION_COORDS[clean_location]
            print("✅ Using predefined coords:", coords)
        else:
            return {"error": f"invalid location: {location}"}

    lat, lon = coords["lat"], coords["lon"]
    print("📌 FINAL COORDS:", lat, lon)

    # ---------------------------------------
    # FETCH TRAFFIC DATA
    # ---------------------------------------
    import asyncio
    flow, incidents = await asyncio.gather(
        get_traffic_flow(lat, lon),
        get_incidents(lat, lon),
    )

    # ---------------------------------------
    # RESULT
    # ---------------------------------------
    result = {
        "location": clean_location,   # 🔥 FIX 3: return actual area
        "coordinates": coords,
        "flow": flow,
        "incidents": incidents,
    }

    # CACHE STORE
    set_cache(clean_location, result)

    return result
