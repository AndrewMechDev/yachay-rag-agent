"""Pipeline de indexación: chunks procesados → embeddings → ChromaDB."""

import json
from typing import Any, Dict, List, Optional

from loguru import logger

from src.config import DATA_PROCESSED_DIR
from src.indexing.embedder import LocalEmbedder
from src.indexing.vector_store import ChromaVectorStore


def run_indexing_pipeline(chunks: Optional[List[Dict[str, Any]]] = None) -> None:
    """Indexa chunks en el vector store. Si no se pasan, los carga de data/processed/chunks.json."""
    logger.info("=" * 60)
    logger.info("YACHAY — Iniciando pipeline de indexación")
    logger.info("=" * 60)

    if chunks is None:
        chunks_path = DATA_PROCESSED_DIR / "chunks.json"
        if not chunks_path.exists():
            logger.error("No hay chunks procesados. Ejecuta primero la ingestión.")
            return
        with open(chunks_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)

    if not chunks:
        logger.error("No hay chunks para indexar.")
        return

    logger.info(f"Chunks a indexar: {len(chunks)}")

    embedder = LocalEmbedder()
    vector_store = ChromaVectorStore()

    ids = [c["chunk_id"] for c in chunks]
    texts = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    logger.info("Generando embeddings (esto puede tomar unos minutos)...")
    embeddings = embedder.embed_texts(texts)
    logger.info(f"Embeddings generados: {len(embeddings)} vectores de dim {len(embeddings[0])}")

    vector_store.add_documents(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)

    logger.info(f"Indexación completa. Total en vector store: {vector_store.count()}")
