import { Link } from 'react-router-dom';

export function NotFoundPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-3 bg-gray-50 text-center">
      <h1 className="text-3xl font-semibold text-gray-900">404</h1>
      <p className="text-sm text-gray-500">Aradığınız sayfa bulunamadı.</p>
      <Link to="/dashboard" className="btn-primary">
        Panele Dön
      </Link>
    </div>
  );
}
