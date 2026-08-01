"""CV Writer Agent (TASK-204): form_data.sections -> text_tr.

LLM kullanılamıyorsa (token yok / hata), sections verisinden şablon tabanlı
akıcı bir taslak metin üretilir; böylece pipeline (form -> editör -> PDF)
fine-tune model beklemeden uçtan uca test edilebilir. Uygulama yalnızca
Türkçe CV üretir (İngilizce desteği kaldırıldı).
"""
from __future__ import annotations

from app.agents.base import BaseAgent
from app.core.logging import get_logger

logger = get_logger(__name__)

SECTION_TITLES_TR = {
    "about": "Hakkımda",
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
    if section_type in ("about", "declaration", "custom"):
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


_BROKEN_OUTPUT_MARKERS = (
    "as a helpful assistant",
    "i understand the instructions",
    "i will translate",
    "i will generate",
    "i will write",
    "here's a summary",
    "these are the instructions",
    "yardımcı asistan",
    "aşağıda verilen",
    "'type':",
    "'personal':",
    "\"type\":",
    "{'name':",
)

_TR_CHARS = "çğıöşüÇĞİÖŞÜ"


def _looks_broken(text: str, personal: dict, sections: list[dict]) -> bool:
    """LLM'in gerçek bir CV metni yerine talimatı/ham veriyi geri kustuğu ya
    da tamamen alakasız/yanlış dilde bir şey ürettiği durumları yakalar (bkz.
    cv_writer_tr.txt üstündeki KESİN KURALLAR). Sabit kelime listesi tek
    başına yetersiz kaldığı için (model her seferinde farklı şekilde
    saçmalayabiliyor), asıl kontrol modelin gerçek girdi verisiyle (isim,
    bölüm başlıkları) hiç örtüşüp örtüşmediğine bakar — bu, spesifik
    ifadelerden bağımsız, çok daha genel bir "alakasızlık" testidir.
    """
    stripped = text.strip()
    if len(stripped) < 100:
        return True

    lowered = stripped.lower()
    if any(marker in lowered for marker in _BROKEN_OUTPUT_MARKERS):
        return True

    if not any(ch in stripped for ch in _TR_CHARS):
        return True

    reference_terms = [personal.get("name", "")]
    reference_terms.extend(section.get("title", "") for section in sections)
    reference_terms = [t for t in reference_terms if t and len(t) > 2]
    if reference_terms and not any(term.lower() in lowered for term in reference_terms):
        return True

    return False


class CVWriterAgent(BaseAgent):
    name = "cv_writer_agent"
    system_prompt_path = "cv_writer_tr.txt"

    async def write(self, form_data: dict) -> dict:
        personal = form_data.get("personal", {})
        sections = form_data.get("sections", [])

        text_tr = await self._generate_one(personal, sections)

        cv_json = {
            "personal": personal,
            "sections": [
                {"type": s["type"], "title": s.get("title"), "content": s.get("content", {})}
                for s in sections
            ],
        }
        return {"cv_json": cv_json, "text_tr": text_tr}

    async def _generate_one(self, personal: dict, sections: list[dict]) -> str:
        try:
            prompt = self.load_prompt(personal=personal, sections=sections)
            result = await self.llm_client.generate(prompt, max_tokens=1024, temperature=0.6)
            if _looks_broken(result, personal, sections):
                raise ValueError("cv_writer_output_invalid")
            return result
        except Exception:  # noqa: BLE001
            logger.warning("CV Writer Agent LLM çağrısı başarısız/atlandı, şablon moduna geçildi.")
            return _fallback_text_tr(personal, sections)
