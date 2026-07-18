import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Lock } from 'lucide-react';

export function AdminLogin({ onLogin }: { onLogin: () => void }) {
  const [token, setToken] = useState('');
  const [error, setError] = useState('');

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (!token.trim()) {
      setError('Token is required');
      return;
    }
    localStorage.setItem('adminToken', token.trim());
    onLogin();
  };

  return (
    <div className="flex items-center justify-center py-20 px-4">
      <Card className="w-full max-w-md shadow-lg border border-gray-200 dark:border-zinc-800">
        <CardHeader className="text-center pb-6">
          <div className="mx-auto w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center mb-4">
            <Lock className="w-6 h-6 text-blue-600 dark:text-blue-400" />
          </div>
          <CardTitle className="text-2xl font-bold text-gray-900 dark:text-gray-100">Admin Access</CardTitle>
          <CardDescription className="text-gray-500 dark:text-gray-400 mt-2">Enter your admin token to access the dashboard</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleLogin} className="space-y-4">
            <div className="space-y-2">
              <input
                type="password"
                placeholder="Admin Token"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                className="w-full px-4 py-3 border border-gray-200 dark:border-zinc-700 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-zinc-900 text-gray-900 dark:text-gray-100"
              />
            </div>
            {error && <p className="text-sm text-red-500 font-medium">{error}</p>}
            <button
              type="submit"
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-md transition-colors shadow-sm"
            >
              Login to Dashboard
            </button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
