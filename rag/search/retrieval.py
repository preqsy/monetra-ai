from pprint import pprint
from typing import Any, Dict

from qdrant_client import QdrantClient
from rag.embedder import OllamaEmbedder
from rag.qdrant_indexer import QdrantIndexer
from rag.schemas.transaction import (
    TransactionSearchHit,
    TransactionSearchRequest,
    TransactionSearchResponse,
)
from rag.search.filters import build_transaction_search_filters


class Retrieval:
    def __init__(
        self,
        indexer: QdrantIndexer,
        qdrant_client: QdrantClient,
        embedder: OllamaEmbedder,
    ) -> None:
        self._REQUIRED_PAYLOAD_KEYS = ["doc_id", "doc_type"]
        self.indexer = indexer
        self.qdrant_client = qdrant_client
        self.embedder = embedder

    def _get_payload(self, payload: Dict[str, Any], key: str, default: Any = "") -> Any:
        v = payload.get(key, default)
        return default if v is None else v

    def search_transactions(
        self, req: TransactionSearchRequest
    ) -> TransactionSearchResponse:
        user_id = req.user_id
        if not user_id:
            raise ValueError
        query = req.query
        if not query:
            raise ValueError

        self.indexer.ensure_collection(768)
        query_vec = self.embedder.embed(query)

        qfilter = build_transaction_search_filters(user_id=user_id, f=req.filters)

        # print(f"Qdrant filter: {qfilter}")
        results = self.qdrant_client.query_points(
            collection_name=("monetra_collection"),
            query=query_vec,
            query_filter=qfilter,
            with_payload=True,
            with_vectors=False,
            # score_threshold=None,  # Enable if I want hard cutoff
        )
        hits: list[TransactionSearchHit] = []
        for r in results.points:
            payload = r.payload or {}
            for k in self._REQUIRED_PAYLOAD_KEYS:
                self._get_payload(payload, k)

            if payload.get("user_id") != user_id:
                continue

            hits.append(
                TransactionSearchHit(
                    score=float(r.score),
                    point_id=str(r.id),
                    doc_id=str(payload["doc_id"]),
                    transaction_id=str(payload["transaction_id"]),
                    account_id=str(payload["account_id"]),
                    category_id=str(payload["category_id"]),
                    currency=str(payload["currency"]),
                    amount=int(payload["amount"]),
                    date_utc=str(payload["date_utc"]),
                    doc_type=str(payload.get("doc_type") or "transaction"),
                    payload=payload,
                    transaction_type=str(payload.get("transaction_type")),
                    category=str(payload["category"]),
                )
            )
        hit_list = [
            {
                "transaction_type": h.transaction_type,
                "scores": h.score,
                "category": h.category,
            }
            for h in hits
        ]
        pprint(f"Hits: {hit_list}")
        return TransactionSearchResponse(hits=hits)
