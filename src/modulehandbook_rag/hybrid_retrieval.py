from __future__ import annotations

from .bm25_retrieval import BM25Retriever
from .dense_retrieval import DenseRetriever
from .schemas import Chunk, SearchResult


def _normalize(scores: dict[str, float]) -> dict[str, float]:
    if not scores:
        return {}
    vals = list(scores.values())
    lo, hi = min(vals), max(vals)
    if hi == lo:
        return {k: 1.0 for k in scores}
    return {k: (v - lo) / (hi - lo) for k, v in scores.items()}


class HybridRetriever:
    def __init__(self, chunks: list[Chunk], alpha: float = 0.5):
        self.chunks = chunks
        self.alpha = alpha
        self.bm25 = BM25Retriever(chunks)
        self.dense = DenseRetriever(chunks)
        self.by_id = {c.chunk_id: c for c in chunks}

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        bm25_results = self.bm25.search(query, top_k=max(top_k * 4, 20))
        dense_results = self.dense.search(query, top_k=max(top_k * 4, 20))

        bm25_scores = _normalize({r.chunk.chunk_id: r.score for r in bm25_results})
        dense_scores = _normalize({r.chunk.chunk_id: r.score for r in dense_results})
        ids = set(bm25_scores) | set(dense_scores)
        combined = {
            cid: self.alpha * dense_scores.get(cid, 0.0) + (1 - self.alpha) * bm25_scores.get(cid, 0.0)
            for cid in ids
        }
        ranked = sorted(combined.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return [
            SearchResult(chunk=self.by_id[cid], score=float(score), rank=rank + 1)
            for rank, (cid, score) in enumerate(ranked)
        ]
