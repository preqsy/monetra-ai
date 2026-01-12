from rag.embedder_providers.base import EmbedderABC
from config import settings


def get_embedding_model() -> EmbedderABC:

    if settings.EMBEDDING_MODEL_PROVIDER == "ollama":
        # Good for offline testing esp when you have local LLMs & Ollama installed
        print(f"Using model: {settings.EMBEDDING_MODEL_PROVIDER}")
        from rag.embedder_providers.ollama_model import OllamaEmbedder

        return OllamaEmbedder()

    elif settings.EMBEDDING_MODEL_PROVIDER == "google":
        # Good for production a bit
        print(f"Using model: {settings.EMBEDDING_MODEL_PROVIDER}")
        from rag.embedder_providers.google_model import GoogleEmbedder

        return GoogleEmbedder()

    else:
        raise
