import inspect
import json
from pydantic import ValidationError

import logfire
from nl.llm_providers.factory import get_llm_provider
from nl.models import Interpretation, NLParse, NLResolveRequest, NLResolveResult
from nl.prompt import (
    EXPLANATION_PROMPT,
    PRICE_FORMAT_PROMPT,
    SYSTEM_PROMPT,
    TRANSLATE_USER_INTENTION,
)
from rag.search.retrieval import Retrieval
from config import settings


class NLQueryResolver:
    def __init__(
        self,
        retriever: Retrieval,
        llm_provider: str,
        temperature: float = 0.5,
    ) -> None:
        self.llm = get_llm_provider(temperature=temperature, llm_provider=llm_provider)
        self.retriever = retriever
        self.temperature = temperature

    def extract_json(self, text: str) -> str:
        text = text.strip()
        if text.startswith("```"):
            text = text.split("```", 2)[1]
        return text.strip()

    async def parse_query_llm(self, query: str, prompt: str = SYSTEM_PROMPT) -> NLParse:
        q = query.strip()
        if not q:
            raise ValueError("Empty query")

        with logfire.span(
            "LLM Chat for NL Parsing",
            temperature=self.temperature,
            model_name=settings.LLM_MODEL_NAME,
        ):
            raw = await self.llm.chat(
                query=q,
                prompt=f"{prompt}\n\nUSER QUERY: {json.dumps(q)}",
            )

        logfire.info("llm_raw_response", text=raw.response)

        clean = self.extract_json(raw.response)
        data = json.loads(clean)

        try:
            parsed = NLParse.model_validate(data)
        except ValidationError as e:
            raise ValueError(f"NLParse validation failed: {e}") from e

        parsed.target_text = parsed.target_text.strip().lower()
        return parsed

    async def interpret_user_query(
        self,
        query: str,
    ) -> Interpretation:

        llm_parse_rsp = await self.parse_query_llm(query)

        llm_rsp = await self.llm.chat_with_format(
            query=query,
            prompt=f"{TRANSLATE_USER_INTENTION} \n\nPARSE: {llm_parse_rsp.model_dump_json()}",
        )

        clean = self.extract_json(llm_rsp.response)
        json_data = json.loads(clean)
        try:
            llm_rsp_obj = Interpretation(**json_data)
        except ValidationError as e:
            raise ValueError(f"Interpretation validation failed: {e}") from e
        return llm_rsp_obj

    async def explaination_request(
        self,
        query: str,
    ):
        stream = await self.llm.stream(
            prompt=EXPLANATION_PROMPT + f"\n\nUSER QUERY: {json.dumps(query)}"
        )

        streamed = ""
        if inspect.isawaitable(stream):
            stream = await stream
        async for chunk in stream:
            delta = getattr(chunk, "delta", None)
            if delta:
                streamed += delta
                yield delta
                continue

            text = getattr(chunk, "text", None)
            if text:
                if text.startswith(streamed):
                    remainder = text[len(streamed) :]
                    if remainder:
                        yield remainder
                    streamed = text
                    continue

                if text != streamed:
                    yield text
                    streamed = text
                continue

            choices = getattr(chunk, "choices", None)
            if choices:
                choice = choices[0]
                choice_delta = getattr(choice, "delta", None)
                content = getattr(choice_delta, "content", None)
                if content:
                    streamed += content
                    yield content

    async def resolve_nl(self, req: NLResolveRequest) -> NLResolveResult:
        user_id = req.user_id
        query = req.query.strip()

        if not user_id:
            return NLResolveResult(
                ok=False,
                error="user_id required",
            )
        if not query:
            return NLResolveResult(
                ok=False,
                error="query required",
            )
        try:
            # with log
            parsed = await self.parse_query_llm(query)
        except Exception as e:
            return NLResolveResult(
                ok=False,
                error=str(e),
            )

        logfire.info(
            f"Parsed NL Query: {parsed.model_dump()}",
        )

        search_text = parsed.target_text if parsed.target_kind != "unknown" else query

        data_dict = {}

        if parsed.target_kind == "category":
            data = self.retriever.resolve_category_id_from_transactions(
                user_id=user_id,
                search_text=search_text,
            )
            data_dict = data

        return NLResolveResult(
            **data_dict,
            ok=True,
            parse=parsed,
        )

    async def format_price_query(
        self,
        amount: int,
        category: str,
        currency: str,
    ):
        prompt = (
            f"{PRICE_FORMAT_PROMPT}\n\n"
            f"AMOUNT: {json.dumps(amount)} "
            f"CATEGORY: {json.dumps(category)} "
            f"CURRENCY: {json.dumps(currency)}"
        )

        streamed = ""
        stream = await self.llm.stream(prompt=prompt)
        if inspect.isawaitable(stream):
            stream = await stream
        async for chunk in stream:
            delta = getattr(chunk, "delta", None)
            if delta:
                streamed += delta
                yield delta
                continue

            text = getattr(chunk, "text", None)
            if text:
                if text.startswith(streamed):
                    remainder = text[len(streamed) :]
                    if remainder:
                        yield remainder
                    streamed = text
                    continue

                if text != streamed:
                    yield text
                    streamed = text
                continue

            choices = getattr(chunk, "choices", None)
            if choices:
                choice = choices[0]
                choice_delta = getattr(choice, "delta", None)
                content = getattr(choice_delta, "content", None)
                if content:
                    streamed += content
                    yield content
