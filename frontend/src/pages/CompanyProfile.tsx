import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useCompany, useCompanyProblems, useFollowCompany, useUnfollowCompany } from '../hooks/useCompanies';
import { useCompanyNews, useRefreshNews } from '../hooks/useNews';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Skeleton } from '../components/ui/skeleton';
import { ArrowLeft, ExternalLink, Globe, Target, MapPin, Newspaper, Settings, Layers, RefreshCw, BrainCircuit, Building2, Star } from 'lucide-react';

export function CompanyProfile() {
  const { slug } = useParams<{ slug: string }>();
  const { data: company, isLoading: companyLoading } = useCompany(slug);
  const { data: problems, isLoading: problemsLoading } = useCompanyProblems(slug);
  const { data: news, isLoading: newsLoading } = useCompanyNews(slug);
  const { mutate: refreshNews, isPending: isRefreshingNews } = useRefreshNews();
  const { mutate: followCompany } = useFollowCompany();
  const { mutate: unfollowCompany } = useUnfollowCompany();

  if (companyLoading) {
    return (
      <div className="space-y-6 animate-in fade-in">
        <Skeleton className="h-40 w-full rounded-xl" />
        <Skeleton className="h-[400px] w-full rounded-xl" />
      </div>
    );
  }

  if (!company) {
    return (
      <div className="text-center py-20">
        <h2 className="text-2xl font-bold">Company Not Found</h2>
        <Link to="/companies" className="text-blue-500 hover:underline mt-4 inline-block">
          Return to Directory
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-500 pb-20">
      <div>
        <Link to="/companies" className="inline-flex items-center text-sm text-gray-500 hover:text-gray-900 dark:hover:text-gray-100 mb-6 transition-colors">
          <ArrowLeft size={16} className="mr-2" />
          Back to Directory
        </Link>

        <div className="flex flex-col md:flex-row md:items-start justify-between gap-6">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-4xl font-bold tracking-tight text-gray-900 dark:text-gray-100">{company.name}</h1>
              {company.maturity && (
                <Badge variant={company.maturity >= 4 ? 'default' : 'secondary'} className="text-sm">
                  Level {company.maturity}
                </Badge>
              )}
            </div>
            
            <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-sm text-gray-500 dark:text-gray-400 mt-4">
              <div className="flex items-center gap-2">
                <MapPin size={16} />
                <span>{company.country}</span>
              </div>
              {company.ai_category && (
                <div className="flex items-center gap-2">
                  <Target size={16} />
                  <span>{company.ai_category}</span>
                </div>
              )}
              {company.company_type && (
                <div className="flex items-center gap-2">
                  <Building2 size={16} />
                  <span>{company.company_type}</span>
                </div>
              )}
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => {
                if (company.is_followed) {
                  unfollowCompany(company.slug);
                } else {
                  followCompany(company.slug);
                }
              }}
              className={`inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring border h-9 px-4 py-2 ${company.is_followed ? 'border-yellow-200 bg-yellow-50 text-yellow-700 hover:bg-yellow-100 dark:border-yellow-900 dark:bg-yellow-900/30 dark:text-yellow-400 dark:hover:bg-yellow-900/50' : 'border-gray-200 bg-white text-gray-700 hover:bg-gray-100 dark:border-zinc-800 dark:bg-zinc-950 dark:text-gray-300 dark:hover:bg-zinc-900'}`}
            >
              <Star size={16} className={`mr-2 ${company.is_followed ? 'fill-yellow-500 text-yellow-500' : ''}`} />
              {company.is_followed ? 'Following' : 'Follow'}
            </button>
            
            {company.website && (
              <a 
                href={company.website} 
                target="_blank" 
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring bg-blue-600 text-white shadow hover:bg-blue-700 h-9 px-4 py-2"
              >
                <Globe size={16} className="mr-2" />
                Visit Website
              </a>
            )}
          </div>
        </div>
      </div>

      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="w-full justify-start border-b border-gray-200 dark:border-zinc-800 rounded-none bg-transparent h-auto p-0 space-x-6">
          <TabsTrigger 
            value="overview" 
            className="rounded-none border-b-2 border-transparent data-[state=active]:border-blue-600 data-[state=active]:bg-transparent px-0 py-3 data-[state=active]:shadow-none"
          >
            Overview
          </TabsTrigger>
          <TabsTrigger 
            value="problems" 
            className="rounded-none border-b-2 border-transparent data-[state=active]:border-blue-600 data-[state=active]:bg-transparent px-0 py-3 data-[state=active]:shadow-none"
          >
            Problems Solved
          </TabsTrigger>
          <TabsTrigger 
            value="news" 
            className="rounded-none border-b-2 border-transparent data-[state=active]:border-blue-600 data-[state=active]:bg-transparent px-0 py-3 data-[state=active]:shadow-none"
          >
            Newsletter
          </TabsTrigger>
        </TabsList>

        <div className="mt-6">
          <TabsContent value="overview" className="m-0 space-y-6 focus-visible:outline-none focus-visible:ring-0">
            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <Layers size={18} className="text-blue-500" />
                      Market Segments
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2">
                      {company.segment_tags && company.segment_tags.length > 0 ? (
                        company.segment_tags.map(tag => (
                          <Badge key={tag} variant="secondary">{tag}</Badge>
                        ))
                      ) : (
                        <span className="text-gray-500 text-sm">No segment data available.</span>
                      )}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <Settings size={18} className="text-purple-500" />
                      Key Use Cases
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2">
                      {company.use_cases && company.use_cases.length > 0 ? (
                        company.use_cases.map(uc => (
                          <Badge key={uc} variant="outline" className="bg-gray-50 dark:bg-zinc-900">{uc}</Badge>
                        ))
                      ) : (
                        <span className="text-gray-500 text-sm">No use cases specified.</span>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </div>

              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <Building2 size={18} className="text-orange-500" />
                      Company Details
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex justify-between items-center py-2 border-b border-gray-100 dark:border-zinc-800">
                      <span className="text-sm font-medium text-gray-500">Status</span>
                      <Badge variant="outline">{company.status}</Badge>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b border-gray-100 dark:border-zinc-800">
                      <span className="text-sm font-medium text-gray-500">Source</span>
                      <span className="text-sm text-gray-900 dark:text-gray-100 capitalize">{company.source}</span>
                    </div>
                    {company.funding !== null && (
                      <div className="flex justify-between items-center py-2 border-b border-gray-100 dark:border-zinc-800">
                        <span className="text-sm font-medium text-gray-500">Funding</span>
                        <span className="text-sm text-gray-900 dark:text-gray-100">${company.funding}M</span>
                      </div>
                    )}
                    {company.estimated_revenue !== null && (
                      <div className="flex justify-between items-center py-2 border-b border-gray-100 dark:border-zinc-800">
                        <span className="text-sm font-medium text-gray-500">Est. Revenue</span>
                        <span className="text-sm text-gray-900 dark:text-gray-100">${company.estimated_revenue}M</span>
                      </div>
                    )}
                    {company.germany_presence && (
                      <div className="flex justify-between items-center py-2 border-b border-gray-100 dark:border-zinc-800">
                        <span className="text-sm font-medium text-gray-500">Germany Presence</span>
                        <span className="text-sm text-gray-900 dark:text-gray-100">{company.germany_presence}</span>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {(company.top_german_customers?.length > 0 || company.deployment_evidence) && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-lg">
                        <Globe size={18} className="text-green-500" />
                        Traction & Evidence
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      {company.top_german_customers?.length > 0 && (
                        <div>
                          <span className="text-xs font-semibold uppercase tracking-wider text-gray-500 block mb-2">Top Customers</span>
                          <div className="flex flex-wrap gap-2">
                            {company.top_german_customers.map(c => (
                              <Badge key={c} variant="secondary">{c}</Badge>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      {company.deployment_evidence && (
                        <div>
                          <span className="text-xs font-semibold uppercase tracking-wider text-gray-500 block mb-2 mt-4">Deployment Evidence</span>
                          <p className="text-sm text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-zinc-900 p-3 rounded-md">
                            {company.deployment_evidence}
                          </p>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                )}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="problems" className="m-0 focus-visible:outline-none focus-visible:ring-0">
            {problemsLoading ? (
              <div className="space-y-4">
                <Skeleton className="h-32 w-full" />
                <Skeleton className="h-32 w-full" />
              </div>
            ) : problems && problems.length > 0 ? (
              <div className="grid gap-4 md:grid-cols-2">
                {problems.map((problem) => (
                  <Card key={problem.id}>
                    <CardHeader className="pb-3">
                      <div className="flex justify-between items-start">
                        <div>
                          <Badge variant="outline" className="mb-2 bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 border-blue-200 dark:border-blue-800">
                            {problem.category}
                          </Badge>
                          <CardTitle className="text-lg">{problem.problem_name}</CardTitle>
                        </div>
                        {problem.severity && (
                          <Badge variant={problem.severity.toLowerCase() === 'high' ? 'destructive' : 'secondary'}>
                            {problem.severity}
                          </Badge>
                        )}
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-3 text-sm text-gray-600 dark:text-gray-300">
                      {problem.roi_benchmark && (
                        <div className="flex justify-between border-b border-gray-100 dark:border-zinc-800 pb-2">
                          <span className="text-gray-500">ROI Benchmark</span>
                          <span className="font-medium text-green-600 dark:text-green-400">{problem.roi_benchmark}</span>
                        </div>
                      )}
                      {problem.payback_period && (
                        <div className="flex justify-between">
                          <span className="text-gray-500">Payback Period</span>
                          <span className="font-medium">{problem.payback_period}</span>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 bg-white dark:bg-zinc-950 rounded-xl border border-gray-200 dark:border-zinc-800">
                <p className="text-gray-500">No structured problem data available for this company.</p>
              </div>
            )}
          </TabsContent>

          <TabsContent value="news" className="m-0 focus-visible:outline-none focus-visible:ring-0">
            <div className="flex justify-end mb-4">
              <button
                onClick={() => slug && refreshNews(slug)}
                disabled={isRefreshingNews}
                className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring border border-gray-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 shadow-sm hover:bg-gray-100 dark:hover:bg-zinc-900 h-9 px-4 py-2 disabled:opacity-50"
              >
                <RefreshCw size={16} className={`mr-2 ${isRefreshingNews ? 'animate-spin' : ''}`} />
                Refresh News
              </button>
            </div>

            {newsLoading ? (
              <div className="space-y-4">
                <Skeleton className="h-40 w-full" />
                <Skeleton className="h-40 w-full" />
              </div>
            ) : news && news.length > 0 ? (
              <div className="space-y-6 border-l-2 border-gray-100 dark:border-zinc-800 ml-3 pl-6">
                {news.map((item) => (
                  <div key={item.id} className="relative">
                    <div className="absolute -left-[35px] top-2 w-4 h-4 rounded-full bg-blue-100 border-2 border-blue-500 dark:bg-zinc-900" />
                    <Card>
                      <CardHeader className="pb-2">
                        <div className="flex justify-between items-start gap-4">
                          <CardTitle className="text-lg leading-tight">
                            <a href={item.url || '#'} target="_blank" rel="noopener noreferrer" className="hover:text-blue-600 transition-colors inline-flex items-center">
                              {item.headline}
                              <ExternalLink size={14} className="ml-2 text-gray-400" />
                            </a>
                          </CardTitle>
                          <span className="text-xs text-gray-500 whitespace-nowrap bg-gray-100 dark:bg-zinc-800 px-2 py-1 rounded-md">
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
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 bg-white dark:bg-zinc-950 rounded-xl border border-gray-200 dark:border-zinc-800">
                <Newspaper size={48} className="mx-auto text-gray-300 dark:text-gray-600 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">No recent news</h3>
                <p className="text-gray-500 dark:text-gray-400 mt-1">We haven't indexed any relevant articles for this company yet.</p>
              </div>
            )}
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );
}
