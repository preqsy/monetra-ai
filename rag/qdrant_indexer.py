import uuid
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct

from rag.embedder import OllamaEmbedder
from rag.schemas.transaction import TransactionDoc


class QdrantIndexer:
    def __init__(
        self,
        qdrant_client: QdrantClient,
        embedder: OllamaEmbedder,
    ) -> None:
        self.qdrant_client = qdrant_client
        self.embedder = embedder
        self.DOC_ID_NAMESPACE = uuid.UUID("4b1f7a2e-3c2b-4b2f-9c8a-8d8f5b2f9d10")

    def ensure_collection(self, vector_size: int = 768):
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
            points=[
                PointStruct(
                    id=self.qdrant_point_id(doc.doc_id),
                    vector=embedded_doc,
                    payload=payload,
                )
            ],
        )
        print(f"Added doc: {doc.doc_id} to Qdrant, text: {doc.text}")

    def qdrant_point_id(self, doc_id: str) -> str:
        return str(uuid.uuid5(self.DOC_ID_NAMESPACE, doc_id))
