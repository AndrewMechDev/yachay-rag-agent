"""Interfaz de chat con Streamlit. Sistema visual glassmorphism (ver skill
yachay-ui-streamlit). Indica que es un agente de IA, muestra fuentes citadas,
permite feedback e historial por sesión."""

import base64
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import APP_NAME, BUSINESS_CATEGORIES, LLM_PROVIDER_NAME
from src.engine_singleton import get_engine
from src.logging_config import setup_logging
from src.rag_engine import RAGEngine

STATIC_DIR = Path(__file__).resolve().parent / "static"
_avatar_assistant_path = STATIC_DIR / "avatar-assistant.png"
_avatar_user_path = STATIC_DIR / "avatar-user.png"
_owl_logo_path = STATIC_DIR / "logo-owl.png"
_logo_svg_path = STATIC_DIR / "logo.svg"

# Favicon: búho PNG (branding). Fallback Material Symbol si el archivo falta.
_page_icon = (
    str(_owl_logo_path)
    if _owl_logo_path.exists()
    else (str(_logo_svg_path) if _logo_svg_path.exists() else ":material/psychology:")
)

st.set_page_config(
    page_title=f"{APP_NAME} - Asistente de Conocimiento Corporativo",
    page_icon=_page_icon,
    layout="wide",
    initial_sidebar_state="expanded",
)

setup_logging()


def _png_data_uri(path: Path) -> str:
    """Convierte un PNG local a data URI para embeberlo en HTML del brand header."""
    if not path.exists():
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


_OWL_DATA_URI = _png_data_uri(_owl_logo_path)
# Brand logo en header/sidebar: búho PNG. Si falta, fallback al SVG abstracto.
if _OWL_DATA_URI:
    LOGO_HTML = f'<img src="{_OWL_DATA_URI}" alt="{APP_NAME}" />'
elif _logo_svg_path.exists():
    LOGO_HTML = _logo_svg_path.read_text(encoding="utf-8")
else:
    LOGO_HTML = ""

# Icono SVG de documento para chips de citas (sin emoji decorativo).
ICON_DOCUMENT_SVG = (
    '<svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" '
    'stroke-width="1.8" style="vertical-align:-2px"><path d="M6 2.5h8l4 4V21a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V3.5a1 1 0 0 1 1-1z"/>'
    '<path d="M14 2.5V7h4"/><path d="M8 12h8M8 16h8M8 8.5h3"/></svg>'
)
_ICON_USER_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
    'stroke="#EDEBFF" stroke-width="1.6"><circle cx="12" cy="8" r="3.6"/>'
    '<path d="M4.5 20c1.4-3.6 4.4-5.5 7.5-5.5s6.1 1.9 7.5 5.5"/></svg>'
)

# Avatar del asistente: búho. Avatar de usuario: PNG propio o SVG de persona.
AVATAR_ASSISTANT = (
    str(_avatar_assistant_path)
    if _avatar_assistant_path.exists()
    else (str(_owl_logo_path) if _owl_logo_path.exists() else ":material/psychology:")
)
AVATAR_USER = str(_avatar_user_path) if _avatar_user_path.exists() else _ICON_USER_SVG

THEME_CSS = """
<style>
:root {
    /* Amanecer andino: slate calido + oro vivo + turquesa (amigable, no IA morada) */
    --yachay-bg-1: #1A3350;
    --yachay-bg-2: #0E1C2C;
    --yachay-bg-3: #071018;
    --yachay-accent: #F5C451;
    --yachay-accent-2: #3ECFCF;
    --yachay-text: #F4F7FB;
    --yachay-muted: rgba(244, 247, 251, 0.72);
    --yachay-font: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
    --yachay-glass-bg: rgba(255, 255, 255, 0.07);
    --yachay-glass-border: rgba(62, 207, 207, 0.22);
    --yachay-radius: 20px;
}

html, body, .stApp, [class*="css"] {
    font-family: var(--yachay-font) !important;
}

.stApp {
    /* Concepto "mapa de conocimiento": rejilla + color plano (no glow/degradado tipico de IA) */
    background-color: #0A1F2E;
    background-image:
        repeating-linear-gradient(
            90deg,
            transparent 0,
            transparent 39px,
            rgba(245, 196, 81, 0.05) 39px,
            rgba(245, 196, 81, 0.05) 40px
        ),
        repeating-linear-gradient(
            0deg,
            transparent 0,
            transparent 39px,
            rgba(62, 207, 207, 0.04) 39px,
            rgba(62, 207, 207, 0.04) 40px
        );
}

@keyframes yachay-fade-in {
    from { opacity: 0; transform: translateY(4px); }
    to { opacity: 1; transform: translateY(0); }
}

header[data-testid="stHeader"] {
    background: transparent !important;
}
[data-testid="stMainBlockContainer"] {
    padding-top: 2.75rem !important;
    padding-bottom: 2rem !important;
}
[data-testid="stSidebarContent"] {
    padding-top: 1.25rem !important;
}

div[data-testid="stElementContainer"]:has(.yachay-hero),
div[data-testid="stElementContainer"]:has(.welcome-card),
div[data-testid="stVerticalBlockBorderWrapper"]:has(.yachay-hero),
div[data-testid="stVerticalBlockBorderWrapper"]:has(.welcome-card) {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
    outline: none !important;
}
div[data-testid="stElementContainer"]:has(.yachay-hero) {
    margin-bottom: 0.85rem !important;
}

[data-testid="stSidebar"] {
    background: rgba(14, 28, 44, 0.72);
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
    background: rgba(255, 255, 255, 0.06);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(62, 207, 207, 0.35);
    border-radius: 16px;
}
/* CTA enviar: se nota como accion principal */
[data-testid="stChatInput"] button {
    background: var(--yachay-accent) !important;
    color: #0A1F2E !important;
    border: 2px solid var(--yachay-accent) !important;
    box-shadow: 2px 2px 0 rgba(62, 207, 207, 0.45) !important;
}
[data-testid="stChatInput"] button:hover {
    background: #FFE08A !important;
    border-color: #FFE08A !important;
}
[data-testid="stChatInput"] button svg {
    fill: #0A1F2E !important;
    color: #0A1F2E !important;
}

/* Selectbox = lista desplegable clara (no solo una flechita invisible) */
[data-testid="stSidebar"] [data-testid="stSelectbox"] label p {
    font-size: 0.8rem !important;
    color: var(--yachay-muted) !important;
}
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background: rgba(245, 196, 81, 0.12) !important;
    border: 2px solid var(--yachay-accent) !important;
    border-radius: 12px !important;
    min-height: 2.85rem !important;
    box-shadow: 3px 3px 0 rgba(62, 207, 207, 0.35) !important;
}
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div:hover {
    background: rgba(245, 196, 81, 0.18) !important;
    border-color: #FFE08A !important;
}
[data-testid="stSidebar"] [data-testid="stSelectbox"] svg {
    width: 1.35rem !important;
    height: 1.35rem !important;
    color: var(--yachay-accent) !important;
    opacity: 1 !important;
}
.select-hint {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    margin: 0 0 0.35rem 0;
    font-size: 0.75rem;
    color: var(--yachay-accent-2);
    font-weight: 600;
    letter-spacing: 0.02em;
}
.select-hint .chev {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 1.15rem;
    height: 1.15rem;
    border-radius: 4px;
    background: rgba(62, 207, 207, 0.2);
    border: 1px solid rgba(62, 207, 207, 0.45);
    font-size: 0.65rem;
    line-height: 1;
}

div.stButton > button {
    background: rgba(18, 42, 61, 0.95);
    border: 2px solid rgba(62, 207, 207, 0.4);
    border-radius: 12px;
    color: var(--yachay-text);
    box-shadow: 3px 3px 0 rgba(245, 196, 81, 0.25);
    transition: border-color 0.15s ease-out, color 0.15s ease-out, box-shadow 0.15s ease-out, transform 0.1s ease-out;
}
div.stButton > button:hover {
    border-color: var(--yachay-accent);
    color: var(--yachay-accent);
    background: rgba(245, 196, 81, 0.12);
    box-shadow: 4px 4px 0 rgba(62, 207, 207, 0.35);
}
div.stButton > button:active {
    transform: scale(0.97);
}

.brand-row { display: flex; align-items: center; gap: 0.65rem; position: relative; z-index: 1; }
.brand-logo svg, .brand-logo img { display: block; width: 44px; height: 44px; border-radius: 50%; object-fit: cover; }
.brand-logo.sidebar svg, .brand-logo.sidebar img { width: 32px; height: 32px; }

.sidebar-brand { margin-bottom: 0.55rem; }
.sidebar-brand .brand-subtitle {
    margin-top: 0.15rem;
    font-size: 0.8rem;
    line-height: 1.35;
    color: var(--yachay-muted);
}

.yachay-hero {
    position: relative;
    overflow: hidden;
    /* Cartel editorial: color plano + barra lateral (lomo de documento) + sombra dura */
    background: #122A3D;
    border: 2px solid var(--yachay-accent);
    border-left: 7px solid var(--yachay-accent);
    border-radius: 14px;
    box-shadow: 7px 7px 0 rgba(62, 207, 207, 0.35);
    padding: 1.15rem 1.25rem 1.15rem;
    margin: 0.35rem 0 0.25rem 0;
}
.yachay-hero .brand-subtitle,
.yachay-hero .value-prop,
.yachay-hero .purpose-line,
.yachay-hero .how-steps { position: relative; z-index: 1; }
/* Motivo escalonado andino (chakana) en esquina — no blob/glow */
.yachay-hero::after {
    content: "";
    position: absolute;
    right: 0.85rem;
    top: 0.85rem;
    width: 52px;
    height: 52px;
    opacity: 0.35;
    background:
        linear-gradient(var(--yachay-accent-2), var(--yachay-accent-2)) 0 18px / 52px 4px no-repeat,
        linear-gradient(var(--yachay-accent-2), var(--yachay-accent-2)) 18px 0 / 4px 52px no-repeat,
        linear-gradient(var(--yachay-accent), var(--yachay-accent)) 10px 10px / 32px 4px no-repeat,
        linear-gradient(var(--yachay-accent), var(--yachay-accent)) 10px 10px / 4px 32px no-repeat,
        linear-gradient(var(--yachay-accent), var(--yachay-accent)) 10px 38px / 32px 4px no-repeat,
        linear-gradient(var(--yachay-accent), var(--yachay-accent)) 38px 10px / 4px 32px no-repeat;
    pointer-events: none;
    z-index: 0;
}

.brand-title {
    font-size: 1.85rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: var(--yachay-accent);
    margin: 0;
    line-height: 1.15;
}
.brand-title.sidebar { font-size: 1.35rem; color: var(--yachay-accent); }
.brand-subtitle {
    color: var(--yachay-muted);
    font-size: 0.95rem;
    margin-top: 0.2rem;
    margin-bottom: 0;
}
.value-prop {
    color: var(--yachay-text);
    font-size: 0.98rem;
    line-height: 1.5;
    margin: 0.75rem 0 0.4rem 0;
    max-width: 42rem;
}
.value-prop strong { color: var(--yachay-accent); font-weight: 600; }
.yachay-hero.compact {
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
}
.yachay-hero.compact .value-prop {
    margin: 0.4rem 0 0;
    font-size: 0.9rem;
}
.yachay-hero.compact .purpose-line,
.yachay-hero.compact .how-steps {
    display: none;
}
.yachay-hero.compact::after {
    width: 36px;
    height: 36px;
    opacity: 0.25;
}
.pitch-line {
    margin: 0.45rem 0 0;
    font-size: 0.8rem;
    color: var(--yachay-accent);
    font-weight: 600;
}
.how-steps {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem 1rem;
    margin: 0;
    padding: 0;
    list-style: none;
}
.how-steps li {
    color: var(--yachay-muted);
    font-size: 0.8125rem;
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
}
.how-steps .step-num {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 1.3rem;
    height: 1.3rem;
    border-radius: 999px;
    background: rgba(62, 207, 207, 0.18);
    border: 1px solid rgba(62, 207, 207, 0.45);
    color: var(--yachay-accent-2);
    font-size: 0.7rem;
    font-weight: 700;
}
.welcome-card {
    background: #122A3D;
    border: 2px solid rgba(62, 207, 207, 0.45);
    border-left: 6px solid var(--yachay-accent-2);
    border-radius: 14px;
    box-shadow: 5px 5px 0 rgba(245, 196, 81, 0.22);
    padding: 0.95rem 1.05rem;
    margin: 0.35rem 0 0.85rem 0;
    color: var(--yachay-text);
    font-size: 0.9rem;
    line-height: 1.55;
}
.welcome-card strong { color: var(--yachay-accent-2); }
.audience-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.5rem;
    margin-top: 0.5rem;
}
.audience-card {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid var(--yachay-glass-border);
    border-radius: 12px;
    padding: 0.65rem 0.75rem;
    font-size: 0.78rem;
    color: var(--yachay-muted);
    line-height: 1.4;
}
.audience-card strong {
    display: block;
    color: var(--yachay-accent);
    font-size: 0.8rem;
    margin-bottom: 0.2rem;
}
.caption-text {
    color: var(--yachay-muted);
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
    background: rgba(245, 196, 81, 0.09);
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
.badge-high { background: rgba(52, 211, 153, 0.16); color: #6EE7B7; border-color: rgba(52, 211, 153, 0.45); }
.badge-medium { background: rgba(245, 196, 81, 0.16); color: var(--yachay-accent); border-color: rgba(245, 196, 81, 0.45); }
.badge-low { background: rgba(248, 113, 113, 0.16); color: #FCA5A5; border-color: rgba(248, 113, 113, 0.4); }

.source-title { font-weight: 600; color: var(--yachay-text); }
.source-meta { color: var(--yachay-muted); font-size: 0.8125rem; }

.source-preview {
    background: rgba(255, 255, 255, 0.04);
    border-left: 2px solid var(--yachay-accent-2);
    border-radius: 8px;
    padding: 0.6rem 0.85rem;
    margin: 0.35rem 0 0.75rem 0;
    color: var(--yachay-muted);
    font-size: 0.8125rem;
    line-height: 1.5;
    font-style: italic;
}

.yachay-answer p { margin-bottom: 0.75rem; line-height: 1.6; }
.yachay-citation {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    background: rgba(245, 196, 81, 0.12);
    border: 1px solid rgba(245, 196, 81, 0.35);
    border-radius: 8px;
    padding: 0.05rem 0.5rem;
    margin: 0.15rem 0.15rem 0.15rem 0;
    font-size: 0.78rem;
    font-style: normal;
    color: #FFE08A;
    white-space: normal;
}
.yachay-citation svg { flex-shrink: 0; }

.badge-mock {
    background: rgba(248, 113, 113, 0.14);
    color: #FDBA74;
    border-color: rgba(248, 113, 113, 0.35);
}
.badge-live {
    background: rgba(52, 211, 153, 0.14);
    color: #6EE7B7;
    border-color: rgba(52, 211, 153, 0.35);
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
    [data-testid="stChatMessage"], .glass-card { animation: none !important; }
    div.stButton > button { transition: none !important; }
    .skeleton-line { animation: none !important; opacity: 0.5 !important; }
}

@media (max-width: 480px) {
    [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; }
    [data-testid="stHorizontalBlock"] > div { min-width: 100% !important; }
    .audience-grid { grid-template-columns: 1fr; }
    .how-steps { flex-direction: column; gap: 0.35rem; }
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


_CITATION_PATTERN = re.compile(r"📄\s*\*\[([^\]]+)\]\*")


def _short_citation_label(inner: str) -> str:
    """De 'archivo.md | Sección: X | Categoría: y' deja 'archivo.md · X'."""
    parts = [p.strip() for p in inner.split("|")]
    if not parts:
        return inner
    file_name = parts[0]
    section = ""
    for part in parts[1:]:
        lower = part.lower()
        if lower.startswith("sección:") or lower.startswith("seccion:"):
            section = part.split(":", 1)[-1].strip()
            break
    return f"{file_name} · {section}" if section else file_name


def format_response_html(text: str) -> str:
    """Convierte el markdown de la respuesta a HTML simple, con las citas
    (📄 *[archivo | sección | categoría]*) como chips cortos (archivo · sección).
    Envuelve párrafos en <p> para el espaciado de .yachay-answer."""

    def _replace_citation(match: re.Match) -> str:
        label = _short_citation_label(match.group(1))
        return f'<span class="yachay-citation">{ICON_DOCUMENT_SVG} [{label}]</span>'

    text = _CITATION_PATTERN.sub(_replace_citation, text)
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
    """Solo avisa en modo mock. El proveedor LLM real se oculta del usuario final
    (vive en el expander 'Para desarrolladores' del sidebar)."""
    if is_mock:
        st.markdown(
            '<span class="badge badge-mock" role="status">Modo simulado — sin conexión al LLM</span>',
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

if "messages" not in st.session_state:
    st.session_state.messages = []
if "feedback" not in st.session_state:
    st.session_state.feedback = {}

with st.sidebar:
    st.markdown(
        f"""<div class="sidebar-brand">
            <div class="brand-row">
                <div class="brand-logo sidebar">{LOGO_HTML}</div>
                <div class="brand-title sidebar">{APP_NAME}</div>
            </div>
            <div class="brand-subtitle">Asistente de conocimiento corporativo</div>
        </div>""",
        unsafe_allow_html=True,
    )

    with st.expander("¿Qué es YACHAY?", expanded=False):
        st.markdown(
            """
**Objetivo:** responder dudas sobre políticas y procesos internos
**citando la fuente exacta**, sin inventar.

Si no hay evidencia en los documentos, lo dice claramente.
            """
        )
        st.markdown(
            """<div class="audience-grid">
                <div class="audience-card">
                    <strong>Colaborador</strong>
                    Encuentra la respuesta en segundos, sin buscar PDFs ni interrumpir a un área.
                </div>
                <div class="audience-card">
                    <strong>RRHH / Legal / Ops</strong>
                    Menos preguntas repetidas por Slack o correo; el documento habla por sí solo.
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown(
        """<div class="glass-alert" style="margin-top: 0.65rem;">
            <strong>Este es un agente de IA.</strong> Las respuestas se generan a partir de
            documentos internos. Verifica con el área responsable antes de decisiones críticas.
        </div>""",
        unsafe_allow_html=True,
    )

    st.subheader("Filtrar por área")
    st.markdown(
        '<div class="select-hint"><span class="chev">▼</span> Lista desplegable — elige el área de documentos</div>',
        unsafe_allow_html=True,
    )
    category_options = {"Todas las áreas": None}
    for key, val in BUSINESS_CATEGORIES.items():
        category_options[val["label"]] = key

    selected_category_label = st.selectbox(
        "Área de documentos",
        options=list(category_options.keys()),
        index=0,
        help="Abre la lista y elige RRHH, Financiero, Legal u Operacional para acotar las respuestas.",
    )
    category_filter = category_options[selected_category_label]

    # Sugerencias en sidebar solo durante la conversacion (evita duplicar
    # los chips del area principal cuando el chat esta vacio).
    if st.session_state.get("messages"):
        if category_filter:
            sidebar_suggestions = QUESTIONS_BY_CATEGORY.get(category_filter, [])
            sidebar_suggestions_label = f"Preguntas frecuentes de {BUSINESS_CATEGORIES[category_filter]['label']}"
        else:
            sidebar_suggestions = [qs[0] for qs in QUESTIONS_BY_CATEGORY.values()]
            sidebar_suggestions_label = "Preguntas frecuentes (todas las áreas)"

        with st.expander(sidebar_suggestions_label, expanded=False):
            for question in sidebar_suggestions:
                if st.button(question, key=f"sidebar_chip_{question}", use_container_width=True):
                    st.session_state.pending_prompt = question
                    st.rerun()
    else:
        st.caption("Las sugerencias de preguntas aparecen en el panel principal.")

    with st.expander("Para desarrolladores", expanded=False):
        st.caption(f"LLM: {LLM_PROVIDER_NAME} · Llama 3.3 70B")
        st.caption("Guion de demo: docs/guion-demo.md")

    if st.button("Limpiar conversación", use_container_width=True):
        st.session_state.messages = []
        st.session_state.feedback = {}
        st.rerun()


if "engine" not in st.session_state:
    st.session_state.engine = load_engine()

_has_messages = bool(st.session_state.messages)
_hero_class = "yachay-hero compact" if _has_messages else "yachay-hero"
# st.html (no markdown): evita que indentación + línea en blanco se vea como code fence.
_hero_extra = ""
if not _has_messages:
    _hero_extra = (
        '<p class="purpose-line">'
        "Para qué sirve: que el colaborador deje de buscar en PDFs o interrumpir a RRHH/Legal, "
        "y que esas áreas dejen de responder las mismas preguntas cien veces."
        "</p>"
        '<ul class="how-steps">'
        '<li><span class="step-num">1</span> Elige un área en la lista de la izquierda</li>'
        '<li><span class="step-num">2</span> Pregunta o usa una sugerencia</li>'
        '<li><span class="step-num">3</span> Lee la respuesta y abre las fuentes citadas</li>'
        "</ul>"
    )

st.html(
    f'<div class="{_hero_class}">'
    f'<div class="brand-row">'
    f'<div class="brand-logo">{LOGO_HTML}</div>'
    f'<div class="brand-title">{APP_NAME}</div>'
    "</div>"
    '<p class="value-prop">'
    "<strong>Tu biblioteca interna que responde:</strong> "
    "políticas y procesos con la fuente exacta; sin inventar. "
    "Si no está en los documentos, lo dice."
    "</p>"
    f"{_hero_extra}"
    "</div>"
)
render_mode_badge(st.session_state.engine.is_mock)

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

if not st.session_state.messages:
    st.markdown(
        f"""<div class="welcome-card">
            <strong>Hola, soy {APP_NAME}.</strong>
            Estoy para ahorrarte la búsqueda: pregúntame por vacaciones, gastos, privacidad,
            incidentes u otros procesos documentados. Empieza con una sugerencia o escribe
            tu pregunta; yo cito el documento.
            <p class="pitch-line">Ejemplo de valor: menos interrupciones a RRHH/Legal por las mismas preguntas repetidas.</p>
        </div>""",
        unsafe_allow_html=True,
    )
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
