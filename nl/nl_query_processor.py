import inspect
import json
from pydantic import ValidationError

import logfire
from nl.llm_providers.factory import get_llm_provider
from nl.models import Interpretation, NLParse, NLResolveRequest, NLResolveResult
from nl.prompt import (
    EXPLANATION_PROMPT,
    PRICE_FORMAT_PROMPT,
    RESOLVE_CATEGORY_PROMPT,
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

    async def interpret_user_query(
        self,
        query: str,
        query_plan: dict,
    ) -> Interpretation:

        prompt = f"{TRANSLATE_USER_INTENTION} \n\n QUERY PLAN: {json.dumps(query_plan)}"

        # print("Using prompt:", prompt)
        llm_rsp = await self.llm.chat_with_format(
            query=query,
            prompt=prompt,
        )

        clean = self.extract_json(llm_rsp.response)
        json_data = json.loads(clean)
        try:
            llm_rsp_obj = Interpretation(**json_data)
        except ValidationError as e:
            logfire.error(f"Interpretation validation failed: {str(e)}")
            raise ValueError(f"Interpretation validation failed: {e}") from e
        return llm_rsp_obj

    async def explain_request(
        self,
        query: str,
        query_plan: str,
        message_list: str,
        result_summary: str,
        calculation_trace: str,
    ):

        print("Explaining request with calculation trace:", calculation_trace)
        prompt = (
            f"{EXPLANATION_PROMPT}\n\n USER QUERY: {json.dumps(query)}\n\n"
            f"QUERY PLAN: {json.dumps(query_plan)}\n\n"
            f"MESSAGE LIST: {json.dumps(message_list)}\n\n"
            f"RESULT SUMMARY: {json.dumps(result_summary)}\n\n"
            f"CALCULATION TRACE: {json.dumps(calculation_trace)}"
        )

        stream = await self.llm.stream(prompt=prompt)
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

    async def resolve_category_nl(self, req: NLResolveRequest) -> NLResolveResult:
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
            parsed = req.parsed
            print(f"Using pre-parsed NLParse: {parsed}")

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

    async def format_resolve_response(
        self,
        amount: int,
        category: str,
        currency: str,
    ):
        """Formats the response from the backend and streams the LLM response"""

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
