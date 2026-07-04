"""
Application configuration.

Values here are DEFAULTS ONLY. In production, API keys are never read from
environment variables on the server for the OpenRouter/Serper calls that
belong to a specific user session — the frontend sends them per-request
(see routers/research.py) so each user can bring their own keys, exactly
like the sidebar configuration screen in the product spec.

Environment variables are still supported as optional server-side fallbacks
(useful for local dev / demo deployments) and for things that ARE global
server secrets, like the Discord bot token if you choose to run one bot
for all users instead of per-user tokens.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Optional server-side fallbacks (used only if the client doesn't send its own key)
    OPENROUTER_API_KEY: str | None = os.getenv("OPENROUTER_API_KEY")
    SERPER_API_KEY: str | None = os.getenv("SERPER_API_KEY")

    # CORS
    ALLOWED_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
        if origin.strip()
    ]

    # Crawling
    MAX_PAGES_TO_CRAWL: int = int(os.getenv("MAX_PAGES_TO_CRAWL", "8"))
    CRAWL_TIMEOUT_SECONDS: int = int(os.getenv("CRAWL_TIMEOUT_SECONDS", "10"))
    MAX_CONTENT_CHARS_PER_PAGE: int = int(os.getenv("MAX_CONTENT_CHARS_PER_PAGE", "6000"))

    # Cache
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "3600"))

    # Default AI model (user can override from the UI)
    DEFAULT_AI_MODEL: str = os.getenv("DEFAULT_AI_MODEL", "anthropic/claude-sonnet-4.5")


settings = Settings()
