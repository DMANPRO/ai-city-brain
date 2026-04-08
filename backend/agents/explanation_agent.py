# backend/agents/explanation_agent.py
# Person 4 — Explanation Agent
# Text explanation via OpenAI GPT + Voice output via OpenAI TTS (fallback: gTTS)

import os
import io
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# ── Main Entry Point (called by orchestrator) ─────────────────────────────────

def run(input_data: dict) -> dict:
    input_data["explanation"] = _generate_explanation(input_data)
    return input_data


# ── Voice Generation (called by app.py separately) ───────────────────────────

def generate_audio(text: str) -> bytes | None:
    """
    Returns MP3 audio bytes of the explanation.
    Primary:  OpenAI TTS  (high quality, uses OPENAI_API_KEY)
    Fallback: gTTS        (free, Indian English accent, no key needed)
    Returns None if both fail.
    """
    if OPENAI_API_KEY:
        audio = _openai_tts(text)
        if audio:
            return audio
    return _gtts_tts(text)


def _openai_tts(text: str) -> bytes | None:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",       # clear female voice — good for city assistant
            input=text,
            speed=0.95          # slightly slower — easier to understand
        )
        return response.content
    except Exception as e:
        print(f"[ExplanationAgent] OpenAI TTS failed: {e}")
        return None


def _gtts_tts(text: str) -> bytes | None:
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang="en", tld="co.in")   # Indian English accent
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf.read()
    except Exception as e:
        print(f"[ExplanationAgent] gTTS failed: {e}")
        return None


# ── Text Explanation ──────────────────────────────────────────────────────────

def _generate_explanation(data: dict) -> str:
    if OPENAI_API_KEY:
        result = _openai_explanation(data)
        if result:
            return result
    return _template_explanation(data)


def _openai_explanation(data: dict) -> str | None:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)

        suggestions_text = ", ".join(data.get("suggestions", [])) or "None"

        prompt = f"""You are an AI traffic assistant for Bengaluru city.
Given real-time traffic data below, write a clear, helpful, human-friendly summary in exactly 2-3 sentences.
Mention location, weather impact, congestion level, and what the commuter should do.
Keep it conversational and specific — not generic.

Location       : {data.get('location', 'Bengaluru')}
Time           : {data.get('time', 'N/A')}
Weather        : {data.get('weather', 'clear')}
Congestion     : {data.get('congestion', 'unknown')}
Avg Speed      : {data.get('avg_speed', 'N/A')} km/h
Traffic Volume : {data.get('traffic_volume', 'N/A')}
Trend          : {data.get('trend', 'stable')}
Spread Level   : {data.get('spread_level', 'unknown')}
Recommended    : {data.get('recommended_mode', 'car')}
Advisory       : {data.get('travel_advisory', 'N/A')}
Delay          : {data.get('estimated_delay', 'N/A')}
Suggestions    : {suggestions_text}"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=160,
            temperature=0.75
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"[ExplanationAgent] OpenAI GPT failed: {e}")
        return None


def _template_explanation(data: dict) -> str:
    location   = data.get("location", "the area")
    weather    = data.get("weather", "current conditions")
    congestion = data.get("congestion", "unknown")
    speed      = data.get("avg_speed", "N/A")
    mode       = data.get("recommended_mode", "car")
    delay      = data.get("estimated_delay", "N/A")
    trend      = data.get("trend", "stable")
    advisory   = data.get("travel_advisory", "")
    spread     = data.get("spread_level", "")

    return (
        f"In {location}, {weather} conditions are causing {congestion} congestion "
        f"with an average speed of {speed} km/h. "
        f"Traffic is {trend} and spreading at a {spread} level — estimated delay is {delay}. "
        f"{advisory}. Best travel option: {mode}."
    )