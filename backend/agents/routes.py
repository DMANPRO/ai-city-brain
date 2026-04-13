# backend/agents/routes.py

THRESHOLDS = {"critical": 85, "high": 65, "moderate": 40, "low": 0}

ROUTE_DB = {
    "critical": [
        {"route": "outer_ring_road",    "eta": 18, "distance": 7},
        {"route": "service_roads",      "eta": 22, "distance": 5},
    ],
    "high": [
        {"route": "parallel_road",      "eta": 20, "distance": 6},
        {"route": "secondary_route",    "eta": 25, "distance": 8},
    ],
    "moderate": [
        {"route": "nearby_alternative", "eta": 15, "distance": 5},
    ],
    "low": [
        {"route": "main_route",         "eta": 12, "distance": 5},
    ],
}

PRIORITY_LABELS = {
    "critical": "Immediate",
    "high":     "Urgent",
    "moderate": "Moderate",
    "low":      "Normal",
}

def classify_severity(score: float) -> str:
    for level, threshold in THRESHOLDS.items():
        if score >= threshold:
            return level
    return "low"

def get_signal_strategy(severity: str) -> dict:
    return {
        "critical": {"signal_mode": "max_green_corridor",  "description": "Extend green along congested corridor", "cycle_adjustment": "+40%"},
        "high":     {"signal_mode": "adaptive_control",    "description": "Dynamically adjust by live flow",       "cycle_adjustment": "+25%"},
        "moderate": {"signal_mode": "balanced_control",    "description": "Maintain balanced timing",              "cycle_adjustment": "+10%"},
        "low":      {"signal_mode": "normal_operation",    "description": "No changes required",                   "cycle_adjustment": "0%"},
    }.get(severity, {"signal_mode": "normal_operation", "description": "Normal", "cycle_adjustment": "0%"})

def get_rerouting(severity: str, incident_count: int) -> dict:
    return {
        "critical": {"reroute": True,  "strategy": "divert_major_flows", "routes": ["outer_ring_road","service_roads"],  "priority": "emergency"},
        "high":     {"reroute": True,  "strategy": "load_balancing",     "routes": ["parallel_road","secondary_route"],  "priority": "high"},
        "moderate": {"reroute": True,  "strategy": "minor_adjustments",  "routes": ["nearby_alternative"],              "priority": "medium"},
        "low":      {"reroute": False, "strategy": "no_change",          "routes": [],                                   "priority": "low"},
    }.get(severity, {"reroute": False, "strategy": "no_change", "routes": [], "priority": "low"})

def run(pred: dict) -> dict:
    if "error" in pred:
        return pred
    try:
        score         = float(pred.get("congestion_score", 50))
        incident_count= int(pred.get("incident_count", 0))
        roadwork      = bool(pred.get("roadwork_active", pred.get("road_work_active", False)))

        severity      = classify_severity(score)
        signal        = get_signal_strategy(severity)
        rerouting     = get_rerouting(severity, incident_count)

        # Build route list with traffic field
        routes = [dict(r, traffic=severity) for r in ROUTE_DB.get(severity, ROUTE_DB["low"])]
        best_route = routes[0] if routes else {"route": "main_route", "eta": 15, "distance": 5}

        emergency = {
            "emergency_mode": True,
            "action": "clear_priority_routes",
            "description": "Emergency traffic clearance active",
        } if (incident_count >= 3 or roadwork) else {"emergency_mode": False}

        distribution = {
            "distribution": "decentralize",
            "description": "Spread traffic across corridors",
        } if score > 70 else {
            "distribution": "normal",
            "description": "Maintain current distribution",
        }

        return {
            "severity":       severity,
            "priority":       PRIORITY_LABELS.get(severity, "Normal"),
            "signal_control": signal,
            "rerouting":      rerouting,
            "routes":         routes,
            "best_route":     best_route,
            "emergency":      emergency,
            "distribution":   distribution,
        }
    except Exception as e:
        return {"error": str(e)}
