from functools import lru_cache
import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "ClinIQ"
    ENVIRONMENT: str = "development"

    API_V1_STR: str = "/api/v1"

    SECRET_KEY: str = "your-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    DATABASE_URL:str= os.getenv("DATABASE_URL")

    REDIS_URL: str = os.getenv("REDIS_URL")

    QDRANT_URL: str = os.getenv("QDRANT_URL")
    QDRANT_COLLECTION: str = os.getenv("QDRANT_COLLECTION")

    ENABLE_VECTOR_SEARCH: bool = True
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL")

    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    ENABLE_EXTERNAL_LLM: bool = False

    FILE_ENCRYPTION_KEY: str = ""
    UPLOAD_DIR: str = "./data/encrypted_uploads"
    MAX_UPLOAD_MB: int = 15

    CORS_ORIGINS: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

    @property
    def cors_origin_list(self):
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()