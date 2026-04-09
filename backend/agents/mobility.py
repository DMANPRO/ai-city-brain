# ---------------------------------------
# MOBILITY ENGINE (USER-LEVEL INTELLIGENCE)
# ---------------------------------------

# ---------------------------------------
# MODE RECOMMENDATION (UPGRADED)
# ---------------------------------------
def recommend_mode(pred, best_route=None, rerouted=False):
    severity = pred["congestion"]
    speed = pred["avg_speed"]

    # 🔥 NEW: route-aware logic
    if rerouted:
        return "metro"

    if severity == "high":
        return "metro"

    elif severity == "medium":
        if speed < 20:
            return "bike"
        return "auto"

    else:
        return "car"


# ---------------------------------------
# TRAVEL ADVISORY (UPGRADED)
# ---------------------------------------
def travel_advisory(pred, rerouted=False):
    severity = pred["congestion"]
    trend = pred["trend"]

    if rerouted:
        return "System rerouted you to avoid congestion"

    if severity == "high":
        return "Avoid travel if possible or switch to public transport"

    if trend == "worsening":
        return "Start early to avoid increasing congestion"

    return "Conditions are stable for travel"


# ---------------------------------------
# DELAY ESTIMATION (UPGRADED WITH ROUTES)
# ---------------------------------------
def estimate_delay(pred, best_route=None):
    score = pred["congestion_score"]

    # 🔥 NEW: if route has ETA use that
    if best_route and "eta" in best_route:
        return f"{best_route['eta']} min (optimized route)"

    if score > 90:
        return "30-45 min delay"
    elif score > 70:
        return "20-30 min delay"
    elif score > 50:
        return "10-20 min delay"
    else:
        return "No significant delay"


# ---------------------------------------
# SMART RECOMMENDATIONS (UPGRADED)
# ---------------------------------------
def smart_suggestions(pred, rerouted=False):
    suggestions = []

    if rerouted:
        suggestions.append("Route optimized to reduce congestion")

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
# NEW: TRAVEL EFFICIENCY SCORE
# ---------------------------------------
def efficiency_score(pred, best_route=None):
    base = 100 - pred["congestion_score"]

    if best_route and "eta" in best_route:
        base += max(0, 30 - best_route["eta"])

    return min(100, max(0, base))


# ---------------------------------------
# MAIN FUNCTION (UPGRADED)
# ---------------------------------------
def run(pred: dict) -> dict:

    if "error" in pred:
        return pred

    # 🔥 NEW: get routing data from pred (passed by orchestrator)
    best_route = pred.get("best_route", {})
    rerouted = pred.get("rerouted", False)

    # original logic (enhanced)
    mode = recommend_mode(pred, best_route, rerouted)
    advisory = travel_advisory(pred, rerouted)
    delay = estimate_delay(pred, best_route)
    suggestions = smart_suggestions(pred, rerouted)
    confidence_msg = interpret_confidence(pred["confidence"])
    experience = user_experience(pred)
    efficiency = efficiency_score(pred, best_route)

    return {
        "recommended_mode": mode,
        "travel_advisory": advisory,
        "estimated_delay": delay,
        "experience_level": experience,
        "confidence": confidence_msg,
        "suggestions": suggestions,

        # 🔥 NEW FIELDS
        "best_route": best_route,
        "rerouted": rerouted,
        "efficiency_score": efficiency
    }