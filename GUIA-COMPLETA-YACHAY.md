# YACHAY — Guía Completa: Preguntas, Costos, Setup y Hardware

---

## 1. ¿QUÉ ES YACHAY?

**YACHAY** (palabra quechua que significa *"conocimiento"*, *"saber"*, *"aprender"*) es un **agente de inteligencia artificial tipo RAG** (Retrieval-Augmented Generation) diseñado para funcionar como el **asistente de conocimiento interno de una empresa**.

### ¿Qué problema resuelve?

En empresas medianas y grandes, los colaboradores pierden un promedio de **1.8 horas al día** (casi el 20% de su jornada laboral) buscando información interna: políticas de vacaciones, procesos de reembolso, normas de seguridad, protocolos de incidentes, etc. Esa información existe, pero está dispersa en PDFs, documentos de Word, presentaciones, hojas de cálculo, y carpetas compartidas que nadie encuentra a tiempo.

YACHAY resuelve esto. Un colaborador escribe una pregunta en lenguaje natural — por ejemplo: *"¿Cuántos días de vacaciones me corresponden si llevo 3 años?"* — y el agente:

1. Busca en los documentos internos indexados.
2. Encuentra los fragmentos más relevantes.
3. Genera una respuesta clara citando la fuente exacta (archivo, página, sección).
4. Si no encuentra información suficiente, lo dice explícitamente en vez de inventar.

### ¿A quién va enfocado?

- Empresas medianas y grandes (100+ colaboradores) con documentación interna dispersa.
- Áreas de RRHH, Legal, Finanzas y Operaciones que reciben preguntas repetitivas.
- Organizaciones que ya usan Oracle Cloud Infrastructure (OCI) como proveedor de nube.
- Sectores regulados (banca, seguros, salud, minería) donde la trazabilidad de respuestas es crítica.

### ¿Qué NO es YACHAY?

- No es un chatbot genérico tipo ChatGPT. YACHAY solo responde con información de los documentos que tú le des.
- No es un buscador. No "googlea" internet. Trabaja exclusivamente con la base de conocimiento interna.
- No inventa. Si no tiene la respuesta, lo dice.

---

## 2. ¿TODO ES GRATUITO? (Análisis de costos para presupuesto cero)

### Respuesta corta: SÍ, todo lo que usas puede ser gratuito o de código abierto.

### Desglose completo:

| Componente | ¿Es gratis? | Detalle |
|---|---|---|
| **Python 3.11** | ✅ 100% gratis | Open source, descarga libre |
| **Todas las librerías Python** (LlamaIndex, Chroma, sentence-transformers, Streamlit, etc.) | ✅ 100% gratis | Todas son open source (licencias MIT/Apache/BSD) |
| **Modelo de embeddings (BAAI/bge-m3)** | ✅ 100% gratis | Open source, corre en tu laptop, no requiere API key ni pago |
| **ChromaDB (base vectorial)** | ✅ 100% gratis | Open source, embebida, corre local |
| **Streamlit (interfaz web)** | ✅ 100% gratis | Open source |
| **Docker** | ✅ 100% gratis | Docker Desktop es gratis para uso personal/educativo |
| **Git + GitHub** | ✅ 100% gratis | Repos públicos son gratis |
| **OCI Generative AI (LLM)** | ⚠️ **Depende** | Ver nota abajo |
| **OCI Compute (VM)** | ✅ Gratis con **Always Free tier** | 2 OCPU / 12 GB RAM (Ampere A1) — suficiente para este proyecto |
| **OCI Object Storage** | ✅ Gratis con **Always Free tier** | 20 GB de almacenamiento de objetos gratis |
| **OCI Vault** | ✅ Gratis con **Always Free tier** | 20 secretos / 150 operaciones por segundo gratis |
| **OCI Logging** | ✅ Gratis con **Always Free tier** | 10 GB de ingestión de logs/mes gratis |
| **OCI Container Registry** | ✅ Gratis con **Always Free tier** | 500 MB gratis |
| **PyTorch (para embeddings locales)** | ✅ 100% gratis | Open source |

### ⚠️ Nota sobre OCI Generative AI (el LLM):

Cuando creas una cuenta de OCI, recibes **US$ 300 de créditos gratuitos por 30 días** (trial). Esos créditos cubren OCI Generative AI, Compute pagado, y todos los servicios de pago. Para este proyecto de 2 días, esos créditos son MÁS que suficientes.

Después del trial, OCI Generative AI tiene un costo por token/carácter, pero es bajo para un proyecto demo. Los modelos como `meta.llama-3.3-70b-instruct` en OCI cobran por carácter de entrada y salida. Para el uso del challenge (unas pocas decenas de preguntas de prueba), el costo sería de centavos de dólar.

**Estrategia para $0:**
1. Crear cuenta OCI con los US$ 300 de trial.
2. Usar Always Free tier para Compute, Object Storage, Vault, Logging.
3. Usar OCI GenAI con los créditos trial para las llamadas al LLM.
4. Los embeddings, el vector store, la interfaz — TODO corre local y es gratis.

**El 90%+ del proyecto es completamente gratuito. El único servicio con costo potencial (OCI GenAI) está cubierto por los créditos trial.**

---

## 3. ¿QUÉ FRAMEWORK SE USA? ¿FastAPI? ¿Django? ¿Python nativo?

### Respuesta directa: NO usas FastAPI ni Django. Usas Streamlit, y TODO es Python.

Déjame explicar por qué:

| Framework | ¿Qué hace? | ¿Se usa en YACHAY? | ¿Por qué? |
|---|---|---|---|
| **FastAPI** | Framework para crear APIs REST (backend web) | ❌ **No** | No necesitas una API REST separada. Streamlit ya tiene backend integrado. Usarlo añadiría complejidad sin beneficio en 2 días. |
| **Django** | Framework web completo (backend + frontend) | ❌ **No** | Es demasiado pesado para un chat simple. Tardarías más configurando Django que construyendo el RAG. |
| **Flask** | Framework web ligero | ❌ **No** | Misma razón que FastAPI: innecesario cuando tienes Streamlit. |
| **Streamlit** | Framework para crear apps web interactivas con SOLO Python | ✅ **SÍ** | Es el que usas. Escribes Python puro y Streamlit genera la interfaz web automáticamente. Sin HTML, sin CSS, sin JavaScript. |

### ¿Cómo funciona Streamlit?

Streamlit es el "frontend" y el "backend" al mismo tiempo. Escribes un archivo Python (`app.py`) con código como:

```python
import streamlit as st

st.title("YACHAY")
pregunta = st.chat_input("Escribe tu pregunta...")
if pregunta:
    respuesta = mi_rag_engine.ask(pregunta)
    st.write(respuesta)
```

Y Streamlit convierte eso en una aplicación web completa con chat, botones, gráficos — todo accesible desde el navegador en `http://localhost:8501`. No necesitas escribir HTML, CSS ni JavaScript.

### ¿Todo se trabaja en un solo lenguaje?

**SÍ. Todo el proyecto es 100% Python.** No hay frontend separado en JavaScript/React/Vue/Angular. No hay backend separado. Todo está en Python:

- La lógica de extracción de documentos → Python
- Los embeddings → Python (sentence-transformers)
- El vector store → Python (chromadb)
- La conexión al LLM (OCI GenAI) → Python (openai SDK)
- La interfaz web → Python (streamlit)
- El deploy → Dockerfile (empaqueta todo el Python)

No vas a tocar ni una línea de otro lenguaje. Solo Python.

---

## 4. ¿QUÉ VERSIÓN EXACTA DE PYTHON?

### Recomendación: **Python 3.11.9** (2 de abril de 2024)

⚠️ **Corrección importante**: en versiones anteriores de esta guía se recomendaba 3.11.12. Eso fue un error — **3.11.9 es la versión correcta a instalar**, y aquí está el porqué.

Python 3.11 entró en fase de "solo correcciones de seguridad" (según el PEP 664). Desde esa fase, Python.org deja de publicar **instaladores binarios (.exe)** para versiones nuevas de la rama — solo publican el código fuente para quien quiera compilarlo manualmente. **3.11.9 fue la última versión de 3.11 con instalador de Windows disponible.** Las versiones posteriores (3.11.10, 3.11.11, 3.11.12, 3.11.13, 3.11.14, 3.11.15) son parches de seguridad sin instalador — por eso no aparecen para descargar en Windows.

| Versión | Veredicto |
|---|---|
| **3.11.9 (Abr 2024)** | ✅ **Recomendada.** Última versión de 3.11 con instalador de Windows. Estable, todos los paquetes tienen wheels precompilados. |
| 3.11.10 en adelante | Solo código fuente, sin instalador de Windows. No usar a menos que compiles Python tú mismo (innecesario para este proyecto). |

### ¿Por qué 3.11 y no 3.12 o 3.14?

- **Python 3.11** tiene la mejor compatibilidad con PyTorch, sentence-transformers, y las librerías de extracción de documentos. Todos los paquetes están probados y optimizados para esta versión.
- **Python 3.12/3.13/3.14** cambiaron algunas cosas internas (GIL, subinterpreters, distutils removido) que causan problemas con paquetes C como PyMuPDF, pytesseract, y algunas versiones de torch. No vale la pena arriesgarse en un proyecto de 2 días.

### Instalación

```bash
# En Windows (descarga desde python.org):
# https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
# IMPORTANTE: marca la casilla "Add python.exe to PATH" durante la instalación

# Verificar:
python --version
# Debe mostrar: Python 3.11.9
```

### ⚠️ Si ya tienes otras versiones instaladas (3.12, 3.14, etc.)

No hace falta desinstalar nada. El instalador de Python en Windows incluye el **`py` launcher**, que permite tener varias versiones conviviendo sin conflicto y elegir cuál usar por proyecto.

```bash
# 1. Ver qué versiones tienes instaladas:
py --list
# Ejemplo de salida:
#  -V:3.14 *      (marcada con * = la que se usa por defecto si escribes "python")
#  -V:3.12
#  -V:3.11

# 2. Crear el entorno virtual del proyecto FORZANDO la versión 3.11:
py -3.11 -m venv venv

# 3. Activar el entorno virtual:
.\venv\Scripts\Activate.ps1

# 4. Verificar que quedó con 3.11.9 (no con 3.12 ni 3.14):
python --version
# Debe mostrar: Python 3.11.9
```

Una vez activado el entorno virtual (venv), cualquier `python` o `pip` que uses en esa terminal apunta exclusivamente a 3.11.9. Tus versiones 3.12 y 3.14 quedan completamente aisladas y disponibles para tus otros proyectos sin ningún conflicto.

**Si `py -3.11` da error** (no reconoce la versión), apunta directo a la ruta del ejecutable:
```bash
C:\Users\TU_USUARIO\AppData\Local\Programs\Python\Python311\python.exe -m venv venv
```

---

## 5. CONFIGURACIÓN DE TU HARDWARE (RTX 4050 + i7-13650HX)

Tu máquina es **excelente** para este proyecto. Veamos por qué:

### Tu hardware:
- **CPU**: Intel i7-13650HX (14 cores, 2.6 GHz) — muy potente
- **RAM**: 24 GB — suficiente para todo
- **GPU**: NVIDIA RTX 4050 Laptop (6 GB VRAM) — puede acelerar embeddings
- **Almacenamiento**: 53 GB libres — justo pero suficiente (bge-m3 ocupa ~2 GB, PyTorch ~3 GB)

### ¿Se necesita la tarjeta gráfica?

**Es opcional pero recomendable.** El modelo de embeddings (bge-m3) puede correr en CPU o GPU:
- **En CPU (i7-13650HX)**: funciona, pero generar embeddings de 200+ chunks tarda 3-5 minutos.
- **En GPU (RTX 4050)**: funciona mucho más rápido, 10-30 segundos para lo mismo.

Para un proyecto de 2 días con ~15-20 documentos, la CPU es suficiente. Pero si quieres rapidez y ya tienes la GPU, úsala.

### Instalación de PyTorch con CUDA (para tu RTX 4050)

```bash
# 1. Primero verifica que tienes los drivers de NVIDIA instalados:
nvidia-smi
# Debe mostrar tu RTX 4050 y la versión del driver (ej: 555.xx o superior)
# Si no funciona, descarga drivers de: https://www.nvidia.com/download/index.aspx

# 2. Instala PyTorch con soporte CUDA:
# Ve a https://pytorch.org/get-started/locally/ y selecciona:
#   - PyTorch Build: Stable
#   - OS: Windows
#   - Package: pip
#   - Language: Python
#   - Compute Platform: CUDA 12.4 (o la más reciente disponible)
#
# Esto te dará un comando como:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# 3. Verifica que CUDA funciona:
python -c "import torch; print(f'CUDA disponible: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0)}')"
# Debe mostrar:
# CUDA disponible: True
# GPU: NVIDIA GeForce RTX 4050 Laptop GPU
```

### Si prefieres NO configurar CUDA (más simple):

```bash
# Instala PyTorch solo CPU (sin CUDA):
pip install torch torchvision torchaudio
# Funciona, solo que los embeddings tardan más.
# Para un proyecto demo de 2 días, la diferencia no es crítica.
```

### Nota sobre VRAM (6 GB):
El modelo bge-m3 ocupa aproximadamente 1.5-2 GB de VRAM. Tu RTX 4050 con 6 GB tiene espacio de sobra. NO necesitas entrenar nada — solo generar embeddings (inferencia), que es mucho menos exigente.

---

## 6. ¿QUÉ NECESITO INSTALAR EN MI MÁQUINA?

### Checklist de instalación (Windows, en orden):

```
1. ☐ Python 3.11.9 (de python.org, marcar "Add python.exe to PATH")
2. ☐ Git (de git-scm.com)
3. ☐ Visual Studio Code (editor recomendado, de code.visualstudio.com)
4. ☐ Docker Desktop (de docker.com — gratis para uso personal/educativo)
5. ☐ Drivers NVIDIA actualizados (de nvidia.com/download — si vas a usar GPU)
6. ☐ Tesseract OCR (de github.com/UB-Mannheim/tesseract/wiki — para PDFs escaneados)
7. ☐ Cuenta OCI (de cloud.oracle.com — Always Free + US$ 300 trial)
8. ☐ Cuenta GitHub (de github.com — gratis)
```

### Paso a paso en la terminal (PowerShell o CMD):

```bash
# === PASO 1: Verificar qué versiones de Python tienes ===
py --list
# Si no tienes 3.11.9: descarga de
# https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe

# === PASO 2: Crear el proyecto ===
mkdir yachay-rag-agent
cd yachay-rag-agent

# === PASO 3: Crear entorno virtual FORZANDO Python 3.11 ===
# (importante si tienes 3.12 o 3.14 instaladas como versión por defecto)
py -3.11 -m venv venv

# Activar (Windows PowerShell):
.\venv\Scripts\Activate.ps1

# Activar (Windows CMD):
.\venv\Scripts\activate.bat

# Verificar que estás en el venv (debe mostrar "(venv)" al inicio del prompt)

# === PASO 4: Instalar PyTorch PRIMERO ===
# CON GPU (recomendado para tu RTX 4050):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# SIN GPU (más simple, funciona igual):
# pip install torch torchvision torchaudio

# === PASO 5: Instalar el resto de dependencias ===
pip install -r requirements.txt

# === PASO 6: Copiar .env.example a .env ===
copy .env.example .env
# Editar .env con tu API Key de OCI GenAI (cuando la tengas)

# === PASO 7: Generar documentos de ejemplo ===
python scripts/generate_sample_docs.py

# === PASO 8: Ejecutar ingestión ===
python scripts/ingest_documents.py
# (La primera vez descarga bge-m3 ~2 GB. Espera.)

# === PASO 9: Probar desde terminal ===
python scripts/test_query.py "¿Cuántos días de vacaciones tengo si llevo 3 años?"

# === PASO 10: Lanzar la interfaz web ===
streamlit run app/app.py
# Abrir en el navegador: http://localhost:8501
```

### Instalar Tesseract OCR en Windows:

```
1. Descargar de: https://github.com/UB-Mannheim/tesseract/wiki
2. Ejecutar el instalador.
3. IMPORTANTE: marcar los idiomas "Spanish" y "English" durante la instalación.
4. Anotar la ruta de instalación (ej: C:\Program Files\Tesseract-OCR)
5. Añadir al PATH del sistema o configurar en el código:
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

---

## 7. COMANDOS DE TERMINAL — REFERENCIA RÁPIDA

### Desarrollo local (Windows):

| Qué quiero hacer | Comando |
|---|---|
| Ver versiones de Python instaladas | `py --list` |
| Crear el entorno virtual con Python 3.11 | `py -3.11 -m venv venv` |
| Activar el entorno virtual | `.\venv\Scripts\Activate.ps1` |
| Instalar dependencias | `pip install -r requirements.txt` |
| Generar docs de ejemplo | `python scripts/generate_sample_docs.py` |
| Ingestir e indexar documentos | `python scripts/ingest_documents.py` |
| Probar una pregunta por terminal | `python scripts/test_query.py "tu pregunta aquí"` |
| Lanzar la app web (Streamlit) | `streamlit run app/app.py` |
| Ver la app en el navegador | Ir a `http://localhost:8501` |
| Detener Streamlit | Ctrl+C en la terminal |
| Instalar un paquete nuevo | `pip install nombre_paquete` |
| Congelar dependencias | `pip freeze > requirements.txt` |

### Docker:

| Qué quiero hacer | Comando |
|---|---|
| Construir imagen Docker | `docker build -t yachay-rag-agent:latest .` |
| Ejecutar contenedor | `docker run -d --name yachay -p 8501:8501 --env-file .env yachay-rag-agent:latest` |
| Ver logs del contenedor | `docker logs yachay -f` |
| Detener contenedor | `docker stop yachay` |
| Eliminar contenedor | `docker rm yachay` |
| Ver contenedores activos | `docker ps` |

### Git:

| Qué quiero hacer | Comando |
|---|---|
| Inicializar repo | `git init` |
| Añadir todo | `git add .` |
| Hacer commit | `git commit -m "mensaje descriptivo"` |
| Conectar con GitHub | `git remote add origin https://github.com/TU_USUARIO/yachay-rag-agent.git` |
| Subir a GitHub | `git push -u origin main` |
| Ver estado | `git status` |

---

## 8. DOCUMENTOS DE EJEMPLO — QUÉ SE GENERÓ

Se crearon **13 documentos corporativos** organizados en 4 categorías, simulando una empresa ficticia llamada **NovaTech Perú S.A.C.** (empresa de tecnología con sedes en Lima, Arequipa y Trujillo):

### Estructura:

```
data/raw/
├── rrhh/                                      (5 documentos)
│   ├── politica-vacaciones-y-permisos.md       ← Vacaciones, permisos con goce, licencias
│   ├── manual-del-colaborador.md               ← Horario, código de conducta, evaluación, vestimenta
│   ├── beneficios-colaboradores.md             ← Seguro médico, bonos, capacitación, trabajo remoto
│   ├── politica-trabajo-remoto.md              ← Teletrabajo, áreas elegibles, subsidios, desconexión
│   └── proceso-onboarding.md                   ← Primer día, primera semana, buddy, documentación
│
├── financiero/                                (4 documentos)
│   ├── politica-gastos-reembolsos.md           ← Límites de gasto, viáticos, proceso de reembolso
│   ├── politica-caja-chica.md                  ← Fondo fijo, procedimiento, montos por sede
│   ├── procedimiento-compras.md                ← Cotizaciones, proveedores homologados, aprobaciones
│   └── politica-facturacion-cobranzas.md       ← Facturación, crédito, cobranza, morosidad
│
├── legal/                                     (3 documentos)
│   ├── politica-privacidad-datos.md            ← Ley 29733, datos ARCO, seguridad, retención
│   ├── codigo-etica-anticorrupcion.md          ← Soborno, conflicto de intereses, canal de denuncias
│   └── reglamento-interno-trabajo.md           ← Jornada, faltas, sanciones, seguridad, hostigamiento
│
└── operacional/                               (4 documentos)
    ├── guia-gestion-incidentes.md              ← Severidades P1-P4, SLA, war room, post-mortem
    ├── plan-continuidad-negocio.md              ← BIA, escenarios de riesgo, sede alterna, failover
    ├── politica-seguridad-informacion.md        ← Clasificación, accesos, BYOD, respuesta a incidentes
    └── sla-proveedores.md                      ← SLAs con proveedores críticos, penalidades, monitoreo
```

### ¿Por qué NovaTech Perú?

Los documentos están escritos con contexto peruano real: Ley 29733 (protección de datos), D.S. 003-97-TR (régimen laboral), EsSalud, CTS, gratificaciones, SUNAT, SUNAFIL, etc. Esto los hace creíbles para un evaluador y demuestra que el agente funciona con documentación corporativa real, no con Lorem Ipsum.

### Preguntas que puedes probar con estos documentos:

| Pregunta | Documento que debería citar |
|---|---|
| "¿Cuántos días de vacaciones me corresponden si llevo 3 años?" | politica-vacaciones-y-permisos.md |
| "¿Cuál es el límite de gastos para taxis?" | politica-gastos-reembolsos.md |
| "¿Qué debo hacer si pierdo mi laptop corporativa?" | politica-seguridad-informacion.md |
| "¿Cuánto subsidio me dan para internet si hago trabajo remoto?" | politica-trabajo-remoto.md |
| "¿Qué pasa si un incidente P1 no se resuelve en 2 horas?" | guia-gestion-incidentes.md |
| "¿Cuánto es el límite de caja chica para la sede Arequipa?" | politica-caja-chica.md |
| "¿Puedo solicitar la eliminación de mis datos personales?" | politica-privacidad-datos.md |
| "¿Cuántas cotizaciones necesito para comprar equipos de S/ 5,000?" | procedimiento-compras.md |
| "¿Qué pasa si no rindo los viáticos a tiempo?" | politica-gastos-reembolsos.md |
| "¿Cómo funciona el canal de denuncias anónimo?" | codigo-etica-anticorrupcion.md |
| "¿Cuál es la política si llego tarde más de 3 veces al mes?" | manual-del-colaborador.md / reglamento-interno-trabajo.md |
| "¿Cuánto descuento tengo en la UNSA para una maestría?" | beneficios-colaboradores.md |
| "¿Cuántas horas extras puedo hacer y cómo se pagan?" | reglamento-interno-trabajo.md |
| "¿Cuál es el SLA de respuesta de Movistar para fallas?" | sla-proveedores.md |
| "¿Qué cubre el seguro médico para mis hijos?" | beneficios-colaboradores.md |
| "¿Cuánto tiempo tengo para reportar una brecha de datos a la ANPDP?" | politica-seguridad-informacion.md + politica-privacidad-datos.md |
| "¿Cuál es la receta del ceviche?" | ❌ DEBE dar fallback (no hay info sobre cocina) |

---

## 9. RESUMEN VISUAL DE LA ARQUITECTURA

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        TU LAPTOP (desarrollo local)                     │
│                                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────────┐  │
│  │ Documentos   │───▶│ Ingestión    │───▶│ Embeddings locales       │  │
│  │ corporativos │    │ (extracción, │    │ (bge-m3 en tu RTX 4050)  │  │
│  │ .md .pdf     │    │  chunking,   │    │ GRATIS, sin internet     │  │
│  │ .docx .xlsx  │    │  metadatos)  │    └───────────┬──────────────┘  │
│  └──────────────┘    └──────────────┘                │                  │
│                                                       ▼                  │
│                                          ┌──────────────────────────┐   │
│                                          │ ChromaDB (vector store)  │   │
│                                          │ HNSW, similitud coseno   │   │
│                                          │ Archivo local en disco   │   │
│                                          │ GRATIS                   │   │
│                                          └───────────┬──────────────┘   │
│                                                       │                  │
│  ┌──────────────┐                                     │                  │
│  │ Colaborador  │    ┌──────────────┐    ┌────────────▼─────────────┐   │
│  │ escribe      │───▶│ Streamlit    │───▶│ RAG Engine (orquestador) │   │
│  │ pregunta     │    │ (UI chat)    │    │ retrieval + rerank +     │   │
│  │ en el        │    │ GRATIS       │    │ contexto                 │   │
│  │ navegador    │    └──────┬───────┘    └────────────┬─────────────┘   │
│  └──────────────┘           │                         │                  │
│                              │                         │ API call         │
│                              │                         ▼                  │
│                              │            ┌──────────────────────────┐   │
│                              │            │ OCI Generative AI        │   │
│                              │            │ (Llama 3.3 70B)          │   │
│                              │            │ EN LA NUBE (São Paulo)   │   │
│                              │            │ Créditos trial: US$ 300  │   │
│                              ▼            └────────────┬─────────────┘   │
│                    ┌──────────────┐                     │                  │
│                    │ Respuesta    │◀────────────────────┘                  │
│                    │ + fuentes    │                                        │
│                    │ + confianza  │                                        │
│                    │ + feedback   │                                        │
│                    └──────────────┘                                        │
└─────────────────────────────────────────────────────────────────────────┘
```

**Todo lo de adentro de "TU LAPTOP" es gratis y offline (excepto la llamada al LLM).**

---

## 10. REQUIREMENTS.TXT ACTUALIZADO PARA TU HARDWARE

### Para tu RTX 4050 con CUDA:

```txt
# === INSTALAR PRIMERO (por separado, antes de pip install -r requirements.txt) ===
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# === LLM Client (OCI GenAI vía OpenAI SDK) ===
openai>=1.40.0

# === Embeddings locales ===
sentence-transformers>=3.0.0
# torch ya instalado arriba con CUDA

# === Framework RAG (LlamaIndex) ===
llama-index-core>=0.11.0
llama-index-llms-openai-like>=0.2.0
llama-index-embeddings-huggingface>=0.3.0
llama-index-vector-stores-chroma>=0.2.0
llama-index-readers-file>=0.2.0

# === Vector Store ===
chromadb>=0.5.0

# === Extracción de documentos ===
pymupdf>=1.24.0
pymupdf4llm>=0.0.10
pytesseract>=0.3.10
Pillow>=10.0.0
python-docx>=1.1.0
openpyxl>=3.1.0
python-pptx>=0.6.23
beautifulsoup4>=4.12.0

# === Interfaz ===
streamlit>=1.37.0

# === Utilidades ===
python-dotenv>=1.0.0
loguru>=0.7.0
```

### Comando de instalación completo:

```bash
# 1. Activar venv
.\venv\Scripts\Activate.ps1

# 2. PyTorch con CUDA (para tu RTX 4050)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# 3. Resto de dependencias
pip install -r requirements.txt

# 4. Verificar GPU
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
# Esperado: True NVIDIA GeForce RTX 4050 Laptop GPU
```

---

*Documento generado como parte de la guía de ejecución del proyecto YACHAY.*
