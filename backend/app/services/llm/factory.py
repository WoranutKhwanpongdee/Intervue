import logging
from app.config import get_settings
from app.services.llm.base import BaseLLMProvider
from app.services.llm.gemini import GeminiProvider
from app.services.llm.groq import GroqProvider
from app.services.llm.ollama import OllamaProvider
from app.services.llm.mock import MockProvider

logger = logging.getLogger("intervue.llm.factory")


def get_llm_provider() -> BaseLLMProvider:
    settings = get_settings()
    pref = (settings.LLM_PROVIDER or "auto").lower()

    if pref == "gemini" and settings.GEMINI_API_KEY:
        logger.info(f"Using Gemini LLM Provider ({settings.GEMINI_MODEL})")
        return GeminiProvider(api_key=settings.GEMINI_API_KEY, model=settings.GEMINI_MODEL)

    if pref == "groq" and settings.GROQ_API_KEY:
        logger.info(f"Using Groq LLM Provider ({settings.GROQ_MODEL})")
        return GroqProvider(api_key=settings.GROQ_API_KEY, model=settings.GROQ_MODEL)

    if pref == "ollama":
        logger.info(f"Using Ollama LLM Provider ({settings.OLLAMA_MODEL}) at {settings.OLLAMA_BASE_URL}")
        return OllamaProvider(base_url=settings.OLLAMA_BASE_URL, model=settings.OLLAMA_MODEL)

    # Auto detection mode
    if pref == "auto":
        if settings.GEMINI_API_KEY:
            logger.info(f"Auto-selected Gemini LLM Provider ({settings.GEMINI_MODEL})")
            return GeminiProvider(api_key=settings.GEMINI_API_KEY, model=settings.GEMINI_MODEL)
        if settings.GROQ_API_KEY:
            logger.info(f"Auto-selected Groq LLM Provider ({settings.GROQ_MODEL})")
            return GroqProvider(api_key=settings.GROQ_API_KEY, model=settings.GROQ_MODEL)

    # Fallback to Mock Provider
    logger.info("Using Realistic Mock LLM Provider (No API keys required)")
    return MockProvider()
