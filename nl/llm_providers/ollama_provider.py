import json
from nl.llm_providers.base import ChatResult, LLMProvider
from llama_index.llms.ollama import Ollama


class OllamaProvider(LLMProvider):

    def __init__(self, *, model: str = "Qwen2.5:7b"):
        self.llm = Ollama(
            model=model,
            base_url="http://localhost:11434",
            temperature=0.1,
            additional_kwargs={
                "num_ctx": 2048,
                "num_predict": 128,
            },
            request_timeout=60.0,
        )

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

        return ChatResult(text=data)

    async def stream(
        self,
        prompt: str,
    ):
        return self.llm.astream_complete(prompt)
