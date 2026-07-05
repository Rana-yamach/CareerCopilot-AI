"""Pydantic-settings tabanlı merkezi konfigürasyon.

Tüm ortam değişkenleri burada okunur. `.env.example` (kök dizin) ile senkron
tutulmalıdır (bkz. PROJECT_SPEC.md §9.2).
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"

    # Database
    database_url: str = "postgresql+asyncpg://careercopilot:careercopilot@localhost:5432/careercopilot"
    database_url_sync: str = "postgresql://careercopilot:careercopilot@localhost:5432/careercopilot"

    # Redis / Celery
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    jwt_secret_key: str = "dev-secret-key-change-me"
    jwt_refresh_secret_key: str = "dev-refresh-secret-key-change-me"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 7

    # HuggingFace
    hf_api_token: str = ""
    hf_model_id: str = "mistralai/Mistral-7B-Instruct-v0.2"
    # HF Inference Providers router'ı, bir modelin hangi 3. parti sağlayıcı
    # (ör. featherless-ai, together, novita...) tarafından barındırıldığını
    # bilmek için model kimliğine `:provider` eki gerektirir. Bu eşleme HF
    # tarafından dinamik yönetildiğinden koda sabitlenmez, env ile değişir.
    hf_inference_provider: str = "featherless-ai"
    embedding_model_id: str = "sentence-transformers/all-MiniLM-L6-v2"

    # GitHub
    github_api_token: str = ""

    # Uploads
    max_upload_size_mb: int = 5
    upload_dir: str = "./uploads"

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
