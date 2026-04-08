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

from datetime import datetime


def get_weather_forecast(city: str, target_dt: datetime) -> str:
    """
    Fetches forecast weather for a specific future datetime (up to 5 days).
    Uses OpenWeather 5-day/3-hour forecast API (free tier).
    """
    try:
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}"
        response = requests.get(url, timeout=5)
        data = response.json()

        forecasts = data.get("list", [])
        if not forecasts:
            return get_weather(city)

        target_ts = target_dt.timestamp()
        closest = min(forecasts, key=lambda x: abs(x["dt"] - target_ts))
        return closest["weather"][0]["main"].lower()

    except Exception:
        return get_weather(city)


def get_weather_for_datetime(city: str, target_dt: datetime = None) -> str:
    """
    Smart wrapper:
    - No date given       → current weather (existing API)
    - Within 5 days ahead → forecast API
    - Past / beyond 5 days → current weather fallback
    """
    if target_dt is None:
        return get_weather(city)

    now = datetime.now()
    delta_hours = (target_dt - now).total_seconds() / 3600

    if abs(delta_hours) < 3:
        return get_weather(city)
    elif 0 < delta_hours <= 120:       # up to 5 days in future
        return get_weather_forecast(city, target_dt)
    else:
        return get_weather(city)        # past or too far future
