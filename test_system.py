from backend.agents.traffic_prediction import run as predict
from backend.agents.routes import run as routing
from backend.agents.mobility import run as mobility


# -------------------------
# INPUT TEST CASE
# -------------------------
input_data = {
    "location": "Whitefield",
    "weather": "rain"
}

# -------------------------
# STEP 1: PREDICTION
# -------------------------
pred = predict(input_data)

print("\n=== TRAFFIC PREDICTION ===")
print(pred)

# -------------------------
# STEP 2: ROUTING
# -------------------------
route = routing(pred)

print("\n=== ROUTING DECISION ===")
print(route)

# -------------------------
# STEP 3: MOBILITY
# -------------------------
move = mobility(pred)

print("\n=== MOBILITY ADVICE ===")
print(move)