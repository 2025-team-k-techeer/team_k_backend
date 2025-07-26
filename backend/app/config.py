from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # mongoDB settings
    MONGO_URI: str
    MONGO_ROOT_USERNAME: str
    MONGO_ROOT_PASSWORD: str
    # Monogo Express settings
    MONGO_HOST: str
    MONGO_PORT: int
    MONGO_ADMIN_USERNAME: str
    MONGO_ADMIN_PASSWORD: str
    MONGO_EXPRESS_USER: str
    MONGO_EXPRESS_PASS: str

    # rabbitMQ settings
    RABBITMQ_USER: str
    RABBITMQ_PASS: str
    RABBITMQ_HOST: str
    RABBITMQ_QUEUE: str

    # Redis settings
    REDIS_HOST: str
    REDIS_PORT: int

    # Qdrant settings
    QDRANT_HOST: str
    QDRANT_PORT: int
    QDRANT_SEARCH_URL: str

    # Replicate API key
    REPLICATE_API_KEY: str

    # Google Cloud Storage settings
    GCS_BUCKET: str
    GOOGLE_APPLICATION_CREDENTIALS: str

    # Celery settings
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None  # 로그 파일 경로 (예: "/logs/app.log")

    # database_password: str
    # jwt_secret: str
    # email_password: str


@lru_cache
def get_settings():
    return Settings()
