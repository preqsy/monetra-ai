from enum import Enum


class TransactionTypeEnum(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"
    DEFAULT = "default"
