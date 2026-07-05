import { useEffect, useRef } from 'react';
import { MessageBubble } from './MessageBubble';
import { EmptyState } from '@/components/ui/EmptyState';
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
}

export function ChatWindow({ messages, streamingMessageId, isLoadingMessages }: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingMessageId]);

  if (isLoadingMessages) {
    return <Spinner label={tr.chat.loadingMessages} />;
  }

  if (messages.length === 0) {
    return <EmptyState title={tr.chat.noMessages} />;
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
