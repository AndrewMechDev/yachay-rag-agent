# YACHAY

> **YACHAY** (quechua: *conocimiento, saber*) — Asistente de IA que responde preguntas sobre documentos internos de la empresa, citando siempre la fuente.

## Probarlo ahora (demo en vivo)

La app está desplegada en Streamlit Community Cloud. Ábrela en el navegador (sin instalar nada):

**[Abrir YACHAY en Streamlit](https://yachay-rag-agent-gzjptpjs6mjpqz5454zbrs.streamlit.app/)**

> La primera carga puede tardar unos segundos (la app “despierta” si estuvo inactiva).

---

## ¿Para qué sirve?

Imagina que un colaborador pregunta:

- *¿Cuántos días de vacaciones me corresponden?*
- *¿Cómo reporto un gasto?*
- *¿Qué dice la política de privacidad?*

En vez de buscar en PDFs o preguntar a RRHH/Legal, **YACHAY busca en los documentos internos**, encuentra el fragmento relevante y responde **con la cita del archivo y la sección**.

Si no hay información suficiente en los documentos, **lo dice claramente** (no inventa).

---

## Qué puedes hacer con la app

- Chatear en lenguaje natural sobre políticas y procesos
- Filtrar por área: RRHH, Financiero, Legal u Operacional
- Ver **preguntas sugeridas** según el área que elijas (en el menú lateral)
- Leer el objetivo en **¿Qué es YACHAY?** (para quién es: colaborador vs RRHH/Legal)
- Seguir los **3 pasos** del header: área → pregunta → fuentes citadas
- Revisar las **fuentes consultadas** de cada respuesta
- Dar feedback 👍 / 👎 a las respuestas
- Presentar el agente con el guion de ~2 min: [`docs/guion-demo.md`](docs/guion-demo.md)

---

## Cómo funciona (en simple)

1. **Ingesta**: lee los documentos de `data/raw/`
2. **Indexación**: los convierte en “vectores” y los guarda en ChromaDB
3. **Búsqueda**: cuando preguntas, encuentra los trozos más parecidos
4. **Respuesta**: un LLM (Groq) redacta la respuesta **solo** con esos trozos y cita la fuente

Atajos útiles:
- Saludos tipo “hola” / “gracias” se responden sin llamar al LLM (ahorra tokens)
- Preguntas fuera de tema (ej. “receta de ceviche”) no inventan: avisan que no hay información

---

## Tecnologías

| Pieza | Qué usamos |
|---|---|
| Lenguaje | Python 3.11 |
| Interfaz | Streamlit |
| Búsqueda semántica | LlamaIndex + ChromaDB |
| Embeddings (local) | `paraphrase-multilingual-MiniLM-L12-v2` (~470 MB) |
| LLM | Groq — Llama 3.3 70B |
| Deploy | Streamlit Community Cloud (gratis) |

> **Nota:** se descartó OCI Generative AI (problemas al crear cuenta Free Tier) y Hugging Face Spaces Docker (desde julio 2026 exige plan PRO de pago). Detalle en `docs/sources.md`.

---

## Setup local (Windows)

```powershell
# 1. Crear entorno virtual
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Instalar PyTorch (ajusta cu124 si no tienes GPU NVIDIA)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# 3. Instalar el resto
pip install -r requirements.txt

# 4. Configurar variables
copy .env.example .env
# Edita .env y pega tu API Key de Groq (gratis en https://console.groq.com/keys)
```

---

## Cómo usarlo

### 1. Indexar los documentos (solo la primera vez, o si cambias archivos)

```powershell
python scripts/ingest_documents.py
```

### 2. Probar una pregunta en terminal

```powershell
python scripts/test_query.py "¿Cuántos días de vacaciones tengo si llevo 3 años?"
```

### 3. Abrir la interfaz de chat

```powershell
python run_app.py
```

Abre [http://localhost:8501](http://localhost:8501).

> **Importante en Windows:** usa `python run_app.py`, **no** `streamlit run app/app.py`.
> En Windows, cargar torch + ChromaDB desde el hilo de Streamlit puede cerrar el proceso.
> `run_app.py` precarga el motor en el hilo principal. En Linux/macOS ambas formas funcionan.

---

## Probar sin API key de Groq

Si aún no tienes `LLM_API_KEY`, la app entra en **modo simulado**:
- La búsqueda (retrieval) sigue funcionando con tus documentos
- La “respuesta” muestra los fragmentos encontrados con su score
- Verás el badge: *Modo simulado — sin conexión al LLM*

Cuando pongas tu key en `.env` y reinicies, pasa solo a respuestas reales con Groq.

Preguntas de ejemplo:

- ¿Cuántos días de vacaciones tengo si llevo 3 años?
- ¿Cuál es el límite de gastos de transporte?
- ¿Cómo reporto un incidente P1?
- ¿Cuál es la receta del ceviche? ← fuera de dominio (debe decir que no sabe)

---

## Deploy en Streamlit Community Cloud

Demo pública actual:
[https://yachay-rag-agent-gzjptpjs6mjpqz5454zbrs.streamlit.app/](https://yachay-rag-agent-gzjptpjs6mjpqz5454zbrs.streamlit.app/)

1. Sube el repo a GitHub (público, para el plan gratis).
2. Entra a [share.streamlit.io](https://share.streamlit.io) con GitHub.
3. **Create app** → repo, rama `main`, archivo principal: `app/app.py`.
4. En **Advanced settings → Secrets**, pega:

```toml
LLM_API_KEY = "tu_api_key_de_groq"
LLM_CHAT_MODEL = "llama-3.3-70b-versatile"
LLM_BASE_URL = "https://api.groq.com/openai/v1"
LLM_PROVIDER_NAME = "Groq"
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DIMENSION = "384"
```

5. **Deploy**. La primera vez tarda unos minutos (instala deps, descarga el modelo e indexa los documentos).

La URL queda tipo `https://<algo>.streamlit.app`.

Si el disco se limpia (la app “duerme” tras ~12 h sin visitas), al despertar **reingesta sola** si el vector store está vacío.

---

## Documentos incluidos

16 archivos `.md` de ejemplo (empresa ficticia **NovaTech Perú S.A.C.**) en:

```
data/raw/
  rrhh/
  financiero/
  legal/
  operacional/
```

Contexto peruano real (Ley 29733, D.S. 003-97-TR, EsSalud, etc.).

- Mapa de fuentes y decisiones: [`docs/sources.md`](docs/sources.md)
- Guion para presentar el agente (~2 min): [`docs/guion-demo.md`](docs/guion-demo.md)

---

## Estructura del proyecto (resumen)

| Carpeta / archivo | Rol |
|---|---|
| `app/app.py` | Interfaz Streamlit |
| `app/static/` | Logo (búho), avatares |
| `src/ingest/` | Lectura y chunking de documentos |
| `src/indexing/` | Embeddings + ChromaDB |
| `src/retrieval/` | Búsqueda semántica |
| `src/generation/` | LLM, prompts, small talk, validación |
| `src/rag_engine.py` | Orquestador del pipeline |
| `data/raw/` | Documentos fuente |
| `scripts/` | Ingesta y pruebas por CLI |

---

## Licencia / notas

Proyecto de demostración académica / portfolio. Las respuestas del agente **no sustituyen** la validación con el área responsable antes de decisiones críticas.
