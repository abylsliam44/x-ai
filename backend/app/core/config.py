from functools import lru_cache
from typing import List, Literal, Optional

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # --- Core ---
    PROJECT_NAME: str = "Agentic X Content Platform"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = True

    SECRET_KEY: str = "change-me-in-production-please-use-a-strong-random-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    # --- Database ---
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/agentic_x"
    DATABASE_SYNC_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/agentic_x"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 5

    REDIS_URL: str = "redis://localhost:6379/0"

    # --- Celery ---
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    CELERY_WORKER_CONCURRENCY: int = 1

    # --- Mode ---
    MOCK_MODE: bool = True

    # --- LLM ---
    DEFAULT_LLM_PROVIDER: Literal["openai", "anthropic", "mock"] = "mock"
    ENABLE_MODEL_ROUTING: bool = True

    # OpenAI credentials
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: Optional[str] = None
    OPENAI_ORG_ID: Optional[str] = None
    OPENAI_PROJECT_ID: Optional[str] = None

    # OpenAI model tiers
    OPENAI_MODEL_STRONG: str = "gpt-5.5"
    OPENAI_MODEL_CHEAP: str = "gpt-5.4-mini"
    OPENAI_MODEL_DEFAULT: str = "gpt-5.4-mini"
    OPENAI_MODEL: str = "gpt-5.4-mini"  # legacy single-model fallback

    # OpenAI specialised models
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_IMAGE_MODEL: str = "gpt-image-2"
    OPENAI_STT_MODEL: str = "gpt-4o-transcribe"
    OPENAI_STT_MODEL_CHEAP: str = "gpt-4o-mini-transcribe"
    OPENAI_TTS_MODEL: str = "gpt-4o-mini-tts"
    OPENAI_TTS_VOICE: str = "coral"
    OPENAI_VIDEO_MODEL: Optional[str] = "sora-2"

    # OpenAI call behaviour
    OPENAI_TIMEOUT_SECONDS: int = 60
    OPENAI_MAX_RETRIES: int = 3
    OPENAI_MAX_OUTPUT_TOKENS: int = 4000
    OPENAI_REASONING_EFFORT: str = "medium"
    OPENAI_ENABLE_WEB_SEARCH: bool = False

    # Anthropic
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-sonnet-4-6"

    # --- Media / Search providers ---
    DEFAULT_IMAGE_PROVIDER: Literal["openai", "stability", "mock"] = "mock"
    DEFAULT_AUDIO_PROVIDER: Literal["openai", "elevenlabs", "mock"] = "mock"
    DEFAULT_VIDEO_PROVIDER: Literal["runway", "luma", "mock"] = "mock"
    DEFAULT_SEARCH_PROVIDER: Literal["tavily", "serper", "mock"] = "mock"

    # --- X / Twitter ---
    ENABLE_REAL_X_API: bool = False
    X_CLIENT_ID: Optional[str] = None
    X_CLIENT_SECRET: Optional[str] = None
    X_REDIRECT_URI: str = "http://localhost:8000/api/v1/x/callback"
    X_API_BASE_URL: str = "https://api.x.com/2"
    X_OAUTH_AUTHORIZE_URL: str = "https://x.com/i/oauth2/authorize"
    X_OAUTH_TOKEN_URL: str = "https://api.x.com/2/oauth2/token"
    X_SCOPES: List[str] = Field(
        default=["tweet.read", "tweet.write", "users.read", "offline.access"]
    )

    # X media upload flags
    X_ENABLE_REAL_MEDIA_UPLOAD: bool = False
    X_ENABLE_REAL_IMAGE_UPLOAD: bool = False
    X_ENABLE_REAL_VIDEO_UPLOAD: bool = False
    X_MAX_IMAGES_PER_POST: int = 4

    # --- Feature flags ---
    ENABLE_PGVECTOR: bool = False
    EMBEDDING_DIMENSIONS: int = 1536
    ENABLE_REAL_EMBEDDINGS: bool = False
    ENABLE_REAL_IMAGE_GENERATION: bool = False
    ENABLE_REAL_STT: bool = False
    ENABLE_REAL_TTS: bool = False
    ENABLE_REAL_VIDEO_GENERATION: bool = False
    ENABLE_REAL_WEB_SEARCH: bool = False
    # Legacy alias kept for backwards compat (maps to any real media flag)
    ENABLE_REAL_MEDIA_GENERATION: bool = False

    # --- Storage ---
    STORAGE_PROVIDER: Literal["local", "s3"] = "local"
    LOCAL_STORAGE_PATH: str = "./storage"
    S3_BUCKET: Optional[str] = None
    S3_REGION: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_ENDPOINT_URL: Optional[str] = None

    # --- Limits ---
    MAX_CONCURRENT_GENERATIONS: int = 2
    MAX_UPLOAD_SIZE_MB: int = 100
    MAX_VIDEO_DURATION_SECONDS: int = 140
    MAX_IMAGES_PER_POST: int = 4
    MAX_VIDEO_SIZE_MB: int = 512
    MAX_GIF_SIZE_MB: int = 15
    ALLOWED_IMAGE_MIME_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp", "image/gif"]
    ALLOWED_VIDEO_MIME_TYPES: List[str] = ["video/mp4", "video/quicktime"]
    ALLOWED_AUDIO_MIME_TYPES: List[str] = ["audio/mpeg", "audio/wav", "audio/mp4"]

    # --- RAG ---
    RAG_CHUNK_SIZE: int = 700
    RAG_CHUNK_OVERLAP: int = 100
    RAG_TOP_K: int = 6

    # --- CORS ---
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # --- Logging ---
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    LOG_FORMAT: Literal["json", "text"] = "text"

    # ------------------------------------------------------------------
    # Derived helpers
    # ------------------------------------------------------------------

    @property
    def is_mock(self) -> bool:
        return self.MOCK_MODE or self.DEFAULT_LLM_PROVIDER == "mock"

    @property
    def real_embeddings_enabled(self) -> bool:
        return (
            not self.MOCK_MODE
            and self.ENABLE_REAL_EMBEDDINGS
            and bool(self.OPENAI_API_KEY)
        )

    @property
    def real_image_generation_enabled(self) -> bool:
        return (
            not self.MOCK_MODE
            and (self.ENABLE_REAL_IMAGE_GENERATION or self.ENABLE_REAL_MEDIA_GENERATION)
            and bool(self.OPENAI_API_KEY)
        )

    @property
    def real_stt_enabled(self) -> bool:
        return not self.MOCK_MODE and self.ENABLE_REAL_STT and bool(self.OPENAI_API_KEY)

    @property
    def real_tts_enabled(self) -> bool:
        return not self.MOCK_MODE and self.ENABLE_REAL_TTS and bool(self.OPENAI_API_KEY)

    # ------------------------------------------------------------------
    # Startup validation
    # ------------------------------------------------------------------

    @model_validator(mode="after")
    def _validate_real_mode(self) -> "Settings":
        if self.MOCK_MODE:
            # Mock mode: no secrets required — always valid.
            return self

        if self.DEFAULT_LLM_PROVIDER == "openai" and not self.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY is required when MOCK_MODE=false and "
                "DEFAULT_LLM_PROVIDER=openai. "
                "Either set OPENAI_API_KEY or switch to MOCK_MODE=true."
            )

        if self.DEFAULT_LLM_PROVIDER == "anthropic" and not self.ANTHROPIC_API_KEY:
            raise ValueError(
                "ANTHROPIC_API_KEY is required when MOCK_MODE=false and "
                "DEFAULT_LLM_PROVIDER=anthropic."
            )

        if self.ENABLE_REAL_X_API:
            missing = [
                name
                for name, val in [
                    ("X_CLIENT_ID", self.X_CLIENT_ID),
                    ("X_CLIENT_SECRET", self.X_CLIENT_SECRET),
                ]
                if not val
            ]
            if missing:
                raise ValueError(
                    f"{', '.join(missing)} are required when ENABLE_REAL_X_API=true. "
                    "Either supply them or set ENABLE_REAL_X_API=false."
                )

        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
