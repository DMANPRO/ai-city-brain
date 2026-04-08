from backend.orchestrator import run

if __name__ == "__main__":
    user_input = "Rain at 6 PM in Whitefield"
    result = run(user_input)
    print(result)