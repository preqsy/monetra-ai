import uuid
import logfire
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    VectorParams,
    Distance,
    PointStruct,
    PayloadSchemaType,
)

from rag.embedder import Embedder
from rag.schemas.transaction import TransactionDoc
from config import settings


class QdrantIndexer:
    def __init__(
        self,
        qdrant_client: QdrantClient,
        embedder: Embedder,
    ) -> None:
        self.qdrant_client = qdrant_client
        self.embedder = embedder
        self.DOC_ID_NAMESPACE = uuid.UUID("4b1f7a2e-3c2b-4b2f-9c8a-8d8f5b2f9d10")

    def ensure_collection(self, vector_size: int = 768):
        with logfire.span(
            "ensure_collection",
            collection_name=settings.QDRANT_COLLECTION_NAME,
            vector_size=vector_size,
        ):
            collections = {
                c.name for c in self.qdrant_client.get_collections().collections
            }

            if settings.QDRANT_COLLECTION_NAME in collections:
                self.ensure_user_id_index()
                return

            logfire.info(
                "Creating new collection",
                collection_name=settings.QDRANT_COLLECTION_NAME,
                vector_size=vector_size,
                distance="COSINE",
            )
            self.qdrant_client.create_collection(
                settings.QDRANT_COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE,
                ),
            )
            self.ensure_user_id_index()

    def ensure_user_id_index(self) -> None:
        with logfire.span(
            "ensure_user_id_index", collection_name=settings.QDRANT_COLLECTION_NAME
        ):
            logfire.info(
                "Checking payload schema",
                collection_name=settings.QDRANT_COLLECTION_NAME,
            )
            collection_info = self.qdrant_client.get_collection(
                settings.QDRANT_COLLECTION_NAME
            )
            payload_schema = collection_info.payload_schema or {}
            if (
                TransactionDoc.USER_ID in payload_schema
                and TransactionDoc.DOC_TYPE in payload_schema
            ):
                logfire.info(
                    "Payload indexes already exist",
                    user_id_field=TransactionDoc.USER_ID,
                    doc_type_field=TransactionDoc.DOC_TYPE,
                )
                return

            logfire.info(
                "Creating payload indexes",
                user_id_field=TransactionDoc.USER_ID,
                doc_type_field=TransactionDoc.DOC_TYPE,
            )
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
            logfire.info("Payload indexes created successfully")

    def index_document(self, transaction: TransactionDoc):
        with logfire.span(
            "index_document", doc_id=transaction.doc_id, user_id=transaction.user_id
        ):
            doc = transaction

            logfire.info(
                "Embedding document", doc_id=doc.doc_id, text_length=len(doc.text)
            )
            embedded_doc = self.embedder.embed(doc.text)
            logfire.info(
                "Document embedded successfully",
                doc_id=doc.doc_id,
                embedding_model=embedded_doc.embedding_model,
                vector_length=embedded_doc.length,
            )

            doc.embedding_model = embedded_doc.embedding_model
            self.ensure_collection(vector_size=embedded_doc.length)

            payload = doc.model_dump(
                # exclude={"text"},
                mode="json",
            )

            point_id = self.qdrant_point_id(doc.doc_id)
            logfire.info(
                "Upserting document to Qdrant",
                doc_id=doc.doc_id,
                point_id=point_id,
                collection_name=settings.QDRANT_COLLECTION_NAME,
            )
            self.qdrant_client.upsert(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                points=[
                    PointStruct(
                        id=point_id,
                        vector=embedded_doc.embeddings,
                        payload=payload,
                    )
                ],
            )
            logfire.info(
                "Document successfully upserted to Qdrant",
                doc_id=doc.doc_id,
                text=doc.text,
            )

    def qdrant_point_id(self, doc_id: str) -> str:
        return str(uuid.uuid5(self.DOC_ID_NAMESPACE, doc_id))
