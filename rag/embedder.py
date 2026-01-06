from llama_index.embeddings.ollama import OllamaEmbedding


class Embedder:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.embed_model = OllamaEmbedding(
            model_name=self.model_name,
            base_url="http://localhost:11434",
        )

    def get_embedding(self, text: str):
        return self.embed_model.get_text_embedding(text)


embedder = Embedder(model_name="nomic-embed-text")
embeddings = embedder.get_embedding("Sample text for embedding.")
