import random
import sys
from datetime import date
from qdrant_client import QdrantClient

from rag.embedder import OllamaEmbedder
from rag.schemas.transaction import TransactionDoc
from rag.qdrant_indexer import QdrantIndexer
from rag.qdrant_retrieval import QdrantRetriever


def main():

    if len(sys.argv) > 2:
        return

    query = sys.argv[1]
    qdrant_client = QdrantClient(url="localhost:6333")
    embedder = OllamaEmbedder()
    indexer = QdrantIndexer(qdrant_client=qdrant_client, embedder=embedder)
    retriever = QdrantRetriever(qdrant_client=qdrant_client, embedder=embedder)

    random_doc_id = random.randint(1, 1000)
    random_user_id = random.randint(1, 1000)
    # doc = TransactionDoc(
    #     doc_id=random_doc_id,
    #     doc_type="transaction",
    #     text="Hello world",
    #     user_id=random_user_id,
    #     transaction_id=10,
    #     account_id=4,
    #     category_id=90,
    #     currency="USD",
    #     amount=1000,
    #     date_utc=date.today(),
    #     transaction_type="expense",
    #     category="Food & Dining",
    # )
    # indexer.index_document(doc)
    retriever.retrieve_documents(query=query)


main()
