"""BaseAgent + AgentContext + AgentResult (TASK-202).

Her ajan bu sınıfı genişletir. Prompt dosyaları Jinja2 ile render edilir.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Any, Callable

from jinja2 import Template

from app.core.logging import get_logger
from app.llm.hf_client import HFInferenceClient

PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "prompts")

logger = get_logger(__name__)

_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)


def _extract_json_payload(text: str) -> str:
    """LLM çıktısından JSON gövdesini çıkarır.

    Chat-instruct modeller (fine-tune edilmemiş olsalar dahi) genellikle
    JSON'ı markdown kod bloğuna sarar veya öncesine/sonrasına açıklama
    cümlesi ekler ("İşte analiz:" gibi). Ham metnin tamamını doğrudan
    `json.loads`'a vermek bu gayet yaygın durumlarda gereksiz yere
    başarısız olup heuristik moda düşülmesine yol açıyordu; bu fonksiyon
    önce kod bloğunu, sonra da metindeki en dış JSON nesnesi/dizisini
    ayıklayarak parse'ı olabildiğince toleranslı hale getirir.
    """
    fence_match = _JSON_FENCE_RE.search(text)
    candidate = fence_match.group(1) if fence_match else text

    start_candidates = [i for i in (candidate.find("{"), candidate.find("[")) if i != -1]
    if not start_candidates:
        return candidate.strip()
    start = min(start_candidates)

    end = max(candidate.rfind("}"), candidate.rfind("]"))
    if end == -1 or end < start:
        return candidate.strip()

    return candidate[start : end + 1].strip()


@dataclass
class AgentContext:
    user_id: str | None = None
    session_id: str | None = None
    user_profile: dict = field(default_factory=dict)
    chat_history: list[dict] = field(default_factory=list)
    params: dict[str, Any] = field(default_factory=dict)
    db_session: Any = None


@dataclass
class AgentResult:
    success: bool
    data: dict
    message_tr: str
    tokens_used: int = 0


class BaseAgent:
    name: str = "base_agent"
    system_prompt_path: str = ""

    def __init__(self, llm_client: HFInferenceClient | None = None):
        self.llm_client = llm_client or HFInferenceClient()

    def load_prompt(self, **kwargs: Any) -> str:
        if not self.system_prompt_path:
            return ""
        full_path = os.path.join(PROMPTS_DIR, self.system_prompt_path)
        with open(full_path, encoding="utf-8") as f:
            template = Template(f.read())
        return template.render(**kwargs)

    async def run(self, ctx: AgentContext) -> AgentResult:  # pragma: no cover - abstract
        raise NotImplementedError

    async def generate_json_with_fallback(
        self,
        prompt: str,
        fallback_fn: Callable[[], dict],
        validate_fn: Callable[[dict], bool] | None = None,
        max_tokens: int = 768,
        temperature: float = 0.5,
    ) -> tuple[dict, bool]:
        """Ortak "LLM dene -> JSON parse et -> doğrula, olmazsa heuristic'e düş"
        iskeleti (TASKS.md tekrar azaltma maddesi).

        Fine-tune model henüz hazır olmadığında veya HF Inference API
        hata/timeout/rate-limit döndürdüğünde sistemi bloke etmemek için
        `fallback_fn()` çağrılır ve loglanır.

        Dönüş: `(data, used_fallback)`. `used_fallback=True` olduğunda,
        çağıran ajan LLM başarı yolundan farklı post-processing (ör.
        GitHub dilleriyle zenginleştirme, heuristic skor hesaplama)
        uygulayabilir; bu yüzden ham veriyle birlikte bayrak da döndürülür.
        """
        try:
            llm_output = await self.llm_client.generate(
                prompt, max_tokens=max_tokens, temperature=temperature
            )
            parsed = json.loads(_extract_json_payload(llm_output))
            if validate_fn is not None and not validate_fn(parsed):
                raise ValueError("llm_output_validation_failed")
            return parsed, False
        except Exception:  # noqa: BLE001
            logger.warning(
                "%s: LLM çağrısı başarısız/atlandı, heuristik moda geçildi.", self.name
            )
            return fallback_fn(), True
