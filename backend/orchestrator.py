import re
import random

# ─── Safe imports ─────────────────────────────────────────────────────────────
try:
    from backend.agents.scenario_agent import run as scenario_run
except ImportError:
    scenario_run = None

try:
    from backend.agents.traffic_prediction import run as traffic_run
except ImportError:
    traffic_run = None

try:
    from backend.agents.propagation import run as propagation_run
except ImportError:
    propagation_run = None

try:
    from backend.agents.routes import run as routes_run
except ImportError:
    routes_run = None

try:
    from backend.agents.mobility import run as mobility_run
except ImportError:
    mobility_run = None

try:
    from backend.agents.explanation_agent import run as explanation_run
except ImportError:
    explanation_run = None


# ─── Main run ─────────────────────────────────────────────────────────────────
def run(user_input: str) -> dict:
    try:
        # ── Step 1: Scenario ────────────────────────────────────────────────
        scenario = scenario_run(user_input) if scenario_run else {
            "location": "bengaluru",
            "weather": "clear",
            "time": "now"
        }

        location = scenario.get("location", "bengaluru")
        weather  = scenario.get("weather", "clear")
        time_str = str(scenario.get("time", "now"))

        # ── Step 2: Traffic ────────────────────────────────────────────────
        traffic = traffic_run(scenario) if traffic_run else {
            "congestion": "medium",
            "avg_speed": 30,
            "incident_count": 0,
            "trend": "stable",
            "congestion_score": 50,
            "confidence": "medium",
            "roadwork_active": False
        }

        # ── Step 3: Propagation ────────────────────────────────────────────
        prop = propagation_run({"location": location}) if propagation_run else {
            "spread_level": "medium",
            "affected_zones": []
        }

        # ── Step 4: Routes (FIXED) ─────────────────────────────────────────
        route = routes_run(traffic) if routes_run else {
            "routes": [],
            "best_route": {},
            "rerouting": {"reroute": False}
        }

        # ✅ NEW: extract upgraded routing fields
        routes_list = route.get("routes", [])
        best_route = route.get("best_route", {})
        rerouted = route.get("rerouting", {}).get("reroute", False)

        # ── Step 5: Mobility (FIXED) ───────────────────────────────────────
        mobility_input = {
            **traffic,
            "best_route": best_route,
            "rerouted": rerouted
        }

        mobility = mobility_run(mobility_input) if mobility_run else {
            "recommended_mode": "car",
            "estimated_delay": "10 mins"
        }

        # ── Step 6: Explanation ────────────────────────────────────────────
        if explanation_run:
            merged = {
                **traffic,
                **route,
                **mobility,
                "location": location,
                "weather": weather,
                "time": time_str
            }
            merged = explanation_run(merged)
            explanation = merged.get("explanation", "")
        else:
            explanation = (
                f"{location.title()} has {traffic.get('congestion')} congestion. "
                f"Best route: {best_route.get('route', 'default')}. "
                f"Recommended mode: {mobility.get('recommended_mode')}."
            )

        # ── Step 7: Final Output (CORRECTED) ───────────────────────────────
        return {
            "location": location,
            "weather": weather,
            "time": time_str,

            # 🚦 Traffic
            "congestion": traffic.get("congestion"),
            "avg_speed": traffic.get("avg_speed"),
            "trend": traffic.get("trend"),

            # 🗺️ ROUTING (FIXED)
            "routes": routes_list,
            "best_route": best_route,
            "rerouted": rerouted,

            # 🚇 Mobility
            "recommended_mode": mobility.get("recommended_mode"),
            "estimated_delay": mobility.get("estimated_delay"),
            "travel_advisory": mobility.get("travel_advisory"),
            "suggestions": mobility.get("suggestions", []),

            # 🧠 Explanation
            "explanation": explanation,

            # 🗺️ Map
            "affected_zones": prop.get("affected_zones", []),

            # 🔍 Debug
            "agent_outputs": {
                "scenario": scenario,
                "traffic": traffic,
                "propagation": prop,
                "routes": route,
                "mobility": mobility,
            }
        }

    except Exception as e:
        return {"error": str(e)}