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
# Editar .env con tu API Key de OCI GenAI (opcional, ver más abajo)
```

## Uso

```bash
python scripts/ingest_documents.py
python scripts/test_query.py "¿Cuántos días de vacaciones tengo si llevo 3 años?"
python run_app.py
```

> **Windows**: usa `python run_app.py`, **no** `streamlit run app/app.py` directamente.
> Este entrypoint pre-carga el RAG Engine (torch + chromadb) en el hilo principal
> antes de arrancar Streamlit. Es necesario porque, en Windows, torch y chromadb
> juntos crashean el proceso (`STATUS_ACCESS_VIOLATION 0xC0000005` en `WINHTTP.dll`)
> si se inicializan desde el hilo secundario donde Streamlit ejecuta el script
> ("ScriptRunner"). Ver `src/engine_singleton.py` para el diagnóstico completo.
> En Linux/macOS ambas formas funcionan igual.

## Cómo probarlo ya mismo (sin cuenta OCI)

El pipeline de ingestión, indexación y retrieval **no depende de OCI**: solo la
generación de la respuesta final necesita el LLM. Mientras no tengas
`OCI_GENAI_API_KEY` configurada (o el placeholder de `.env.example` siga tal
cual), el sistema usa automáticamente un `MockLLMClient` que **no inventa
texto**: te devuelve exactamente los fragmentos recuperados con su fuente y
score, para que puedas validar que el retrieval funciona.

1. Verifica que ya corriste la ingestión al menos una vez (genera `chroma_db/`):
   ```bash
   python scripts/ingest_documents.py
   ```
2. Prueba una pregunta desde la terminal, sin interfaz:
   ```bash
   python scripts/test_query.py "¿Cuál es el límite de gastos de transporte?"
   ```
   Vas a ver en la respuesta el prefijo `[MODO MOCK — sin conexión a OCI GenAI...]`
   seguido del contexto real recuperado (archivo, sección, score). Eso confirma
   que el buscador semántico está funcionando correctamente sobre tus 16
   documentos.
3. Pruébalo con interfaz de chat completa:
   ```bash
   python run_app.py
   ```
   Se abre en `http://localhost:8501`. Ahí puedes chatear, filtrar por categoría
   (RRHH/Financiero/Legal/Operacional), ver las fuentes citadas por respuesta y
   dar feedback 👍/👎.
4. **Cuando tengas la API Key de OCI GenAI**: solo edítala en `.env`
   (`OCI_GENAI_API_KEY=...`). No hay que tocar código ni reiniciar nada más que
   el proceso — `get_llm_client()` detecta la key real y cambia automáticamente
   de `MockLLMClient` a `OCIGenAIClient`.

Preguntas de ejemplo para probar (ya validadas contra los documentos reales):
- "¿Cuántos días de vacaciones tengo si llevo 3 años?"
- "¿Cuál es el límite de gastos de transporte?"
- "¿Cómo reporto un incidente P1?"
- "¿Cuál es la receta del ceviche?" (pregunta fuera de dominio, para ver cómo reacciona el sistema)

## Estructura

Ver `yachay-execution-guide.md` sección 2 para el detalle completo del repositorio.
Mapeo de fuentes, categorías y ownership de documentos: `docs/sources.md`.

## Documentos fuente

16 documentos `.md` en `data/raw/` organizados en `rrhh/`, `financiero/`, `legal/`, `operacional/`, sobre una empresa ficticia (NovaTech Perú S.A.C.) con contexto peruano real (Ley 29733, D.S. 003-97-TR, EsSalud, etc.).
