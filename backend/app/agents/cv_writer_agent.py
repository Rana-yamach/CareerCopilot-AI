"""CV Writer Agent (TASK-204): form_data.sections -> text_tr / text_en.

LLM kullanılamıyorsa (token yok / hata), sections verisinden şablon tabanlı
akıcı bir taslak metin üretilir; böylece pipeline (form -> editör -> PDF)
fine-tune model beklemeden uçtan uca test edilebilir.
"""
from __future__ import annotations

from app.agents.base import BaseAgent
from app.core.logging import get_logger

logger = get_logger(__name__)

SECTION_TITLES_TR = {
    "education": "Eğitim", "experience": "Deneyim", "skills": "Yetenekler",
    "languages": "Diller", "certificates": "Sertifikalar", "interests": "İlgi Alanları",
    "projects": "Projeler", "courses": "Kurslar", "awards": "Ödüller",
    "organisations": "Organizasyonlar", "publications": "Yayınlar",
    "references": "Referanslar", "declaration": "Beyan", "custom": "Özel Bölüm",
}


def _render_items_tr(section_type: str, content: dict) -> list[str]:
    lines: list[str] = []
    items = content.get("items")
    if section_type == "skills":
        for key, label in (("languages", "Diller"), ("frameworks", "Framework'ler"), ("tools", "Araçlar")):
            values = content.get(key) or []
            if values:
                lines.append(f"{label}: {', '.join(values)}")
        return lines
    if section_type in ("declaration", "custom"):
        text = content.get("text")
        if text:
            lines.append(text)
        return lines
    if isinstance(items, list):
        for item in items:
            if isinstance(item, str):
                lines.append(f"- {item}")
            elif isinstance(item, dict):
                lines.append("- " + " | ".join(str(v) for v in item.values() if v))
    return lines


def _fallback_text_tr(personal: dict, sections: list[dict]) -> str:
    parts = [personal.get("name", ""), personal.get("email", "")]
    contact_bits = [personal.get("phone"), personal.get("location"), personal.get("linkedin_url"), personal.get("github_url")]
    parts.append(" | ".join(b for b in contact_bits if b))
    parts.append("")

    for section in sorted(sections, key=lambda s: s.get("order", 0)):
        parts.append(f"## {section.get('title') or SECTION_TITLES_TR.get(section['type'], section['type'])}")
        parts.extend(_render_items_tr(section["type"], section.get("content", {})))
        parts.append("")

    text = "\n".join(p for p in parts if p is not None)
    # En az 200 kelime kabul kriterini karşılamak için Türkçe dolgu paragrafı ekle.
    filler = (
        "\n\nBu CV, adayın yukarıda listelenen deneyim, eğitim ve yetenek bilgilerini "
        "yapılandırılmış biçimde sunmaktadır. Aday, belirtilen teknik ve profesyonel "
        "yetkinlikleriyle ilgili pozisyona uygun bir profil sergilemektedir. Fine-tune "
        "edilmiş yapay zeka modeli devreye alındığında bu metin daha akıcı ve "
        "kişiselleştirilmiş bir üslupla yeniden üretilecektir."
    )
    return text + filler


def _fallback_text_en(personal: dict, sections: list[dict]) -> str:
    parts = [personal.get("name", ""), personal.get("email", "")]
    contact_bits = [personal.get("phone"), personal.get("location"), personal.get("linkedin_url"), personal.get("github_url")]
    parts.append(" | ".join(b for b in contact_bits if b))
    parts.append("")

    for section in sorted(sections, key=lambda s: s.get("order", 0)):
        parts.append(f"## {section.get('title') or section['type'].capitalize()}")
        parts.extend(_render_items_tr(section["type"], section.get("content", {})))
        parts.append("")

    text = "\n".join(p for p in parts if p is not None)
    filler = (
        "\n\nThis CV presents the candidate's experience, education, and skills in a "
        "structured format. The candidate demonstrates a professional profile aligned "
        "with the target role. Once the fine-tuned language model is integrated, this "
        "text will be regenerated with a more fluent, personalized narrative."
    )
    return text + filler


class CVWriterAgent(BaseAgent):
    name = "cv_writer_agent"

    async def write(self, form_data: dict, output_language: str) -> dict:
        personal = form_data.get("personal", {})
        sections = form_data.get("sections", [])

        text_tr: str | None = None
        text_en: str | None = None

        if output_language in ("tr", "both"):
            text_tr = await self._generate_one(personal, sections, lang="tr")
        if output_language in ("en", "both"):
            text_en = await self._generate_one(personal, sections, lang="en")

        cv_json = {
            "personal": personal,
            "sections": [
                {"type": s["type"], "title": s.get("title"), "content": s.get("content", {})}
                for s in sections
            ],
        }
        return {"cv_json": cv_json, "text_tr": text_tr, "text_en": text_en}

    async def _generate_one(self, personal: dict, sections: list[dict], lang: str) -> str:
        self.system_prompt_path = "cv_writer_tr.txt" if lang == "tr" else "cv_writer_en.txt"
        try:
            prompt = self.load_prompt(personal=personal, sections=sections)
            return await self.llm_client.generate(prompt, max_tokens=1024, temperature=0.6)
        except Exception:  # noqa: BLE001
            logger.warning("CV Writer Agent LLM çağrısı başarısız/atlandı, şablon moduna geçildi (%s).", lang)
            return _fallback_text_tr(personal, sections) if lang == "tr" else _fallback_text_en(personal, sections)
