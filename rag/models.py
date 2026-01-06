from typing import ClassVar
from pydantic import BaseModel, Field, model_validator


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

    doc_id: int
    doc_type: str = Field(default="transaction")
    text: str
    user_id: int
    transaction_id: int
    account_id: int
    category_id: int
    currency: str
    amount: int
    date_utc: str

    # TODO: Re-implement this validator to generate the text field from transaction data

    # @model_validator(mode="before")
    # @classmethod
    # def from_transactions(cls, values):
    #     direction = "credit" if values.get(cls.AMOUNT) > 0 else "debit"
    #     text_lines = [
    #         "TYPE: transaction",
    #         # f"MERCHANT: {merchant}",
    #         # f"MEMO: {memo}",
    #         f"DIRECTION: {direction}",
    #         f"AMOUNT: {values.get(cls.AMOUNT)}",
    #         f"CURRENCY: {values.get(cls.CURRENCY)}",
    #         f"ACCOUNT: {(values.get(cls.ACCOUNT) or '').strip()}",
    #         f"CATEGORY: {(values.get(cls.CATEGORY) or '').strip()}",
    #         f"BOOKED_AT_UTC: {values.get(cls.DATE_UTC).isoformat().replace('+00:00', 'Z')}",
    #     ]
