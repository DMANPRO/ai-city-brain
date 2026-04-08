from backend.utils.weather_api import get_weather

def run(input_text):
    data = {}

    text = input_text.lower()

    # Extract location
    if "whitefield" in text:
        data["location"] = "Bangalore"
    elif "marathahalli" in text:
        data["location"] = "Bangalore"
    else:
        data["location"] = "Bangalore"  # default

    # Extract time
    if "6" in text:
        data["time"] = 18
    elif "8" in text:
        data["time"] = 8
    else:
        data["time"] = 12  # default

    # 🔥 Fetch real weather using API
    weather = get_weather(data["location"])
    data["weather"] = weather

    return data