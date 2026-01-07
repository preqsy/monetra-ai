from datetime import date
from typing import ClassVar
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
