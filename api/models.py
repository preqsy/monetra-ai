from pydantic import BaseModel, Field


class NLRequestBase(BaseModel):
    user_id: int
    query: str = Field(min_length=3, max_length=500)


class NLRequest(NLRequestBase):
    query_plan: dict = Field(default_factory=dict)


class TranslateRequest(NLRequestBase):
    query_plan: str = Field(default_factory=str)


class ExplainRequest(NLRequestBase):
    message_list: str = Field(default_factory=str)
    query_plan: str = Field(default_factory=str)
    result_summary: str = Field(default_factory=str)


class NLFormatRequest(BaseModel):
    amount: int | float
    category: str
    currency: str
