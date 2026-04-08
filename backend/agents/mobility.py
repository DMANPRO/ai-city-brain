# ---------------------------------------
# MOBILITY ENGINE (USER-LEVEL INTELLIGENCE)
# ---------------------------------------

# ---------------------------------------
# MODE RECOMMENDATION
# ---------------------------------------
def recommend_mode(pred):
    severity = pred["congestion"]
    speed = pred["avg_speed"]

    if severity == "high":
        return "metro"
    elif severity == "medium":
        if speed < 20:
            return "bike"
        return "auto"
    else:
        return "car"


# ---------------------------------------
# TRAVEL ADVISORY
# ---------------------------------------
def travel_advisory(pred):
    severity = pred["congestion"]
    trend = pred["trend"]

    if severity == "high":
        return "Avoid travel if possible or switch to public transport"

    if trend == "worsening":
        return "Start early to avoid increasing congestion"

    return "Conditions are stable for travel"


# ---------------------------------------
# DELAY ESTIMATION
# ---------------------------------------
def estimate_delay(pred):
    score = pred["congestion_score"]

    if score > 90:
        return "30-45 min delay"
    elif score > 70:
        return "20-30 min delay"
    elif score > 50:
        return "10-20 min delay"
    else:
        return "No significant delay"


# ---------------------------------------
# SMART RECOMMENDATIONS
# ---------------------------------------
def smart_suggestions(pred):
    suggestions = []

    if pred["incident_count"] > 0:
        suggestions.append("Possible roadblocks ahead")

    if pred["roadwork_active"]:
        suggestions.append("Road construction may slow traffic")

    if pred["trend"] == "worsening":
        suggestions.append("Traffic likely to increase soon")

    if pred["congestion"] == "high":
        suggestions.append("Consider alternate routes or public transport")

    if not suggestions:
        suggestions.append("Smooth traffic expected")

    return suggestions


# ---------------------------------------
# CONFIDENCE INTERPRETATION
# ---------------------------------------
def interpret_confidence(conf):
    return {
        "high": "Reliable prediction",
        "medium": "Moderate certainty",
        "low": "Prediction may vary"
    }.get(conf, "Unknown confidence")


# ---------------------------------------
# USER EXPERIENCE SCORE
# ---------------------------------------
def user_experience(pred):
    score = pred["congestion_score"]

    if score > 80:
        return "Poor"
    elif score > 60:
        return "Moderate"
    else:
        return "Good"


# ---------------------------------------
# MAIN FUNCTION
# ---------------------------------------
def run(pred: dict) -> dict:

    if "error" in pred:
        return pred

    mode = recommend_mode(pred)
    advisory = travel_advisory(pred)
    delay = estimate_delay(pred)
    suggestions = smart_suggestions(pred)
    confidence_msg = interpret_confidence(pred["confidence"])
    experience = user_experience(pred)

    return {
        "recommended_mode": mode,
        "travel_advisory": advisory,
        "estimated_delay": delay,
        "experience_level": experience,
        "confidence": confidence_msg,
        "suggestions": suggestions
    }