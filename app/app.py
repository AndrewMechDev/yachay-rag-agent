"""Interfaz de chat con Streamlit. Sistema visual glassmorphism (ver skill
yachay-ui-streamlit). Indica que es un agente de IA, muestra fuentes citadas,
permite feedback e historial por sesión."""

import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import APP_NAME, BUSINESS_CATEGORIES, EMBEDDING_MODEL, LLM_PROVIDER_NAME
from src.engine_singleton import get_engine
from src.logging_config import setup_logging
from src.rag_engine import RAGEngine

st.set_page_config(
    page_title=f"{APP_NAME} — Asistente de Conocimiento Corporativo",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

setup_logging()

STATIC_DIR = Path(__file__).resolve().parent / "static"
_avatar_assistant_path = STATIC_DIR / "avatar-assistant.png"
_avatar_user_path = STATIC_DIR / "avatar-user.png"
_logo_path = STATIC_DIR / "logo.svg"
# Fallback a emoji si aún no se agregaron los PNG reales en app/static/
# (evita que st.chat_message falle buscando un archivo inexistente).
AVATAR_ASSISTANT = str(_avatar_assistant_path) if _avatar_assistant_path.exists() else "🧠"
AVATAR_USER = str(_avatar_user_path) if _avatar_user_path.exists() else "🙂"
# El logo se inlinea como SVG crudo en el HTML del brand-title (st.set_page_config
# no soporta SVG como page_icon; PIL no lo decodifica). Vacío = fallback sin logo.
LOGO_SVG = _logo_path.read_text(encoding="utf-8") if _logo_path.exists() else ""

THEME_CSS = """
<style>
:root {
    --yachay-bg-1: #1b2140;
    --yachay-bg-2: #0B0F1A;
    --yachay-bg-3: #05070c;
    --yachay-accent: #D4A855;
    --yachay-text: #EDEBFF;
    --yachay-font: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
    --yachay-glass-bg: rgba(255, 255, 255, 0.035);
    --yachay-glass-border: rgba(255, 255, 255, 0.10);
    --yachay-radius: 20px;
}

html, body, .stApp, [class*="css"] {
    font-family: var(--yachay-font) !important;
}

.stApp {
    background: radial-gradient(circle at top left, var(--yachay-bg-1) 0%, var(--yachay-bg-2) 55%, var(--yachay-bg-3) 100%);
}

@keyframes yachay-fade-in {
    from { opacity: 0; transform: translateY(4px); }
    to { opacity: 1; transform: translateY(0); }
}

[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(20px);
    border-right: 1px solid var(--yachay-glass-border);
}

[data-testid="stChatMessage"] {
    background: var(--yachay-glass-bg);
    backdrop-filter: blur(12px);
    border: 1px solid var(--yachay-glass-border);
    border-radius: var(--yachay-radius);
    padding: 1rem 1rem;
    margin-bottom: 0.5rem;
    animation: yachay-fade-in 0.25s ease-out;
}

[data-testid="stExpander"] {
    background: var(--yachay-glass-bg);
    backdrop-filter: blur(12px);
    border: 1px solid var(--yachay-glass-border);
    border-radius: 16px;
}

[data-testid="stChatInput"] {
    background: rgba(255, 255, 255, 0.04);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(212, 168, 85, 0.3);
    border-radius: 16px;
}

div.stButton > button {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(8px);
    border: 1px solid var(--yachay-glass-border);
    border-radius: 12px;
    color: var(--yachay-text);
    transition: border-color 0.2s ease-out, color 0.2s ease-out, transform 0.1s ease-out;
}
div.stButton > button:hover {
    border-color: var(--yachay-accent);
    color: var(--yachay-accent);
}
div.stButton > button:active {
    transform: scale(0.97);
}

.brand-row { display: flex; align-items: center; gap: 0.75rem; }
.brand-logo svg { display: block; width: 48px; height: 48px; }
.brand-logo.sidebar svg { width: 34px; height: 34px; }

.brand-title {
    font-size: 2.25rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    background: linear-gradient(90deg, var(--yachay-accent), var(--yachay-text));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0;
}
.brand-title.sidebar {
    font-size: 1.5rem;
}
.brand-subtitle {
    color: rgba(237, 235, 255, 0.7);
    font-size: 1rem;
    margin-top: 0.25rem;
}
.caption-text {
    color: rgba(237, 235, 255, 0.65);
    font-size: 0.875rem;
    margin-bottom: 0.5rem;
}

.glass-card {
    background: var(--yachay-glass-bg);
    backdrop-filter: blur(12px);
    border: 1px solid var(--yachay-glass-border);
    border-radius: 16px;
    padding: 1rem;
    margin-bottom: 0.5rem;
    animation: yachay-fade-in 0.2s ease-out;
}

.glass-alert {
    background: rgba(212, 168, 85, 0.07);
    backdrop-filter: blur(12px);
    border-left: 3px solid var(--yachay-accent);
    border-radius: 12px;
    padding: 1rem;
    font-size: 0.875rem;
    color: var(--yachay-text);
}

.badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.8125rem;
    font-weight: 600;
    backdrop-filter: blur(8px);
    border: 1px solid var(--yachay-glass-border);
}
.badge-high { background: rgba(94, 219, 138, 0.15); color: #6EE7A8; border-color: rgba(94, 219, 138, 0.4); }
.badge-medium { background: rgba(212, 168, 85, 0.15); color: var(--yachay-accent); border-color: rgba(212, 168, 85, 0.4); }
.badge-low { background: rgba(224, 92, 92, 0.15); color: #F08787; border-color: rgba(224, 92, 92, 0.4); }

.source-title { font-weight: 600; color: var(--yachay-text); }
.source-meta { color: rgba(237, 235, 255, 0.68); font-size: 0.8125rem; }

.source-preview {
    background: rgba(255, 255, 255, 0.03);
    border-left: 2px solid var(--yachay-glass-border);
    border-radius: 8px;
    padding: 0.6rem 0.85rem;
    margin: 0.35rem 0 0.75rem 0;
    color: rgba(237, 235, 255, 0.75);
    font-size: 0.8125rem;
    line-height: 1.5;
    font-style: italic;
}

.yachay-answer p { margin-bottom: 0.75rem; line-height: 1.6; }
.yachay-citation {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    background: rgba(212, 168, 85, 0.08);
    border: 1px solid rgba(212, 168, 85, 0.25);
    border-radius: 8px;
    padding: 0.05rem 0.5rem;
    margin: 0.15rem 0.15rem 0.15rem 0;
    font-size: 0.78rem;
    font-style: normal;
    color: rgba(212, 168, 85, 0.95);
    white-space: normal;
}

.badge-mock {
    background: rgba(224, 92, 92, 0.12);
    color: #F0A787;
    border-color: rgba(224, 92, 92, 0.35);
}
.badge-live {
    background: rgba(94, 219, 138, 0.12);
    color: #6EE7A8;
    border-color: rgba(94, 219, 138, 0.35);
}

@keyframes yachay-skeleton-pulse {
    0%, 100% { opacity: 0.35; }
    50% { opacity: 0.7; }
}
.skeleton-line {
    height: 0.9rem;
    border-radius: 6px;
    background: var(--yachay-glass-border);
    animation: yachay-skeleton-pulse 1.1s ease-in-out infinite;
    margin-bottom: 0.6rem;
}

h1, h2, h3 { color: var(--yachay-text) !important; font-weight: 600 !important; }

@media (prefers-reduced-motion: reduce) {
    [data-testid="stChatMessage"], .glass-card {
        animation: none !important;
    }
    div.stButton > button {
        transition: none !important;
    }
    .skeleton-line {
        animation: none !important;
        opacity: 0.5 !important;
    }
}

@media (max-width: 480px) {
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
    }
    [data-testid="stHorizontalBlock"] > div {
        min-width: 100% !important;
    }
}
</style>
"""
st.markdown(THEME_CSS, unsafe_allow_html=True)


def save_feedback(msg: dict, feedback_type: str) -> None:
    """Persiste el feedback en logs/feedback.jsonl para monitoreo."""
    feedback_path = Path("logs/feedback.jsonl")
    feedback_path.parent.mkdir(exist_ok=True)
    entry = {
        "timestamp": datetime.now().isoformat(),
        "query": msg.get("query", "")[:200],
        "feedback": feedback_type,
        "confidence": msg.get("confidence", 0),
        "sources_count": len(msg.get("sources", [])),
    }
    with open(feedback_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


_CITATION_PATTERN = re.compile(r"📄\s*\*(\[[^\]]+\])\*")


def format_response_html(text: str) -> str:
    """Convierte el markdown de la respuesta a HTML simple, con las citas
    (📄 *[archivo | sección | categoría]*) como chips en vez de texto itálico
    en crudo. Envuelve párrafos en <p> para el espaciado de .yachay-answer."""
    text = _CITATION_PATTERN.sub(r'<span class="yachay-citation">📄 \1</span>', text)
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    html_paragraphs = []
    for p in paragraphs:
        # Negrita/itálica markdown remanente (fuera de las citas ya convertidas).
        p = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", p)
        p = p.replace("\n", "<br>")
        html_paragraphs.append(f"<p>{p}</p>")
    return f'<div class="yachay-answer">{"".join(html_paragraphs)}</div>'


def render_sources(sources: list) -> None:
    """Renderiza el expander de fuentes citadas como glass cards, con el
    preview del fragmento como cita visual (no como bloque de código)."""
    with st.expander(f"Fuentes consultadas ({len(sources)})"):
        for j, src in enumerate(sources, 1):
            preview = src.get("preview", "").replace("<", "&lt;").replace(">", "&gt;")
            st.markdown(
                f"""<div class="glass-card">
                    <div class="source-title">{j}. {src['file']}</div>
                    <div class="source-meta">Categoría: {src['category']} · Sección: {src['section']} · Score: {src['score']}</div>
                    <div class="source-preview">"{preview}"</div>
                </div>""",
                unsafe_allow_html=True,
            )


def render_skeleton() -> str:
    """Devuelve el markup de un placeholder tipo 'skeleton' mientras se busca la respuesta."""
    return (
        '<div class="skeleton-line" style="width: 90%;"></div>'
        '<div class="skeleton-line" style="width: 75%;"></div>'
        '<div class="skeleton-line" style="width: 50%;"></div>'
    )


def render_answer_streamed(placeholder, text: str, chunk_words: int = 6, delay: float = 0.02) -> None:
    """Efecto typewriter escribiendo sobre el HTML formateado (citas como chips,
    no texto itálico en crudo). Solo se usa en el turno recién generado, nunca
    al re-renderizar el historial (evita repetir la animación en cada rerun)."""
    words = text.split(" ")
    shown = ""
    for i in range(0, len(words), chunk_words):
        shown += " ".join(words[i : i + chunk_words]) + " "
        placeholder.markdown(format_response_html(shown), unsafe_allow_html=True)
        time.sleep(delay)


def render_mode_badge(is_mock: bool) -> None:
    """Badge persistente que indica si las respuestas vienen de MockLLMClient o del LLM real."""
    if is_mock:
        st.markdown(
            '<span class="badge badge-mock" role="status">Modo simulado — sin conexión al LLM</span>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<span class="badge badge-live" role="status">Conectado a {LLM_PROVIDER_NAME}</span>',
            unsafe_allow_html=True,
        )


def render_confidence(confidence: float) -> None:
    """Renderiza el badge de confianza como pill glass, sin emoji ni colores de sistema."""
    if confidence >= 0.7:
        level, label = "high", "Alta"
    elif confidence >= 0.4:
        level, label = "medium", "Media"
    else:
        level, label = "low", "Baja"
    st.markdown(
        f'<span class="badge badge-{level}" role="status">Confianza {label} · {confidence:.0%}</span>',
        unsafe_allow_html=True,
    )


def load_engine() -> RAGEngine:
    """Obtiene el RAG Engine, vía el singleton en src/engine_singleton.py.

    En Windows, `python run_app.py` ya lo pre-cargó en el hilo principal
    (necesario ahí: torch + chromadb juntos crashean con
    STATUS_ACCESS_VIOLATION 0xC0000005 en WINHTTP.dll si se inicializan fuera
    del hilo principal). En Linux (Docker, Streamlit Community Cloud) ese bug
    no aplica, así que get_engine() construye el motor de forma perezosa aquí
    mismo si nadie lo hizo antes — funciona igual con `streamlit run
    app/app.py` directo, sin pasar por run_app.py.
    """
    return get_engine()


with st.sidebar:
    st.markdown(
        f"""<div class="brand-row">
            <div class="brand-logo sidebar">{LOGO_SVG}</div>
            <div class="brand-title sidebar">{APP_NAME}</div>
        </div>""",
        unsafe_allow_html=True,
    )
    st.markdown('<div class="brand-subtitle">Asistente de Conocimiento Corporativo</div>', unsafe_allow_html=True)

    st.divider()

    st.markdown(
        """<div class="glass-alert">
            <strong>Este es un agente de IA.</strong> Las respuestas se generan automáticamente
            a partir de documentos internos. Verifica siempre la información con el
            área responsable antes de tomar decisiones críticas.
        </div>""",
        unsafe_allow_html=True,
    )

    st.divider()

    st.subheader("Filtrar por área")
    category_options = {"Todas las áreas": None}
    for key, val in BUSINESS_CATEGORIES.items():
        category_options[val["label"]] = key

    selected_category_label = st.selectbox(
        "Categoría de documentos:",
        options=list(category_options.keys()),
        index=0,
    )
    category_filter = category_options[selected_category_label]

    st.divider()

    st.subheader("Stack")
    st.markdown(
        f"""
    - **LLM**: {LLM_PROVIDER_NAME} (Llama 3.3 70B)
    - **Embeddings**: {EMBEDDING_MODEL} (local)
    - **Vector Store**: ChromaDB (HNSW)
    - **Orquestación**: LlamaIndex
    """
    )

    if st.button("Limpiar conversación", use_container_width=True):
        st.session_state.messages = []
        st.session_state.feedback = {}
        st.rerun()


if "messages" not in st.session_state:
    st.session_state.messages = []
if "feedback" not in st.session_state:
    st.session_state.feedback = {}
if "engine" not in st.session_state:
    st.session_state.engine = load_engine()

st.markdown(
    f"""<div class="brand-row">
        <div class="brand-logo">{LOGO_SVG}</div>
        <div class="brand-title">{APP_NAME}</div>
    </div>""",
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="brand-subtitle">Pregunta lo que necesites sobre políticas, procesos y documentos internos de la empresa.</p>',
    unsafe_allow_html=True,
)
render_mode_badge(st.session_state.engine.is_mock)
st.divider()

for i, msg in enumerate(st.session_state.messages):
    avatar = AVATAR_USER if msg["role"] == "user" else AVATAR_ASSISTANT
    with st.chat_message(msg["role"], avatar=avatar):
        if msg["role"] == "assistant":
            st.markdown(format_response_html(msg["content"]), unsafe_allow_html=True)
        else:
            st.markdown(msg["content"])

        if msg["role"] == "assistant" and msg.get("sources"):
            render_sources(msg["sources"])
            render_confidence(msg.get("confidence", 0))

            col1, col2, _ = st.columns([1, 1, 8])
            feedback_key = f"feedback_{i}"
            with col1:
                if st.button("👍", key=f"up_{i}"):
                    st.session_state.feedback[feedback_key] = "positive"
                    save_feedback(msg, "positive")
                    st.toast("Gracias por tu feedback")
            with col2:
                if st.button("👎", key=f"down_{i}"):
                    st.session_state.feedback[feedback_key] = "negative"
                    save_feedback(msg, "negative")
                    st.toast("Gracias, mejoraremos la respuesta")

            if feedback_key in st.session_state.feedback:
                fb = st.session_state.feedback[feedback_key]
                st.caption(f"Feedback registrado: {'Positivo' if fb == 'positive' else 'Negativo'}")

QUESTIONS_BY_CATEGORY = {
    "rrhh": [
        "¿Cuántos días de vacaciones tengo al año?",
        "¿Cómo es el proceso de onboarding para nuevos colaboradores?",
        "¿Puedo trabajar de forma remota?",
    ],
    "financiero": [
        "¿Cuál es el límite de gastos de transporte?",
        "¿Cómo reporto un gasto de caja chica?",
        "¿Cuál es el procedimiento para solicitar una compra?",
    ],
    "legal": [
        "¿Cómo protege la empresa mis datos personales?",
        "¿Qué dice el código de ética sobre regalos de proveedores?",
        "¿Cuál es la jornada laboral según el reglamento interno?",
    ],
    "operacional": [
        "¿Cómo reporto un incidente P1?",
        "¿Qué hacer ante una interrupción del servicio?",
        "¿Cuáles son los SLA acordados con proveedores?",
    ],
}

if not st.session_state.messages:
    if category_filter:
        # Categoria especifica seleccionada en el sidebar: sus 3 preguntas.
        suggestions = QUESTIONS_BY_CATEGORY.get(category_filter, [])
        label = f"Preguntas frecuentes de {BUSINESS_CATEGORIES[category_filter]['label']}:"
    else:
        # "Todas las areas": una pregunta representativa por categoria.
        suggestions = [qs[0] for qs in QUESTIONS_BY_CATEGORY.values()]
        label = "Prueba con una de estas preguntas:"

    st.markdown(f'<p class="caption-text">{label}</p>', unsafe_allow_html=True)
    chip_cols = st.columns(len(suggestions))
    for col, question in zip(chip_cols, suggestions):
        with col:
            if st.button(question, key=f"chip_{question}", use_container_width=True):
                st.session_state.pending_prompt = question
                st.rerun()

prompt = st.chat_input("Escribe tu pregunta...")
if not prompt and st.session_state.get("pending_prompt"):
    prompt = st.session_state.pop("pending_prompt")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=AVATAR_USER):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=AVATAR_ASSISTANT):
        placeholder = st.empty()
        placeholder.markdown(render_skeleton(), unsafe_allow_html=True)

        result = st.session_state.engine.ask(query=prompt, category_filter=category_filter)

        render_answer_streamed(placeholder, result["response"])

        if result["sources"]:
            render_sources(result["sources"])
            render_confidence(result.get("confidence", 0))
        st.caption(f"Respondido en {result['latency_ms']}ms")

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result["response"],
            "query": prompt,
            "sources": result["sources"],
            "confidence": result["confidence"],
            "latency_ms": result["latency_ms"],
        }
    )
