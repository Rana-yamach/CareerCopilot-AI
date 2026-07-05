"""SSE event formatlama yardımcıları (`/agent/chat` için)."""
from __future__ import annotations

import json


def sse_event(data: dict, event: str | None = None) -> str:
    lines = []
    if event:
        lines.append(f"event: {event}")
    lines.append(f"data: {json.dumps(data, ensure_ascii=False)}")
    return "\n".join(lines) + "\n\n"


def sse_done() -> str:
    return "event: done\ndata: [DONE]\n\n"


def sse_error(code: str, message: str) -> str:
    return sse_event({"code": code, "message": message}, event="error")
