import React from 'react';
import { useRecentNews, useNewsStatistics } from '../hooks/useNews';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Skeleton } from '../components/ui/skeleton';
import { ExternalLink, BrainCircuit, Newspaper, Activity, AlertCircle } from 'lucide-react';
import { Link } from 'react-router-dom';

export function GlobalNews() {
  const { data: news, isLoading: newsLoading } = useRecentNews(20);
  const { data: stats, isLoading: statsLoading } = useNewsStatistics();

  return (
    <div className="space-y-8 animate-in fade-in duration-500 pb-20">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-gray-900 dark:text-gray-100 flex items-center gap-3">
          <Newspaper className="text-blue-500" />
          Industry News
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mt-2">Latest intelligence across all monitored F&B companies.</p>
      </div>

      <div className="grid md:grid-cols-4 gap-6">
        <div className="md:col-span-1 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Activity size={18} className="text-orange-500" />
                Pipeline Stats
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {statsLoading ? (
                <div className="space-y-2">
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-4 w-5/6" />
                </div>
              ) : stats ? (
                <>
                  <div className="flex justify-between items-center py-2 border-b border-gray-100 dark:border-zinc-800">
                    <span className="text-sm font-medium text-gray-500">Total Articles</span>
                    <span className="text-sm font-bold">{stats.total_articles}</span>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b border-gray-100 dark:border-zinc-800">
                    <span className="text-sm font-medium text-gray-500">Last 24h</span>
                    <Badge variant="secondary" className="bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">+{stats.articles_last_24h}</Badge>
                  </div>
                  
                  <div className="pt-2">
                    <span className="text-xs font-semibold uppercase tracking-wider text-gray-500 block mb-3">Top Sources</span>
                    <div className="space-y-2">
                      {Object.entries(stats.articles_by_provider || {}).slice(0, 5).map(([provider, count]) => (
                        <div key={provider} className="flex justify-between items-center text-sm">
                          <span className="text-gray-700 dark:text-gray-300 capitalize">{provider}</span>
                          <span className="text-gray-500">{count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </>
              ) : (
                <div className="text-center text-gray-500 text-sm">Stats unavailable</div>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="md:col-span-3">
          {newsLoading ? (
            <div className="space-y-4">
              <Skeleton className="h-40 w-full rounded-xl" />
              <Skeleton className="h-40 w-full rounded-xl" />
              <Skeleton className="h-40 w-full rounded-xl" />
            </div>
          ) : news && news.length > 0 ? (
            <div className="space-y-4">
              {news.map((item) => (
                <Card key={item.id} className="hover:shadow-md transition-shadow">
                  <CardHeader className="pb-2">
                    <div className="flex justify-between items-start gap-4">
                      <div>
                        <Badge variant="outline" className="mb-2 bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-900/30 dark:text-blue-400 dark:border-blue-900/50">
                          Company ID: {item.company_id}
                        </Badge>
                        <CardTitle className="text-lg leading-tight">
                          <a href={item.url || '#'} target="_blank" rel="noopener noreferrer" className="hover:text-blue-600 transition-colors inline-flex items-center">
                            {item.headline}
                            <ExternalLink size={14} className="ml-2 text-gray-400 shrink-0" />
                          </a>
                        </CardTitle>
                      </div>
                      <span className="text-xs text-gray-500 whitespace-nowrap bg-gray-100 dark:bg-zinc-800 px-2 py-1 rounded-md shrink-0">
                        {item.published_at ? new Date(item.published_at).toLocaleDateString() : 'Unknown date'}
                      </span>
                    </div>
                  </CardHeader>
                  <CardContent>
                    {item.summary ? (
                      <div className="bg-blue-50/50 dark:bg-blue-900/10 p-4 rounded-lg border border-blue-100 dark:border-blue-900/30">
                        <div className="flex items-center gap-2 mb-2 text-blue-700 dark:text-blue-400 text-xs font-semibold uppercase tracking-wider">
                          <BrainCircuit size={14} />
                          AI Summary
                        </div>
                        <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                          {item.summary}
                        </p>
                      </div>
                    ) : (
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        No summary available.
                      </p>
                    )}
                    <div className="flex items-center gap-4 mt-4">
                      <Badge variant="outline" className="text-xs text-gray-500">
                        Source: {item.provider || item.source || 'Unknown'}
                      </Badge>
                      {item.relevance_score !== null && (
                        <Badge variant="outline" className="text-xs text-gray-500">
                          Relevance: {Math.round(item.relevance_score * 100)}%
                        </Badge>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <div className="text-center py-20 bg-white dark:bg-zinc-950 rounded-xl border border-gray-200 dark:border-zinc-800">
              <AlertCircle size={48} className="mx-auto text-gray-300 dark:text-gray-600 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">No news found</h3>
              <p className="text-gray-500 dark:text-gray-400 mt-2">The intelligence pipeline hasn't collected any global news yet.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
