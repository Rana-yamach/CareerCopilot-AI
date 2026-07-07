import { StreamingText } from './StreamingText';
import { tr } from '@/i18n/tr';
import type { ChatRole } from '@/types/chat';

interface MessageBubbleProps {
  role: ChatRole;
  content: string;
  agentUsed?: string;
  isStreaming?: boolean;
}

function agentLabel(agentUsed?: string): string | null {
  if (!agentUsed) return null;
  const labels = tr.chat.agentLabels as Record<string, string>;
  return labels[agentUsed] ?? agentUsed;
}

export function MessageBubble({ role, content, agentUsed, isStreaming }: MessageBubbleProps) {
  const isUser = role === 'user';
  const label = agentLabel(agentUsed);

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm shadow-sm ${
          isUser
            ? 'bg-primary-700 text-white shadow-primary-600/20'
            : 'border border-border bg-surface-2 text-default'
        }`}
      >
        {!isUser && label && (
          <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-primary-600 dark:text-primary-400">
            {label}
          </p>
        )}
        <StreamingText text={content} isStreaming={isStreaming} />
      </div>
    </div>
  );
}
