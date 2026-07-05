"""PDF render servisi (TASK-208, TASK-301).

Karar: WeasyPrint (bkz. docs/pdf_render_decision.md). Sprint 2'de sade
`cv_simple.html`, Sprint 3'te iyileştirilmiş `cv_styled.html` kullanılır.
"""
from __future__ import annotations

import os

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=True)


def render_cv_pdf(name: str, email: str, body_text: str, styled: bool = True) -> bytes:
    template_name = "cv_styled.html" if styled else "cv_simple.html"
    template = _env.get_template(template_name)
    html_content = template.render(name=name or "", email=email or "", body_text=body_text or "")
    return HTML(string=html_content).write_pdf()
