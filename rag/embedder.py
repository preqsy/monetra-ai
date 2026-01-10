from rag.embedder_providers.base import EmbeddingReturn
from rag.embedder_providers.factory import get_embedding_model


class OllamaEmbedder:

    def __init__(
        self,
    ):
        self.embed_model = get_embedding_model()

    def embed(self, text: str) -> EmbeddingReturn:
        rsp = self.embed_model.embed(text)
        return rsp
