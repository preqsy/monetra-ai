import json
from nl.llm_providers.base import ChatResult, LLMProvider
from llama_index.llms.ollama import Ollama
from config import settings
from nl.models import Interpretation


class OllamaProvider(LLMProvider):

    def __init__(
        self,
        *,
        temperature: float,
        model: str = settings.LLM_MODEL_NAME,
    ):
        self.llm = Ollama(
            model=model,
            base_url="http://localhost:11434",
            temperature=temperature,
            additional_kwargs={
                "num_ctx": 2048,
                "num_predict": 128,
            },
            request_timeout=600.0,
        )
        self.sllm = self.llm.as_structured_llm(output_cls=Interpretation)

    async def chat(
        self,
        query: str,
        prompt: str,
    ) -> ChatResult:
        q = query.strip()

        if not q:
            raise ValueError("Empty Query")

        data = await self.llm.acomplete(
            prompt=f"{prompt} \n\n USER QUERY: {json.dumps(q)}"
        )
        data = data.text

        return ChatResult(response=data)

    async def chat_with_format(
        self,
        query: str,
        prompt: str,
    ) -> ChatResult:
        q = query.strip()

        if not q:
            raise ValueError("Empty Query")

        data = await self.sllm.acomplete(
            prompt=f"{prompt} \n\n USER QUERY: {json.dumps(q)} \n\n"
        )

        return ChatResult(response=data.text)

    async def stream(
        self,
        prompt: str,
    ):
        return self.llm.astream_complete(prompt)
