"""Orchestrator Agent (TASK-211): intent classification + downstream agent
çağrısı + Türkçe SSE yanıtı."""
from __future__ import annotations

from app.agents.base import AgentContext, BaseAgent

VALID_INTENTS = {"cv_agent", "skill_gap", "roadmap", "interview", "cv_writer", "general"}

_KEYWORD_INTENT_MAP = [
    (("mülakat", "interview", "soru sor"), "interview"),
    (("cv oluştur", "cv yaz", "özgeçmiş oluştur"), "cv_writer"),
    (("yol haritası", "roadmap", "plan"), "roadmap"),
    (("cv analiz", "cv puanı", "özgeçmişimi değerlendir"), "cv_agent"),
    (("olmak istiyorum", "pozisyon", "swe", "developer", "mühendis"), "skill_gap"),
]


def _heuristic_intent(message: str) -> str:
    lowered = message.lower()
    for keywords, intent in _KEYWORD_INTENT_MAP:
        if any(k in lowered for k in keywords):
            return intent
    return "general"


class OrchestratorAgent(BaseAgent):
    name = "orchestrator"
    system_prompt_path = "orchestrator_tr.txt"

    async def classify_intent(self, ctx: AgentContext, message: str) -> dict:
        prompt = self.load_prompt(
            user_profile=ctx.user_profile,
            chat_history=ctx.chat_history,
            user_message=message,
        )

        def _fallback() -> dict:
            intent = _heuristic_intent(message)
            return {"intent": intent, "params": {}, "followup_agent": intent}

        parsed, _used_fallback = await self.generate_json_with_fallback(
            prompt,
            fallback_fn=_fallback,
            validate_fn=lambda p: p.get("intent") in VALID_INTENTS,
            max_tokens=128,
            temperature=0.2,
        )
        return parsed

    def build_general_reply(self, message: str) -> str:
        return (
            "Mesajınızı aldım. Şu an için CV oluşturma, beceri boşluğu analizi, "
            "yol haritası veya mülakat simülasyonu konularında size yardımcı "
            "olabilirim. Hangi konuda destek istediğinizi biraz daha detaylandırabilir misiniz?"
        )
