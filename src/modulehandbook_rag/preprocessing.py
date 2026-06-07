from __future__ import annotations

import re
import unicodedata


def clean_text(text: str) -> str:
    """Normalize PDF-extracted text while preserving German characters."""
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\u00ad", "")
    text = text.replace("￾", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"(?<=\w)-\n(?=\w)", "", text)  # de-hyphenate line breaks
    text = re.sub(r"(?<!\n)\n(?!\n)", "\n", text)
    return text.strip()


def tokenize_german(text: str) -> list[str]:
    """Simple tokenizer suitable for BM25 baseline."""
    text = text.lower()
    return re.findall(r"[a-zäöüß0-9]+", text, flags=re.IGNORECASE)
