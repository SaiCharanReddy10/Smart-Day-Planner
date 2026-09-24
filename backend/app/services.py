import os
import httpx

async def search_places(query):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": query, "format": "jsonv2", "limit": 5}
    headers = {"User-Agent": "smart-day-planner-student-app/1.0"}
    async with httpx.AsyncClient(timeout=10, headers=headers) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        return r.json()


async def weather_for(lat, lon, date):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "forecast_days": 1,
        "timezone": "auto",
        "start_date": date,
        "end_date": date,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        data = r.json().get("daily", {})
        return {
            "temperature_max": data.get("temperature_2m_max", [None])[0],
            "temperature_min": data.get("temperature_2m_min", [None])[0],
            "rain_probability": data.get("precipitation_probability_max", [None])[0],
            "weather_code": data.get("weather_code", [None])[0],
        }

async def make_summary(title, date, places, total_cost, total_minutes, weather):
    url = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434")
    model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    names = ", ".join(p["name"] for p in places) or "no places"
    rain = ", ".join(str(w.get("rain_probability")) for w in weather if w.get("rain_probability") is not None)
    prompt = (
        f"Write a short practical day-trip summary for {title} on {date}. "
        f"Stops: {names}. Total cost: {total_cost}. Total planned time: {total_minutes} minutes. "
        f"Rain probabilities: {rain or 'unknown'}. Keep it to 3 sentences and do not invent facts."
    )
    try:
        async with httpx.AsyncClient(timeout=25) as client:
            r = await client.post(f"{url}/api/generate", json={"model": model, "prompt": prompt, "stream": False})
            r.raise_for_status()
            return r.json().get("response", "").strip() or fallback_summary(places, total_cost, total_minutes)
    except Exception:
        return fallback_summary(places, total_cost, total_minutes)


def fallback_summary(places, total_cost, total_minutes):
    names = ", ".join(p["name"] for p in places)
    if not names:
        return "No stops fit within the selected time and budget."
    return f"Your plan covers {names}. The estimated spend is ₹{total_cost} and planned time is {total_minutes} minutes. Check the weather before leaving and adjust stops if needed."
