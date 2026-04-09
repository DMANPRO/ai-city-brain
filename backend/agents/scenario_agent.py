# ---------------------------------------
# SCENARIO AGENT (SMART INPUT PARSER)
# ---------------------------------------

import re
from datetime import datetime
from backend.utils.weather_api import get_weather


# ---------------------------------------
# EXTRACT LOCATION (IMPROVED 🔥)
# ---------------------------------------
def extract_location(text: str) -> str:
    """
    Extract location using NLP pattern
    Example: 'traffic in whitefield at 6pm'
    """
    text = text.lower()

    # Capture text after "in" but stop before "at"
    match = re.search(r"in ([a-zA-Z\s]+?)(?: at|$)", text)

    if match:
        location = match.group(1).strip()
        return f"{location}, bengaluru"

    return "bengaluru"


# ---------------------------------------
# EXTRACT TIME (SMART + NOW SUPPORT 🔥)
# ---------------------------------------
def extract_time(text: str) -> int:
    """
    Extract hour from text (supports 6pm, 8am, 'now')
    """
    text = text.lower()

    # ✅ handle "now"
    if "now" in text:
        return datetime.now().hour

    # match time like 6pm, 8am
    match = re.search(r"(\d{1,2})(am|pm)?", text)

    if match:
        hour = int(match.group(1))
        suffix = match.group(2)

        if suffix == "pm" and hour != 12:
            hour += 12
        elif suffix == "am" and hour == 12:
            hour = 0

        return hour

    # fallback → current hour
    return datetime.now().hour


# ---------------------------------------
# MAIN FUNCTION
# ---------------------------------------
def run(input_text: str) -> dict:
    """
    Converts user input → structured data
    """

    # Step 1: Extract location
    location = extract_location(input_text)

    # Step 2: Extract time
    time = extract_time(input_text)

    # Step 3: Get real weather
    weather = get_weather(location)

    # fallback if API fails
    if not weather:
        weather = "clear"

    return {
        "location": location,
        "time": time,        # 👈 feeds into traffic_prediction
        "weather": weather
    }