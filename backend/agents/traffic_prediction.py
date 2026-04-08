import asyncio
from datetime import datetime
from backend.utils.data_loader import get_live_data 
WEATHER_MULTIPLIERS = {
    "clear":  1.0,
    "rain":   1.3,
    "fog":    1.2,
    "storm":  1.5,
    "cloudy": 1.05,
}

def classify_congestion(score: float) -> str:
    if score >= 100:  return "high"
    elif score >= 60: return "medium"
    else:             return "low"

def classify_volume(ratio: float) -> str:
    if ratio <= 0.3:   return "very high"
    elif ratio <= 0.5: return "high"
    elif ratio <= 0.75: return "medium"
    else:              return "low"

def get_confidence(tomtom_confidence: float) -> str:
    if tomtom_confidence >= 0.8: return "high"
    elif tomtom_confidence >= 0.5: return "medium"
    else: return "low"

def get_trend(current_speed: float, free_flow_speed: float) -> dict:
    ratio = current_speed / free_flow_speed if free_flow_speed > 0 else 1.0
    delta = round((1 - ratio) * 100, 2)
    if delta > 40:   
        trend = "worsening"
    elif delta > 15: 
        trend = "moderate"
    else:            
        trend = "stable"
    return {"trend": trend, "delta": delta}
async def fetch_prediction(input_data: dict) -> dict:
    location = input_data.get("location", "").strip().lower()
    weather  = input_data.get("weather", "clear").strip().lower()
    now = datetime.now()
    time     = now.strftime("%H:%M")
    live_data = await get_live_data(location)
    if "error" in live_data:
        return live_data
    flow = live_data.get("flow", {})
    incidents = live_data.get("incidents", {})
    current_speed = float(flow.get("current_speed", 30))
    free_flow_speed = float(flow.get("free_flow_speed", 60))
    confidence = float(flow.get("confidence", 0.5))
    speed_ratio = current_speed / free_flow_speed if free_flow_speed > 0 else 1.0
    base_score = round((1 - speed_ratio) * 100, 2)
    weather_mult = WEATHER_MULTIPLIERS.get(weather, 1.0)
    adjusted_score = min(round(base_score * weather_mult, 2), 200)
    incident_count = incidents.get("incident_count", 0)
    if incident_count > 0:
        adjusted_score = min(round(adjusted_score * 1.2, 2), 200)
    roadwork_active = incidents.get("has_incident", False)
    trend_data = get_trend(current_speed, free_flow_speed)
    return {
        "location":          location,
        "time":              time,
        "weather":           weather,
        "congestion":        classify_congestion(adjusted_score),
        "congestion_score":  adjusted_score,
        "avg_speed":         current_speed,
        "free_flow_speed":   free_flow_speed,
        "traffic_volume":    classify_volume(speed_ratio),
        "incident_count":    incident_count,
        "roadwork_active":   roadwork_active,
        "confidence":        get_confidence(confidence),
        "trend":             trend_data["trend"],
        "trend_delta":       trend_data["delta"],
    }

def run(input_data: dict) -> dict:
    return asyncio.run(fetch_prediction(input_data))
