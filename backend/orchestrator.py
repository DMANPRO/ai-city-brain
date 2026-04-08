from backend.agents import (
    scenario_agent,       # Person 2's file
    traffic_prediction,   # Person 1's file
    congestion_detection, # Person 3's file
    propagation,          # Person 2's file
    routing,              # Person 3's file
    mobility,             # Person 3's file
    explanation_agent     # YOUR file
)

def run(user_input):
    scenario   = scenario_agent.run(user_input)
    traffic    = traffic_prediction.run(scenario)
    decision   = congestion_detection.run(traffic)
    prop       = propagation.run(decision)
    route      = routing.run(prop)
    mob        = mobility.run(route)
    final      = explanation_agent.run(mob)
    return final