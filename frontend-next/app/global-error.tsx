'use client';

import { useEffect } from 'react';
import Link from 'next/link';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('Global error:', error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 px-4">
      <div className="text-center max-w-md">
        <h1 className="text-5xl font-bold text-red-600 mb-4">Error</h1>
        <h2 className="text-xl font-semibold text-gray-800 mb-2">Algo salió mal</h2>
        <p className="text-gray-500 mb-6">
          Ocurrió un error inesperado. Por favor intenta nuevamente.
        </p>
        <div className="flex gap-3 justify-center">
          <button
            onClick={reset}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            Reintentar
          </button>
          <Link
            href="/dashboard"
            className="inline-flex items-center px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300 transition-colors"
          >
            Dashboard
          </Link>
        </div>
        {error.digest && (
          <p className="mt-4 text-xs text-gray-400">
            ID: {error.digest}
          </p>
        )}
      </div>
    </div>
  );
}
