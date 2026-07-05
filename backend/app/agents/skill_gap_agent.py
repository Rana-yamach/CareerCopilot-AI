"""Skill Gap Agent (TASK-205): kullanıcı becerileri + pgvector RAG -> missing_skills.

RAG sorgusu: `metadata->>'source_label' = 'skill_requirement'` filtresiyle
cosine benzerlik (pgvector `<=>` operatörü) üzerinden LIMIT 5 chunk getirir.
"""
from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import BaseAgent
from app.core.logging import get_logger
from app.services.embedding_service import encode_one

logger = get_logger(__name__)

DEFAULT_RESOURCE = {"title": "Genel öğrenme kaynağı araştırması yapın", "type": "kurs", "url": "https://www.coursera.org"}


async def fetch_skill_requirement_chunks(db: AsyncSession, target_position: str, limit: int = 5) -> list[str]:
    try:
        query_vector = encode_one(target_position)
    except Exception:  # noqa: BLE001
        logger.warning("Embedding modeli yüklenemedi, RAG sorgusu atlanıyor.")
        return []

    vector_literal = "[" + ",".join(str(v) for v in query_vector) + "]"
    sql = text(
        """
        SELECT content
        FROM document_embedding
        WHERE metadata->>'source_label' = 'skill_requirement'
        ORDER BY embedding <=> (:query_vector)::vector
        LIMIT :limit
        """
    )
    try:
        result = await db.execute(sql, {"query_vector": vector_literal, "limit": limit})
        return [row[0] for row in result.fetchall()]
    except Exception:  # noqa: BLE001
        logger.warning("pgvector RAG sorgusu başarısız oldu.")
        return []


def _merge_user_skills(documents_parsed_skills: list[dict]) -> set[str]:
    merged: set[str] = set()
    for parsed in documents_parsed_skills:
        for key in ("languages", "frameworks", "tools"):
            merged.update(parsed.get(key, []) or [])
    return merged


_BASELINE_SKILLS_BY_KEYWORD = {
    # Google SWE / genel yazılım mühendisliği
    "swe": ["Sistem Tasarımı", "Veri Yapıları ve Algoritmalar", "Dağıtık Sistemler", "Big-O Analizi", "Code Review Pratikleri"],
    "software engineer": ["Sistem Tasarımı", "Veri Yapıları ve Algoritmalar", "Dağıtık Sistemler", "Big-O Analizi"],
    "yazılım mühendis": ["Sistem Tasarımı", "Veri Yapıları ve Algoritmalar", "Dağıtık Sistemler", "Big-O Analizi"],
    "google": ["Sistem Tasarımı", "Veri Yapıları ve Algoritmalar", "Dağıtık Sistemler", "Big-O Analizi"],

    # ML / Data Science / AI
    "ml engineer": ["PyTorch/TensorFlow", "MLOps ve Model Deployment", "Feature Engineering", "İstatistik ve Olasılık"],
    "machine learning": ["PyTorch/TensorFlow", "MLOps ve Model Deployment", "Feature Engineering", "İstatistik ve Olasılık"],
    "makine öğrenmesi": ["PyTorch/TensorFlow", "MLOps ve Model Deployment", "Feature Engineering", "İstatistik ve Olasılık"],
    "data scientist": ["İstatistik ve Olasılık", "SQL İleri Sorgulama", "Makine Öğrenmesi Temelleri", "Veri Görselleştirme"],
    "veri bilimci": ["İstatistik ve Olasılık", "SQL İleri Sorgulama", "Makine Öğrenmesi Temelleri", "Veri Görselleştirme"],
    "data": ["İstatistik ve Olasılık", "SQL İleri Sorgulama", "Makine Öğrenmesi Temelleri", "Veri Görselleştirme"],

    # Frontend
    "frontend": ["Modern JavaScript Framework'leri", "Erişilebilirlik (a11y)", "Performans Optimizasyonu", "TypeScript"],
    "front-end": ["Modern JavaScript Framework'leri", "Erişilebilirlik (a11y)", "Performans Optimizasyonu", "TypeScript"],
    "ön yüz": ["Modern JavaScript Framework'leri", "Erişilebilirlik (a11y)", "Performans Optimizasyonu", "TypeScript"],

    # Backend
    "backend": ["API Tasarımı", "Veritabanı Optimizasyonu", "Mikroservis Mimarisi", "Kimlik Doğrulama (JWT/OAuth2)"],
    "back-end": ["API Tasarımı", "Veritabanı Optimizasyonu", "Mikroservis Mimarisi", "Kimlik Doğrulama (JWT/OAuth2)"],
    "arka yüz": ["API Tasarımı", "Veritabanı Optimizasyonu", "Mikroservis Mimarisi", "Kimlik Doğrulama (JWT/OAuth2)"],

    # DevOps
    "devops": ["Konteynerizasyon", "CI/CD Pipeline Kurulumu", "Bulut Altyapı Yönetimi", "Infrastructure as Code", "Monitoring/Logging"],

    # Mobile
    "mobile": ["Native/Cross-platform Mobil Geliştirme", "Mobil UI/UX Prensipleri", "REST API Entegrasyonu", "Performans ve Bellek Yönetimi"],
    "mobil": ["Native/Cross-platform Mobil Geliştirme", "Mobil UI/UX Prensipleri", "REST API Entegrasyonu", "Performans ve Bellek Yönetimi"],
    "android": ["Kotlin/Java (Android)", "Mobil UI/UX Prensipleri", "REST API Entegrasyonu", "Performans ve Bellek Yönetimi"],
    "ios": ["Swift (iOS)", "Mobil UI/UX Prensipleri", "REST API Entegrasyonu", "Performans ve Bellek Yönetimi"],

    # Product Management
    "product manager": ["Ürün Stratejisi ve Roadmap Yönetimi", "Veri Odaklı Karar Verme (A/B Testing)", "Paydaş Yönetimi", "Agile/Scrum"],
    "ürün yönetici": ["Ürün Stratejisi ve Roadmap Yönetimi", "Veri Odaklı Karar Verme (A/B Testing)", "Paydaş Yönetimi", "Agile/Scrum"],
    "product owner": ["Ürün Stratejisi ve Roadmap Yönetimi", "Veri Odaklı Karar Verme (A/B Testing)", "Paydaş Yönetimi", "Agile/Scrum"],
}


def _tr_lower(text: str) -> str:
    """Türkçe "İ" harfini Python'un varsayılan `str.lower()` iki karaktere
    ("i" + birleşen nokta) açmasının önüne geçen güvenli küçük harfe çevirme.
    Bu olmadan "İOS Developer" gibi girdilerde "ios" anahtar kelimesi
    sessizce eşleşmeyebilir.
    """
    return text.replace("İ", "i").replace("I", "ı").lower()


def _heuristic_missing_skills(target_position: str, user_skills: set[str]) -> list[dict]:
    lowered = _tr_lower(target_position)
    candidates: list[str] = []
    seen: set[str] = set()
    for keyword, skills in _BASELINE_SKILLS_BY_KEYWORD.items():
        if keyword in lowered:
            for skill in skills:
                if skill not in seen:
                    seen.add(skill)
                    candidates.append(skill)
    if not candidates:
        candidates = ["Sistem Tasarımı", "İletişim Becerileri", "Proje Yönetimi"]

    missing = [c for c in candidates if c not in user_skills] or candidates[:3]

    return [
        {
            "name": name,
            "priority": idx + 1,
            "estimated_weeks": 3 + idx,
            "resources": [DEFAULT_RESOURCE],
        }
        for idx, name in enumerate(missing[:5])
    ]


class SkillGapAgent(BaseAgent):
    name = "skill_gap_agent"
    system_prompt_path = "skill_gap_tr.txt"

    async def analyze(
        self,
        db: AsyncSession,
        target_position: str,
        documents_parsed_skills: list[dict],
    ) -> dict:
        user_skills = _merge_user_skills(documents_parsed_skills)
        context_chunks = await fetch_skill_requirement_chunks(db, target_position)

        prompt = self.load_prompt(
            target_position=target_position,
            user_skills=list(user_skills),
            context_chunks=context_chunks,
        )

        def _fallback() -> dict:
            missing_skills = _heuristic_missing_skills(target_position, user_skills)
            match_score = max(10, 90 - len(missing_skills) * 15)
            return {"match_score": match_score, "missing_skills": missing_skills}

        parsed, used_fallback = await self.generate_json_with_fallback(
            prompt, fallback_fn=_fallback, max_tokens=768, temperature=0.4
        )
        if used_fallback:
            return parsed
        return {
            "match_score": parsed.get("match_score", 50),
            "missing_skills": parsed.get("missing_skills", []),
        }
