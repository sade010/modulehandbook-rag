from __future__ import annotations

from rank_bm25 import BM25Okapi

from .preprocessing import tokenize_german
from .schemas import Chunk, SearchResult


class BM25Retriever:
    def __init__(self, chunks: list[Chunk]):
        if not chunks:
            raise ValueError("Cannot build retriever with zero chunks.")
        self.chunks = chunks
        self.tokenized = [tokenize_german(chunk.text) for chunk in chunks]
        self.index = BM25Okapi(self.tokenized)

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        query_tokens = tokenize_german(query)
        scores = self.index.get_scores(query_tokens)
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]
        return [
            SearchResult(chunk=self.chunks[i], score=float(score), rank=rank + 1)
            for rank, (i, score) in enumerate(ranked)
        ]
