from functools import lru_cache
from typing import List, Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "Agentic X Content Platform"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = True

    SECRET_KEY: str = "change-me-in-production-please-use-a-strong-random-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/agentic_x"
    DATABASE_SYNC_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/agentic_x"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 5

    REDIS_URL: str = "redis://localhost:6379/0"

    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    CELERY_WORKER_CONCURRENCY: int = 1

    DEFAULT_LLM_PROVIDER: Literal["openai", "anthropic", "mock"] = "mock"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-sonnet-4-6"

    DEFAULT_IMAGE_PROVIDER: Literal["openai", "stability", "mock"] = "mock"
    DEFAULT_AUDIO_PROVIDER: Literal["openai", "elevenlabs", "mock"] = "mock"
    DEFAULT_VIDEO_PROVIDER: Literal["runway", "luma", "mock"] = "mock"
    DEFAULT_SEARCH_PROVIDER: Literal["tavily", "serper", "mock"] = "mock"

    X_CLIENT_ID: Optional[str] = None
    X_CLIENT_SECRET: Optional[str] = None
    X_REDIRECT_URI: str = "http://localhost:8000/api/v1/x/callback"
    X_API_BASE_URL: str = "https://api.twitter.com/2"
    X_OAUTH_BASE_URL: str = "https://twitter.com/i/oauth2/authorize"
    X_TOKEN_URL: str = "https://api.twitter.com/2/oauth2/token"
    X_SCOPES: List[str] = [
        "tweet.read",
        "tweet.write",
        "users.read",
        "offline.access",
        "media.write",
    ]

    STORAGE_PROVIDER: Literal["local", "s3"] = "local"
    LOCAL_STORAGE_PATH: str = "./storage"
    S3_BUCKET: Optional[str] = None
    S3_REGION: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_ENDPOINT_URL: Optional[str] = None

    MAX_CONCURRENT_GENERATIONS: int = 2
    MAX_UPLOAD_SIZE_MB: int = 100
    MAX_VIDEO_DURATION_SECONDS: int = 140
    MAX_IMAGES_PER_POST: int = 4
    MAX_VIDEO_SIZE_MB: int = 512
    MAX_GIF_SIZE_MB: int = 15
    ALLOWED_IMAGE_MIME_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp", "image/gif"]
    ALLOWED_VIDEO_MIME_TYPES: List[str] = ["video/mp4", "video/quicktime"]
    ALLOWED_AUDIO_MIME_TYPES: List[str] = ["audio/mpeg", "audio/wav", "audio/mp4"]

    ENABLE_PGVECTOR: bool = False
    EMBEDDING_DIMENSIONS: int = 1536

    ENABLE_REAL_X_API: bool = False
    ENABLE_REAL_MEDIA_GENERATION: bool = False
    ENABLE_REAL_WEB_SEARCH: bool = False
    MOCK_MODE: bool = True

    RAG_CHUNK_SIZE: int = 700
    RAG_CHUNK_OVERLAP: int = 100
    RAG_TOP_K: int = 6

    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    LOG_FORMAT: Literal["json", "text"] = "text"

    @property
    def is_mock(self) -> bool:
        return self.MOCK_MODE or self.DEFAULT_LLM_PROVIDER == "mock"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
