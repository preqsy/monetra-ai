from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    LLM_MODEL_NAME: str = "Qwen2.5:7b"
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: str = ""
    QDRANT_URL: str = ""
    QDRANT_COLLECTION_NAME: str = "monetra_collection"
    EMBEDDING_MODEL: str = "nomic-embed-text"
    BACKEND_HEADER: str = ""
    GROQ_API_KEY: str = ""

    KAFKA_PEM: str = ""
    KAFKA_SERVICE_CERT: str = ""
    KAFKA_SERVICE_KEY: str = ""
    KAFKA_URL: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
