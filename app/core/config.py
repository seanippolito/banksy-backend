from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv, find_dotenv

# Load the nearest .env (works from repo root, backend dir, or inside Docker)
load_dotenv(find_dotenv())

class Settings(BaseSettings):
    # DB & server
    DATABASE_URL: str = "sqlite+aiosqlite:///./banksy.db"

    # Clerk / JWT
    CLERK_JWKS_URL: str = Field(..., description="Clerk JWKS endpoint")
    JWT_AUDIENCE: str | None = None
    JWT_ISSUER: str | None = None

    # CORS (comma-separated list)
    CORS_ORIGINS: str = "http://localhost:3000"

    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

settings = Settings()
