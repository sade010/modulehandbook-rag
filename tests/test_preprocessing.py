from modulehandbook_rag.preprocessing import tokenize_german


def test_tokenize_german_umlauts():
    assert "prüfung" in tokenize_german("Die Prüfung ist wichtig.")
