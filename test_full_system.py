from backend.agents.scenario_agent import run as scenario
from backend.agents.traffic_prediction import run as predict
from backend.agents.propagation import run as propagation
from backend.agents.routes import run as routing
from backend.agents.mobility import run as mobility
import json


# -----------------------------
# TEST INPUT
# -----------------------------
input_text = "Traffic in Electronic City at 5pm"


# -----------------------------
# STEP 1: SCENARIO (Branch 2)
# -----------------------------
scenario_data = scenario(input_text)

print("\n=== SCENARIO ===")
print(json.dumps(scenario_data, indent=2))


# -----------------------------
# STEP 2: PREDICTION (Branch 1)
# -----------------------------
prediction = predict(scenario_data)

print("\n=== PREDICTION ===")
print(json.dumps(prediction, indent=2))


# -----------------------------
# STEP 3: PROPAGATION (Branch 2)
# -----------------------------
spread = propagation(scenario_data)

print("\n=== PROPAGATION ===")
print(json.dumps(spread, indent=2))


# -----------------------------
# STEP 4: ROUTING (Branch 3)
# -----------------------------
route = routing(prediction)

print("\n=== ROUTING ===")
print(json.dumps(route, indent=2))


# -----------------------------
# STEP 5: MOBILITY (Branch 3)
# -----------------------------
move = mobility(prediction)

print("\n=== MOBILITY ===")
print(json.dumps(move, indent=2))