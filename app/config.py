import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    REASONING_MODEL = "gemini-flash-lite-latest"
    FAST_MODEL = "gemini-flash-lite-latest"

settings = Settings()