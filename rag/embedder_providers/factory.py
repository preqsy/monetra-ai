from rag.embedder_providers.base import EmbedderABC
from rag.embedder_providers.google_model import GoogleEmbedder
from rag.embedder_providers.ollama_model import OllamaEmbedder


MODEL = "ollama"


def get_embedding_model() -> EmbedderABC:
    if MODEL == "ollama":
        return OllamaEmbedder()

    elif MODEL == "google":
        return GoogleEmbedder()

    else:
        return OllamaEmbedder()
