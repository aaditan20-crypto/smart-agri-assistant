import time
import google.generativeai as genai
from app.config import settings
from app.utils.token_tracker import log_token_usage

genai.configure(api_key=settings.GEMINI_API_KEY)

def ask_gemini(system_prompt: str, user_message: str, model: str = None, max_retries: int = 3, agent_name: str = "unknown_agent") -> str:
    model_name = model or settings.REASONING_MODEL
    gemini_model = genai.GenerativeModel(model_name=model_name, system_instruction=system_prompt)

    for attempt in range(max_retries):
        try:
            response = gemini_model.generate_content(user_message)
            usage = response.usage_metadata
            log_token_usage(
                agent_name=agent_name,
                prompt_tokens=usage.prompt_token_count,
                response_tokens=usage.candidates_token_count,
                total_tokens=usage.total_token_count,
                cached=False
            )
            return response.text
        except Exception as e:
            error_str = str(e)
            if "RESOURCE_EXHAUSTED" in error_str or "429" in error_str:
                wait_time = 20 * (attempt + 1)
                print(f"Rate limit hit. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
            else:
                raise

    raise Exception("Gemini rate limit exceeded after multiple retries. Please wait a minute and try again.")


def ask_gemini_with_image(system_prompt: str, image_bytes: bytes, mime_type: str = "image/jpeg", model: str = None, max_retries: int = 3, agent_name: str = "unknown_agent") -> str:
    model_name = model or settings.REASONING_MODEL
    gemini_model = genai.GenerativeModel(model_name=model_name, system_instruction=system_prompt)
    image_part = {"mime_type": mime_type, "data": image_bytes}

    for attempt in range(max_retries):
        try:
            response = gemini_model.generate_content([image_part, "Analyze this image."])
            usage = response.usage_metadata
            log_token_usage(
                agent_name=agent_name,
                prompt_tokens=usage.prompt_token_count,
                response_tokens=usage.candidates_token_count,
                total_tokens=usage.total_token_count,
                cached=False
            )
            return response.text
        except Exception as e:
            error_str = str(e)
            if "RESOURCE_EXHAUSTED" in error_str or "429" in error_str:
                wait_time = 20 * (attempt + 1)
                print(f"Rate limit hit. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
            else:
                raise

    raise Exception("Gemini rate limit exceeded after multiple retries. Please wait a minute and try again.")