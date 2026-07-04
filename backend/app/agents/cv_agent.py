"""CV Agent (TASK-203): raw_text + github_languages -> parsed_skills + cv_score.

HF Inference API üzerinden LLM çağrısı dener; token tanımlı değilse veya
LLM hata verirse (fine-tune model henüz hazır değilse), sistemi bloke
etmemek için basit sezgisel (heuristic) bir çıkarım yapar (bkz. TASKS.md
Genel Kurallar madde 3 ruhu: "bloke olma, base/placeholder ile devam et").
"""
from __future__ import annotations

import re

from app.agents.base import BaseAgent
from app.models.enums import DocumentType

COMMON_LANGUAGES = [
    "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust",
    "PHP", "Ruby", "Kotlin", "Swift", "SQL",
]
COMMON_FRAMEWORKS = [
    "React", "FastAPI", "Django", "Flask", "Vue", "Angular", "Spring",
    "Express", "Node.js", "Next.js", ".NET",
]
COMMON_TOOLS = ["Docker", "Git", "Kubernetes", "AWS", "Azure", "GCP", "Linux", "CI/CD"]


def _heuristic_parsed_skills(raw_text: str) -> dict:
    text = raw_text or ""

    def find_matches(vocabulary: list[str]) -> list[str]:
        return [term for term in vocabulary if re.search(rf"\b{re.escape(term)}\b", text, re.IGNORECASE)]

    return {
        "languages": find_matches(COMMON_LANGUAGES),
        "frameworks": find_matches(COMMON_FRAMEWORKS),
        "tools": find_matches(COMMON_TOOLS),
        "experience": [],
        "education": [],
    }


def _heuristic_cv_score(parsed_skills: dict, raw_text: str) -> tuple[int, str]:
    skill_count = sum(len(parsed_skills.get(key, [])) for key in ("languages", "frameworks", "tools"))
    length_score = min(len(raw_text or "") // 200, 40)
    score = min(100, 30 + skill_count * 5 + length_score)
    explanation = (
        f"Tespit edilen {skill_count} teknik beceri ve belge uzunluğuna göre otomatik "
        "ön skor hesaplandı. Bu skor, fine-tune LLM entegrasyonu tamamlandığında "
        "daha isabetli hale gelecektir."
    )
    return score, explanation


class CVAgent(BaseAgent):
    name = "cv_agent"
    system_prompt_path = "cv_agent_tr.txt"

    async def analyze(
        self,
        raw_text: str,
        document_type: DocumentType | str,
        github_languages: dict | None = None,
    ) -> dict:
        doc_type_value = document_type.value if hasattr(document_type, "value") else document_type

        prompt = self.load_prompt(raw_text=raw_text[:6000], github_languages=github_languages or {})

        def _fallback() -> dict:
            return {"parsed_skills": _heuristic_parsed_skills(raw_text)}

        parsed, used_fallback = await self.generate_json_with_fallback(
            prompt, fallback_fn=_fallback, max_tokens=768, temperature=0.3
        )

        if used_fallback:
            parsed_skills = parsed["parsed_skills"]
            if github_languages:
                parsed_skills["languages"] = list(
                    {*parsed_skills["languages"], *github_languages.keys()}
                )
            cv_score = None
            cv_score_explanation = None
            if doc_type_value == DocumentType.CV.value:
                cv_score, cv_score_explanation = _heuristic_cv_score(parsed_skills, raw_text)
        else:
            parsed_skills = parsed.get("parsed_skills", _heuristic_parsed_skills(raw_text))
            cv_score = parsed.get("cv_score")
            cv_score_explanation = parsed.get("cv_score_explanation")
            if doc_type_value != DocumentType.CV.value:
                cv_score = None
                cv_score_explanation = None

        return {
            "parsed_skills": parsed_skills,
            "cv_score": cv_score,
            "cv_score_explanation": cv_score_explanation,
        }
