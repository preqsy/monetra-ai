from abc import ABC, abstractmethod
from typing import Dict, Literal, Optional

from pydantic import BaseModel

Role = Literal["system", "user", "assistant"]


class ChatResult(BaseModel):
    response: str
    metadata: Optional[Dict] = {}


class ChatMessage(BaseModel):
    role: Role
    content: str


class LLMProvider(ABC):

    @abstractmethod
    async def chat(self, query: str, prompt: str) -> ChatResult:
        raise NotImplementedError

    @abstractmethod
    async def chat_with_format(self, query: str, prompt: str) -> ChatResult:
        raise NotImplementedError

    @abstractmethod
    async def stream(
        self,
        prompt: str,
    ):
        raise NotImplemented
