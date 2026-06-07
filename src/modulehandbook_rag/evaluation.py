from __future__ import annotations

from math import log2


def precision_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    if k == 0:
        return 0.0
    return sum(1 for item in retrieved[:k] if item in relevant) / k


def recall_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    if not relevant:
        return 0.0
    return sum(1 for item in retrieved[:k] if item in relevant) / len(relevant)


def mrr(retrieved: list[str], relevant: set[str]) -> float:
    for idx, item in enumerate(retrieved, start=1):
        if item in relevant:
            return 1 / idx
    return 0.0


def ndcg_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    dcg = 0.0
    for idx, item in enumerate(retrieved[:k], start=1):
        if item in relevant:
            dcg += 1 / log2(idx + 1)
    ideal_hits = min(len(relevant), k)
    idcg = sum(1 / log2(i + 1) for i in range(1, ideal_hits + 1))
    return dcg / idcg if idcg else 0.0
