from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Server
    APP_NAME: str = "AI Test Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database (默认使用 SQLite，可改为 PostgreSQL)
    DATABASE_URL: str = "sqlite:///./ai_test_platform.db"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: str = ""

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # LLM Configuration
    LLM_PROVIDER: str = "openai"  # openai, gemini, local, custom
    LLM_API_KEY: str = ""
    LLM_API_BASE: str = "https://api.openai.com/v1"
    LLM_MODEL: str = "gpt-4-turbo-preview"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 4000

    # OpenAI specific (兼容配置)
    OPENAI_API_KEY: str = ""
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_TEMPERATURE: float = 0.7  # 向后兼容
    OPENAI_MAX_TOKENS: int = 4000  # 向后兼容

    # Google Gemini specific
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-pro"

    # Local/Custom LLM specific
    LOCAL_LLM_API_BASE: str = "http://localhost:8080/v1"
    LOCAL_LLM_MODEL: str = "local-model"

    # JWT
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: str = "http://localhost:8000,http://localhost:3000"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    @property
    def cors_origins_list(self) -> List[str]:
        """Convert comma-separated CORS_ORIGINS to list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

