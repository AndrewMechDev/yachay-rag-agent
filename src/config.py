"""Configuración centralizada: variables de entorno, paths y constantes del proyecto."""

import os

# Debe fijarse antes de importar torch/chromadb: en Windows, torch (MKL/OpenMP)
# y chromadb (hnswlib, su propio runtime OpenMP) inicializan cada uno su copia
# del runtime en el mismo proceso y eso puede tumbar el proceso sin traceback
# de Python (el workaround estándar de Intel para este conflicto).
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

# Segunda guarda contra telemetria de ChromaDB (independiente del
# Settings(anonymized_telemetry=False) en vector_store.py): algunas versiones
# de chromadb/posthog leen esta variable de entorno como fallback. Reduce
# candidatos a llamadas de red durante el crash WinHTTP intermitente en Windows.
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# === LLM (generación) ===
# Se descartó OCI Generative AI: el registro de la cuenta gratuita de Oracle
# quedó bloqueado por su sistema antifraude (ver docs/sources.md). Se usa
# Groq en su lugar, vía su endpoint compatible con OpenAI — mismo cliente
# (src/generation/llm_client.py), solo cambian estas variables. Cualquier
# proveedor compatible con OpenAI (Gemini, OpenRouter, etc.) funciona igual
# sin tocar código, solo ajustando LLM_BASE_URL/LLM_CHAT_MODEL.
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
LLM_CHAT_MODEL = os.getenv("LLM_CHAT_MODEL", "llama-3.3-70b-versatile")
LLM_PROVIDER_NAME = os.getenv("LLM_PROVIDER_NAME", "Groq")

# === Embeddings ===
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1024"))

# === Chroma ===
CHROMA_PERSIST_DIR = BASE_DIR / os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "yachay_docs")

# === Aplicación ===
APP_NAME = os.getenv("APP_NAME", "YACHAY")
APP_PORT = int(os.getenv("APP_PORT", "8501"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = BASE_DIR / os.getenv("LOG_FILE", "./logs/yachay.jsonl")

# === Chunking ===
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "80"))

# === Retrieval ===
TOP_K_RETRIEVAL = int(os.getenv("TOP_K_RETRIEVAL", "10"))
TOP_K_RERANK = int(os.getenv("TOP_K_RERANK", "5"))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.35"))

# === Datos ===
DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_PROCESSED_DIR = BASE_DIR / "data" / "processed"

# === Categorías de negocio (detectadas por carpeta padre en data/raw/) ===
BUSINESS_CATEGORIES = {
    "rrhh": {
        "label": "Recursos Humanos",
        "owner": "Gerencia de RRHH",
        "description": "Políticas de personal, beneficios, onboarding, vacaciones",
    },
    "financiero": {
        "label": "Financiero",
        "owner": "Gerencia de Finanzas",
        "description": "Políticas de gastos, presupuestos, reembolsos, reportes",
    },
    "legal": {
        "label": "Legal",
        "owner": "Gerencia Legal",
        "description": "Políticas de privacidad, contratos, compliance, normativa",
    },
    "operacional": {
        "label": "Operacional",
        "owner": "Gerencia de Operaciones",
        "description": "Manuales de procesos, SLAs, guías de incidentes, procedimientos",
    },
}

# === Formatos soportados por el pipeline de ingestión ===
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".pptx", ".md", ".csv", ".json", ".html", ".txt"}
