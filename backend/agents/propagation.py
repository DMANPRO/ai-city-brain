def run(input_data):
    location = input_data.get("location")
    weather = input_data.get("weather")

    # Nearby area mapping
    nearby_map = {
        "Bangalore": ["Whitefield", "Marathahalli", "Brookefield"],
        "Whitefield": ["Brookefield", "Marathahalli"],
        "Marathahalli": ["Bellandur", "Whitefield"]
    }

    affected = nearby_map.get(location, [])

    # 🔥 Smart logic based on weather
    if weather in ["rain", "storm", "drizzle"]:
        spread_level = "high"
        affected = affected + ["Outer Ring Road"]
    elif weather in ["clouds", "mist"]:
        spread_level = "medium"
    else:
        spread_level = "low"

    return {
        "affected_areas": affected,
        "spread_level": spread_level
    }