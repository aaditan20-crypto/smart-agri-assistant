import json
import os
from datetime import datetime

LOG_FILE = "token_usage_log.jsonl"

def log_token_usage(agent_name: str, prompt_tokens: int, response_tokens: int, total_tokens: int, cached: bool = False):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "agent": agent_name,
        "prompt_tokens": prompt_tokens,
        "response_tokens": response_tokens,
        "total_tokens": total_tokens,
        "was_cached": cached
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"[TOKEN LOG] {agent_name}: {total_tokens} tokens (cached={cached})")

def get_total_tokens_used() -> dict:
    if not os.path.exists(LOG_FILE):
        return {"total_tokens": 0, "total_calls": 0, "by_agent": {}, "cached_calls_saved": 0}

    total_tokens = 0
    total_calls = 0
    cached_calls_saved = 0
    by_agent = {}

    with open(LOG_FILE, "r") as f:
        for line in f:
            entry = json.loads(line)
            total_calls += 1
            if entry["was_cached"]:
                cached_calls_saved += 1
            else:
                total_tokens += entry["total_tokens"]

            agent = entry["agent"]
            if agent not in by_agent:
                by_agent[agent] = {"calls": 0, "tokens": 0}
            by_agent[agent]["calls"] += 1
            if not entry["was_cached"]:
                by_agent[agent]["tokens"] += entry["total_tokens"]

    return {
        "total_tokens": total_tokens,
        "total_calls": total_calls,
        "by_agent": by_agent,
        "cached_calls_saved": cached_calls_saved
    }