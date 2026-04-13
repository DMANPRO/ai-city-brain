# backend/agents/mobility.py

def recommend_mode(congestion: str, speed: float, rerouted: bool) -> str:
    if rerouted:
        return "Metro"
    if congestion in ("critical", "high"):
        return "Metro"
    if congestion in ("moderate", "medium"):
        return "Bike" if speed < 20 else "Auto"
    return "Car"

def travel_advisory(congestion: str, trend: str, rerouted: bool) -> str:
    if rerouted:
        return "System rerouted you to avoid congestion. Follow the suggested route."
    if congestion in ("critical", "high"):
        return "Avoid travel if possible. Switch to public transport."
    if trend == "worsening":
        return "Traffic is worsening. Start early to avoid delays."
    if congestion in ("moderate", "medium"):
        return "Moderate conditions. Allow extra time for your journey."
    return "Traffic is clear. Good time to travel."

def estimate_delay(score: float, best_route: dict) -> str:
    if best_route and "eta" in best_route:
        return f"{best_route['eta']} min (optimised route)"
    if score > 90: return "45–60 min delay"
    if score > 75: return "30–45 min delay"
    if score > 60: return "20–30 min delay"
    if score > 40: return "10–20 min delay"
    return "Under 10 min delay"

def smart_suggestions(pred: dict, rerouted: bool) -> list:
    suggestions = []
    if rerouted:
        suggestions.append("Route optimised to reduce your journey time.")
    if pred.get("incident_count", 0) > 0:
        suggestions.append("Active incidents reported — expect possible delays.")
    if pred.get("roadwork_active", False):
        suggestions.append("Road construction active — reduced lanes ahead.")
    if pred.get("trend") == "worsening":
        suggestions.append("Congestion is increasing — depart sooner if possible.")
    if pred.get("congestion") in ("critical", "high"):
        suggestions.append("Consider alternate routes or public transport today.")
    if not suggestions:
        suggestions.append("Conditions are smooth. No action needed.")
    return suggestions

def efficiency_score(score: float, best_route: dict) -> int:
    base = max(0, 100 - int(score))
    if best_route and "eta" in best_route:
        base += max(0, 30 - best_route.get("eta", 30))
    return min(100, max(0, base))

def user_experience(score: float) -> str:
    if score > 80: return "Poor"
    if score > 55: return "Moderate"
    return "Good"

def run(pred: dict) -> dict:
    if "error" in pred:
        return pred
    try:
        congestion  = str(pred.get("congestion", "medium")).lower()
        speed       = float(pred.get("avg_speed", 20))
        score       = float(pred.get("congestion_score", 50))
        trend       = str(pred.get("trend", "stable")).lower()
        best_route  = pred.get("best_route", {})
        rerouted    = bool(pred.get("rerouted", False))

        return {
            "recommended_mode": recommend_mode(congestion, speed, rerouted),
            "travel_advisory":  travel_advisory(congestion, trend, rerouted),
            "estimated_delay":  estimate_delay(score, best_route),
            "suggestions":      smart_suggestions(pred, rerouted),
            "experience_level": user_experience(score),
            "efficiency_score": efficiency_score(score, best_route),
            "best_route":       best_route,
            "rerouted":         rerouted,
        }
    except Exception as e:
        return {"error": str(e)}