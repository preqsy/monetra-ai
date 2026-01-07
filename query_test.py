from pprint import pprint
from qdrant_client import QdrantClient
from nl.llm_parse import LLMParse
from nl.models import NLResolveRequest
from rag.embedder import OllamaEmbedder
from rag.qdrant_indexer import QdrantIndexer
from rag.qdrant_retrieval import QdrantRetriever
from rag.search.retrieval import Retrieval


def main():
    qdrant_client = QdrantClient(url="localhost:6333")
    embedder = OllamaEmbedder()
    indexer = QdrantIndexer(qdrant_client=qdrant_client, embedder=embedder)
    # retriever = QdrantRetriever(qdrant_client=qdrant_client, embedder=embedder)
    retrieval = Retrieval(
        indexer=indexer, qdrant_client=qdrant_client, embedder=embedder
    )
    llm = LLMParse(retriever=retrieval)

    req = NLResolveRequest(
        user_id=4,
        query="how much did i spend on food",
        top_k=25,
        dominance_threshold=0.40,
        min_winner_hits=4,
    )

    res = llm.resolve_nl(req=req)

    pprint(f"NL Response: {res.model_dump()}")


main()
