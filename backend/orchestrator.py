import re, asyncio

def _try_import(path, fn="run"):
    try:
        import importlib
        mod = importlib.import_module(path)
        return getattr(mod, fn, None)
    except Exception:
        return None

scenario_run    = _try_import("backend.agents.scenario_agent")
traffic_run     = _try_import("backend.agents.traffic_prediction")
propagation_run = _try_import("backend.agents.propagation")
routes_run      = _try_import("backend.agents.routes")
mobility_run    = _try_import("backend.agents.mobility")
explanation_run = _try_import("backend.agents.explanation_agent")

WEATHER_MAP = {
    "heavy rain":"rainy","rain":"rainy","raining":"rainy","rainy":"rainy",
    "flood":"flooded","storm":"stormy","stormy":"stormy",
    "fog":"foggy","mist":"foggy","haze":"foggy","foggy":"foggy",
    "clear":"clear","sunny":"clear","cloudy":"cloudy",
}

def _get_coords_sync(location: str) -> dict:
    """Sync wrapper around the async geocoder."""
    try:
        from backend.utils.data_loader import get_coords
        return asyncio.run(get_coords(location))
    except Exception:
        return {"lat": 12.9716, "lon": 77.5946}

def _clean_location(raw: str) -> str:
    loc = str(raw).lower().strip()
    loc = re.sub(r',?\s*(bengaluru|bangalore).*$', '', loc).strip()
    return re.sub(r'\s+', ' ', loc) or "bengaluru"

def _parse_input(text: str) -> dict:
    """Emergency fallback parser when scenario_agent unavailable."""
    from backend.agents.scenario_agent import extract_location, extract_time, extract_weather
    return {
        "location": extract_location(text),
        "time":     extract_time(text),
        "weather":  extract_weather(text) or "clear",
    }

def _fallback_congestion(weather: str, time_str: str):
    bad  = weather in ("rainy","stormy","flooded","foggy")
    peak = any(h in time_str.replace(" ","") for h in
               ["8am","9am","6pm","7pm","5pm","08:","09:","17:","18:","19:"])
    if bad and peak: return "high",   82.0
    if bad or peak:  return "high",   68.0
    return               "medium",    45.0

def _fallback_zones(location: str) -> list:
    coords = _get_coords_sync(location)
    return [{"zone": location, "lat": coords["lat"], "lon": coords["lon"]}]

def _safe_float(v, default=0.0):
    try:    return float(v)
    except: return default

# ─── Main run ─────────────────────────────────────────────────────────────────
def run(user_input: str) -> dict:
    try:
        # ── Step 1: Scenario ─────────────────────────────────────────
        scenario = {}
        if scenario_run:
            out = scenario_run(user_input)
            if isinstance(out, dict) and "error" not in out:
                scenario = out
        if not scenario:
            scenario = _parse_input(user_input)

        location = _clean_location(scenario.get("location", "bengaluru"))
        weather  = str(scenario.get("weather", "clear")).strip()
        time_str = str(scenario.get("time", "now")).strip()

        # ── Step 2: Traffic prediction ────────────────────────────────
        traffic = {}
        if traffic_run:
            out = traffic_run({"location": location, "weather": weather, "time": time_str})
            if isinstance(out, dict) and "error" not in out:
                traffic = out

        cong_label, cong_score = _fallback_congestion(weather, time_str)
        traffic.setdefault("location",         location)
        traffic.setdefault("weather",          weather)
        traffic.setdefault("time",             time_str)
        traffic.setdefault("congestion",       cong_label)
        traffic.setdefault("congestion_score", cong_score)
        traffic.setdefault("avg_speed",        22.0)
        traffic.setdefault("free_flow_speed",  60.0)
        traffic.setdefault("traffic_volume",   "medium")
        traffic.setdefault("incident_count",   0)
        traffic.setdefault("incident_types",   [])
        traffic.setdefault("road_work_active", False)
        traffic.setdefault("roadwork_active",  False)
        traffic.setdefault("confidence",       "medium")
        traffic.setdefault("trend",            "stable")
        traffic.setdefault("trend_delta",      "")
        traffic["location"]        = location
        traffic["congestion_score"]= _safe_float(traffic["congestion_score"], cong_score)
        traffic["avg_speed"]       = _safe_float(traffic["avg_speed"], 22.0)
        traffic["free_flow_speed"] = _safe_float(traffic["free_flow_speed"], 60.0)
        traffic["roadwork_active"] = bool(traffic.get("road_work_active",
                                          traffic.get("roadwork_active", False)))
        traffic["road_work_active"]= traffic["roadwork_active"]

        # ── Step 3: Propagation ───────────────────────────────────────
        prop = {}
        if propagation_run:
            out = propagation_run({"location": location})
            if isinstance(out, dict) and "error" not in out:
                prop = out
        prop.setdefault("spread_level",   "medium")
        prop.setdefault("affected_zones", _fallback_zones(location))
        zones = [z for z in prop.get("affected_zones", [])
                 if isinstance(z, dict) and "lat" in z and "lon" in z]
        if not zones:
            zones = _fallback_zones(location)
        prop["affected_zones"] = zones

        # ── Step 4: Routes ────────────────────────────────────────────
        route = {}
        if routes_run:
            out = routes_run(traffic)
            if isinstance(out, dict) and "error" not in out:
                route = out
        route.setdefault("severity",       "high")
        route.setdefault("priority",       "Urgent")
        route.setdefault("signal_control", {"signal_mode":"adaptive_control","description":"Dynamic","cycle_adjustment":"+25%"})
        route.setdefault("rerouting",      {"reroute":True,"strategy":"load_balancing","routes":[],"priority":"high"})
        route.setdefault("routes",         [{"route":"main_route","traffic":"medium","eta":20,"distance":5}])
        route.setdefault("best_route",     {"route":"main_route","eta":20,"distance":5})
        route.setdefault("emergency",      {"emergency_mode":False})
        route.setdefault("distribution",   {"distribution":"normal","description":"Normal flow"})

        # ── Step 5: Mobility ──────────────────────────────────────────
        mobility = {}
        if mobility_run:
            out = mobility_run({**traffic, "best_route": route["best_route"],
                                "rerouted": route["rerouting"].get("reroute", False)})
            if isinstance(out, dict) and "error" not in out:
                mobility = out
        mobility.setdefault("recommended_mode", "Metro")
        mobility.setdefault("travel_advisory",  "Check live conditions before travelling.")
        mobility.setdefault("estimated_delay",  "10-20 min")
        mobility.setdefault("experience_level", "Moderate")
        mobility.setdefault("suggestions",      [])
        mobility.setdefault("efficiency_score", 55)
        mobility.setdefault("best_route",       route["best_route"])
        mobility.setdefault("rerouted",         False)

        # ── Step 6: Explanation ───────────────────────────────────────
        merged = {**traffic, **prop, **route, **mobility,
                  "location": location, "weather": weather, "time": time_str}
        explanation = ""
        if explanation_run:
            out = explanation_run(merged)
            if isinstance(out, dict):
                merged.update(out)
                explanation = merged.get("explanation", "")
            elif isinstance(out, str):
                explanation = out
        if not explanation:
            delay = mobility.get("estimated_delay", "N/A")
            mode  = mobility.get("recommended_mode", "car")
            explanation = (
                f"In {location.title()}, {weather} conditions are causing "
                f"{traffic['congestion']} congestion with average speed "
                f"{traffic['avg_speed']} km/h. Estimated delay: {delay}. "
                f"Best travel option: {mode}."
            )

        # ── Resolve coordinates for map ───────────────────────────────
        coords = _get_coords_sync(location)

        return {
            "location":         location,
            "coordinates":      coords,
            "weather":          weather,
            "time":             time_str,
            "congestion":       traffic["congestion"],
            "congestion_score": traffic["congestion_score"],
            "avg_speed":        traffic["avg_speed"],
            "free_flow_speed":  traffic["free_flow_speed"],
            "traffic_volume":   traffic["traffic_volume"],
            "incident_count":   traffic["incident_count"],
            "incident_types":   traffic["incident_types"],
            "road_work_active": traffic["road_work_active"],
            "trend":            traffic["trend"],
            "trend_delta":      traffic["trend_delta"],
            "confidence":       traffic["confidence"],
            "spread_level":     prop["spread_level"],
            "affected_zones":   zones,
            "estimated_delay":  mobility["estimated_delay"],
            "recommended_mode": mobility["recommended_mode"],
            "travel_advisory":  mobility["travel_advisory"],
            "suggestions":      mobility["suggestions"],
            "experience_level": mobility["experience_level"],
            "efficiency_score": mobility["efficiency_score"],
            "routes":           route["routes"],
            "best_route":       route["best_route"],
            "explanation":      explanation,
            "agent_outputs": {
                "scenario":    scenario,
                "traffic":     traffic,
                "propagation": prop,
                "routes":      route,
                "mobility":    mobility,
            },
        }
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}
