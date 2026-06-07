from __future__ import annotations

import re

from .citations import format_source
from .schemas import SearchResult

KEY_FIELDS = [
    "ECTS",
    "Teilnahmevoraussetzung",
    "Zeitpunkt im Studienverlauf",
    "Dauer",
    "Inhalte",
    "Qualifikationsziele",
    "Form der Modulprufung",
    "Form der Modulprüfung",
    "Art der Bewertung",
    "Modulverantwortliche/r",
    "Unterrichtssprache",
]


def answer_from_results(query: str, results: list[SearchResult]) -> str:
    """Template-based answer that stays grounded in retrieved chunks.

    This is a safe local fallback before connecting a real LLM.
    """
    if not results:
        return "Ich habe keine passenden Stellen im Modulhandbuch gefunden."

    best = results[0].chunk
    answer_lines = []
    answer_lines.append("Antwort auf Basis der gefundenen Modulhandbuchstellen:")
    answer_lines.append("")

    extracted = _extract_likely_answer(query, best.text)
    if extracted:
        answer_lines.append(extracted)
    else:
        answer_lines.append(_short_summary(best.text))

    answer_lines.append("")
    answer_lines.append("Quellen:")
    for result in results[:3]:
        answer_lines.append(f"- {format_source(result.chunk)}")
    return "\n".join(answer_lines)


def _extract_likely_answer(query: str, text: str) -> str | None:
    q = query.lower()
    field_hints = []
    if "ects" in q or "punkte" in q:
        ects_sentence = _extract_ects_sentence(text) or _sentence_containing(text, "ECTS-Punkte")
        if ects_sentence:
            return ects_sentence
        field_hints.append("ECTS")
    if "prüf" in q or "pruef" in q or "klausur" in q or "hausarbeit" in q:
        field_hints.extend(["Form der Modulprufung", "Form der Modulprüfung"])
    if "voraussetzung" in q:
        field_hints.append("Teilnahmevoraussetzung")
    if "semester" in q:
        field_hints.append("Zeitpunkt im Studienverlauf")
    if "verantwort" in q or "dozent" in q:
        field_hints.append("Modulverantwortliche/r")
    if "inhalt" in q or "behandelt" in q or "themen" in q:
        field_hints.append("Inhalte")

    for field in field_hints:
        value = _extract_field(text, field)
        if value:
            return f"{field}: {value}"

    # fallback: return first sentence containing any important query token
    query_terms = [t for t in re.findall(r"[a-zäöüß0-9]+", q) if len(t) > 4]
    sentences = re.split(r"(?<=[.!?])\s+|\n+", text)
    for sentence in sentences:
        lower = sentence.lower()
        if any(term in lower for term in query_terms):
            return sentence.strip()
    return None


def _extract_ects_sentence(text: str) -> str | None:
    match = re.search(r"Im Modul\s+.*?insgesamt\s+(\d+)\s+ECTS", text, re.IGNORECASE | re.DOTALL)
    if match:
        return f"Im Modul müssen insgesamt {match.group(1)} ECTS-Punkte erworben werden."
    return None


def _sentence_containing(text: str, term: str) -> str | None:
    sentences = re.split(r"(?<=[.!?])\s+|\n+", text)
    for sentence in sentences:
        if term.lower() in sentence.lower():
            cleaned = re.sub(r"\s+", " ", sentence).strip()
            if len(cleaned) > 15:
                return cleaned[:900]
    return None


def _extract_field(text: str, field: str) -> str | None:
    labels = "|".join(re.escape(label) for label in KEY_FIELDS)
    pattern = re.compile(rf"{re.escape(field)}\s*(.*?)(?=\n(?:{labels})\b|$)", re.IGNORECASE | re.DOTALL)
    match = pattern.search(text)
    if not match:
        return None
    value = re.sub(r"\s+", " ", match.group(1)).strip()
    return value[:900] if value else None


def _short_summary(text: str, max_chars: int = 900) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars] + (" …" if len(text) > max_chars else "")
