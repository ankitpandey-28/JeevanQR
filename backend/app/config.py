"""
QR Emergency Alert System - Configuration

Environment variables:
  PORT            - Server port (default: 3000)
  ALLOWED_ORIGIN  - CORS origin restriction (optional)
  SITE_URL        - Full site URL for QR generation (optional)
  VERCEL_URL      - Vercel deployment URL (auto-set by Vercel)
  VERCEL          - Set by Vercel when running in serverless
  NODE_ENV        - Environment mode (development/production)
  HOME            - Home directory (absent in some serverless envs)
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables and .env file."""

    PORT: int = 3000
    ALLOWED_ORIGIN: str | None = None
    SITE_URL: str | None = None
    VERCEL_URL: str | None = None
    VERCEL: str | None = None
    NODE_ENV: str = "development"
    HOME: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def ENVIRONMENT(self) -> str:
        """Current environment name."""
        return self.NODE_ENV or "development"

    @property
    def is_serverless(self) -> bool:
        """Detect serverless environment (Vercel or production without HOME)."""
        return (
            self.VERCEL is not None
            or (self.NODE_ENV == "production" and self.HOME is None)
        )

    @property
    def BASE_DIR(self) -> Path:
        """Project root directory (parent of backend/)."""
        return Path(__file__).resolve().parent.parent.parent

    @property
    def FRONTEND_DIR(self) -> Path:
        """Frontend static files directory."""
        return self.BASE_DIR / "frontend"

    @property
    def DATABASE_DIR(self) -> Path:
        """JSON database files directory."""
        return self.BASE_DIR / "database"

    @property
    def UPLOADS_DIR(self) -> Path:
        """Uploaded files directory."""
        return self.BASE_DIR / "uploads"


settings = Settings()
