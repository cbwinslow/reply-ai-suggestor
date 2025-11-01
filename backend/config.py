import os
from typing import List, Optional
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application Configuration
    app_name: str = Field(default="reply-ai-suggester", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    app_env: str = Field(default="development", env="APP_ENV")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_workers: int = Field(default=1, env="API_WORKERS")
    
    # Database Configuration
    database_url: Optional[str] = Field(default=None, env="DATABASE_URL")
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    
    # AI Provider Configuration
    gemini_api_key: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    openrouter_api_key: Optional[str] = Field(default=None, env="OPENROUTER_API_KEY")
    qwen_api_key: Optional[str] = Field(default=None, env="QWEN_API_KEY")
    
    # Security Configuration
    secret_key: str = Field(default="dev-secret-key", env="SECRET_KEY")
    jwt_secret_key: str = Field(default="dev-jwt-secret", env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(default=30, env="JWT_EXPIRE_MINUTES")
    
    # Monitoring & Observability
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    metrics_enabled: bool = Field(default=True, env="METRICS_ENABLED")
    health_check_enabled: bool = Field(default=True, env="HEALTH_CHECK_ENABLED")
    
    # Cache Configuration
    cache_ttl: int = Field(default=300, env="CACHE_TTL")
    max_cache_size: int = Field(default=1000, env="MAX_CACHE_SIZE")
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")
    
    # Personalization
    personalization_enabled: bool = Field(default=True, env="PERSONALIZATION_ENABLED")
    encryption_key: Optional[str] = Field(default=None, env="ENCRYPTION_KEY")
    
    # CORS Configuration
    cors_origins: List[str] = Field(
        default=["http://localhost:8000", "http://127.0.0.1:8000", "http://localhost:8080"], 
        env="CORS_ORIGINS"
    )
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: List[str] = Field(default=["*"], env="CORS_ALLOW_METHODS")
    cors_allow_headers: List[str] = Field(default=["*"], env="CORS_ALLOW_HEADERS")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    def get_api_url(self) -> str:
        """Get the full API URL."""
        return f"http://{self.api_host}:{self.api_port}"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.app_env.lower() == "development"

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env.lower() == "production"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()