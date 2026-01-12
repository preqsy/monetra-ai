from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from rag.embedder_providers.base import EmbedderABC, EmbeddingReturn


class LlamaHFEmbedder(EmbedderABC):

    def __init__(self, model_name: str = "BAAI/bge-base-en-v1.5"):
        self.embed_model = HuggingFaceEmbedding(model_name=model_name)

    def embed(self, text: str):
        embeddings = self.embed_model.get_text_embedding(text)
        return EmbeddingReturn(embeddings=embeddings, length=len(embeddings))
