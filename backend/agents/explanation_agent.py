def run(input_data):
    congestion = input_data.get("congestion", "unknown")
    mode = input_data.get("recommended_mode", "unknown")
    location = input_data.get("location", "the area")
    weather = input_data.get("weather", "current conditions")

    explanation = (
        f"Due to {weather} in {location}, traffic congestion is {congestion}. "
        f"The recommended travel mode is {mode}."
    )
    input_data["explanation"] = explanation
    return input_data