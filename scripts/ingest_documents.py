"""CLI para ejecutar la ingestión completa.

Uso: python scripts/ingest_documents.py

Escanea data/raw/, extrae, limpia y chunkea los documentos, y guarda:
- data/catalog.json (catálogo de documentos con metadatos)
- data/processed/chunks.json (chunks listos para indexación en Fase 3)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.ingest.pipeline import run_ingestion_pipeline
from src.logging_config import setup_logging

if __name__ == "__main__":
    setup_logging()
    chunks = run_ingestion_pipeline()

    if not chunks:
        print("No se generaron chunks. Revisa data/raw/ y los logs.")
    else:
        print(f"Ingestión completa: {len(chunks)} chunks generados en data/processed/chunks.json")
        print("Siguiente paso (Fase 3): python scripts/... indexación en ChromaDB.")
