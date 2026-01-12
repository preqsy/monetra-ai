from rag.embedder_providers.base import EmbedderABC, EmbeddingReturn
from llama_index.embeddings.ollama import OllamaEmbedding


class OllamaEmbedder(EmbedderABC):
    def __init__(self) -> None:
        self.embedder = OllamaEmbedding(model_name="nomic-embed-text")

    def embed(self, text: str):
        embedded_doc = self.embedder.get_text_embedding(text)

        return EmbeddingReturn(
            embeddings=embedded_doc,
            length=len(embedded_doc),
            embedding_model="ollama",
        )
