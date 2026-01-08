from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from rag.schemas.enums import TransactionTypeEnum


IntentType = Literal["spent_total", "list_transaction", "unknown"]
TargetKind = Literal["category", "unknown"]


class NLParse(BaseModel):
    schema_version: Literal["v1"] = "v1"
    intent: IntentType
    target_kind: TargetKind
    target_text: str = Field(min_length=1, max_length=120)


class CategoryCandidate(BaseModel):
    category_id: int
    category: str = Field(default="")
    hits: int = Field(ge=0)
    share: float = Field(ge=0.0, le=1.0)

    avg_hit_score: float = Field(ge=0.0)
    lexical_match: float = Field(ge=0.0)
    name_sim: float = Field(ge=0.0)
    final_score: float = Field(ge=0.0)


class NLResolveRequest(BaseModel):
    user_id: int
    query: str = Field(min_length=1, max_length=500)

    top_k: int = Field(default=25, ge=5, le=100)
    dominance_threshold: float = Field(default=0.40, ge=0.1, le=0.95)
    min_winner_hits: int = Field(default=4, ge=1, le=50)


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

    total_hits_considered: int = Field(ge=0)
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
