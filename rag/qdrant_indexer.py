from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct

from rag.embedder import OllamaEmbedder
from rag.models import TransactionDoc


class QdrantIndexer:
    def __init__(
        self,
        qdrant_client: QdrantClient,
        embedder: OllamaEmbedder,
    ) -> None:
        self.qdrant_client = qdrant_client
        self.embedder = embedder

    def ensure_collection(self, vector_size: int):
        collections = {c.name for c in self.qdrant_client.get_collections().collections}

        if "monetra_collection" in collections:
            return
        self.qdrant_client.create_collection(
            "monetra_collection",
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
            ),
        )

    def index_document(self, transaction: TransactionDoc):
        doc = transaction

        embedded_doc = self.embedder.embed(doc.text)
        self.ensure_collection(vector_size=len(embedded_doc))
        payload = doc.model_dump(
            # exclude={"text"},
            mode="json",
        )

        self.qdrant_client.upsert(
            collection_name="monetra_collection",
            points=[PointStruct(id=doc.doc_id, vector=embedded_doc, payload=payload)],
        )
        print(f"Added doc: {doc.doc_id} to Qdrant, text: {doc.text}")
