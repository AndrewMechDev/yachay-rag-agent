"""Wrapper de embeddings locales (BAAI/bge-m3, GPU si hay CUDA disponible)."""

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

# Streamlit (`streamlit run`) ejecuta el script en su propio modelo de hilos
# (ScriptRunner); combinado con el contexto CUDA de PyTorch en Windows, eso
# corrompe memoria de forma intermitente (crashea en un DLL nativo distinto
# cada vez: WINHTTP.dll, arrow.dll — access violation 0xC0000005). Confirmado
# que NO ocurre fuera de Streamlit, ni con streamlit importado, solo con el
# server real corriendo. La app en vivo fuerza CPU para eliminar la clase de
# bug; la ingestión por CLI (scripts/ingest_documents.py) sigue en GPU.
_FORCE_CPU = os.getenv("YACHAY_FORCE_CPU_EMBEDDER") == "1"


class LocalEmbedder:
    """Genera embeddings con bge-m3 local. Mismo modelo para documentos y queries."""

    def __init__(self):
        device = "cpu" if _FORCE_CPU else None
        logger.info(f"Cargando modelo de embeddings: {EMBEDDING_MODEL} (device={device or 'auto'})")
        self.model = SentenceTransformer(EMBEDDING_MODEL, device=device)
        logger.info(f"Modelo cargado. Dispositivo: {self.model.device}. Dimensión: {EMBEDDING_DIMENSION}")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Genera embeddings para una lista de textos (documentos/chunks)."""
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True,
            batch_size=32,
        )
        # bge-m3 es Matryoshka: se puede truncar a EMBEDDING_DIMENSION sin re-entrenar.
        return [emb[:EMBEDDING_DIMENSION].tolist() for emb in embeddings]

    def embed_query(self, query: str) -> List[float]:
        """Genera embedding para una pregunta de usuario."""
        embedding = self.model.encode(query, normalize_embeddings=True)
        return embedding[:EMBEDDING_DIMENSION].tolist()
