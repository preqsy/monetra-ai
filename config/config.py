from typing import Literal
from pydantic_settings import BaseSettings


class KafkaConfig(BaseSettings):
    KAFKA_PEM: str = ""
    KAFKA_SERVICE_CERT: str = ""
    KAFKA_SERVICE_KEY: str = ""
    KAFKA_URL: str = ""
    KAFKA_GROUP_ID: str = "monetra-ai"

    class Config:
        env_file = ".env"
        extra = "ignore"


class Settings(BaseSettings):
    ENVIRONMENT: str = "prod"
    LLM_MODEL_NAME: str = (
        "llama3.2:3b" if ENVIRONMENT == "dev" else "llama-3.1-8b-instant"
    )
    # LLM_MODEL_NAME: str = (
    #     "llama-3.1-8b-instant" if ENVIRONMENT == "dev" else "llama-3.1-8b-instant"
    # )

    QDRANT_API_KEY: str = ""
    QDRANT_URL: str = "localhost:6333"
    QDRANT_COLLECTION_NAME: str = "monetra_collection"

    BACKEND_HEADER: str = ""
    GROQ_API_KEY: str = ""
    GOOGLE_EM_API_KEY: str = ""
    EMBEDDING_MODEL_PROVIDER: Literal["google", "ollama"] = "ollama"
    KAFKA_CONFIG: KafkaConfig = KafkaConfig()

    class Config:
        env_file = ".env"

        extra = "ignore"


settings = Settings()
