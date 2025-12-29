"""Application configuration via Pydantic Settings."""

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    database_url: str = "postgresql+asyncpg://washflow:washflow@localhost:5433/washflow"

    # JWT
    jwt_secret: str = "change-me-in-production"
    jwt_access_ttl_min: int = 30
    jwt_refresh_ttl_days: int = 7
    jwt_algorithm: str = "HS256"

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # App
    debug: bool = False
    log_level: str = "INFO"
    frontend_url: str = "http://localhost:5173"

    # Feature flags
    feature_notifications: bool = True
    feature_whatsapp: bool = False  # Disabled until real provider configured
    feature_sms: bool = True

    @field_validator("database_url", mode="before")
    @classmethod
    def convert_database_url(cls, v: str) -> str:
        """Convert standard postgres:// URL to asyncpg format."""
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        if v.startswith("postgresql://") and "+asyncpg" not in v:
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience alias for direct import
settings = get_settings()
