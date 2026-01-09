import json
from typing import Sequence
from nl.llm_providers.base import ChatMessage, ChatResult, LLMProvider

# from llama_index.llms.openai import OpenAI
from openai import AsyncOpenAI
from nl.prompt import SYSTEM_PROMPT


class GroqProvider(LLMProvider):

    def __init__(
        self,
        model: str = "llama-3.1-8b-instant",
    ) -> None:
        self.llm = AsyncOpenAI(
            api_key="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",
            base_url="https://api.groq.com/openai/v1",
        )
        self.model = model

    async def chat(self, query: str, prompt: str) -> ChatResult:
        query = query.strip()
        if not query:
            raise ValueError("Empty query")

        response = await self.llm.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": query},
            ],
        )
        print(f"OpenAI Response: {response}")
        text = response.choices[0].message.content
        return ChatResult(text=text)

    def stream(self, prompt: str):
        return self.llm.api_key
