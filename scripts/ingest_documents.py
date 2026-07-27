"""CLI para ejecutar la ingestión e indexación completa.

Uso: python scripts/ingest_documents.py

1. Ingestión: escanea data/raw/, extrae, limpia y chunkea los documentos.
2. Indexación: genera embeddings (bge-m3) y los inserta en ChromaDB.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.indexing.indexer import run_indexing_pipeline
from src.ingest.pipeline import run_ingestion_pipeline
from src.logging_config import setup_logging


def main():
    setup_logging()

    print("=" * 60)
    print("YACHAY — Ingestión e indexación de documentos")
    print("=" * 60)

    chunks = run_ingestion_pipeline()
    if not chunks:
        print("No se generaron chunks. Verifica los documentos en data/raw/")
        sys.exit(1)

    print(f"\nIngestión completa: {len(chunks)} chunks generados")

    run_indexing_pipeline(chunks)

    print("\nIndexación completa. El agente está listo para recibir preguntas.")
    print("Siguiente paso (Fase 4): retrieval + generación con OCI GenAI.")


if __name__ == "__main__":
    main()
