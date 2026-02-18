# import logging

import logfire
from qdrant_client import QdrantClient
from config.topics.transaction import TRANSACTION_CREATED
from consumer import KafkaConsumer
from rag.embedder import Embedder
from rag.schemas.transaction import TransactionDoc
from rag.qdrant_indexer import QdrantIndexer
from config import settings
from dotenv import load_dotenv

load_dotenv()


def index_transaction(transaction_data, qdrant_client, embedder, indexer):
    doc = TransactionDoc(**transaction_data)
    indexer.index_document(doc)


if __name__ == "__main__":

    logfire.configure(service_name="monetraai", environment=settings.ENVIRONMENT)

    logfire.info("worker starting")

    # Initialize services once
    qdrant_client = QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY if settings.ENVIRONMENT == "prod" else None,
    )
    embedder = Embedder()
    indexer = QdrantIndexer(qdrant_client=qdrant_client, embedder=embedder)

    topic = TRANSACTION_CREATED
    try:
        consumer = KafkaConsumer(topic)
        # Pass services to handler using lambda
        consumer.consume_message(
            lambda data: index_transaction(data, qdrant_client, embedder, indexer)
        )
    except Exception as exc:
        logfire.exception("Kafka consumer failed to start")
        raise
