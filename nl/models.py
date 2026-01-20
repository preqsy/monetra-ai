from __future__ import annotations

from typing import List, Literal, Optional

from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, model_validator


from rag.schemas.enums import TransactionTypeEnum


IntentType = Literal["spent_total", "list_transaction", "unknown"]
TargetKind = Literal["category", "unknown"]


class NLParse(BaseModel):
    schema_version: Literal["v1"] = "v1"
    intent: IntentType
    target_kind: TargetKind
    target_text: str = Field(min_length=1, max_length=120)


class NLResolveRequest(BaseModel):
    user_id: int
    query: str = Field(min_length=1, max_length=500)

    top_k: int = Field(default=25, ge=5, le=100)


class TransactionObj(BaseModel):
    doc_id: str
    transaction_type: TransactionTypeEnum
    amount: int
    currency: str
    account_id: int
    category: str
    date_utc: str


class ResolvedCategory(BaseModel):
    transaction_id: int
    category_id: int
    hit_score: float
    cat_sim: float
    category: str
    payload: TransactionObj


class DiscardedCategory(BaseModel):
    transaction_id: int
    category: str


class NLResolveResult(BaseModel):
    ok: bool
    parse: Optional[NLParse] = None

    resolved_category: Optional[str] = ""
    resolved_category_id: Optional[int] = None
    resolved_candidates: List[ResolvedCategory] = Field(default_factory=list)
    discarded_candidates: List[DiscardedCategory] = Field(default_factory=list)
    category_scores: Optional[list] = []

    error: Optional[str] = None

    @model_validator(mode="after")
    def validate_shape(self):
        if self.ok and self.parse is None:
            raise ValueError("ok=true requires parse")
        if self.resolved_category and not self.resolved_category_id:
            raise ValueError("resolved_category=true requires category_id")
        if (not self.ok) and not self.error:
            raise ValueError("ok=false requires error")
        return self


class QueryDelta(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intent: Optional[str] = None
    target_kind: Optional[TargetKind] = None
    target_reference: Optional[str] = (
        None  # natural-language reference; backend resolves to IDs
    )
    currency_mode: Optional[str] = None  # e.g. "EUR", "USD", "BASE"
    grouping: Optional[str] = None  # e.g. "category", "merchant", "day"


class Ambiguity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    present: bool
    reason: Optional[str] = None


class Interpretation(BaseModel):
    """
    LLM output envelope. Backend owns routing/decisions; this is advisory structure only.
    """

    model_config = ConfigDict(extra="forbid")

    explanation_request: bool
    delta: Optional[QueryDelta] = None
    ambiguity: Optional[Ambiguity] = None
