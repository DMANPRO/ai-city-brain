# backend/orchestrator.py
# Person 4 - Integration & Orchestrator
# Branch: person4-integration

from backend.agents import scenario_agent
from backend.agents import traffic_prediction
from backend.agents import propagation
from backend.agents import explanation_agent

import re
from datetime import datetime, timedelta
from backend.utils.weather_api import get_weather_for_datetime

# congestion_detection.py is Person 3's file - safe import
try:
    from backend.agents import congestion_detection
except ImportError:
    class congestion_detection:
        @staticmethod
        def run(input_data):
            return input_data

# routing.py is Person 3's file - safe import
try:
    from backend.agents import routing
except ImportError:
    class routing:
        @staticmethod
        def run(input_data):
            return {
                "severity": "unknown",
                "priority": "normal",
                "signal_control": {"signal_mode": "normal_operation", "description": "N/A", "cycle_adjustment": "0%"},
                "rerouting": {"reroute": False, "strategy": "no_change", "routes": [], "priority": "low"},
                "emergency": {"emergency_mode": False},
                "distribution": {"distribution": "normal", "description": "N/A"}
            }

# mobility.py is Person 3's file - safe import
try:
    from backend.agents import mobility
except ImportError:
    class mobility:
        @staticmethod
        def run(input_data):
            return {
                "recommended_mode": "car",
                "travel_advisory": "Conditions are stable for travel",
                "estimated_delay": "No significant delay",
                "experience_level": "Good",
                "confidence": "Moderate certainty",
                "suggestions": ["Smooth traffic expected"]
            }

def extract_target_datetime(text: str) -> datetime | None:
    """
    Extracts a target date+time from the user input text.
    Supports: tomorrow, next week, day names, 'April 15', '15th', etc.
    Returns a datetime object, or None if no date is found.
    """
    text_lower = text.lower()
    now = datetime.now()

    # Extract hour
    hour = now.hour
    time_match = re.search(r'(\d{1,2})\s*(am|pm)', text_lower)
    if time_match:
        hour = int(time_match.group(1))
        if time_match.group(2) == 'pm' and hour != 12:
            hour += 12
        elif time_match.group(2) == 'am' and hour == 12:
            hour = 0

    def make_dt(base): return base.replace(hour=hour, minute=0, second=0, microsecond=0)

    if 'tomorrow'  in text_lower: return make_dt(now + timedelta(days=1))
    if 'next week' in text_lower: return make_dt(now + timedelta(days=7))
    if 'next month' in text_lower: return make_dt(now + timedelta(days=30))

    day_map = {'monday':0,'tuesday':1,'wednesday':2,'thursday':3,
               'friday':4,'saturday':5,'sunday':6}
    for day_name, day_num in day_map.items():
        if day_name in text_lower:
            ahead = (day_num - now.weekday()) % 7 or 7
            return make_dt(now + timedelta(days=ahead))

    month_map = {
        'january':1,'february':2,'march':3,'april':4,'may':5,'june':6,
        'july':7,'august':8,'september':9,'october':10,'november':11,'december':12,
        'jan':1,'feb':2,'mar':3,'apr':4,'jun':6,'jul':7,'aug':8,
        'sep':9,'oct':10,'nov':11,'dec':12
    }
    for month_str, month_num in month_map.items():
        if month_str in text_lower:
            day_match = re.search(r'(\d{1,2})(?:st|nd|rd|th)?', text_lower)
            if day_match:
                try:
                    dt = now.replace(month=month_num, day=int(day_match.group(1)),
                                     hour=hour, minute=0, second=0, microsecond=0)
                    return dt if dt >= now else dt.replace(year=now.year + 1)
                except Exception:
                    pass
    return None

# ── Main Pipeline ─────────────────────────────────────────────────────────────

def run(user_input: str) -> dict:
    """
    Full AI City Brain pipeline.
    Input:  Plain text e.g. "Rain at 6 PM in Whitefield"
    Output: Complete traffic intelligence dict
    """

    print(f"\n[Orchestrator] Input: {user_input}")

    # Step 1 — Scenario Agent (Person 2) + date-aware weather override
    target_dt = extract_target_datetime(user_input)
    scenario  = scenario_agent.run(user_input)

    if target_dt:
        location_raw = scenario.get("location", "bengaluru")
        scenario["weather"]     = get_weather_for_datetime(location_raw, target_dt)
        scenario["target_date"] = target_dt.strftime("%d %b %Y, %I:%M %p")
        print(f"[Step 1] Date detected: {target_dt} → weather: {scenario['weather']}")
    else:
        scenario["target_date"] = "Now (Live)"

    print(f"[Step 1] Scenario: {scenario}")

    # Step 2 — Traffic Prediction (Person 1)
    # Uses TomTom API + weather multiplier → congestion, speed, volume, trend
    traffic = traffic_prediction.run(scenario)
    if "error" in traffic:
        print(f"[Step 2] Error: {traffic['error']}")
        return traffic
    print(f"[Step 2] Traffic: {traffic}")

    # Step 3 — Congestion Detection (Person 3)
    # Detects hotspots from traffic data
    detection = congestion_detection.run(traffic)
    print(f"[Step 3] Detection done")

    # Step 4 — Propagation (Person 2)
    # Simulates how congestion spreads to nearby zones using TomTom
    prop = propagation.run(traffic)
    print(f"[Step 4] Propagation: {prop}")

    # Merge: carry all traffic data forward + add propagation-specific fields
    # routing and mobility both need keys from traffic (congestion_score, avg_speed, etc.)
    merged = {**traffic}
    merged["spread_level"]   = prop.get("spread_level", "unknown")
    merged["affected_zones"] = prop.get("affected_zones", [])

    # Step 5 — Routing (Person 3)
    # Signal control + rerouting strategy based on congestion_score, trend
    route = routing.run(merged)
    print(f"[Step 5] Routing done")

    # Merge routing results in for mobility
    merged = {**merged, **route}

    # Step 6 — Mobility Recommendation (Person 3)
    # Best travel mode, delay estimate, advisory based on full traffic data
    mob = mobility.run(merged)
    print(f"[Step 6] Mobility done")

    # Build complete final dict for explanation agent
    final_data = {**merged, **mob}

    # Step 7 — Explanation Agent (Person 4 - YOU)
    # Converts all data into human-readable explanation using OpenAI
    final = explanation_agent.run(final_data)
    print(f"[Orchestrator] Pipeline complete ✅\n")

    return final