from functools import lru_cache
from typing import TYPE_CHECKING, Literal

from fastapi import Query
from fastapi.responses import StreamingResponse
from qdrant_client import QdrantClient
from nl.models import NLResolveRequest
from nl.nl_query_processor import NLQueryResolver
from rag.embedder import OllamaEmbedder
from rag.qdrant_indexer import QdrantIndexer
from rag.search.retrieval import Retrieval


class NLService:

    def __init__(
        self,
        llm_provider: str,
        temperature: float = 0.5,
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

        self.llm = NLQueryResolver(
            retriever=self.retriever, temperature=temperature, llm_provider=llm_provider
        )

    async def resolve_user_query(self, data_obj: "NLRequest"):
        req = NLResolveRequest(**data_obj.model_dump())
        return await self.llm.resolve_nl(req)

    async def format_price_with_category(self, data_obj: "PriceFormat"):
        stream = self.llm.format_price_query(
            amount=data_obj.amount,
            category=data_obj.category,
            currency=data_obj.currency,
        )
        chunks = []
        async for token in stream:
            chunks.append(token)
        return "".join(chunks)

    async def format_price_with_category_stream(self, data_obj: "PriceFormat"):
        async def sse_wrap():
            stream = self.llm.format_price_query(
                amount=data_obj.amount,
                category=data_obj.category,
                currency=data_obj.currency,
            )
            async for token in stream:
                yield f"data: {token}\n\n"

        return StreamingResponse(
            sse_wrap(),
            media_type="text/event-stream",
        )


LLM_PROVIDER = Literal["groq", "ollama"]


@lru_cache(maxsize=1)
def get_nl_service(llm_provider: LLM_PROVIDER = Query()):
    return NLService(llm_provider=llm_provider)


if TYPE_CHECKING:
    from api.models import NLRequest, PriceFormat
