import json
from app.utils.llm_client import ask_gemini
from app.utils.mock_weather import get_mock_weather
from app.utils.cache import get_cached_weather, set_cached_weather
from app.utils.token_tracker import log_token_usage

SYSTEM_PROMPT = """You are a Weather Intelligence Agent in an agricultural AI system.
You receive a 7-day weather forecast (temperature, humidity, rainfall, wind speed)
for a farmer's location, along with their farm profile.

Analyze the forecast and provide practical, farmer-friendly recommendations.

Respond ONLY with valid JSON in this exact format, no other text:
{
  "best_sowing_window": "e.g. Day 2-3, once rainfall settles",
  "irrigation_recommendation": "short practical advice based on rainfall pattern",
  "harvest_alert": "any warning if harvest-time weather looks risky, or 'None' if not applicable",
  "extreme_weather_alert": "warn about heavy rain, heatwave, or high wind if forecast shows it, or 'None'",
  "summary": "one short paragraph summarizing the week's weather outlook for the farmer"
}
"""

class WeatherIntelligenceAgent:
    def analyze(self, location: str, farm_profile: dict, season: str = "Kharif") -> dict:
        # 1. Try cache first - this is the key optimization your mentor wants
        cached_result = get_cached_weather(location, season)
        if cached_result is not None:
            log_token_usage(
                agent_name="weather",
                prompt_tokens=0,
                response_tokens=0,
                total_tokens=0,
                cached=True
            )
            print(f"[CACHE HIT] Weather for {location} ({season}) served from cache. No tokens used.")
            return cached_result

        # 2. Not cached - fetch fresh data and call Gemini
        weather_data = get_mock_weather(location, season)

        user_message = f"""
Location: {location}
Season: {season}
7-Day Forecast: {json.dumps(weather_data['forecast_7_day'])}
Farm Profile: {json.dumps(farm_profile)}
"""
        raw_response = ask_gemini(SYSTEM_PROMPT, user_message, agent_name="weather")
        cleaned = raw_response.strip().replace("```json", "").replace("```", "").strip()

        try:
            weather_insights = json.loads(cleaned)
        except json.JSONDecodeError:
            weather_insights = {
                "best_sowing_window": "Unknown",
                "irrigation_recommendation": "Unknown",
                "harvest_alert": "Unknown",
                "extreme_weather_alert": "Unknown",
                "summary": raw_response
            }

        weather_insights["raw_forecast"] = weather_data["forecast_7_day"]

        # 3. Save to cache for next time
        set_cached_weather(location, season, weather_insights)

        return weather_insights

weather_agent = WeatherIntelligenceAgent()