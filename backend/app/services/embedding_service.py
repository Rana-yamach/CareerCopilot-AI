"""Embedding servisi (TASK-146): sentence-transformers/all-MiniLM-L6-v2.

Model process başına bir kez (singleton) yüklenir. Sprint 2 RAG akışında
(Skill Gap Agent, seed script) kullanılır.
"""
from __future__ import annotations

import threading

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_model = None
_model_lock = threading.Lock()

EMBEDDING_DIM = 384


def _get_model():
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                # Import burada yapılır: sentence-transformers/torch yükleme maliyeti
                # yalnızca ilk gerçek kullanımda ödenir (worker/app start-up hızlı kalır).
                from sentence_transformers import SentenceTransformer

                logger.info("Embedding modeli yükleniyor: %s", settings.embedding_model_id)
                _model = SentenceTransformer(settings.embedding_model_id)
    return _model


def encode(texts: str | list[str]) -> list[list[float]]:
    """Metin(ler)i 384 boyutlu embedding vektörüne dönüştürür."""
    single = isinstance(texts, str)
    inputs = [texts] if single else texts
    if not inputs:
        return []

    model = _get_model()
    vectors = model.encode(inputs, convert_to_numpy=True, normalize_embeddings=True)
    return [vector.tolist() for vector in vectors]


def encode_one(text: str) -> list[float]:
    vectors = encode([text])
    return vectors[0] if vectors else [0.0] * EMBEDDING_DIM
