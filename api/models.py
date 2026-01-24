from pydantic import BaseModel, Field


class NLRequestBase(BaseModel):
    user_id: int
    query: str = Field(min_length=3, max_length=500)


class NLRequest(NLRequestBase):
    query_plan: dict = Field(default_factory=dict)


class TranslateRequest(NLRequestBase):
    query_plan: dict = Field(default_factory=dict)


class CalculationTrace(BaseModel):
    transactions_count: int
    currency: str
    date_range: dict
    operation: str
    metric: str


class ResultSummary(BaseModel):
    total_amount_in_default: float
    currency: str
    transactions: list[dict]


class ExplainRequest(NLRequestBase):
    message_list: list[dict] = Field(default_factory=list)
    query_plan: dict = Field(default_factory=dict)
    result_summary: ResultSummary
    calculation_trace: CalculationTrace


class NLFormatRequest(BaseModel):
    amount: int | float
    category: str
    currency: str
