import { Button } from './Button';
import { tr } from '@/i18n/tr';

interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
}

export function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div className="rounded-2xl border border-red-200 bg-red-50 px-6 py-8 text-center dark:border-red-900/40 dark:bg-red-950/40">
      <p className="text-sm font-medium text-red-700 dark:text-red-300">
        {message ?? tr.common.genericError}
      </p>
      {onRetry && (
        <Button variant="secondary" className="mt-4" onClick={onRetry}>
          {tr.common.tryAgain}
        </Button>
      )}
    </div>
  );
}
