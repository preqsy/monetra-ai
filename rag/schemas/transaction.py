from datetime import date
from typing import Any, ClassVar, Dict, List, Optional
from pydantic import BaseModel, Field, model_validator

from rag.schemas.enums import TransactionTypeEnum


class TransactionDoc(BaseModel):
    DOC_ID: ClassVar[str] = "doc_id"
    DOC_TYPE: ClassVar[str] = "doc_type"
    TEXT: ClassVar[str] = "text"
    USER_ID: ClassVar[str] = "user_id"
    TRANSACTION_ID: ClassVar[str] = "transaction_id"
    ACCOUNT: ClassVar[str] = "account"
    CATEGORY: ClassVar[str] = "category"
    CURRENCY: ClassVar[str] = "currency"
    AMOUNT: ClassVar[str] = "amount"
    DATE_UTC: ClassVar[str] = "date_utc"
    TRANSACTION_TYPE: ClassVar[str] = "transaction_type"

    doc_id: str
    doc_type: str = Field(default="transaction")
    text: str
    user_id: int
    transaction_id: int
    transaction_type: TransactionTypeEnum
    account_id: int
    category_id: int
    category: str
    currency: str
    amount: int
    date_utc: date = date.today()

    # TODO: Re-implement this validator to generate the text field from transaction data

    @model_validator(mode="before")
    @classmethod
    def from_transactions(cls, values):
        text_lines = [
            "TYPE: transaction",
            f"TRANSACTION_TYPE: {values.get(cls.TRANSACTION_TYPE)}",
            f"AMOUNT: {values.get(cls.AMOUNT)}",
            f"CURRENCY: {values.get(cls.CURRENCY)}",
            f"ACCOUNT: {(values.get(cls.ACCOUNT) or '').strip()}",
            f"CATEGORY: {(values.get(cls.CATEGORY) or '').strip()}",
            f"BOOKED_AT_UTC: {values.get(cls.DATE_UTC)}",
        ]
        values["text"] = " ".join(text_lines)
        return values

    @model_validator(mode="before")
    @classmethod
    def set_doc_id(cls, values):
        doc_type = values.get(cls.DOC_TYPE)
        if doc_type == "transaction":
            values["doc_id"] = f"transaction-{values.get(cls.TRANSACTION_ID)}"
        return values


class TransactionSearchFilters(BaseModel):
    doc_type: str = "transaction"

    # optional payload filters
    account_id: Optional[str] = None
    category_id: Optional[str] = None
    currency: Optional[str] = None
    is_transfer: Optional[bool] = None

    # epoch seconds in UTC
    date_from_utc: Optional[int] = Field(default=None, ge=0)
    date_to_utc: Optional[int] = Field(default=None, ge=0)


class TransactionSearchRequest(BaseModel):
    user_id: int
    query: str = Field(min_length=1, max_length=500)
    top_k: int = Field(default=10, ge=1, le=50)
    filters: TransactionSearchFilters = Field(default_factory=TransactionSearchFilters)


class TransactionSearchHit(BaseModel):
    score: float
    point_id: str
    doc_id: str
    transaction_id: str
    transaction_type: str
    account_id: str
    category_id: str
    category: str
    currency: str
    amount: int
    date_utc: str
    doc_type: str = "transaction"
    payload: Dict[str, Any] = Field(default_factory=dict)


class TransactionSearchResponse(BaseModel):
    hits: List[TransactionSearchHit]
