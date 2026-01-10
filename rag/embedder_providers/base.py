from abc import ABC, abstractmethod

from pydantic import BaseModel


class EmbeddingReturn(BaseModel):
    length: int
    embeddings: list


class EmbedderABC(ABC):
    @abstractmethod
    def embed(self, text: str) -> EmbeddingReturn:
        raise NotImplemented
