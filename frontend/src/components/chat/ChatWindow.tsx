import { useEffect, useRef } from 'react';
import { Sparkles } from 'lucide-react';
import { MessageBubble } from './MessageBubble';
import { Spinner } from '@/components/ui/Spinner';
import { tr } from '@/i18n/tr';
import type { ChatRole } from '@/types/chat';

export interface ChatMessageVM {
  id: string;
  role: ChatRole;
  content: string;
  agent_used?: string;
}

interface ChatWindowProps {
  messages: ChatMessageVM[];
  streamingMessageId?: string | null;
  isLoadingMessages?: boolean;
  onSuggestionSelect?: (text: string) => void;
}

function ChatHeroEmptyState({ onSuggestionSelect }: { onSuggestionSelect?: (text: string) => void }) {
  const suggestions = [tr.chat.suggestion1, tr.chat.suggestion2, tr.chat.suggestion3];
  return (
    <div className="relative flex flex-1 flex-col items-center justify-center overflow-hidden px-6 py-10 text-center">
      <Sparkles
        aria-hidden="true"
        className="pointer-events-none absolute h-56 w-56 text-primary-100 opacity-60 dark:text-primary-500/10"
      />
      <div className="relative flex h-16 w-16 items-center justify-center rounded-full bg-surface shadow-md">
        <Sparkles aria-hidden="true" className="h-7 w-7 text-primary-600 dark:text-primary-400" />
      </div>
      <h2 className="relative mt-4 text-lg font-semibold text-default">{tr.chat.heroTitle}</h2>
      <p className="relative mt-2 max-w-md text-sm text-muted">{tr.chat.heroSubtitle}</p>
      <div className="relative mt-5 flex flex-wrap justify-center gap-2">
        {suggestions.map((suggestion) => (
          <button
            key={suggestion}
            type="button"
            onClick={() => onSuggestionSelect?.(suggestion)}
            className="rounded-full border border-border bg-surface px-4 py-2 text-sm text-muted transition-colors hover:border-primary-300 hover:text-primary-700 dark:hover:text-primary-300"
          >
            "{suggestion}"
          </button>
        ))}
      </div>
    </div>
  );
}

export function ChatWindow({
  messages,
  streamingMessageId,
  isLoadingMessages,
  onSuggestionSelect,
}: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingMessageId]);

  if (isLoadingMessages) {
    return <Spinner label={tr.chat.loadingMessages} />;
  }

  if (messages.length === 0) {
    return <ChatHeroEmptyState onSuggestionSelect={onSuggestionSelect} />;
  }

  return (
    <div className="flex-1 space-y-3 overflow-y-auto p-4">
      {messages.map((message) => (
        <MessageBubble
          key={message.id}
          role={message.role}
          content={message.content}
          agentUsed={message.agent_used}
          isStreaming={message.id === streamingMessageId}
        />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
