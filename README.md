# YACHAY

> **YACHAY** (quechua: *conocimiento, saber*) — Agente RAG corporativo que responde preguntas de colaboradores a partir de documentos internos, desplegado sobre Oracle Cloud Infrastructure.

## Qué es

YACHAY busca en documentos internos (políticas, manuales, procedimientos), recupera los fragmentos relevantes y genera una respuesta citando la fuente exacta. Si no encuentra información suficiente, lo dice explícitamente en vez de inventar.

## Stack

- Python 3.11.9
- LlamaIndex + ChromaDB (vector store local)
- Embeddings: `BAAI/bge-m3` (local, GPU CUDA)
- LLM: OCI Generative AI (`meta.llama-3.3-70b-instruct`)
- UI: Streamlit
- Deploy: Docker + OCI Compute

## Setup local

```bash
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
pip install -r requirements.txt
copy .env.example .env
# Editar .env con tu API Key de OCI GenAI
```

## Uso

```bash
python scripts/ingest_documents.py
python scripts/test_query.py "¿Cuántos días de vacaciones tengo si llevo 3 años?"
streamlit run app/app.py
```

## Estructura

Ver `yachay-execution-guide.md` sección 2 para el detalle completo del repositorio.

## Documentos fuente

16 documentos `.md` en `data/raw/` organizados en `rrhh/`, `financiero/`, `legal/`, `operacional/`, sobre una empresa ficticia (NovaTech Perú S.A.C.) con contexto peruano real (Ley 29733, D.S. 003-97-TR, EsSalud, etc.).
