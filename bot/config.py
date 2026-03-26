"""Configuration loading from environment variables."""

import os
from dotenv import load_dotenv


def load_config() -> dict:
    """Load configuration from .env.bot.secret.
    
    Returns:
        Dictionary with configuration values.
    """
    # Load from .env.bot.secret in the same directory
    env_path = os.path.join(os.path.dirname(__file__), ".env.bot.secret")
    load_dotenv(env_path)
    
    return {
        "bot_token": os.getenv("BOT_TOKEN", ""),
        "lms_api_base_url": os.getenv("LMS_API_BASE_URL", ""),
        "lms_api_key": os.getenv("LMS_API_KEY", ""),
        "llm_api_key": os.getenv("LLM_API_KEY", ""),
        "llm_api_base_url": os.getenv("LLM_API_BASE_URL", ""),
        "llm_api_model": os.getenv("LLM_API_MODEL", "coder-model"),
    }
