class Settings:
    TELEGRAM_TOKEN = "APII_TOKEN_HERE"
    TELEGRAM_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
    OPENAI_API_KEY = "API_KEY"
    OPENAI_MODEL = "gpt-4o-mini"
    NOVITA_API_KEY = "API_KEY"
    NOVITA_API_URL = "https://api.novita.ai/v3beta/flux-1-schnell"
    GROQ_API_KEY = "API_KEY"

settings = Settings()
