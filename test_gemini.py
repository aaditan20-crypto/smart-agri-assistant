from app.config import settings

print("Key loaded:", settings.GEMINI_API_KEY)

from app.utils.llm_client import ask_gemini

response = ask_gemini(
    system_prompt="You are a helpful farming assistant.",
    user_message="In one sentence, why is soil testing important for farmers?"
)
print(response)