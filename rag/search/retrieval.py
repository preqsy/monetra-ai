from collections import Counter
from pprint import pprint
from typing import Any, Dict, List

from qdrant_client import QdrantClient
from nl.models import CategoryCandidate
from rag.embedder import OllamaEmbedder
from rag.qdrant_indexer import QdrantIndexer
from rag.schemas.transaction import (
    TransactionSearchFilters,
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

    def resolve_category_id_from_transactions(
        self,
        *,
        user_id: int,
        search_text: str,
        top_k: int,
        dominance_threshold: float,
        min_winner_hits: int,
    ) -> tuple[bool, str | None, List[CategoryCandidate], int]:

        self.indexer.ensure_collection(768)
        vec = self.embedder.embed(search_text)
        trans_filter = TransactionSearchFilters()
        flt = build_transaction_search_filters(user_id=user_id, f=trans_filter)

        results = self.qdrant_client.query_points(
            collection_name="monetra_collection",
            query=vec,
            query_filter=flt,
            limit=top_k,
            with_payload=True,
            with_vectors=False,
        )

        counts: Counter[str] = Counter()
        total = 0

        for r in results.points:
            payload: Dict[str, Any] = r.payload or {}

            if payload.get("user_id") != user_id:
                continue

            category_id = payload.get("category_id")

            if not category_id:
                continue

            counts[category_id] += 1
            total += 1

        if total == 0 or not counts:
            return False, None, [], 0

        ranked = counts.most_common()
        candidates: List[CategoryCandidate] = [
            CategoryCandidate(category_id=category_id, hits=hits, share=hits / total)
            for category_id, hits in ranked[:5]
        ]
        winner_id, winner_hits = ranked[0]
        winner_share = winner_hits / total
        resolved = (winner_hits >= min_winner_hits) and (
            winner_share >= dominance_threshold
        )

        return resolved, (winner_id if resolved else None), candidates, total
