# YACHAY

> **YACHAY** (quechua: *conocimiento, saber*) — Agente RAG corporativo que responde preguntas de colaboradores a partir de documentos internos.

## Qué es

YACHAY busca en documentos internos (políticas, manuales, procedimientos), recupera los fragmentos relevantes y genera una respuesta citando la fuente exacta. Si no encuentra información suficiente, lo dice explícitamente en vez de inventar.

## Stack

- Python 3.11.9
- LlamaIndex + ChromaDB (vector store local)
- Embeddings: `paraphrase-multilingual-MiniLM-L12-v2` (local, ~470MB — elegido por el límite de RAM de Streamlit Community Cloud; localmente con GPU/más RAM se puede usar `BAAI/bge-m3` para mejor calidad, ver `.env.example`)
- LLM: Groq (`llama-3.3-70b-versatile`) vía endpoint compatible con OpenAI — se descartó OCI Generative AI por bloqueos del antifraude en el registro de cuenta gratuita de Oracle (ver `docs/sources.md`)
- UI: Streamlit
- Deploy: Streamlit Community Cloud — se descartó Hugging Face Spaces porque en julio 2026 movieron Docker/Gradio Spaces detrás de una suscripción PRO de pago sin aviso previo (ver `docs/sources.md`)

## Setup local

```bash
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
pip install -r requirements.txt
copy .env.example .env
# Editar .env con tu API Key de Groq (opcional, ver más abajo) — gratis en https://console.groq.com/keys
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

## Cómo probarlo ya mismo (sin API key de LLM)

El pipeline de ingestión, indexación y retrieval **no depende de ningún LLM**:
solo la generación de la respuesta final lo necesita. Mientras no tengas
`LLM_API_KEY` configurada (o el placeholder de `.env.example` siga tal cual),
el sistema usa automáticamente un `MockLLMClient` que **no inventa texto**: te
devuelve exactamente los fragmentos recuperados con su fuente y score, para
que puedas validar que el retrieval funciona.

1. Verifica que ya corriste la ingestión al menos una vez (genera `chroma_db/`):
   ```bash
   python scripts/ingest_documents.py
   ```
2. Prueba una pregunta desde la terminal, sin interfaz:
   ```bash
   python scripts/test_query.py "¿Cuál es el límite de gastos de transporte?"
   ```
   Vas a ver en la respuesta el prefijo `[MODO MOCK — sin conexión al LLM...]`
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
4. **Cuando tengas tu API Key de Groq** (gratis, sin tarjeta, en
   [console.groq.com/keys](https://console.groq.com/keys)): solo edítala en
   `.env` (`LLM_API_KEY=...`). No hay que tocar código ni reiniciar nada más
   que el proceso — `get_llm_client()` detecta la key real y cambia
   automáticamente de `MockLLMClient` a `RemoteLLMClient`.

Preguntas de ejemplo para probar (ya validadas contra los documentos reales):
- "¿Cuántos días de vacaciones tengo si llevo 3 años?"
- "¿Cuál es el límite de gastos de transporte?"
- "¿Cómo reporto un incidente P1?"
- "¿Cuál es la receta del ceviche?" (pregunta fuera de dominio, para ver cómo reacciona el sistema)

## Deploy (Streamlit Community Cloud)

Se descartó Hugging Face Spaces: desde julio 2026 exige suscripción **PRO** de
pago para crear Spaces con Docker o Gradio (solo dejan gratis los Spaces
"Static", sin backend Python — ver `docs/sources.md`). El deploy usa
**Streamlit Community Cloud**, el hosting oficial de Streamlit: gratis, sin
tarjeta nunca, se conecta directo a GitHub y no necesita Dockerfile (Community
Cloud arma el entorno solo con `requirements.txt` y `packages.txt`).

Su límite de RAM es ajustado (~1-2.7GB), por eso el modelo de embeddings se
cambió de `bge-m3` (2.2GB) a `paraphrase-multilingual-MiniLM-L12-v2` (~470MB).
Como esta plataforma no tiene un paso de build propio (a diferencia del
`Dockerfile`) y su disco es efímero, la app corre la ingestión + indexación
automáticamente en el primer arranque si detecta el vector store vacío (ver
`src/engine_singleton.py`); `data/raw/` (16 `.md`) está versionado en git, así
que siempre tiene datos con qué trabajar.

1. Sube este repo a GitHub (público, requerido para el tier gratuito) si aún
   no está ahí.
2. Crea cuenta en [share.streamlit.io](https://share.streamlit.io) con tu
   cuenta de GitHub (sin tarjeta).
3. Click en **"Create app"** → conecta el repo, rama `main`, archivo principal
   `app/app.py`.
4. Antes de desplegar, abre **"Advanced settings"** y pega en el campo
   **Secrets** (formato TOML):
   ```toml
   LLM_API_KEY = "tu_api_key_de_groq"
   LLM_CHAT_MODEL = "llama-3.3-70b-versatile"
   LLM_BASE_URL = "https://api.groq.com/openai/v1"
   LLM_PROVIDER_NAME = "Groq"
   EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
   EMBEDDING_DIMENSION = "384"
   ```
   (Streamlit expone cada clave de nivel raíz como variable de entorno, que es
   justo lo que lee `src/config.py` vía `os.getenv()` — no hace falta tocar código).
5. Click **Deploy**. La primera vez tarda varios minutos: instala dependencias,
   descarga el modelo de embeddings y corre la ingestión/indexación automática.
   Sigue el progreso en los logs dentro de la misma página.
6. Cuando termine, la app queda pública en `https://<algo>.streamlit.app`.

Si el disco se reinicia (redeploy, o la app "duerme" tras 12h sin visitas y
despierta), el chequeo de vector store vacío en `src/engine_singleton.py`
vuelve a correr la ingestión automáticamente — no requiere intervención manual.

## Estructura

Ver `yachay-execution-guide.md` sección 2 para el detalle completo del repositorio.
Mapeo de fuentes, categorías y ownership de documentos: `docs/sources.md`.

## Documentos fuente

16 documentos `.md` en `data/raw/` organizados en `rrhh/`, `financiero/`, `legal/`, `operacional/`, sobre una empresa ficticia (NovaTech Perú S.A.C.) con contexto peruano real (Ley 29733, D.S. 003-97-TR, EsSalud, etc.).
