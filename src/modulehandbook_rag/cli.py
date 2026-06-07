from __future__ import annotations

from pathlib import Path
from typing import Literal

import typer
from rich.console import Console
from rich.panel import Panel

from .bm25_retrieval import BM25Retriever
from .chunking import make_chunks
from .citations import format_result
from .data_loader import load_documents
from .dense_retrieval import DenseRetriever
from .hybrid_retrieval import HybridRetriever
from .rag import answer_from_results
from .utils import read_jsonl, write_jsonl

app = typer.Typer(help="RAG-style search over university module handbooks.")
console = Console()


@app.command()
def ingest(
    input_path: Path = typer.Argument(..., help="PDF/TXT/MD file or directory."),
    out: Path = typer.Option(Path("data/processed/chunks.jsonl"), help="Output JSONL path."),
    chunking: Literal["naive", "module", "field"] = typer.Option("module", help="Chunking strategy."),
    chunk_size: int = typer.Option(900, help="Size for naive chunking."),
    overlap: int = typer.Option(120, help="Overlap for naive chunking."),
) -> None:
    docs = load_documents(input_path)
    chunks = make_chunks(docs, mode=chunking, chunk_size=chunk_size, overlap=overlap)
    write_jsonl(chunks, out)
    console.print(f"Loaded {len(docs)} document/page units.")
    console.print(f"Wrote {len(chunks)} chunks to [bold]{out}[/bold].")


@app.command()
def stats(
    chunks: Path = typer.Option(Path("data/processed/chunks.jsonl"), help="Chunks JSONL path."),
) -> None:
    chunk_list = read_jsonl(chunks)
    modules = sorted({c.module_code for c in chunk_list if c.module_code})
    console.print(f"Chunks: {len(chunk_list)}")
    console.print(f"Detected modules: {len(modules)}")
    if modules:
        console.print(", ".join(modules))


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query."),
    chunks: Path = typer.Option(Path("data/processed/chunks.jsonl"), help="Chunks JSONL path."),
    retriever: Literal["bm25", "dense", "hybrid"] = typer.Option("bm25", help="Retriever type."),
    top_k: int = typer.Option(5, help="Number of results."),
) -> None:
    chunk_list = read_jsonl(chunks)
    retr = _make_retriever(retriever, chunk_list)
    results = retr.search(query, top_k=top_k)
    for result in results:
        console.print(Panel(format_result(result), title=f"Treffer {result.rank}"))


@app.command()
def ask(
    query: str = typer.Argument(..., help="Question."),
    chunks: Path = typer.Option(Path("data/processed/chunks.jsonl"), help="Chunks JSONL path."),
    retriever: Literal["bm25", "dense", "hybrid"] = typer.Option("bm25", help="Retriever type."),
    top_k: int = typer.Option(5, help="Number of context chunks."),
) -> None:
    chunk_list = read_jsonl(chunks)
    retr = _make_retriever(retriever, chunk_list)
    results = retr.search(query, top_k=top_k)
    answer = answer_from_results(query, results)
    console.print(Panel(answer, title="Antwort"))


def _make_retriever(name: str, chunks):
    if name == "bm25":
        return BM25Retriever(chunks)
    if name == "dense":
        return DenseRetriever(chunks)
    if name == "hybrid":
        return HybridRetriever(chunks)
    raise ValueError(f"Unknown retriever: {name}")


if __name__ == "__main__":
    app()
