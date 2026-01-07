from llama_index.embeddings.ollama import OllamaEmbedding


class OllamaEmbedder:
    def __init__(self, model_name: str = "nomic-embed-text"):
        self.model_name = model_name
        self.embed_model = OllamaEmbedding(
            model_name=self.model_name,
            base_url="http://localhost:11434",
        )

    def embed(self, text: str):
        return self.embed_model.get_text_embedding(text)
