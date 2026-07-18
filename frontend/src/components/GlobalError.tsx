import React from 'react';
import { useRouteError, Link } from 'react-router-dom';
import { AlertTriangle, Home } from 'lucide-react';

export function GlobalError() {
  const error = useRouteError();
  const errorMessage = error instanceof Error ? error.message : (error as any)?.statusText || 'An unexpected error occurred.';

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-zinc-950 p-4">
      <div className="max-w-md w-full bg-white dark:bg-zinc-900 border border-red-200 dark:border-red-900/50 rounded-xl p-8 shadow-sm text-center">
        <AlertTriangle size={48} className="mx-auto text-red-500 mb-6" />
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">Something went wrong</h1>
        <p className="text-gray-500 dark:text-gray-400 mb-6">
          {errorMessage}
        </p>
        <Link 
          to="/"
          className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring bg-blue-600 text-white shadow hover:bg-blue-700 h-10 px-6 py-2"
        >
          <Home size={16} className="mr-2" />
          Return to Dashboard
        </Link>
      </div>
    </div>
  );
}
