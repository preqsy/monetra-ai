from datetime import date
from qdrant_client import QdrantClient

from rag.embedder import OllamaEmbedder
from rag.models import TransactionDoc
from rag.qdrant_indexer import QdrantIndexer


qdrant_client = QdrantClient(url="localhost:6333")
embedder = OllamaEmbedder()
indexer = QdrantIndexer(qdrant_client=qdrant_client, embedder=embedder)


doc = TransactionDoc(
    doc_id=1,
    doc_type="transaction",
    text="Hello world",
    user_id=10,
    transaction_id=10,
    account_id=4,
    category_id=90,
    currency="USD",
    amount=1000,
    date_utc=date.today(),
)
indexer.index_document(doc)
