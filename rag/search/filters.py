from qdrant_client import models as qm

from rag.schemas.transaction import TransactionSearchFilters


def build_transaction_search_filters(
    *,
    user_id: int,
    f: TransactionSearchFilters,
) -> qm.Filter:
    must_conditions = [
        qm.FieldCondition(
            key="user_id",
            match=qm.MatchValue(value=user_id),
        ),
        qm.FieldCondition(key="doc_type", match=qm.MatchValue(value=f.doc_type)),
    ]
    return qm.Filter(must=must_conditions)
