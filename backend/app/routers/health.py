from fastapi import APIRouter
from app.config import get_settings
from app.services.llm.factory import get_llm_provider

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    settings = get_settings()
    provider = get_llm_provider()
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "llm_provider": provider.__class__.__name__,
        "configured_provider": settings.LLM_PROVIDER,
        "database_url_target": "PostgreSQL" if "postgres" in settings.DATABASE_URL else "SQLite"
    }
