import json
from llama_index.llms.ollama import Ollama
from pydantic import ValidationError

from nl.llm_providers.factory import get_llm_provider
from nl.models import NLParse, NLResolveRequest, NLResolveResult
from nl.prompt import PRICE_FORMAT_PROMPT, SYSTEM_PROMPT
from rag.search.retrieval import Retrieval


class NLQueryResolver:
    def __init__(
        self,
        retriever: Retrieval,
        model: str = "llama3.2:3b",
        # model: str = "Qwen2.5:7b",
        temperature: float = 0.0,
    ) -> None:
        self.llm = get_llm_provider()
        # self.llm = Ollama(
        #     model=model,
        #     base_url="http://localhost:11434",
        #     temperature=temperature,
        #     additional_kwargs={"num_ctx": 2048, "num_predict": 128},
        #     request_timeout=60.0,
        # )
        self.retriever = retriever

    def extract_json(self, text: str) -> str:
        text = text.strip()
        if text.startswith("```"):
            text = text.split("```", 2)[1]
        return text.strip()

    async def parse_query_llm(self, query: str) -> NLParse:
        q = query.strip()
        if not q:
            raise ValueError("Empty query")

        raw = await self.llm.chat(query=q, prompt=SYSTEM_PROMPT)

        print(f"LLM data response: {raw.text}")
        clean = self.extract_json(raw.text)
        data = json.loads(clean)

        try:
            parsed = NLParse.model_validate(data)
        except ValidationError as e:
            raise ValueError(f"NLParse validation failed: {e}") from e

        parsed.target_text = parsed.target_text.strip().lower()
        return parsed

    async def resolve_nl(self, req: NLResolveRequest) -> NLResolveResult:
        user_id = req.user_id
        query = req.query.strip()

        if not user_id:
            return NLResolveResult(
                ok=False,
                total_hits_considered=0,
                error="user_id required",
            )
        if not query:
            return NLResolveResult(
                ok=False,
                total_hits_considered=0,
                error="query required",
            )
        try:
            parsed = await self.parse_query_llm(query)
        except Exception as e:
            return NLResolveResult(
                ok=False,
                total_hits_considered=0,
                error=str(e),
            )

        search_text = parsed.target_text if parsed.target_kind != "unknown" else query

        print(f"**** Search text: {search_text}")

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
            total_hits_considered=1,
            parse=parsed,
        )

    def format_price_query(
        self,
        amount: int,
        category: str,
        currency: str,
    ):
        print(f"Amount: {amount}")
        prompt = (
            f"{PRICE_FORMAT_PROMPT}\n\n"
            f"AMOUNT: {json.dumps(amount)} "
            f"CATEGORY: {json.dumps(category)} "
            f"CURRENCY: {json.dumps(currency)}"
        )

        streamed = ""
        for chunk in self.llm.stream(prompt=prompt):
            delta = getattr(chunk, "delta", None)
            if delta:
                streamed += delta
                yield delta
                continue

            text = getattr(chunk, "text", None)
            if not text:
                continue

            if text.startswith(streamed):
                remainder = text[len(streamed) :]
                if remainder:
                    yield remainder
                streamed = text
                continue

            if text != streamed:
                yield text
                streamed = text
