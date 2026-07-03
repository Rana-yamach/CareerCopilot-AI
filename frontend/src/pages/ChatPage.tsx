import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { getChatSessions, getSessionMessages } from '@/api/chat';
import { useSSE } from '@/hooks/useSSE';
import { ChatWindow } from '@/components/chat/ChatWindow';
import type { ChatMessageVM } from '@/components/chat/ChatWindow';
import { Button } from '@/components/ui/Button';
import { Spinner } from '@/components/ui/Spinner';
import { tr } from '@/i18n/tr';

function newId(): string {
  return typeof crypto !== 'undefined' && 'randomUUID' in crypto
    ? crypto.randomUUID()
    : `id-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

/**
 * Orkestratör ajan ile SSE tabanlı sohbet (bkz. API_CONTRACT.md §9, TASK-234).
 */
export function ChatPage() {
  const queryClient = useQueryClient();
  const sse = useSSE();

  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessageVM[]>([]);
  const [streamingMessageId, setStreamingMessageId] = useState<string | null>(null);
  const [input, setInput] = useState('');

  const sessionsQuery = useQuery({
    queryKey: ['chatSessions'],
    queryFn: getChatSessions,
  });

  const messagesQuery = useQuery({
    queryKey: ['chatMessages', currentSessionId],
    queryFn: () => getSessionMessages(currentSessionId as string),
    enabled: !!currentSessionId,
  });

  useEffect(() => {
    if (!currentSessionId) return;
    if (messagesQuery.data) {
      setMessages(
        messagesQuery.data.messages.map((message) => ({
          id: message.message_id,
          role: message.role,
          content: message.content,
          agent_used: message.agent_used,
        })),
      );
    }
  }, [currentSessionId, messagesQuery.data]);

  function handleSelectSession(sessionId: string) {
    if (sessionId === currentSessionId) return;
    sse.cancel();
    setStreamingMessageId(null);
    setCurrentSessionId(sessionId);
  }

  function handleNewSession() {
    sse.cancel();
    setStreamingMessageId(null);
    setCurrentSessionId(null);
    setMessages([]);
  }

  async function handleSend(event: FormEvent) {
    event.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || sse.isStreaming) return;

    const userMessage: ChatMessageVM = { id: newId(), role: 'user', content: trimmed };
    const assistantId = newId();
    setMessages((prev) => [...prev, userMessage]);
    setInput('');

    await sse.send(
      { message: trimmed, session_id: currentSessionId },
      {
        onMetadata: (data) => {
          setCurrentSessionId(data.session_id);
          setMessages((prev) => [
            ...prev,
            { id: assistantId, role: 'assistant', content: '', agent_used: data.agent },
          ]);
          setStreamingMessageId(assistantId);
        },
        onToken: (token) => {
          setMessages((prev) =>
            prev.map((message) =>
              message.id === assistantId
                ? { ...message, content: message.content + token }
                : message,
            ),
          );
        },
        onDone: () => {
          setStreamingMessageId(null);
          queryClient.invalidateQueries({ queryKey: ['chatSessions'] });
        },
        onError: (error) => {
          toast.error(error.message || tr.chat.errorSending);
          setStreamingMessageId(null);
        },
      },
    );
  }

  const sessions = sessionsQuery.data?.sessions ?? [];

  return (
    <div className="flex h-[calc(100vh-8rem)] flex-col gap-4 sm:flex-row">
      {/* Masaüstü oturum listesi */}
      <aside className="hidden w-64 shrink-0 flex-col overflow-hidden rounded-xl border border-gray-200 bg-white sm:flex">
        <div className="flex items-center justify-between border-b border-gray-200 p-3">
          <h2 className="text-sm font-semibold text-gray-900">{tr.chat.sessionsTitle}</h2>
          <Button variant="secondary" className="!px-2 !py-1 text-xs" onClick={handleNewSession}>
            {tr.chat.newSession}
          </Button>
        </div>
        <div className="flex-1 overflow-y-auto p-2">
          {sessionsQuery.isLoading && <Spinner size="sm" label={tr.common.loading} />}
          {!sessionsQuery.isLoading && sessions.length === 0 && (
            <p className="p-2 text-sm text-gray-500">{tr.chat.noSessions}</p>
          )}
          {sessions.map((session) => (
            <button
              key={session.session_id}
              type="button"
              onClick={() => handleSelectSession(session.session_id)}
              className={`mb-1 block w-full rounded-lg px-3 py-2 text-left text-sm transition-colors ${
                session.session_id === currentSessionId
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <p className="truncate font-medium">{session.last_message_preview}</p>
              <p className="text-xs text-gray-400">{session.message_count} mesaj</p>
            </button>
          ))}
        </div>
      </aside>

      {/* Mobil oturum seçici */}
      <div className="flex items-center gap-2 sm:hidden">
        <select
          className="input-field"
          value={currentSessionId ?? ''}
          onChange={(event) => {
            if (event.target.value) handleSelectSession(event.target.value);
          }}
        >
          <option value="">{tr.chat.newSession}</option>
          {sessions.map((session) => (
            <option key={session.session_id} value={session.session_id}>
              {session.last_message_preview}
            </option>
          ))}
        </select>
        <Button variant="secondary" onClick={handleNewSession}>
          {tr.chat.newSession}
        </Button>
      </div>

      <div className="flex flex-1 flex-col overflow-hidden rounded-xl border border-gray-200 bg-white">
        <ChatWindow
          messages={messages}
          streamingMessageId={streamingMessageId}
          isLoadingMessages={!!currentSessionId && messagesQuery.isLoading}
        />
        <form onSubmit={handleSend} className="flex items-center gap-2 border-t border-gray-200 p-3">
          <input
            type="text"
            className="input-field"
            placeholder={tr.chat.inputPlaceholder}
            value={input}
            onChange={(event) => setInput(event.target.value)}
            disabled={sse.isStreaming}
          />
          <Button type="submit" isLoading={sse.isStreaming} disabled={!input.trim()}>
            {sse.isStreaming ? tr.chat.sending : tr.chat.send}
          </Button>
        </form>
      </div>
    </div>
  );
}
