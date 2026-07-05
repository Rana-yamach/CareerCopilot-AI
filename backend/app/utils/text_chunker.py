"""RAG için metin chunk'lama (ARCHITECTURE.md §9.4).

chunk_size=500 karakter, overlap=50 karakter. Paragraf sınırlarında
bölmeye öncelik verir (\n\n).
"""
from __future__ import annotations

import re

PARAGRAPH_SPLIT_RE = re.compile(r"\n\s*\n")


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[dict]:
    """Metni {content, chunk_index} sözlük listesine böler."""
    text = (text or "").strip()
    if not text:
        return []

    paragraphs = [p.strip() for p in PARAGRAPH_SPLIT_RE.split(text) if p.strip()]
    if not paragraphs:
        paragraphs = [text]

    chunks: list[str] = []
    buffer = ""

    for paragraph in paragraphs:
        candidate = f"{buffer}\n\n{paragraph}".strip() if buffer else paragraph
        if len(candidate) <= chunk_size:
            buffer = candidate
            continue

        if buffer:
            chunks.append(buffer)
        if len(paragraph) <= chunk_size:
            buffer = paragraph
        else:
            # Paragraf tek başına chunk_size'dan büyükse karakter bazlı böl.
            start = 0
            while start < len(paragraph):
                end = start + chunk_size
                chunks.append(paragraph[start:end])
                start = end - overlap if end - overlap > start else end
            buffer = ""

    if buffer:
        chunks.append(buffer)

    # Overlap uygulaması: her chunk'ın başına bir önceki chunk'ın son `overlap`
    # karakterini ekle (ilk chunk hariç).
    overlapped: list[str] = []
    for idx, chunk in enumerate(chunks):
        if idx == 0 or overlap <= 0:
            overlapped.append(chunk)
        else:
            prefix = overlapped[idx - 1][-overlap:]
            overlapped.append((prefix + chunk)[: chunk_size + overlap])

    return [{"content": c, "chunk_index": i} for i, c in enumerate(overlapped)]
