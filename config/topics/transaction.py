from config import settings

TRANSACTION_CREATED = (
    "transaction.created.dev"
    if settings.ENVIRONMENT == "dev"
    else "transaction.created.prod"
)
