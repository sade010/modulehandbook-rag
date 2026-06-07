# Modulehandbook RAG

A retrieval-augmented question answering system for university module handbooks.

The project was developed for the CIS/LMU seminar **Suchmaschinen**. Its goal is not simply to build a generic “chat with a PDF” application. Instead, it focuses on **structure-aware retrieval for semi-structured academic documents**, especially module handbooks.

The system can answer questions such as:

- Welche Prüfungsform hat WP3 Information Retrieval?
- Wie viele ECTS hat P10 Statistische Methoden in der Sprachverarbeitung?
- Wer ist modulverantwortlich für P11 Informationsextraktion?
- Welche Module behandeln maschinelles Lernen?
- Welche Inhalte werden in P8 behandelt?

The included demo document is the LMU Bachelor Computerlinguistik module handbook.

## Project idea

University module handbooks are not ordinary free-text documents. They contain repeated sections such as module title, ECTS, prerequisites, contents, learning outcomes, exam type and responsible lecturer.

This project uses that structure for retrieval. Instead of only splitting the document into fixed-size text windows, it supports different chunking strategies:

- naive fixed-size chunks
- module-level chunks
- field-level chunks

The main research question is:

> Does structure-aware chunking improve retrieval quality for RAG systems on university module handbooks?

## Current scope

The prototype currently supports:

- PDF, TXT and Markdown ingestion
- text cleaning for German PDF extraction artifacts
- naive, module-level and field-level chunking
- BM25 retrieval
- optional dense retrieval with sentence-transformers
- optional hybrid retrieval
- template-based grounded answers with sources
- LLM-based RAG answers via Ollama
- small evaluation set for retrieval quality

## Project structure

```text
modulehandbook-rag/
  README.md
  pyproject.toml
  data/
    raw/
      cl_bsc_modulhandbuch.pdf
    processed/
    eval/
      demo_queries.jsonl
  outputs/
  src/
    modulehandbook_rag/
      cli.py
      data_loader.py
      pdf_extraction.py
      preprocessing.py
      chunking.py
      bm25_retrieval.py
      dense_retrieval.py
      hybrid_retrieval.py
      rag.py
      llm.py
      citations.py
      evaluation.py
```

## Local setup

### Windows / Git Bash

From the project folder:

```bash
py -3.12 -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

### Dense and hybrid retrieval

Dense and hybrid retrieval require additional dependencies:

```bash
python -m pip install -e .[dense]
```

## Create chunks

The project supports three chunking modes.

### Module-level chunks

One chunk corresponds to one complete module.

```bash
python -m modulehandbook_rag.cli ingest data/raw --out data/processed/chunks_module.jsonl --chunking module
```

### Field-level chunks

One chunk corresponds to one field within a module, for example contents, exam type or module coordinator.

```bash
python -m modulehandbook_rag.cli ingest data/raw --out data/processed/chunks_field.jsonl --chunking field
```

### Naive baseline chunks

The document is split into fixed-size text windows.

```bash
python -m modulehandbook_rag.cli ingest data/raw --out data/processed/chunks_naive.jsonl --chunking naive
```

## Search examples

Search returns the most relevant chunks for a query.

```bash
python -m modulehandbook_rag.cli search "Welche Prüfungsform hat WP3 Information Retrieval?" --chunks data/processed/chunks_field.jsonl --top-k 5
```

```bash
python -m modulehandbook_rag.cli search "Welche Inhalte behandelt P11 Informationsextraktion?" --chunks data/processed/chunks_field.jsonl --top-k 5
```

## Template-based QA

The command `ask` uses retrieved chunks and produces a fast grounded answer. This mode is useful for debugging because it makes it easy to check whether the correct chunk was retrieved.

```bash
python -m modulehandbook_rag.cli ask "Wie viele ECTS hat WP3 Information Retrieval?" --chunks data/processed/chunks_field.jsonl --top-k 1
```

```bash
python -m modulehandbook_rag.cli ask "Welche Prüfungsform hat WP3 Information Retrieval?" --chunks data/processed/chunks_field.jsonl --top-k 1
```

```bash
python -m modulehandbook_rag.cli ask "Wer ist modulverantwortlich für P10 Statistische Methoden in der Sprachverarbeitung?" --chunks data/processed/chunks_field.jsonl --top-k 1
```

## LLM-based RAG with Ollama

The command `ask-llm` is the actual LLM-based RAG mode.

It first retrieves relevant chunks from the module handbook, then passes them as context to a local language model via Ollama. The model is instructed to answer only from the retrieved context and not to add unsupported information.

The pipeline is:

```text
Question → retrieval over module-handbook chunks → context construction → LLM answer → source display
```

### Ollama setup

Install Ollama and download a local model:

```bash
ollama pull llama3.1:8b
```

For smaller machines, a smaller model can be used:

```bash
ollama pull llama3.2:3b
```

### LLM-RAG example: exam type

```bash
python -m modulehandbook_rag.cli ask-llm "Welche Prüfungsform hat WP3 Information Retrieval?" --chunks data/processed/chunks_field.jsonl --top-k 1 --model llama3.1:8b --temperature 0
```

Example output:

```text
Die Prüfungsform für WP3 Information Retrieval ist eine Hausarbeit (ca. 25 000 Zeichen) oder eine Programmieraufgabe (6 Wochen) mit einer anschließenden Präsentation (15-30 Minuten). (Quelle 1)

Gefundene Quellen:
- WP3 | Information Retrieval | Abschnitt: Form der Modulprüfung | Seite 33
```

### LLM-RAG example: ECTS

```bash
python -m modulehandbook_rag.cli ask-llm "Wie viele ECTS hat WP3 Information Retrieval?" --chunks data/processed/chunks_field.jsonl --top-k 1 --model llama3.1:8b --temperature 0
```

### LLM-RAG example: broader content question

```bash
python -m modulehandbook_rag.cli ask-llm "Welche Module behandeln maschinelles Lernen?" --chunks data/processed/chunks_field.jsonl --top-k 3 --model llama3.1:8b --temperature 0
```

### Smaller model option

`llama3.2:3b` is faster and easier to run locally, but may produce less complete answers than `llama3.1:8b`.

```bash
python -m modulehandbook_rag.cli ask-llm "Welche Prüfungsform hat WP3 Information Retrieval?" --chunks data/processed/chunks_field.jsonl --top-k 1 --model llama3.2:3b --temperature 0
```

## Dense and hybrid retrieval

After installing dense dependencies, dense retrieval can be used as follows:

```bash
python -m modulehandbook_rag.cli search "Welche Module behandeln Informationssuche?" --chunks data/processed/chunks_field.jsonl --retriever dense --top-k 5
```

Hybrid retrieval combines lexical and semantic retrieval:

```bash
python -m modulehandbook_rag.cli search "Welche Module behandeln Informationssuche?" --chunks data/processed/chunks_field.jsonl --retriever hybrid --top-k 5
```

## Evaluation

The project includes a small set of demo queries with relevance labels.

Evaluate BM25 on module-level chunks:

```bash
python -m modulehandbook_rag.cli evaluate --chunks data/processed/chunks_module.jsonl --retriever bm25 --top-k 3
```

Evaluate BM25 on field-level chunks:

```bash
python -m modulehandbook_rag.cli evaluate --chunks data/processed/chunks_field.jsonl --retriever bm25 --top-k 3
```

Run stricter evaluation requiring both the correct module and the correct section:

```bash
python -m modulehandbook_rag.cli evaluate --chunks data/processed/chunks_field.jsonl --retriever bm25 --top-k 3 --require-section
```

## Suggested experiments

The project can be used to compare different retrieval settings:

1. Naive chunks vs. module-level chunks vs. field-level chunks
2. BM25 vs. dense retrieval vs. hybrid retrieval
3. Template-based answers vs. LLM-based RAG answers
4. Short factual questions vs. broader content questions
5. German queries vs. optional English queries

A useful experimental setup for the seminar is:

```text
Data: university module handbook
Queries: questions about ECTS, exam type, contents, prerequisites and module coordinators
Chunking: naive, module-level, field-level
Retrieval: BM25, dense, hybrid
Metrics: Hit@1, Hit@3, MRR, optional nDCG
Demo: question → retrieved source → LLM answer with citation
```


## Notes

The system is designed for module handbooks with a semi-structured layout. It should transfer to other module handbooks if they contain similar fields such as module title, ECTS, contents, exam type and module coordinator. For strongly different layouts, scanned PDFs or documents without a text layer, the parser may need to be adapted.