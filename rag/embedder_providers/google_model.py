from google import genai
from google.genai import types
from config import settings
from rag.embedder_providers.base import EmbedderABC, EmbeddingReturn


class GoogleEmbedder(EmbedderABC):

    def __init__(self, model_name: str = "BAAI/bge-base-en-v1.5") -> None:
        self.client = genai.client.Client(api_key=settings.GOOGLE_EM_API_KEY)

    def embed(self, text: str):
        [embedding_doc] = (
            self.client.models.embed_content(
                model="gemini-embedding-001",
                contents=text,
                config=types.EmbedContentConfig(output_dimensionality=768),
            ),
        )

        embedding_obj = embedding_doc.embeddings
        if len(embedding_obj) < 1:
            raise ValueError()
        embeddings = embedding_obj[0].values

        return EmbeddingReturn(embeddings=embeddings, length=len(embeddings))
