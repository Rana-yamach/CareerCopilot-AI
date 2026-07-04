"""Hugging Face Inference Providers wrapper (TASK-201).

`HF_MODEL_ID` env değişkeninden okunur. Fine-tune adaptörü hazır olana kadar
varsayılan `mistralai/Mistral-7B-Instruct-v0.2` (base model) kullanılır
(bkz. TASKS.md Genel Kurallar madde 3). Adaptör hazır olduğunda yalnızca
env değiştirilerek geçiş yapılır — kod değişikliği gerekmez.

Not: Eski `https://api-inference.huggingface.co/models/{model_id}` serverless
endpoint'i artık aktif değil (DNS çözümlenmiyor). Hugging Face inference'ı
"Inference Providers" sistemine taşıdı: tek sabit endpoint
(`https://router.huggingface.co/v1/chat/completions`), OpenAI chat-completions
şemasıyla birebir uyumlu. Model kimliğine hangi 3. parti sağlayıcının (ör.
`featherless-ai`) bu modeli barındırdığını belirten bir `:provider` eki
eklenmesi gerekir; bu eşleme HF tarafından dinamik yönetildiği için
`HF_INFERENCE_PROVIDER` env değişkeninden okunur, koda sabitlenmez.

- 30 saniye timeout (ARCHITECTURE.md §9.3)
- tenacity ile 3 deneme, exponential backoff
- 429 -> RateLimitError (Türkçe "sunucu yoğun" mesajı)
"""
from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import settings
from app.core.constants import MSG_LLM_BUSY, MSG_LLM_ERROR
from app.core.exceptions import LLMError, RateLimitError
from app.core.logging import get_logger

logger = get_logger(__name__)

HF_ROUTER_CHAT_COMPLETIONS_URL = "https://router.huggingface.co/v1/chat/completions"
REQUEST_TIMEOUT_SECONDS = 30.0


class TransientLLMError(Exception):
    """Retry edilebilir geçici hata (timeout, 5xx)."""


class HFInferenceClient:
    """Hugging Face Inference Providers (router) için async ince istemci."""

    def __init__(
        self,
        model_id: str | None = None,
        api_token: str | None = None,
        provider: str | None = None,
    ):
        self.model_id = model_id or settings.hf_model_id
        self.api_token = api_token or settings.hf_api_token
        self.provider = provider or settings.hf_inference_provider

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        return headers

    def _routed_model(self) -> str:
        """Router'ın hangi sağlayıcıya yönlendireceğini belirten model string'i.

        HF Inference Providers, hangi sağlayıcının hangi modeli barındırdığını
        dinamik yönettiğinden bu değer koda sabitlenmez; `HF_INFERENCE_PROVIDER`
        env değişkeninden gelir.
        """
        if not self.provider:
            return self.model_id
        return f"{self.model_id}:{self.provider}"

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type(TransientLLMError),
    )
    async def _post(self, payload: dict) -> httpx.Response:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
            try:
                response = await client.post(
                    HF_ROUTER_CHAT_COMPLETIONS_URL, headers=self._headers(), json=payload
                )
            except httpx.TimeoutException as exc:
                raise TransientLLMError("timeout") from exc
            except httpx.HTTPError as exc:
                raise TransientLLMError(str(exc)) from exc

        if response.status_code == 429:
            raise RateLimitError(MSG_LLM_BUSY)
        if response.status_code >= 500:
            raise TransientLLMError(f"HF 5xx: {response.status_code}")
        return response

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> str:
        """Prompt'u modele gönderir, tam metni döner (non-stream)."""
        if not self.api_token:
            logger.warning(
                "HF_API_TOKEN tanımlı değil; LLM çağrısı yapılamıyor (Sprint 2 placeholder davranışı)."
            )
            raise LLMError(MSG_LLM_ERROR)

        payload = {
            "model": self._routed_model(),
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        try:
            response = await self._post(payload)
        except RateLimitError:
            raise
        except TransientLLMError as exc:
            logger.error("HF Inference API'ye ulaşılamadı: %s", exc)
            raise LLMError(MSG_LLM_ERROR) from exc

        if response.status_code != 200:
            logger.error("HF Inference API hata döndü: %s - %s", response.status_code, response.text[:200])
            raise LLMError(MSG_LLM_ERROR)

        data = response.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            logger.error("HF Inference API beklenmeyen yanıt şeması döndürdü: %s", str(data)[:200])
            raise LLMError(MSG_LLM_ERROR) from None

    async def generate_stream(self, prompt: str, max_tokens: int = 1024) -> AsyncIterator[str]:
        """Router'dan gerçek SSE token akışı üretir.

        Router, OpenAI chat-completions SSE formatını kullanır: her satır
        `data: {...}` ile başlar, akış `data: [DONE]` ile biter. Her chunk'ın
        `choices[0].delta.content` alanı (varsa) yield edilir.

        Not (tenacity sınırlaması): `@retry` dekoratörü coroutine'leri sarmalayacak
        şekilde tasarlanmıştır; bir async generator'ı sarmalarsa yalnızca generator
        *nesnesinin oluşturulmasını* dener (gövde iterasyona kadar hiç çalışmaz),
        bu yüzden retry hiçbir zaman tetiklenmez. Bu yüzden burada tenacity yerine
        elle bir retry döngüsü kullanılır: yalnızca *hiç token akmadan* önce oluşan
        geçici hatalarda (bağlantı/timeout/5xx) yeniden denenir; akış başladıktan
        sonra bir hata oluşursa (kullanıcıya kısmi metin gitmiş olabileceğinden)
        akış tekrar baştan başlatılmaz, doğrudan `LLMError` fırlatılır.
        """
        if not self.api_token:
            logger.warning(
                "HF_API_TOKEN tanımlı değil; LLM çağrısı yapılamıyor (Sprint 2 placeholder davranışı)."
            )
            raise LLMError(MSG_LLM_ERROR)

        payload = {
            "model": self._routed_model(),
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "stream": True,
        }

        max_attempts = 3
        delay = 1.0
        yielded_any = False
        for attempt in range(1, max_attempts + 1):
            try:
                async for token in self._stream_once(payload):
                    yielded_any = True
                    yield token
                return
            except RateLimitError:
                raise
            except LLMError:
                raise
            except TransientLLMError as exc:
                if yielded_any or attempt >= max_attempts:
                    logger.error("HF Inference API stream'ine ulaşılamadı: %s", exc)
                    raise LLMError(MSG_LLM_ERROR) from exc
                logger.warning(
                    "HF stream geçici hata (deneme %s/%s): %s", attempt, max_attempts, exc
                )
                await asyncio.sleep(delay)
                delay = min(delay * 2, 8)

    async def _stream_once(self, payload: dict) -> AsyncIterator[str]:
        """Router'a tek bir SSE stream isteği açar (retry içermez)."""
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
            try:
                async with client.stream(
                    "POST", HF_ROUTER_CHAT_COMPLETIONS_URL, headers=self._headers(), json=payload
                ) as response:
                    if response.status_code == 429:
                        raise RateLimitError(MSG_LLM_BUSY)
                    if response.status_code >= 500:
                        raise TransientLLMError(f"HF 5xx: {response.status_code}")
                    if response.status_code != 200:
                        body = await response.aread()
                        logger.error(
                            "HF Inference API hata döndü: %s - %s", response.status_code, body[:200]
                        )
                        raise LLMError(MSG_LLM_ERROR)

                    async for line in response.aiter_lines():
                        if not line or not line.startswith("data:"):
                            continue
                        data_str = line[len("data:"):].strip()
                        if data_str == "[DONE]":
                            return
                        try:
                            chunk = json.loads(data_str)
                        except json.JSONDecodeError:
                            continue
                        try:
                            delta = chunk["choices"][0]["delta"]
                        except (KeyError, IndexError, TypeError):
                            continue
                        content = delta.get("content")
                        if content:
                            yield content
            except httpx.TimeoutException as exc:
                raise TransientLLMError("timeout") from exc
            except httpx.HTTPError as exc:
                raise TransientLLMError(str(exc)) from exc
