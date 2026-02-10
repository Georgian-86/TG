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
    SECRET_KEY: str = ""  # REQUIRED: Set via environment variable
    
    @property
    def check_secret_key(self):
        if not self.SECRET_KEY or len(self.SECRET_KEY) < 32:
            raise ValueError("FATAL: SECRET_KEY must be at least 32 characters!")
        if self.ENVIRONMENT == "production" and "temporary" in self.SECRET_KEY.lower():
            raise ValueError("FATAL: You must set a strong SECRET_KEY in production!")
            
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # ===== Database (Supabase PostgreSQL) =====
    DATABASE_URL: str = ""  # REQUIRED: Set via environment variable
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
    EMAIL_API_KEY: str = ""  # REQUIRED: Set via environment variable
    EMAIL_FROM: str = ""  # REQUIRED: Set via environment variable (e.g., info@teachgenie.ai)
    
    # ===== Rate Limiting (Anti-abuse) =====
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # ===== CORS (Add your frontend URL) =====
    FRONTEND_URL: str = ""  # AWS Amplify or custom domain
    
    @property
    def cors_origins(self) -> list[str]:
        """Dynamic CORS origins from environment + defaults"""
        origins = [
            "http://localhost:3000",           # Local development
            "http://127.0.0.1:3000",
        ]
        
        # Add Amplify/production URLs from environment
        if self.FRONTEND_URL:
            origins.append(self.FRONTEND_URL)
        
        # Add hardcoded domains
        origins.extend([
            "https://teachgenie.ai",
            "https://www.teachgenie.ai",
            "https://teachgenie.vercel.app",
        ])
        
        return origins
    
    # ===== Monitoring (Optional for MVP) =====
    SENTRY_DSN: Optional[str] = None  # Add later if needed
    
    # ===== Usage Quotas =====
    FREE_TIER_LESSONS_PER_MONTH: int = 100
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
