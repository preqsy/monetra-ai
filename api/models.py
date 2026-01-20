from pydantic import BaseModel, Field


class NLRequest(BaseModel):
    user_id: int
    query: str = Field(min_length=3, max_length=500)


class TranslateRequest(NLRequest):
    query_plan: dict = Field(default_factory=dict)


class ExplainRequest(NLRequest):
    message_list: list[dict] = Field(default_factory=list)
    query_plan: dict = Field(default_factory=dict)


class NLFormatRequest(BaseModel):
    amount: int | float
    category: str
    currency: str
