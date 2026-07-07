import type { ReactNode } from 'react';
import { tr } from '@/i18n/tr';

interface ItemCardProps {
  index: number;
  onRemove: () => void;
  children: ReactNode;
}

export function ItemCard({ index, onRemove, children }: ItemCardProps) {
  return (
    <div className="relative rounded-xl border border-border bg-surface-2/40 p-4">
      <button
        type="button"
        onClick={onRemove}
        aria-label={`${tr.cvBuilder.removeItem} ${index + 1}`}
        className="absolute right-3 top-3 text-xs font-medium text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
      >
        {tr.cvBuilder.removeItem}
      </button>
      <div className="grid grid-cols-1 gap-3 pr-16 sm:grid-cols-2">{children}</div>
    </div>
  );
}
