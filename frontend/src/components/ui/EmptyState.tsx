import type { ReactNode } from 'react';

interface EmptyStateProps {
  title: string;
  description?: string;
  action?: ReactNode;
}

export function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-border bg-surface px-6 py-10 text-center">
      <p className="text-base font-medium text-default">{title}</p>
      {description && <p className="mt-1 text-sm text-faint">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
