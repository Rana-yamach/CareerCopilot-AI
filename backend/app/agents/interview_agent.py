"""Interview Agent (TASK-210): soru üretimi (question mode) + değerlendirme
(evaluation mode)."""
from __future__ import annotations

from app.agents.base import BaseAgent

_QUESTION_BANK = {
    ("algorithmic", "junior"): [
        "İki sıralı diziyi O(n) zamanda nasıl birleştirirsiniz? Türkçe açıklayın.",
        "Bir dizide en büyük iki sayıyı tek geçişte nasıl bulursunuz?",
        "Bir string'in palindrom olup olmadığını nasıl kontrol edersiniz?",
    ],
    ("algorithmic", "mid"): [
        "Bir binary search tree'de en küçük k'ıncı elemanı nasıl bulursunuz?",
        "Dinamik programlama ile en uzun ortak alt diziyi (LCS) nasıl bulursunuz?",
    ],
    ("system", "junior"): [
        "Basit bir URL kısaltma servisinin temel bileşenlerini anlatın.",
        "Bir web uygulamasında caching neden ve nasıl kullanılır?",
    ],
    ("system", "mid"): [
        "Yüksek trafikli bir e-ticaret sisteminde veritabanı ölçeklendirmeyi nasıl tasarlarsınız?",
        "Dağıtık bir sistemde eventual consistency kavramını örnekle açıklayın.",
    ],
    ("behavioral", "junior"): [
        "Bir takım arkadaşınızla anlaşmazlık yaşadığınız bir durumu STAR formatında anlatın.",
    ],
    ("behavioral", "mid"): [
        "Baskı altında öncelik belirlemeniz gereken bir projeyi nasıl yönettiniz?",
    ],
}


def _heuristic_question(category: str, difficulty: str, index: int) -> str:
    bank = _QUESTION_BANK.get((category, difficulty)) or _QUESTION_BANK.get(("algorithmic", "junior"))
    return bank[index % len(bank)]


def _heuristic_feedback(user_answer: str) -> dict:
    length = len(user_answer.strip())
    score = min(10, max(2, length // 40))
    feedback = (
        "Cevabınız temel yaklaşımı içeriyor. Daha fazla teknik detay ve örnek "
        "vererek yanıtınızı güçlendirebilirsiniz."
        if length < 200
        else "Cevabınız kapsamlı ve iyi yapılandırılmış görünüyor. Sınır durumlarını da "
        "değerlendirdiğinizden emin olun."
    )
    hint = "İdeal cevap; problemi adım adım analiz eder, zaman/alan karmaşıklığını belirtir ve örnekle destekler."
    return {"feedback": feedback, "score": score, "correct_answer_hint": hint}


class InterviewAgent(BaseAgent):
    name = "interview_agent"
    system_prompt_path = "interview_tr.txt"

    async def generate_question(
        self, target_position: str, difficulty: str, category: str, question_index: int, previous_qa: list[dict]
    ) -> str:
        prompt = self.load_prompt(
            target_position=target_position,
            difficulty=difficulty,
            category=category,
            previous_qa=previous_qa,
            user_answer=None,
        )
        parsed, _used_fallback = await self.generate_json_with_fallback(
            prompt,
            fallback_fn=lambda: {"question": _heuristic_question(category, difficulty, question_index)},
            validate_fn=lambda p: bool(p.get("question")),
            max_tokens=256,
            temperature=0.7,
        )
        return parsed["question"]

    async def evaluate_answer(
        self, target_position: str, difficulty: str, category: str, question: str, user_answer: str
    ) -> dict:
        prompt = self.load_prompt(
            target_position=target_position,
            difficulty=difficulty,
            category=category,
            previous_qa=[{"question": question}],
            user_answer=user_answer,
        )
        parsed, _used_fallback = await self.generate_json_with_fallback(
            prompt,
            fallback_fn=lambda: _heuristic_feedback(user_answer),
            validate_fn=lambda p: "score" in p,
            max_tokens=512,
            temperature=0.5,
        )
        return parsed
