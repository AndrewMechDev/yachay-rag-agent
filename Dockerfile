FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-spa \
    libgl1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Hornea el modelo de embeddings en la imagen (evita descargarlo en cada
# arranque del contenedor). Usa EMBEDDING_MODEL de src/config.py para no
# desalinearse si cambia el modelo por defecto.
RUN python -c "from src.config import EMBEDDING_MODEL; from sentence_transformers import SentenceTransformer; SentenceTransformer(EMBEDDING_MODEL)"

# Ingestion + indexacion en build time: data/raw/ (16 .md) esta versionado en
# git, chroma_db/ y data/processed/ estan gitignored (son artefactos
# generados), asi que se construyen aqui y quedan horneados en la imagen. No
# hay Object Storage ni disco persistente en este deploy: si se agregan
# documentos nuevos, hay que reconstruir y volver a desplegar la imagen.
RUN python scripts/ingest_documents.py

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8501}/_stcore/health || exit 1

# $PORT lo inyectan Render/Railway/Fly en runtime; Hugging Face Spaces usa
# 7860 fijo (se configura via variable de entorno PORT=7860 en el Space).
CMD ["sh", "-c", "python run_app.py --server.port=${PORT:-8501} --server.address=0.0.0.0 --server.headless=true"]
