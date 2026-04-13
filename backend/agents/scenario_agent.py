# backend/agents/scenario_agent.py

import re
from datetime import datetime
from backend.utils.weather_api import get_weather

# Known zones — checked first, longest match wins
KNOWN_ZONES = [
    # Multi-word first (longest match wins)
    "electronic city", "mg road", "hsr layout", "jp nagar", "kr puram",
    "silk board", "frazer town", "richmond town", "vasanth nagar",
    "sadashivanagar", "rt nagar", "ht layout", "bannerghatta road",
    "old airport road", "new bel road", "rajajinagar", "malleswaram",
    "seshadripuram", "shivajinagar",
    # Single-word zones
    "whitefield", "koramangala", "indiranagar", "hebbal", "marathahalli",
    "jayanagar", "yeshwanthpur", "banashankari", "ulsoor",
    "bellandur", "sarjapur", "domlur", "bommanahalli",
    "uttarahalli", "kanakapura", "mysore road", "tumkur road",
    "hosur road", "yelahanka", "devanahalli", "hennur", "kogilu",
    "banaswadi", "ramamurthy nagar", "hoodi", "mahadevapura",
    "brookefield", "varthur", "panathur", "kadugodi", "vidyaranyapura",
    "peenya", "nagarbhavi", "kengeri", "rajarajeshwari nagar",
    "ullal", "nagarabhavi", "jalahalli", "jakkur", "thanisandra",
    "kalyan nagar", "kammanahalli", "st johns", "kodigehalli",
    "vijayanagar", "basaveshwara nagar", "rajanukunte", "attibele",
    "chandapura", "anekal", "begur", "gottigere", "hulimavu",
    "btm layout", "hbr layout", "sahakara nagar",
    "bengaluru", "bangalore",
]

TIME_RE  = re.compile(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)', re.I)
HOUR_RE  = re.compile(r'\b(\d{1,2})\s*(am|pm)\b', re.I)
STOP_RE  = re.compile(r'\s+(at|during|when|from|to|with|rain|fog|storm|traffic|congestion)\b', re.I)

WEATHER_KW = {
    "heavy rain": "rainy", "rain": "rainy", "raining": "rainy",
    "flood": "flooded",    "storm": "stormy",
    "fog": "foggy",        "mist": "foggy",  "haze": "foggy",
    "clear": "clear",      "sunny": "clear", "cloudy": "cloudy",
}

def extract_location(text: str) -> str:
    t = text.lower()
    # 1. Check known zones by name (longest match wins)
    for zone in KNOWN_ZONES:
        if zone in t:
            return zone
    # 2. Regex fallback: "in <location> at/during/..."
        # 2. Regex: "in <location> at/during/..."
    m = re.search(r'\bin\s+([a-z][a-z\s]{1,25}?)(?=\s+at\b|\s+during\b|\s+when\b|\s+with\b|\s*$)', t)
    if m:
        loc = m.group(1).strip()
        if loc and loc not in ("bengaluru", "bangalore", "the", "a"):
            return loc

    # 3. First word(s) before a time or keyword — e.g. "uttarahalli 6pm tomorrow"
    m2 = re.search(r'^([a-z][a-z\s]{1,30}?)(?=\s+\d{1,2}(?:am|pm|\s*:\s*\d{2})|\s+at\b|\s+tomorrow|\s+today|\s+tonight|\s+morning|\s+evening|\s+now\b)', t)
    if m2:
        loc = m2.group(1).strip()
        stop = {"traffic","congestion","road","route","how","is","the","what","a","an"}
        if loc and loc not in stop and len(loc) > 2:
            return loc

    return "bengaluru"

def extract_time(text: str) -> str:
    t = text.lower()
    m = TIME_RE.search(t) or HOUR_RE.search(t)
    if m:
        groups = m.groups()
        hour = int(groups[0])
        suffix = groups[-1].lower() if groups[-1] else None
        if suffix == "pm" and hour != 12:
            hour += 12
        elif suffix == "am" and hour == 12:
            hour = 0
        minute = int(groups[1]) if len(groups) > 2 and groups[1] else 0
        return f"{hour:02d}:{minute:02d}"
    return datetime.now().strftime("%H:%M")

def extract_weather(text: str) -> str:
    t = text.lower()
    for kw, label in WEATHER_KW.items():
        if kw in t:
            return label
    return None   # Will be replaced by live weather

def run(input_text: str) -> dict:
    location = extract_location(input_text)
    time_str = extract_time(input_text)
    weather_hint = extract_weather(input_text)

    # Try live weather; fall back to text hint or "clear"
    try:
        live_weather = get_weather(location)
        weather = live_weather if live_weather else (weather_hint or "clear")
    except Exception:
        weather = weather_hint or "clear"

    return {
        "location": location,
        "time":     time_str,
        "weather":  weather,
    }