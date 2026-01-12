from functools import lru_cache
import logging
from typing import TYPE_CHECKING, Literal

from fastapi import Query
from fastapi.responses import StreamingResponse
from qdrant_client import QdrantClient
from nl.models import NLResolveRequest
from nl.nl_query_processor import NLQueryResolver
from rag.embedder import Embedder
from rag.qdrant_indexer import QdrantIndexer
from rag.search.retrieval import Retrieval
from config import settings

logger = logging.getLogger(__name__)


class NLService:

    def __init__(
        self,
        llm_provider: str,
        temperature: float = 0.5,
    ) -> None:
        self.qdrant_client = QdrantClient(
            url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY
        )
        self.embedder = Embedder()
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
        logger.debug(f"Resolving user query: {data_obj.query}")
        req = NLResolveRequest(**data_obj.model_dump())
        try:
            resolved = await self.llm.resolve_nl(req)
            logger.info(f"Successfully resolved: {req.model_dump()} ")
        except Exception as e:
            logger.error(f"Failed to resolve user query: {str(e)}")
            raise
        return resolved

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
        logger.debug(f"Started streaming price formatting: {data_obj.model_dump()}")

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
def get_nl_service(llm_provider: LLM_PROVIDER = Query(default="ollama")):
    try:
        service = NLService(llm_provider=llm_provider)
        logger.info(f"NLService initialized with provider: {llm_provider}")
    except Exception as e:
        logger.error(
            f"Failed to initialize NLService with provider {llm_provider}: {e}"
        )
        raise
    return service


if TYPE_CHECKING:
    from api.models import NLRequest, PriceFormat
