from rag.embedder_providers.base import EmbedderABC
from config import settings


def get_embedding_model() -> EmbedderABC:

    if settings.EMBEDDING_MODEL == "ollama":
        print(f"Using model: {settings.EMBEDDING_MODEL}")
        from rag.embedder_providers.ollama_model import OllamaEmbedder

        return OllamaEmbedder()

    elif settings.EMBEDDING_MODEL == "google":
        print(f"Using model: {settings.EMBEDDING_MODEL}")
        from rag.embedder_providers.google_model import GoogleEmbedder

        return GoogleEmbedder()

    else:
        from rag.embedder_providers.ollama_model import OllamaEmbedder

        return OllamaEmbedder()
