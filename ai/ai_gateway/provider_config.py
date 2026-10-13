import os

from dotenv import load_dotenv


# ---------------------------------------------------------
# Load project-root .env
# ---------------------------------------------------------

load_dotenv()


class AIProviderConfig:

    # -----------------------------------------------------
    # Gateway
    # -----------------------------------------------------

    enabled = (
        os.getenv(
            "SENTINELAI_AI_ENABLED",
            "true",
        ).lower()
        == "true"
    )

    primary_provider = os.getenv(
        "SENTINELAI_AI_PRIMARY_PROVIDER",
        "gemini",
    )

    fallback_providers = [
        item.strip()
        for item in os.getenv(
            "SENTINELAI_AI_FALLBACK_PROVIDERS",
            "gemini,groq",
        ).split(",")
        if item.strip()
    ]

    # -----------------------------------------------------
    # Gemini
    # -----------------------------------------------------

    gemini_api_key = os.getenv(
        "GEMINI_API_KEY"
    )

    gemini_api_key_2 = os.getenv(
        "GEMINI_API_KEY_2"
    )

    gemini_model = os.getenv(
        "SENTINELAI_GEMINI_MODEL",
        "gemini-2.5-flash-lite",
    )

    gemini_fallback_model = os.getenv(
        "SENTINELAI_GEMINI_FALLBACK_MODEL",
        "gemini-2.5-flash",
    )

    # -----------------------------------------------------
    # Groq
    # -----------------------------------------------------

    groq_api_key = os.getenv(
        "GROQ_API_KEY"
    )

    groq_model = os.getenv(
        "SENTINELAI_GROQ_MODEL",
        "openai/gpt-oss-120b",
    )

    # -----------------------------------------------------
    # Runtime
    # -----------------------------------------------------

    timeout_seconds = int(
        os.getenv(
            "SENTINELAI_AI_TIMEOUT_SECONDS",
            "60",
        )
    )

    max_retries = int(
        os.getenv(
            "SENTINELAI_AI_MAX_RETRIES",
            "1",
        )
    )
