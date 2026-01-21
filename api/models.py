from pydantic import BaseModel, Field


class NLRequest(BaseModel):
    user_id: int
    query: str = Field(min_length=3, max_length=500)


class TranslateRequest(NLRequest):
    query_plan: str = Field(default_factory=str)


class ExplainRequest(NLRequest):
    message_list: str = Field(default_factory=str)
    query_plan: str = Field(default_factory=str)
    result_summary: str = Field(default_factory=str)


class NLFormatRequest(BaseModel):
    amount: int | float
    category: str
    currency: str
