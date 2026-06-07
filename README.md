# Modulehandbook RAG

Lokales Seminarprojekt: ein RAG-artiges Such- und Frage-Antwort-System für universitäre Modulhandbücher.

## Idee

Das System liest Modulhandbücher als PDF, TXT oder Markdown ein, extrahiert Text, erkennt Module wie `P1 Einführung in die Programmierung` oder `WP3 Information Retrieval`, erstellt Chunks und erlaubt Suchanfragen wie:

- Welche Prüfungsform hat WP3 Information Retrieval?
- Wie viele ECTS hat P10?
- Welche Module behandeln maschinelles Lernen?
- Wer ist für P11 verantwortlich?

Der technische Fokus liegt nicht nur auf „Chat mit PDF“, sondern auf **struktur-aware Retrieval**: Modulhandbücher sind halbstrukturierte Dokumente, daher vergleichen wir naive Chunks mit modulbasierten Chunks.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -e .
```

Optional für Dense Retrieval:

```bash
pip install -e ".[dense]"
```

## Daten

Lege Modulhandbuch-PDFs in:

```text
data/raw/
```

Im Projekt liegt bereits ein Beispiel:

```text
data/raw/cl_bsc_modulhandbuch.pdf
```

## Schnellstart

### 1. Daten einlesen und Module extrahieren

```bash
python -m modulehandbook_rag.cli ingest data/raw --out data/processed/chunks.jsonl --chunking module
```

### 2. Suchen

```bash
python -m modulehandbook_rag.cli search "Welche Prüfungsform hat WP3 Information Retrieval?" --chunks data/processed/chunks.jsonl --top-k 5
```

### 3. Fragen beantworten

```bash
python -m modulehandbook_rag.cli ask "Wie viele ECTS hat WP3 Information Retrieval?" --chunks data/processed/chunks.jsonl --top-k 5
```

## CLI-Befehle

```bash
python -m modulehandbook_rag.cli --help
```

Befehle:

- `ingest`: liest Dokumente ein und erzeugt Chunks
- `search`: gibt Top-k Treffer mit Scores aus
- `ask`: gibt eine einfache quellengestützte Antwort aus
- `stats`: zeigt Korpusstatistiken

## Projektstruktur

```text
modulehandbook-rag/
  data/
    raw/
    processed/
  outputs/
  src/modulehandbook_rag/
    cli.py
    config.py
    data_loader.py
    pdf_extraction.py
    preprocessing.py
    chunking.py
    bm25_retrieval.py
    dense_retrieval.py
    hybrid_retrieval.py
    rag.py
    citations.py
    evaluation.py
    schemas.py
    utils.py
  tests/
```

## Präsentationskern

**Forschungsfrage:**

> Verbessert struktur-aware Chunking die Retrieval-Qualität bei RAG-Systemen für Modulhandbücher im Vergleich zu naivem Passage-Chunking?

**Demo:**

Nutzerfrage → Retrieval relevanter Modulabschnitte → Antwort mit Quellen.
