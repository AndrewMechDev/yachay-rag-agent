"""Limpieza de ruido en textos extraídos: headers/footers, paginación, espacios redundantes."""

import re


def clean_text(text: str) -> str:
    """Limpia ruido común en documentos corporativos antes del chunking."""
    if not text:
        return ""

    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^[-=_*]{3,}\s*$", "", text, flags=re.MULTILINE)

    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines)

    return text.strip()
