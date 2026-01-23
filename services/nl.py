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
import logfire


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

    async def resolve_user_query(
        self, user_id: int, query: str, parsed: dict, top_k: int = 25
    ):
        logfire.debug(f"Resolving user query: {query}")
        print(f"Parsed dict: {parsed}")
        req = NLResolveRequest(
            user_id=user_id,
            query=query,
            parsed=parsed,
            top_k=top_k,
        )
        try:
            resolved = await self.llm.resolve_category_nl(req)
            logfire.info(f"Successfully resolved: {req.model_dump()} ")
        except Exception as e:
            logfire.error(f"Failed to resolve user query: {str(e)}")
            raise
        return resolved

    async def format_price_with_category_stream(self, data_obj: "NLFormatRequest"):
        logfire.debug(f"Started streaming price formatting: {data_obj.model_dump()}")

        async def sse_wrap():
            stream = self.llm.format_resolve_response(
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

    async def interpret_user_query(
        self,
        query: str,
        query_plan: dict,
    ):
        logfire.debug(f"Interpreting user query: {query}")
        interpretation = await self.llm.interpret_user_query(
            query=query,
            query_plan=query_plan,
        )
        logfire.info(f"Successfully interpreted query.")
        return interpretation

    async def explain_request(
        self,
        query: str = "",
        query_plan: str = "",
        result_summary: str = "",
        message_list: str = "",
    ):
        logfire.debug(f"Explaining request.")

        async def sse_wrap():
            stream = self.llm.explaination_request(
                query=query,
                query_plan=query_plan,
                message_list=message_list,
                result_summary=result_summary,
            )
            async for token in stream:
                yield f"data: {token}\n\n"

        logfire.info(f"Successfully generated explanation.")
        return StreamingResponse(
            sse_wrap(),
            media_type="text/event-stream",
        )


LLM_PROVIDER = Literal["groq", "ollama"]


@lru_cache(maxsize=1)
def get_nl_service(
    llm_provider: LLM_PROVIDER = Query(
        default="groq" if settings.ENVIRONMENT == "dev" else "groq"
    ),
) -> NLService:
    try:
        service = NLService(llm_provider=llm_provider)
        logfire.info(f"NLService initialized with provider: {llm_provider}")
    except Exception as e:
        logfire.error(
            f"Failed to initialize NLService with provider {llm_provider}: {e}"
        )
        raise
    return service


if TYPE_CHECKING:
    from api.models import NLRequestBase, NLFormatRequest
