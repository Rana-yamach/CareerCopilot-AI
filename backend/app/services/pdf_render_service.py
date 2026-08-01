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


def render_cv_pdf(
    personal: dict,
    sections: list[dict],
    body_text: str = "",
    headline: str = "",
    styled: bool = True,
) -> bytes:
    """CV'yi `form_data` (kişisel bilgiler + yapılandırılmış bölümler) üzerinden
    render eder. `body_text` (CV Writer Agent çıktısı) varsa "Profil" bölümü
    olarak başa eklenir; asıl yapı (Eğitim, Deneyim, Yetenekler vb.) her zaman
    `sections`'tan gelir — TASK-301 düz metin sorununu çözer.
    """
    template_name = "cv_styled.html" if styled else "cv_simple.html"
    template = _env.get_template(template_name)
    html_content = template.render(
        personal=personal or {},
        sections=sections or [],
        body_text=body_text or "",
        headline=headline or "",
    )
    return HTML(string=html_content).write_pdf()
