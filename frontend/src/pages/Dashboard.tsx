import React from 'react';
import { useCompanyStatistics } from '../hooks/useCompanies';
import { useDiscoveryStatistics } from '../hooks/useDiscovery';
import { useNewsHealth } from '../hooks/useNews';
import { useQuery } from '@tanstack/react-query';
import api from '../services/api';
import { 
  Building2,
  BrainCircuit,
  Search,
  CheckCircle2,
  TrendingUp,
  Activity,
  AlertTriangle,
  XCircle
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Skeleton } from '../components/ui/skeleton';
import { Badge } from '../components/ui/badge';

export function Dashboard() {
  const { data: compStats, isLoading: compLoading } = useCompanyStatistics();
  const { data: discStats, isLoading: discLoading } = useDiscoveryStatistics();
  const { data: newsHealth, isLoading: newsLoading } = useNewsHealth();
  
  const { data: sysHealth, isLoading: sysLoading } = useQuery({
    queryKey: ['system-health'],
    queryFn: async () => {
      // Calling the global /health endpoint (not under /api/v1)
      // Since api instance adds /api/v1, we use a custom base for this request or strip it.
      // Easiest is to just use standard fetch or create a separate axios instance,
      // but for simplicity we assume the proxy handles /health or we can construct it.
      const baseUrl = api.defaults.baseURL?.replace('/api/v1', '') || '';
      const response = await fetch(`${baseUrl}/health`);
      if (!response.ok) throw new Error('Health check failed');
      return response.json();
    },
    refetchInterval: 60000,
    refetchOnWindowFocus: false,
  });

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-gray-900 dark:text-gray-100">Overview</h1>
        <p className="text-gray-500 dark:text-gray-400">Welcome to the AI Atlas Platform</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {compLoading ? (
          <>
            <Skeleton className="h-32 w-full rounded-xl" />
            <Skeleton className="h-32 w-full rounded-xl" />
            <Skeleton className="h-32 w-full rounded-xl" />
            <Skeleton className="h-32 w-full rounded-xl" />
          </>
        ) : (
          <>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Total Companies</CardTitle>
                <Building2 className="h-4 w-4 text-blue-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{compStats?.total_companies || 0}</div>
                <p className="text-xs text-muted-foreground mt-1 text-gray-500">
                  Indexed in directory
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">AI Categories</CardTitle>
                <BrainCircuit className="h-4 w-4 text-purple-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{compStats ? Object.keys(compStats.companies_per_ai_category || {}).length : 0}</div>
                <p className="text-xs text-muted-foreground mt-1 text-gray-500">
                  Unique AI specialties
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Discovery Runs</CardTitle>
                <Activity className="h-4 w-4 text-green-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{discStats?.discovery_runs || 0}</div>
                <p className="text-xs text-muted-foreground mt-1 text-gray-500">
                  Total pipeline executions
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Pending Candidates</CardTitle>
                <Search className="h-4 w-4 text-orange-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{discStats?.pending_candidates || 0}</div>
                <p className="text-xs text-muted-foreground mt-1 text-gray-500">
                  Awaiting manual approval
                </p>
              </CardContent>
            </Card>
          </>
        )}
      </div>
      
      <div className="grid gap-4 md:grid-cols-2">
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-blue-500" />
              Live Telemetry
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center border-b border-gray-100 dark:border-zinc-800 pb-2">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Core API & Database</span>
                {sysLoading ? <Skeleton className="h-5 w-16" /> : (
                  <Badge variant={sysHealth?.status === 'healthy' ? 'outline' : 'destructive'} className={sysHealth?.status === 'healthy' ? 'bg-green-50 text-green-700 border-green-200 dark:bg-green-900/30 dark:text-green-400' : ''}>
                    {sysHealth?.status === 'healthy' ? 'Online' : 'Degraded'}
                  </Badge>
                )}
              </div>
              <div className="flex justify-between items-center border-b border-gray-100 dark:border-zinc-800 pb-2">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">News Provider API</span>
                {newsLoading ? <Skeleton className="h-5 w-16" /> : (
                  <Badge variant={newsHealth?.provider_status === 'OK' ? 'outline' : 'destructive'} className={newsHealth?.provider_status === 'OK' ? 'bg-green-50 text-green-700 border-green-200 dark:bg-green-900/30 dark:text-green-400' : ''}>
                    {newsHealth?.provider_status === 'OK' ? 'Online' : 'Missing Key'}
                  </Badge>
                )}
              </div>
              <div className="flex justify-between items-center border-b border-gray-100 dark:border-zinc-800 pb-2">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Background Scheduler</span>
                {newsLoading ? <Skeleton className="h-5 w-16" /> : (
                  <Badge variant={newsHealth?.scheduler_status === 'RUNNING' ? 'outline' : 'secondary'} className={newsHealth?.scheduler_status === 'RUNNING' ? 'bg-green-50 text-green-700 border-green-200 dark:bg-green-900/30 dark:text-green-400' : ''}>
                    {newsHealth?.scheduler_status === 'RUNNING' ? 'Active' : 'Stopped'}
                  </Badge>
                )}
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Discovery Pipeline</span>
                {discLoading ? <Skeleton className="h-5 w-16" /> : (
                  <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200 dark:bg-green-900/30 dark:text-green-400">
                    Online
                  </Badge>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
