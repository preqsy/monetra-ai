from pydantic import BaseModel, Field


class NLRequest(BaseModel):
    user_id: int
    query: str = Field(min_length=3, max_length=500)


class ExplainRequest(NLRequest):
    message_list: list[str] = Field(default_factory=list)


class NLFormatRequest(BaseModel):
    amount: int | float
    category: str
    currency: str
