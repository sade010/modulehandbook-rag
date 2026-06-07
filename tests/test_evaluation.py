from modulehandbook_rag.evaluation import precision_at_k, recall_at_k, mrr


def test_metrics():
    retrieved = ["a", "b", "c"]
    relevant = {"b"}
    assert precision_at_k(retrieved, relevant, 2) == 0.5
    assert recall_at_k(retrieved, relevant, 2) == 1.0
    assert mrr(retrieved, relevant) == 0.5
