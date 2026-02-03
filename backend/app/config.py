"""
Application Configuration - MVP Phase 1
Simplified for Railway + Supabase + Cloudflare R2 deployment
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """Application settings optimized for MVP deployment"""
    
    # ===== Application =====
    APP_NAME: str = "TeachGenie API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, production
    
    # ===== Security (REQUIRED) =====
    SECRET_KEY: str = "temporary-secret-key-at-least-32-chars-long-123"  # REQUIRED: Generate with secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # ===== Database (Supabase PostgreSQL) =====
    DATABASE_URL: str = "postgresql+asyncpg://postgres.vpwukmvfqbrxrtcihfpy:Q2taZnxFpn8Vc6rH@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres" # REQUIRED: Supabase connection string
    # Note: Railway/Supabase auto-manage connection pooling in free tier
    
    # ===== Redis (Railway built-in) =====
    REDIS_URL: str = "redis://localhost:6379/0"  # REQUIRED: Auto-provided by Railway
    CACHE_TTL: int = 3600  # 1 hour cache
    
    # ===== OpenAI (REQUIRED) =====
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"  # Cost-optimized model
    OPENAI_MAX_TOKENS: int = 2000
    OPENAI_TEMPERATURE: float = 0.3
    
    # ===== Storage (Cloudflare R2 - 10GB free) =====
    # Leave empty strings if not using storage yet (optional for MVP)
    S3_ENDPOINT_URL: str = ""  # Format: https://[account-id].r2.cloudflarestorage.com
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    S3_BUCKET_NAME: str = "teachgenie-lessons"
    
    # ===== Email (Resend - 3k emails free) =====
    # Leave empty if not using email yet (optional for MVP)
    EMAIL_API_KEY: str = "re_En6xUdyE_7QaXeHcgnwUayP2zoeb6uWrB"
    EMAIL_FROM: str = "noreply@teachgenie.ai"
    
    # ===== Rate Limiting (Anti-abuse) =====
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # ===== CORS (Add your frontend URL) =====
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",           # Local development
        "https://teachgenie.ai",           # Production (root domain)
        "https://www.teachgenie.ai",       # Production (www subdomain)
        "https://teachgenie.vercel.app",   # Vercel deployment
        "https://*.vercel.app"             # Vercel preview deployments
    ]
    
    # ===== Monitoring (Optional for MVP) =====
    SENTRY_DSN: Optional[str] = None  # Add later if needed
    
    # ===== Usage Quotas =====
    FREE_TIER_LESSONS_PER_MONTH: int = 5
    BASIC_TIER_LESSONS_PER_MONTH: int = 50
    PRO_TIER_LESSONS_PER_MONTH: int = 999999
    
    # ===== Google OAuth =====
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"
    
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent / ".env"),  # backend/.env
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
