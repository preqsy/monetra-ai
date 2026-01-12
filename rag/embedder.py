from rag.embedder_providers.base import EmbeddingReturn
from rag.embedder_providers.factory import get_embedding_model


class Embedder:

    def __init__(
        self,
    ):
        self.embed_model = get_embedding_model()

    def embed(self, text: str) -> EmbeddingReturn:
        try:
            rsp = self.embed_model.embed(text)
        except Exception as e:
            print(f"Error embedding doc: {str(e)}")
            raise
        return rsp
