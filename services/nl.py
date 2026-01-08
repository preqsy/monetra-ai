from qdrant_client import QdrantClient
from api.models import NLRequest, PriceFormat
from nl.models import NLResolveRequest
from nl.nl_query_processor import NLQueryResolver
from rag.embedder import OllamaEmbedder
from rag.qdrant_indexer import QdrantIndexer
from rag.search.retrieval import Retrieval


class NLService:
    def __init__(
        self,
    ) -> None:
        self.qdrant_client = QdrantClient(url="localhost:6333")
        self.embedder = OllamaEmbedder()
        self.indexer = QdrantIndexer(
            qdrant_client=self.qdrant_client,
            embedder=self.embedder,
        )
        self.retriever = Retrieval(
            indexer=self.indexer,
            embedder=self.embedder,
            qdrant_client=self.qdrant_client,
        )

        self.llm = NLQueryResolver(retriever=self.retriever)

    async def resolve_user_query(self, data_obj: NLRequest):
        req = NLResolveRequest(**data_obj.model_dump())
        rsp = self.llm.resolve_nl(req)

        return rsp

    async def format_price_with_category(self, data_obj: PriceFormat):
        return self.llm.format_price_query(
            amount=data_obj.amount,
            category=data_obj.category,
            currency=data_obj.currency,
        )


def get_nl_service():
    return NLService()
