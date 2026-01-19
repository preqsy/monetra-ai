import json
from typing import Sequence
from nl.llm_providers.base import ChatMessage, ChatResult, LLMProvider

from openai import AsyncOpenAI, BaseModel
from nl.models import Interpretation
from nl.prompt import SYSTEM_PROMPT
from config import settings
from openai.types import ResponseFormatJSONSchema


class GroqProvider(LLMProvider):

    def __init__(
        self,
        # model: str = "llama-3.1-70b-versatile",
        temperature: float,
        model: str = settings.LLM_MODEL_NAME,
    ) -> None:
        self.llm = AsyncOpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
        )
        self.model = model
        self.temperature = temperature

    async def chat(self, query: str, prompt: str) -> ChatResult:
        query = query.strip()
        if not query:
            raise ValueError("Empty query")

        # TODO: Use a response format
        response = await self.llm.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": query},
            ],
            temperature=self.temperature,
        )
        # print(f"OpenAI Response: {response}")
        text = response.choices[0].message.content
        return ChatResult(response=text, metadata={"model": response.model})

    async def chat_with_format(
        self,
        query: str,
        prompt: str,
    ) -> ChatResult:
        query = query.strip()
        if not query:
            raise ValueError("Empty query")

        response = await self.llm.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": query},
            ],
            temperature=self.temperature,
        )

        # print(f"OpenAI Response: {response}")

        text = response.choices[0].message.content

        # print(f"{text}")
        return ChatResult(response=text, metadata={"model": response.model})

    async def stream(self, prompt: str):
        return await self.llm.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": prompt},
            ],
            stream=True,
            temperature=self.temperature,
        )
