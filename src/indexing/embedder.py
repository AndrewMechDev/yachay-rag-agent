"""Wrapper de embeddings locales (modelo configurable en src/config.py, GPU si
hay CUDA disponible)."""

import os

# Debe fijarse antes de importar sentence_transformers/transformers: sus barras
# tqdm rompen con OSError "Invalid argument" al hacer flush() en consolas
# mintty/Git Bash de Windows durante la carga de pesos del modelo.
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

# NO forzar modo offline por defecto: en deploys sin build propio (Streamlit
# Community Cloud) el modelo nunca se cachea de antemano y necesita
# descargarse la primera vez que arranca la app. El crash de Windows
# (STATUS_ACCESS_VIOLATION 0xC0000005 en WINHTTP.dll) resultó ser un problema
# de threading (torch + chromadb fuera del hilo principal, ver
# src/engine_singleton.py), no de la llamada de red — por eso ya no hace falta
# este workaround. Si en algún entorno local se necesita forzar offline
# (modelo ya cacheado, sin salida a internet), setear YACHAY_EMBEDDER_OFFLINE=1.
if os.getenv("YACHAY_EMBEDDER_OFFLINE") == "1":
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

from typing import List

from loguru import logger
from sentence_transformers import SentenceTransformer
from transformers.utils import logging as hf_logging

from src.config import EMBEDDING_DIMENSION, EMBEDDING_MODEL

hf_logging.disable_progress_bar()

class LocalEmbedder:
    """Genera embeddings con el modelo local configurado. Mismo modelo para
    documentos y queries."""

    def __init__(self):
        logger.info(f"Cargando modelo de embeddings: {EMBEDDING_MODEL} (device=auto)")
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        logger.info(f"Modelo cargado. Dispositivo: {self.model.device}. Dimensión: {EMBEDDING_DIMENSION}")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Genera embeddings para una lista de textos (documentos/chunks)."""
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True,
            batch_size=32,
        )
        # Truncado defensivo a EMBEDDING_DIMENSION: no-op con el modelo actual
        # (su salida nativa ya es 384), pero deja la puerta abierta a modelos
        # Matryoshka (ej. bge-m3) que sí soportan truncar sin re-entrenar.
        return [emb[:EMBEDDING_DIMENSION].tolist() for emb in embeddings]

    def embed_query(self, query: str) -> List[float]:
        """Genera embedding para una pregunta de usuario."""
        embedding = self.model.encode(query, normalize_embeddings=True)
        return embedding[:EMBEDDING_DIMENSION].tolist()
