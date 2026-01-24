from pydantic import BaseModel, Field


class NLRequestBase(BaseModel):
    user_id: int
    query: str = Field(min_length=3, max_length=500)


class NLRequest(NLRequestBase):
    query_plan: dict = Field(default_factory=dict)


class TranslateRequest(NLRequestBase):
    query_plan: dict = Field(default_factory=dict)


class ExplainRequest(NLRequestBase):
    message_list: list = Field(default_factory=list)
    query_plan: dict = Field(default_factory=dict)
    result_summary: dict = Field(default_factory=dict)
    calculation_trace: dict = Field(default_factory=dict)


class NLFormatRequest(BaseModel):
    amount: int | float
    category: str
    currency: str
