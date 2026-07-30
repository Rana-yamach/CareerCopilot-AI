from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from huggingface_hub import AsyncInferenceClient
import os
import json

router = APIRouter()

# Hugging Face Async İstemcisi
hf_client = AsyncInferenceClient(
    model=os.getenv("HF_MODEL_ID", "mistralai/Mistral-7B-Instruct-v0.2"),
    token=os.getenv("HF_API_TOKEN")
)

async def generate_token_stream(user_message: str):
    """LLM'den gelen her kelimeyi (token) anında Frontend'e SSE olarak gönderir."""
    
    # API Kontratına uygun ilk metadata event'i
    yield f"event: metadata\ndata: {json.dumps({'agent': 'orchestrator'})}\n\n"
    
    # Mistral-7B formata uygun prompt (Türkçe kalması için zorlama)
    prompt = f"<s>[INST] Sen Türkçe konuşan bir kariyer asistanısın. Sadece Türkçe yanıt ver. Kullanıcı: {user_message} [/INST]"
    
    try:
        # Gerçek zamanlı akış (streaming)
        async for chunk in hf_client.text_generation(prompt, stream=True, max_new_tokens=512):
            if chunk:
                # SSE formatında token gönderimi
                yield f"data: {json.dumps({'token': chunk})}\n\n"
        
        # Bitiş event'i
        yield "event: done\ndata: {}\n\n"
    except Exception as e:
        yield f"event: error\ndata: {json.dumps({'message': str(e)})}\n\n"

@router.post("/agent/chat/stream")
async def chat_stream_endpoint(payload: dict):
    """Frontend'in fetch + ReadableStream ile bağlanacağı endpoint."""
    user_msg = payload.get("message", "")
    return StreamingResponse(
        generate_token_stream(user_msg), 
        media_type="text/event-stream"
    )
