interface SpinnerProps {
  label?: string;
  size?: 'sm' | 'md' | 'lg';
}

const sizeClass: Record<NonNullable<SpinnerProps['size']>, string> = {
  sm: 'h-4 w-4 border-2',
  md: 'h-8 w-8 border-2',
  lg: 'h-12 w-12 border-4',
};

export function Spinner({ label, size = 'md' }: SpinnerProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-8" role="status">
      <span
        className={`animate-spin rounded-full border-primary-600 border-t-transparent ${sizeClass[size]}`}
        aria-hidden="true"
      />
      {label && <p className="text-sm text-gray-600">{label}</p>}
    </div>
  );
}
