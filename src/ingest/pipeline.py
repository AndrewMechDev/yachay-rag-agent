"""Pipeline de ingestión: escanear → extraer → limpiar → chunk → guardar."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from loguru import logger

from src.config import BUSINESS_CATEGORIES, DATA_PROCESSED_DIR, DATA_RAW_DIR, SUPPORTED_EXTENSIONS
from src.ingest.chunker import chunk_text
from src.ingest.cleaner import clean_text
from src.ingest.extractors import extract_file

MIN_WORDS_PER_SEGMENT = 10


def detect_category(file_path: Path) -> str:
    """Detecta la categoría de negocio a partir de la carpeta padre del archivo."""
    parent = file_path.parent.name.lower()
    for cat_key in BUSINESS_CATEGORIES:
        if cat_key in parent:
            return cat_key
    return "general"


def scan_documents(base_dir: Path = DATA_RAW_DIR) -> List[Path]:
    """Escanea recursivamente `data/raw/` en busca de formatos soportados."""
    files: List[Path] = []
    for ext in SUPPORTED_EXTENSIONS:
        files.extend(base_dir.rglob(f"*{ext}"))
    files.sort()
    logger.info(f"Documentos encontrados: {len(files)}")
    return files


def build_catalog(files: List[Path]) -> List[Dict[str, Any]]:
    """Construye el catálogo de documentos con metadatos de categoría y ownership."""
    catalog = []
    for f in files:
        category = detect_category(f)
        catalog.append(
            {
                "file": f.name,
                "path": str(f.relative_to(DATA_RAW_DIR)),
                "format": f.suffix.lower(),
                "category": category,
                "category_label": BUSINESS_CATEGORIES.get(category, {}).get("label", "General"),
                "owner": BUSINESS_CATEGORIES.get(category, {}).get("owner", "Sin asignar"),
                "size_kb": round(f.stat().st_size / 1024, 1),
                "last_modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                "ingested_at": datetime.now().isoformat(),
            }
        )
    return catalog


def run_ingestion_pipeline() -> List[Dict[str, Any]]:
    """Ejecuta el pipeline completo y devuelve todos los chunks procesados con metadatos."""
    logger.info("=" * 60)
    logger.info("YACHAY — Iniciando pipeline de ingestión")
    logger.info("=" * 60)

    files = scan_documents()
    if not files:
        logger.error(f"No se encontraron documentos en {DATA_RAW_DIR}")
        return []

    catalog = build_catalog(files)
    catalog_path = DATA_RAW_DIR.parent / "catalog.json"
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    logger.info(f"Catálogo guardado: {catalog_path} ({len(catalog)} documentos)")

    all_chunks: List[Dict[str, Any]] = []
    stats = {"total_files": len(files), "success": 0, "failed": 0, "total_chunks": 0}

    for file_path in files:
        try:
            category = detect_category(file_path)
            logger.info(f"Procesando: {file_path.name} (categoría: {category})")

            raw_segments = extract_file(file_path)

            for segment in raw_segments:
                cleaned = clean_text(segment["text"])
                if len(cleaned.split()) < MIN_WORDS_PER_SEGMENT:
                    continue

                chunks = chunk_text(text=cleaned, metadata=segment["metadata"], category=category)
                all_chunks.extend(chunks)

            stats["success"] += 1
            logger.info(f"  → {len(raw_segments)} segmentos extraídos")

        except Exception as e:
            stats["failed"] += 1
            logger.error(f"Error procesando {file_path.name}: {e}")

    stats["total_chunks"] = len(all_chunks)

    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    chunks_path = DATA_PROCESSED_DIR / "chunks.json"
    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    logger.info("=" * 60)
    logger.info(f"Ingestión completa: {stats}")
    logger.info(f"Chunks guardados: {chunks_path}")
    logger.info("=" * 60)

    return all_chunks
