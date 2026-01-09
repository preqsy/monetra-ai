import random
from qdrant_client import QdrantClient
from consumer import KafkaConsumer
from rag.embedder import OllamaEmbedder
from rag.schemas.transaction import TransactionDoc
from rag.qdrant_indexer import QdrantIndexer
from config import settings


def index_transaction(transaction_data):

    qdrant_client = QdrantClient(
        url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY
    )
    embedder = OllamaEmbedder()
    indexer = QdrantIndexer(qdrant_client=qdrant_client, embedder=embedder)
    # retriever = QdrantRetriever(qdrant_client=qdrant_client, embedder=embedder)

    # random_doc_id = random.randint(1, 1000)
    # random_user_id = random.randint(1, 1000)
    doc = TransactionDoc(**transaction_data)
    indexer.index_document(doc)
    # retriever.retrieve_documents(query=doc)


if __name__ == "__main__":
    topic = "transaction.created.dev"
    consumer = KafkaConsumer(topic)
    consumer.consume_message(index_transaction)
