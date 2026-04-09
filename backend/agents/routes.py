# ---------------------------------------
# ROUTING ENGINE (CITY-LEVEL CONTROL)
# ---------------------------------------

# ---------------------------------------
# THRESHOLDS (TUNABLE)
# ---------------------------------------
CONGESTION_THRESHOLDS = {
    "critical": 85,
    "high": 65,
    "moderate": 40,
    "low": 0,
}


# ---------------------------------------
# CLASSIFY SEVERITY
# ---------------------------------------
def classify_severity(score: float) -> str:
    for level, threshold in CONGESTION_THRESHOLDS.items():
        if score >= threshold:
            return level
    return "low"


# ---------------------------------------
# SIGNAL CONTROL STRATEGY
# ---------------------------------------
def get_signal_strategy(severity: str, trend: str):
    if severity == "critical":
        return {
            "signal_mode": "max_green_corridor",
            "description": "Extend green lights along congested corridor",
            "cycle_adjustment": "+40%"
        }

    elif severity == "high":
        return {
            "signal_mode": "adaptive_control",
            "description": "Dynamically adjust signals based on flow",
            "cycle_adjustment": "+25%"
        }

    elif severity == "moderate":
        return {
            "signal_mode": "balanced_control",
            "description": "Maintain balanced signal timing",
            "cycle_adjustment": "+10%"
        }

    else:
        return {
            "signal_mode": "normal_operation",
            "description": "No changes required",
            "cycle_adjustment": "0%"
        }


# ---------------------------------------
# REROUTING STRATEGY
# ---------------------------------------
def get_rerouting_strategy(severity: str, incident_count: int):
    if severity == "critical":
        return {
            "reroute": True,
            "strategy": "divert_major_flows",
            "routes": ["outer_ring_road", "service_roads"],
            "priority": "emergency"
        }

    elif severity == "high":
        return {
            "reroute": True,
            "strategy": "load_balancing",
            "routes": ["parallel_roads", "secondary_routes"],
            "priority": "high"
        }

    elif severity == "moderate":
        return {
            "reroute": True,
            "strategy": "minor_adjustments",
            "routes": ["nearby_alternatives"],
            "priority": "medium"
        }

    else:
        return {
            "reroute": False,
            "strategy": "no_change",
            "routes": [],
            "priority": "low"
        }


# ---------------------------------------
# NEW: GENERATE ROUTE OPTIONS
# ---------------------------------------
def generate_route_options(reroute_plan, severity):
    """
    Convert abstract routes into frontend-usable route objects
    """
    base_routes = reroute_plan.get("routes", [])

    route_options = []

    for i, r in enumerate(base_routes):
        route_options.append({
            "route": r,
            "traffic": severity,
            "eta": 20 + (i * 5),  # simulated ETA
            "distance": 5 + (i * 2)
        })

    # fallback if no routes
    if not route_options:
        route_options.append({
            "route": "main_route",
            "traffic": severity,
            "eta": 15,
            "distance": 5
        })

    return route_options


# ---------------------------------------
# NEW: CHOOSE BEST ROUTE
# ---------------------------------------
def choose_best_route(route_options):
    """
    Select best route based on ETA
    """
    return sorted(route_options, key=lambda x: x["eta"])[0]


# ---------------------------------------
# EMERGENCY HANDLING
# ---------------------------------------
def emergency_override(pred):
    if pred["incident_count"] >= 3 or pred["roadwork_active"]:
        return {
            "emergency_mode": True,
            "action": "clear_priority_routes",
            "description": "Activate emergency traffic clearance"
        }

    return {
        "emergency_mode": False
    }


# ---------------------------------------
# TRAFFIC DISTRIBUTION STRATEGY
# ---------------------------------------
def traffic_distribution(pred):
    if pred["congestion_score"] > 70:
        return {
            "distribution": "decentralize",
            "description": "Spread traffic across multiple corridors"
        }
    else:
        return {
            "distribution": "normal",
            "description": "Maintain current distribution"
        }


# ---------------------------------------
# MAIN ROUTING FUNCTION (UPGRADED)
# ---------------------------------------
def run(pred: dict) -> dict:

    if "error" in pred:
        return pred

    # Step 1: classify severity
    severity = classify_severity(pred["congestion_score"])

    # Step 2: signal strategy
    signal_plan = get_signal_strategy(severity, pred["trend"])

    # Step 3: rerouting strategy
    reroute_plan = get_rerouting_strategy(severity, pred["incident_count"])

    # Step 4: NEW route generation
    route_options = generate_route_options(reroute_plan, severity)

    # Step 5: NEW best route selection
    best_route = choose_best_route(route_options)

    # Step 6: emergency override
    emergency_plan = emergency_override(pred)

    # Step 7: traffic distribution
    distribution_plan = traffic_distribution(pred)

    # Step 8: priority level
    priority = {
        "critical": "🚨 immediate",
        "high": "⚠️ urgent",
        "moderate": "🔄 moderate",
        "low": "✅ normal"
    }.get(severity, "normal")

    # Step 9: FINAL OUTPUT (UPGRADED)
    return {
        "severity": severity,
        "priority": priority,

        "signal_control": signal_plan,

        # 🔥 upgraded routing
        "rerouting": reroute_plan,
        "routes": route_options,
        "best_route": best_route,

        "emergency": emergency_plan,
        "distribution": distribution_plan
    }