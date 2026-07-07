interface ComingSoonPageProps {
  title: string;
}

/**
 * Sprint 2/3'te implemente edilecek sayfalar için geçici yer tutucu.
 */
export function ComingSoonPage({ title }: ComingSoonPageProps) {
  return (
    <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-border bg-surface px-6 py-16 text-center">
      <h1 className="text-xl font-semibold text-default">{title}</h1>
      <p className="mt-2 text-sm text-faint">Bu bölüm yakında kullanıma açılacak.</p>
    </div>
  );
}
