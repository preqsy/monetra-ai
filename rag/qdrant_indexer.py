import uuid
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    VectorParams,
    Distance,
    PointStruct,
    PayloadSchemaType,
)

from rag.embedder import OllamaEmbedder
from rag.schemas.transaction import TransactionDoc
from config import settings


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

        if settings.QDRANT_COLLECTION_NAME in collections:
            self.ensure_user_id_index()
            return
        self.qdrant_client.create_collection(
            settings.QDRANT_COLLECTION_NAME,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
            ),
        )
        self.ensure_user_id_index()

    def ensure_user_id_index(self) -> None:
        collection_info = self.qdrant_client.get_collection(
            settings.QDRANT_COLLECTION_NAME
        )
        payload_schema = collection_info.payload_schema or {}
        if (
            TransactionDoc.USER_ID in payload_schema
            and TransactionDoc.DOC_TYPE in payload_schema
        ):
            return
        self.qdrant_client.create_payload_index(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            field_name=TransactionDoc.USER_ID,
            field_schema=PayloadSchemaType.INTEGER,
        )
        self.qdrant_client.create_payload_index(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            field_name=TransactionDoc.DOC_TYPE,
            field_schema=PayloadSchemaType.KEYWORD,
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
            collection_name=settings.QDRANT_COLLECTION_NAME,
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
