import logging

from qdrant_client import QdrantClient
from config.topics.transaction import TRANSACTION_CREATED
from consumer import KafkaConsumer
from rag.embedder import Embedder
from rag.schemas.transaction import TransactionDoc
from rag.qdrant_indexer import QdrantIndexer
from config import settings


def index_transaction(transaction_data):

    qdrant_client = QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY if settings.ENVIRONMENT == "prod" else None,
    )
    embedder = Embedder()

    indexer = QdrantIndexer(qdrant_client=qdrant_client, embedder=embedder)
    doc = TransactionDoc(**transaction_data)
    indexer.index_document(doc)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    logger = logging.getLogger("run_service")
    logger.info("worker starting")
    topic = TRANSACTION_CREATED
    try:
        consumer = KafkaConsumer(topic)
        consumer.consume_message(index_transaction)
    except Exception as exc:
        logger.exception("Kafka consumer failed to start")
        raise
