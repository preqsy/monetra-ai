from pprint import pprint
from qdrant_client import QdrantClient

from rag.embedder import OllamaEmbedder


class QdrantRetriever:
    def __init__(
        self,
        qdrant_client: QdrantClient,
        embedder: OllamaEmbedder,
    ) -> None:
        self.qdrant_client = qdrant_client
        self.embedder = embedder

    def retrieve_documents(self, query: str):

        query = query.strip()
        if not query:
            return []
        print(f"Query to search: {query}")
        embedded_query = self.embedder.embed(query)

        results = self.qdrant_client.query_points(
            "monetra_collection",
            query=embedded_query,
            limit=2,
            with_payload=True,
            with_vectors=False,
        )
        pprint(f"Big Results: {results}")
        return [
            {
                "doc_id": r.id,
                "text": r.payload.get("text") if r.payload else None,
            }
            for r in results.points
        ]
