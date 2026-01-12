from collections import defaultdict
from pprint import pprint
from typing import Any, Dict, List

from qdrant_client import QdrantClient
from rag.embedder import Embedder
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
        embedder: Embedder,
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
            query=query_vec.embeddings,
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

    def _consine(self, a: List[float], b: List[float]) -> float:
        import math

        dot = 0.0
        na = 0.0
        nb = 0.0

        for x, y in zip(a, b):
            dot += x * y
            na += x * x
            nb += y * y

        if na == 0.0 or nb == 0.0:
            return 0.0
        return dot / (math.sqrt(na) * math.sqrt(nb))

    def _norm(self, s: Any) -> str:
        return str(s or "").strip().lower()

    def resolve_category_id_from_transactions(
        self,
        *,
        user_id: int,
        search_text: str,
        category_sim_threshold: float = 0.65,
        min_kept: int = 3,
        top_k: int = 50,
    ) -> Dict[str, Any]:
        """
        - Retrieve top-k matching transactions (vector search)
        - Aggregate by category_id
        - Validate category label alginment using payload["category"] against search_text
            lexical match + embedding similarity
        - Select winner by combined score + threshold

        Returns:
        (Resolved, winner_category_id, top_candidates)
        """

        search_text = search_text.strip().lower()

        if not user_id or not search_text:
            return {
                "kept": [],
                "discarded": [],
                "best_category_id": None,
                "category_scores": [],
            }

        self.indexer.ensure_collection()
        query_vec = self.embedder.embed(search_text)
        trans_filter = TransactionSearchFilters()
        flt = build_transaction_search_filters(user_id=user_id, f=trans_filter)

        results = self.qdrant_client.query_points(
            collection_name="monetra_collection",
            query=query_vec.embeddings,
            query_filter=flt,
            limit=top_k,
            with_payload=True,
            with_vectors=False,
        )
        # print(f"Query Results; {results}")
        cat_vec_cache: Dict[str, List[float]] = {}
        kept = []
        discarded = []

        for idx, r in enumerate(results.points):
            payload: Dict[str, Any] = r.payload or {}

            if payload.get("user_id") != user_id:
                continue

            cat_id = payload.get("category_id")
            cat_label = self._norm(payload.get("category"))
            txn_id = payload.get("transaction_id")

            if not cat_label or cat_id is None or txn_id is None:
                discarded.append(
                    {"payload": payload, "hit_score": float(r.score), "cat_sim": 0.0}
                )
                continue

            if cat_label not in cat_vec_cache:
                cat_vec_cache[cat_label] = self.embedder.embed(cat_label).embeddings

            cat_sim = self._consine(query_vec.embeddings, cat_vec_cache[cat_label])
            cat_sim = max(0.0, min(1.0, float(cat_sim)))

            row = {
                "transaction_id": txn_id,
                "category_id": cat_id,
                "hit_score": float(r.score),
                "cat_sim": cat_sim,
                "payload": payload,
                "category": cat_label,
            }

            if cat_sim >= category_sim_threshold:
                kept.append(row)

            else:
                discarded.append(row)

        evidence_by_cat: Dict[str, float] = defaultdict(float)
        label_by_cat = {}

        for row in kept:
            cid = row["category_id"]
            evidence_by_cat[cid] += row["hit_score"] * row["cat_sim"]
            label_by_cat[cid] = row["category"]

        category_scores = [
            {
                "category_id": cid,
                "category": label_by_cat.get(cid, ""),
                "evidence": float(ev),
            }
            for cid, ev in evidence_by_cat.items()
        ]

        category_scores.sort(key=lambda x: x["evidence"], reverse=True)
        best_category_id = (
            category_scores[0]["category_id"] if category_scores else None
        )
        kept.sort(key=lambda x: (x["cat_sim"], x["hit_score"]), reverse=True)

        return {
            "resolved_candidates": kept,
            "discarded_candidates": discarded,
            "resolved_category_id": best_category_id,
            "category_scores": category_scores[:5],
        }
