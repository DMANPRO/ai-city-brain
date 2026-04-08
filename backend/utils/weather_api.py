import requests
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}"
        response = requests.get(url)
        data = response.json()

        weather = data["weather"][0]["main"].lower()
        return weather

    except:
        return "clear"