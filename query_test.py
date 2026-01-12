from pprint import pprint
from qdrant_client import QdrantClient
from nl.nl_query_processor import NLQueryResolver
from nl.models import NLResolveRequest
from rag.embedder import Embedder
from rag.qdrant_indexer import QdrantIndexer
from rag.search.retrieval import Retrieval
import asyncio


async def main():
    qdrant_client = QdrantClient(url="localhost:6333")
    embedder = Embedder()
    indexer = QdrantIndexer(qdrant_client=qdrant_client, embedder=embedder)
    retrieval = Retrieval(
        indexer=indexer, qdrant_client=qdrant_client, embedder=embedder
    )
    llm = NLQueryResolver(retriever=retrieval, llm_provider="ollama")

    req = NLResolveRequest(
        user_id=5,
        query="how much did i spend on investment",
        top_k=25,
    )

    res = await llm.resolve_nl(req=req)

    # amount = llm.format_price_query(amount=1000, category="food", currency="NGN")
    pprint(f"NL Response: {res}")
    # pprint(f"NL Response: {res.model_dump()}")


asyncio.run(main())
