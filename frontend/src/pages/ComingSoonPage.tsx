interface ComingSoonPageProps {
  title: string;
}

/**
 * Sprint 2/3'te implemente edilecek sayfalar için geçici yer tutucu.
 */
export function ComingSoonPage({ title }: ComingSoonPageProps) {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-gray-300 bg-white px-6 py-16 text-center">
      <h1 className="text-xl font-semibold text-gray-900">{title}</h1>
      <p className="mt-2 text-sm text-gray-500">Bu bölüm yakında kullanıma açılacak.</p>
    </div>
  );
}
