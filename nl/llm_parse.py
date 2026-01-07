import json
from llama_index.llms.ollama import Ollama
from pydantic import ValidationError

from nl.models import NLParse, NLResolveRequest, NLResolveResult
from nl.prompt import SYSTEM_PROMPT
from rag.search.retrieval import Retrieval


class LLMParse:
    def __init__(
        self,
        retriever: Retrieval,
        model: str = "Qwen2.5:7b",
        temperature: float = 0.0,
    ) -> None:
        self.llm = Ollama(
            model=model,
            base_url="http://localhost:11434",
            temperature=temperature,
            additional_kwargs={"num_ctx": 2048, "num_predict": 128},
            request_timeout=60.0,
        )
        self.retriever = retriever

    def extract_json(self, text: str) -> str:
        text = text.strip()
        if text.startswith("```"):
            # remove ```json or ``` and trailing ```
            text = text.split("```", 2)[1]
        return text.strip()

    def parse_query_llm(self, query: str) -> NLParse:
        q = query.strip()
        if not q:
            raise ValueError("Empty query")

        raw = self.llm.complete(
            prompt=f"{SYSTEM_PROMPT}\n\nUSER_QURY: {json.dumps(q)}"
        ).text

        print(f"LLM data response: {raw}")
        clean = self.extract_json(raw)
        data = json.loads(clean)

        parsed = NLParse.model_validate(data)
        # parsed = NLParse(**data)
        # print(f"Parsed: {parsed}")
        # try:
        #     parsed = NLParse.model_validate(data)
        # except ValidationError as e:
        #     raise ValueError(f"NLParse validation failed: {e}") from e

        parsed.target_text = parsed.target_text.strip().lower()
        return parsed

    def resolve_nl(self, req: NLResolveRequest) -> NLResolveResult:
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
        # parsed = self.parse_query_llm(query)
        try:
            parsed = self.parse_query_llm(query)
        except Exception as e:
            # print(f"Parsed: {parsed}")
            return NLResolveResult(
                ok=False,
                total_hits_considered=0,
                error=str(e),
            )

        search_text = parsed.target_text if parsed.target_kind != "unknown" else query

        resolved_category = False
        category_id = None
        candidates = []
        total = 0

        if parsed.target_kind == "category":
            resolved_category, category_id, candidates, total = (
                self.retriever.resolve_category_id_from_transactions(
                    user_id=user_id,
                    search_text=search_text,
                    top_k=req.top_k,
                    dominance_threshold=req.dominance_threshold,
                    min_winner_hits=req.min_winner_hits,
                )
            )
        else:
            # Minimal: only category resolution in v1
            total = 0

        return NLResolveResult(
            ok=True,
            parse=parsed,
            resolved_category=resolved_category,
            category_id=category_id,
            category_candidates=candidates,
            total_hits_considered=total,
            error=(
                None
                if resolved_category
                else (
                    "Category not confidently resolved"
                    if parsed.target_kind == "category"
                    else "Non-category query in v1"
                )
            ),
        )
