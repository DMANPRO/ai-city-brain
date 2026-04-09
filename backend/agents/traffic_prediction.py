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
TIME_SPEED_MAP = {
    "morning_rush":  {"hours": range(7, 11),  "speed": 15},  # 7-10am
    "evening_rush":  {"hours": range(17, 21), "speed": 12},  # 5-8pm
    "afternoon":     {"hours": range(11, 17), "speed": 28},  # 11am-5pm
    "night":         {"hours": range(21, 24), "speed": 45},  # 9pm-12am
    "late_night":    {"hours": range(0, 6),   "speed": 50},  # 12am-6am
    "early_morning": {"hours": range(6, 7),   "speed": 35},  # 6-7am
}

def get_simulated_speed(hour: int, free_flow_speed: float) -> float:
    for period, data in TIME_SPEED_MAP.items():
        if hour in data["hours"]:
            return min(data["speed"], free_flow_speed)
    return free_flow_speed * 0.8

TIME_MULTIPLIERS = {
    range(7, 11):  1.3,   # morning rush
    range(17, 21): 1.5,   # evening peak
    range(0, 6):   0.7,   # late night
    range(22, 24): 0.7,   # night
}

def get_time_multiplier(hour: int) -> float:
    for time_range, mult in TIME_MULTIPLIERS.items():
        if hour in time_range:
            return mult
    return 1.0

def classify_congestion(score: float) -> str:
    if score >= 100:  return "high"
    elif score >= 60: return "medium"
    else:             return "low"

def classify_volume(ratio: float) -> str:
    if ratio <= 0.3:    return "very high"
    elif ratio <= 0.5:  return "high"
    elif ratio <= 0.75: return "medium"
    else:               return "low"

def get_confidence(tomtom_confidence: float) -> str:
    if tomtom_confidence >= 0.8:   return "high"
    elif tomtom_confidence >= 0.5: return "medium"
    else:                          return "low"

def get_trend(current_speed: float, free_flow_speed: float) -> dict:
    ratio = current_speed / free_flow_speed if free_flow_speed > 0 else 1.0
    delta = round((1 - ratio) * 100, 2)
    if delta > 40:   trend = "worsening"
    elif delta > 15: trend = "moderate"
    else:            trend = "stable"
    return {"trend": trend, "delta": delta}

async def fetch_prediction(input_data: dict) -> dict:

    location = input_data.get("location", "").strip().lower()
    weather  = input_data.get("weather", "clear").strip().lower()
    input_time = input_data.get("time")
    if isinstance(input_time, int):
        hour = input_time
    elif isinstance(input_time, str):
        try:
            hour = int(input_time.split(":")[0])
        except Exception:
            hour = datetime.now().hour
    else:
        hour = datetime.now().hour

    custom_time_given = input_data.get("time") is not None
    live_data = await get_live_data(location)
    if "error" in live_data:
        return live_data

    flow      = live_data.get("flow", {})
    incidents = live_data.get("incidents", {})

    current_speed   = float(flow.get("current_speed", 30))
    free_flow_speed = float(flow.get("free_flow_speed", 60))
    confidence      = float(flow.get("confidence", 0.5))
    weather_mult = WEATHER_MULTIPLIERS.get(weather, 1.0)

    if custom_time_given:
        # Simulate speed at requested hour using Bangalore real-world averages
        simulated_speed = get_simulated_speed(hour, free_flow_speed)
        speed_ratio     = simulated_speed / free_flow_speed if free_flow_speed > 0 else 1.0
        base_score      = round((1 - speed_ratio) * 100, 2)
        adjusted_score  = min(round(base_score * weather_mult, 2), 200)
        display_speed   = round(simulated_speed, 2)
    else:
        # Use real live TomTom speed + time multiplier
        time_mult      = get_time_multiplier(hour)
        speed_ratio    = current_speed / free_flow_speed if free_flow_speed > 0 else 1.0
        base_score     = round((1 - speed_ratio) * 100, 2)
        adjusted_score = min(round(base_score * weather_mult * time_mult, 2), 200)
        display_speed  = current_speed

    incident_count = incidents.get("incident_count", 0)
    incident_list  = incidents.get("incidents", [])
    incident_types = list(set(i["type"] for i in incident_list))

    if incident_count > 0:
        adjusted_score = min(round(adjusted_score * 1.2, 2), 200)

    roadwork_active = any(i["type_id"] == 9 for i in incident_list)
    trend_data = get_trend(current_speed, free_flow_speed)
    return {
        "location":          location,
        "time":              f"{hour}:00",
        "weather":           weather,
        "congestion":        classify_congestion(adjusted_score),
        "congestion_score":  adjusted_score,
        "avg_speed":         display_speed,
        "free_flow_speed":   free_flow_speed,
        "traffic_volume":    classify_volume(speed_ratio),
        "incident_count":    incident_count,
        "incident_types":    incident_types,
        "roadwork_active":   roadwork_active,
        "confidence":        get_confidence(confidence),
        "trend":             trend_data["trend"],
        "trend_delta":       trend_data["delta"],
    }

def run(input_data: dict) -> dict:
    return asyncio.run(fetch_prediction(input_data))
