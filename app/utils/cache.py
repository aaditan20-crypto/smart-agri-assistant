import json
import os
import hashlib
from datetime import datetime, timedelta

CACHE_FILE = "weather_cache.json"
CACHE_VALID_HOURS = 6

def _make_cache_key(location: str, season: str) -> str:
    raw_key = f"{location.strip().lower()}_{season.strip().lower()}"
    return hashlib.md5(raw_key.encode()).hexdigest()

def get_cached_weather(location: str, season: str):
    if not os.path.exists(CACHE_FILE):
        return None
    with open(CACHE_FILE, "r") as f:
        try:
            cache = json.load(f)
        except json.JSONDecodeError:
            return None

    key = _make_cache_key(location, season)
    if key not in cache:
        return None

    entry = cache[key]
    cached_time = datetime.fromisoformat(entry["cached_at"])
    if datetime.now() - cached_time > timedelta(hours=CACHE_VALID_HOURS):
        return None

    return entry["data"]

def set_cached_weather(location: str, season: str, data: dict):
    cache = {}
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            try:
                cache = json.load(f)
            except json.JSONDecodeError:
                cache = {}

    key = _make_cache_key(location, season)
    cache[key] = {
        "cached_at": datetime.now().isoformat(),
        "data": data
    }

    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)