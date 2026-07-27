"""Wrapper de embeddings locales (modelo configurable en src/config.py, GPU si
hay CUDA disponible)."""

import os

# Debe fijarse antes de importar sentence_transformers/transformers: sus barras
# tqdm rompen con OSError "Invalid argument" al hacer flush() en consolas
# mintty/Git Bash de Windows durante la carga de pesos del modelo.
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

# El modelo ya está en caché local — evita la llamada de red que hace
# sentence-transformers al Hub para chequear metadata. Esa llamada es la que
# crashea el proceso (access violation en WINHTTP.dll, ver Event Viewer:
# STATUS_ACCESS_VIOLATION 0xC0000005), probablemente por software de
# seguridad/VPN interceptando tráfico HTTPS de Windows.
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
