import { useCallback, useRef, useState } from 'react';
import { config } from '@/config';
import { useAuthStore } from '@/store/authStore';
import { tr } from '@/i18n/tr';
import type { ChatErrorEvent, ChatMetadataEvent, SendChatMessageRequest } from '@/types/chat';

interface UseSSEHandlers {
  onMetadata?: (data: ChatMetadataEvent) => void;
  onToken?: (token: string) => void;
  onDone?: () => void;
  onError?: (error: ChatErrorEvent) => void;
}

/**
 * `POST /agent/chat` SSE tüketimi. `EventSource` `Authorization` header'ı
 * desteklemediği için (bkz. ARCHITECTURE.md §6.3, §8.1) `fetch` +
 * `ReadableStream` kullanılır. Event bloklari boş satırla (`\n\n`) ayrılır;
 * `event:` satırı tipi, `data:` satırı payload'ı belirtir.
 */
export function useSSE() {
  const [isStreaming, setIsStreaming] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const cancel = useCallback(() => {
    abortRef.current?.abort();
  }, []);

  const send = useCallback(async (payload: SendChatMessageRequest, handlers: UseSSEHandlers) => {
    const controller = new AbortController();
    abortRef.current = controller;
    setIsStreaming(true);

    function processEvent(rawEvent: string) {
      const lines = rawEvent.split('\n');
      let eventType = 'message';
      const dataLines: string[] = [];
      for (const line of lines) {
        if (line.startsWith('event:')) {
          eventType = line.slice('event:'.length).trim();
        } else if (line.startsWith('data:')) {
          dataLines.push(line.slice('data:'.length).trim());
        }
      }
      const dataStr = dataLines.join('\n');
      if (!dataStr) return;

      if (eventType === 'done') {
        handlers.onDone?.();
        return;
      }
      if (eventType === 'error') {
        try {
          handlers.onError?.(JSON.parse(dataStr) as ChatErrorEvent);
        } catch {
          handlers.onError?.({ code: 'PARSE_ERROR', message: dataStr });
        }
        return;
      }
      if (eventType === 'metadata') {
        try {
          handlers.onMetadata?.(JSON.parse(dataStr) as ChatMetadataEvent);
        } catch {
          // yoksay: bozuk metadata event'i akışı durdurmamalı
        }
        return;
      }
      // Öntanımlı (event satırı olmayan) event'ler token akışıdır.
      try {
        const parsed = JSON.parse(dataStr) as { token?: string };
        if (typeof parsed.token === 'string') {
          handlers.onToken?.(parsed.token);
        }
      } catch {
        // yoksay: bozuk token event'i akışı durdurmamalı
      }
    }

    try {
      const accessToken = useAuthStore.getState().accessToken;
      const response = await fetch(`${config.apiBaseUrl}/agent/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
        },
        body: JSON.stringify(payload),
        signal: controller.signal,
      });

      if (!response.ok || !response.body) {
        let message: string = tr.chat.errorSending;
        try {
          const body = (await response.json()) as { error?: { message?: string } };
          if (body?.error?.message) message = body.error.message;
        } catch {
          // response gövdesi JSON değilse öntanımlı mesaj kullanılır
        }
        handlers.onError?.({ code: String(response.status), message });
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      for (;;) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        let boundary = buffer.indexOf('\n\n');
        while (boundary !== -1) {
          const rawEvent = buffer.slice(0, boundary);
          buffer = buffer.slice(boundary + 2);
          processEvent(rawEvent);
          boundary = buffer.indexOf('\n\n');
        }
      }
    } catch (error) {
      if ((error as Error).name !== 'AbortError') {
        handlers.onError?.({ code: 'NETWORK_ERROR', message: tr.common.networkError });
      }
    } finally {
      setIsStreaming(false);
    }
  }, []);

  return { send, cancel, isStreaming };
}
