import React from 'react';
import { useEval } from '../hooks/useEval';
import { CheckCircle, XCircle, Activity, Play } from 'lucide-react';

export function Evaluation() {
  const { data, isLoading, isFetching, refetch, isError, error } = useEval();
  
  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">System Evaluation</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Run automated tests against the Ask AI knowledge base to evaluate RAG accuracy and hallucination prevention.
          </p>
        </div>
        <button
          onClick={() => refetch()}
          disabled={isLoading || isFetching}
          className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm"
        >
          {isFetching ? <Activity className="animate-spin" size={18} /> : <Play size={18} />}
          {isFetching ? 'Running Tests...' : 'Run Evaluation'}
        </button>
      </div>

      {isError && (
        <div className="bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 p-6 rounded-xl border border-red-200 dark:border-red-900/30">
          <h3 className="font-bold mb-2 flex items-center gap-2">
            <XCircle size={20} />
            Evaluation Failed
          </h3>
          <p>
            The evaluation request failed. This usually happens if the backend takes longer than the API timeout limit, or if the server crashed.
          </p>
          <p className="mt-2 text-sm opacity-80">{error instanceof Error ? error.message : String(error)}</p>
        </div>
      )}

      {data && (
        <div className="bg-white dark:bg-zinc-900 shadow-sm rounded-xl overflow-hidden border border-gray-200 dark:border-zinc-800">
          <div className="p-6 border-b border-gray-200 dark:border-zinc-800 bg-gray-50 dark:bg-zinc-800/30 flex justify-between items-center">
            <div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Results Summary</h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">Tested against {data.total_tests} predefined use cases.</p>
            </div>
            <div className={`px-4 py-2 rounded-lg font-bold text-lg flex items-center gap-2 ${data.score_percentage === 100 ? 'bg-green-100 text-green-800 dark:bg-green-500/20 dark:text-green-400' : 'bg-amber-100 text-amber-800 dark:bg-amber-500/20 dark:text-amber-400'}`}>
              Score: {data.score_percentage.toFixed(0)}% 
              <span className="text-sm opacity-80 font-medium ml-1">({data.passed_count}/{data.total_tests})</span>
            </div>
          </div>
          
          <ul className="divide-y divide-gray-100 dark:divide-zinc-800/60">
            {data.results.map((result) => (
              <li key={result.id} className="p-6 hover:bg-gray-50/50 dark:hover:bg-zinc-800/20 transition-colors">
                <div className="flex items-start gap-4">
                  <div className="mt-1 flex-shrink-0">
                    {result.passed ? (
                      <CheckCircle className="text-green-500 dark:text-green-400" size={24} />
                    ) : (
                      <XCircle className="text-red-500 dark:text-red-400" size={24} />
                    )}
                  </div>
                  <div className="flex-1 min-w-0 space-y-3">
                    <div className="flex items-center justify-between gap-4">
                      <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100 truncate">{result.description}</h3>
                      <span className={`flex-shrink-0 text-xs font-semibold px-2.5 py-1 rounded-full ${result.passed ? 'bg-green-100 text-green-700 dark:bg-green-500/10 dark:text-green-400' : 'bg-red-100 text-red-700 dark:bg-red-500/10 dark:text-red-400'}`}>
                        {result.passed ? 'PASSED' : 'FAILED'}
                      </span>
                    </div>
                    
                    <div className="bg-gray-100 dark:bg-zinc-950/50 p-4 rounded-lg text-sm text-gray-800 dark:text-gray-200 font-medium">
                      <span className="text-blue-600 dark:text-blue-400 mr-2">Q:</span> 
                      {result.question}
                    </div>
                    
                    {result.error ? (
                      <div className="text-red-500 text-sm bg-red-50 dark:bg-red-900/10 p-3 rounded-lg border border-red-100 dark:border-red-900/30">
                        Error: {result.error}
                      </div>
                    ) : (
                      <div className="text-sm space-y-1">
                        <p className="font-semibold text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider">AI Answer</p>
                        <p className="text-gray-700 dark:text-gray-300 leading-relaxed">{result.answer}</p>
                      </div>
                    )}
                    
                    {!result.passed && !result.error && (
                      <div className="text-sm mt-3 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 p-3 rounded-lg border border-red-100 dark:border-red-900/30 flex items-start gap-2">
                        <XCircle size={16} className="mt-0.5 flex-shrink-0 opacity-70" />
                        <div>
                          <strong className="block mb-1">Reason for failure:</strong>
                          {result.expect_refusal 
                            ? "Expected the model to refuse to answer (hallucination prevention), but it attempted to provide an answer."
                            : `Expected the answer to contain at least one of these keywords: ${result.expected_keywords.join(', ')}`}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
