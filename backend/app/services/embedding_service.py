"""Embedding servisi (TASK-146): sentence-transformers/all-MiniLM-L6-v2.

HF Inference Providers'ın (hf-inference) feature-extraction endpoint'i
üzerinden uzaktan çağrılır. Daha önce bu model yerel `sentence-transformers`
+ `torch` ile process içinde yükleniyordu; bu, aynı container'da çalışan
FastAPI + Celery worker ile birlikte bellek kullanımını Render'ın ücretsiz
katmanındaki 512 MB sınırının üzerine çıkarıp OOM'a (container'ın bellek
yetersizliğinden öldürülüp yeniden başlatılmasına) yol açtığı için uzak API
çağrısına taşındı.
"""
from __future__ import annotations

import httpx

from app.config import settings
from app.core.constants import MSG_LLM_ERROR
from app.core.exceptions import LLMError
from app.core.logging import get_logger

logger = get_logger(__name__)

EMBEDDING_DIM = 384

_FEATURE_EXTRACTION_URL = (
    "https://router.huggingface.co/hf-inference/models/{model_id}/pipeline/feature-extraction"
)
_REQUEST_TIMEOUT_SECONDS = 30.0


async def encode(texts: str | list[str]) -> list[list[float]]:
    """Metin(ler)i 384 boyutlu embedding vektörüne dönüştürür (HF Inference Providers üzerinden)."""
    single = isinstance(texts, str)
    inputs = [texts] if single else texts
    if not inputs:
        return []

    url = _FEATURE_EXTRACTION_URL.format(model_id=settings.embedding_model_id)
    headers = {"Authorization": f"Bearer {settings.hf_api_token}"} if settings.hf_api_token else {}

    try:
        async with httpx.AsyncClient(timeout=_REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.post(url, headers=headers, json={"inputs": inputs, "normalize": True})
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError:
        logger.exception("Embedding API çağrısı başarısız oldu.")
        raise LLMError(MSG_LLM_ERROR) from None


async def encode_one(text: str) -> list[float]:
    vectors = await encode([text])
    return vectors[0] if vectors else [0.0] * EMBEDDING_DIM
