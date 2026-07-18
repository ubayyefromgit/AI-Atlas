import React, { useState } from 'react';
import { useCompanies, useCompanyFilters, useFollowCompany, useUnfollowCompany } from '../hooks/useCompanies';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Skeleton } from '../components/ui/skeleton';
import { Search, LayoutGrid, List as ListIcon, Building2, MapPin, Target, Filter, X, Star } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useDebounce } from '../hooks/useDebounce';

export function CompanyDirectory() {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [search, setSearch] = useState('');
  const [segment, setSegment] = useState<string>('');
  const [category, setCategory] = useState<string>('');
  const [companyType, setCompanyType] = useState<string>('');
  const [country, setCountry] = useState<string>('');
  const [maturity, setMaturity] = useState<number | undefined>(undefined);
  const [status, setStatus] = useState<string>('');
  const [showFilters, setShowFilters] = useState(false);
  const [showWatchlist, setShowWatchlist] = useState(false);

  const debouncedSearch = useDebounce(search, 300);
  const [page, setPage] = useState(1);
  const size = 12;

  const { data: filtersData } = useCompanyFilters();
  const { data, isLoading } = useCompanies({ 
    page, 
    size, 
    search: debouncedSearch,
    segment: segment || undefined,
    category: category || undefined,
    company_type: companyType || undefined,
    country: country || undefined,
    maturity: maturity || undefined,
    status: status || undefined
  });

  const { mutate: followCompany } = useFollowCompany();
  const { mutate: unfollowCompany } = useUnfollowCompany();

  const handleSearch = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
  };

  React.useEffect(() => {
    setPage(1);
  }, [debouncedSearch, segment, category, companyType, country, maturity, status]);

  const clearFilters = () => {
    setSegment('');
    setCategory('');
    setCompanyType('');
    setCountry('');
    setMaturity(undefined);
    setStatus('');
    setShowWatchlist(false);
  };

  const hasActiveFilters = segment || category || companyType || country || maturity !== undefined || status || showWatchlist;

  const toggleFollow = (e: React.MouseEvent, company: any) => {
    e.preventDefault(); // Prevent navigating to company profile
    e.stopPropagation();
    if (company.is_followed) {
      unfollowCompany(company.slug);
    } else {
      followCompany(company.slug);
    }
  };

  // Filter local for watchlist if not supported by backend yet
  const displayItems = data?.items?.filter(c => showWatchlist ? c.is_followed : true) || [];

  return (
    <div className="space-y-6 animate-in fade-in duration-500 pb-10">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4 border-b border-gray-200 dark:border-zinc-800 pb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-900 dark:text-gray-100">Company Directory</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">Browse and discover AI companies in the F&B sector</p>
        </div>
        
        <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
          <form onSubmit={handleSearch} className="relative flex-1 md:flex-none">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
            <input 
              type="text" 
              placeholder="Search companies..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 pr-4 py-2 border border-gray-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 rounded-md text-sm outline-none focus:ring-2 focus:ring-blue-500 transition-all w-full md:w-64 text-gray-900 dark:text-gray-100"
            />
          </form>

          <button
            onClick={() => setShowWatchlist(!showWatchlist)}
            className={`flex items-center gap-2 px-3 py-2 border rounded-md text-sm font-medium transition-colors ${showWatchlist ? 'bg-yellow-50 border-yellow-200 text-yellow-700 dark:bg-yellow-900/30 dark:border-yellow-900 dark:text-yellow-400' : 'border-gray-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-zinc-900'}`}
          >
            <Star size={16} className={showWatchlist ? "fill-yellow-500 text-yellow-500" : ""} />
            Watchlist
          </button>
          
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`flex items-center gap-2 px-3 py-2 border rounded-md text-sm font-medium transition-colors ${showFilters || hasActiveFilters ? 'bg-blue-50 border-blue-200 text-blue-700 dark:bg-blue-900/30 dark:border-blue-900 dark:text-blue-400' : 'border-gray-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-zinc-900'}`}
          >
            <Filter size={16} />
            Filters {hasActiveFilters && <span className="flex h-2 w-2 rounded-full bg-blue-600"></span>}
          </button>

          <div className="flex border border-gray-200 dark:border-zinc-800 rounded-md overflow-hidden bg-white dark:bg-zinc-950">
            <button 
              onClick={() => setViewMode('grid')}
              className={`p-2 transition-colors ${viewMode === 'grid' ? 'bg-gray-100 dark:bg-zinc-800 text-blue-600' : 'text-gray-500 hover:bg-gray-50 dark:hover:bg-zinc-800/50'}`}
            >
              <LayoutGrid size={18} />
            </button>
            <button 
              onClick={() => setViewMode('list')}
              className={`p-2 transition-colors ${viewMode === 'list' ? 'bg-gray-100 dark:bg-zinc-800 text-blue-600' : 'text-gray-500 hover:bg-gray-50 dark:hover:bg-zinc-800/50'}`}
            >
              <ListIcon size={18} />
            </button>
          </div>
        </div>
      </div>

      {showFilters && (
        <Card className="bg-gray-50/50 dark:bg-zinc-900/30 border-dashed border-gray-200 dark:border-zinc-800">
          <CardContent className="p-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">Segment</label>
                <select 
                  value={segment} 
                  onChange={e => setSegment(e.target.value)}
                  className="w-full text-sm border-gray-200 dark:border-zinc-700 bg-white dark:bg-zinc-950 rounded-md py-1.5 px-2 outline-none focus:ring-1 focus:ring-blue-500 text-gray-900 dark:text-gray-100"
                >
                  <option value="">All Segments</option>
                  {filtersData?.segments?.map(s => <option key={s.value} value={s.value}>{s.value} ({s.count})</option>)}
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">AI Category</label>
                <select 
                  value={category} 
                  onChange={e => setCategory(e.target.value)}
                  className="w-full text-sm border-gray-200 dark:border-zinc-700 bg-white dark:bg-zinc-950 rounded-md py-1.5 px-2 outline-none focus:ring-1 focus:ring-blue-500 text-gray-900 dark:text-gray-100"
                >
                  <option value="">All AI Categories</option>
                  {filtersData?.ai_categories?.map(c => <option key={c.value} value={c.value}>{c.value} ({c.count})</option>)}
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">Company Type</label>
                <select 
                  value={companyType} 
                  onChange={e => setCompanyType(e.target.value)}
                  className="w-full text-sm border-gray-200 dark:border-zinc-700 bg-white dark:bg-zinc-950 rounded-md py-1.5 px-2 outline-none focus:ring-1 focus:ring-blue-500 text-gray-900 dark:text-gray-100"
                >
                  <option value="">All Types</option>
                  {filtersData?.company_types?.map(t => <option key={t.value} value={t.value}>{t.value} ({t.count})</option>)}
                </select>
              </div>
              
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">Country</label>
                <select 
                  value={country} 
                  onChange={e => setCountry(e.target.value)}
                  className="w-full text-sm border-gray-200 dark:border-zinc-700 bg-white dark:bg-zinc-950 rounded-md py-1.5 px-2 outline-none focus:ring-1 focus:ring-blue-500 text-gray-900 dark:text-gray-100"
                >
                  <option value="">All Countries</option>
                  {filtersData?.countries?.map(c => <option key={c.value} value={c.value}>{c.value} ({c.count})</option>)}
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">Maturity Level</label>
                <select 
                  value={maturity || ''} 
                  onChange={e => setMaturity(e.target.value ? Number(e.target.value) : undefined)}
                  className="w-full text-sm border-gray-200 dark:border-zinc-700 bg-white dark:bg-zinc-950 rounded-md py-1.5 px-2 outline-none focus:ring-1 focus:ring-blue-500 text-gray-900 dark:text-gray-100"
                >
                  <option value="">Any Level</option>
                  {[1, 2, 3, 4, 5].map(lvl => <option key={lvl} value={lvl}>Level {lvl}</option>)}
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">Approval Status</label>
                <select 
                  value={status} 
                  onChange={e => setStatus(e.target.value)}
                  className="w-full text-sm border-gray-200 dark:border-zinc-700 bg-white dark:bg-zinc-950 rounded-md py-1.5 px-2 outline-none focus:ring-1 focus:ring-blue-500 text-gray-900 dark:text-gray-100"
                >
                  <option value="">All Statuses</option>
                  <option value="APPROVED">Approved</option>
                  <option value="PENDING">Pending</option>
                  <option value="REJECTED">Rejected</option>
                </select>
              </div>
            </div>
            
            {hasActiveFilters && (
              <div className="mt-4 pt-4 border-t border-gray-200 dark:border-zinc-800 flex justify-between items-center">
                <div className="flex flex-wrap gap-2">
                  {showWatchlist && <Badge variant="secondary" className="flex items-center gap-1 bg-yellow-100 text-yellow-800">Watchlist <X size={12} className="cursor-pointer" onClick={() => setShowWatchlist(false)}/></Badge>}
                  {segment && <Badge variant="secondary" className="flex items-center gap-1">{segment} <X size={12} className="cursor-pointer" onClick={() => setSegment('')}/></Badge>}
                  {category && <Badge variant="secondary" className="flex items-center gap-1">{category} <X size={12} className="cursor-pointer" onClick={() => setCategory('')}/></Badge>}
                  {companyType && <Badge variant="secondary" className="flex items-center gap-1">{companyType} <X size={12} className="cursor-pointer" onClick={() => setCompanyType('')}/></Badge>}
                  {country && <Badge variant="secondary" className="flex items-center gap-1">{country} <X size={12} className="cursor-pointer" onClick={() => setCountry('')}/></Badge>}
                  {maturity && <Badge variant="secondary" className="flex items-center gap-1">Level {maturity} <X size={12} className="cursor-pointer" onClick={() => setMaturity(undefined)}/></Badge>}
                  {status && <Badge variant="secondary" className="flex items-center gap-1">{status} <X size={12} className="cursor-pointer" onClick={() => setStatus('')}/></Badge>}
                </div>
                <button onClick={clearFilters} className="text-xs text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 font-medium shrink-0">
                  Clear All
                </button>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {isLoading ? (
        <div className={viewMode === 'grid' ? "grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4" : "space-y-4"}>
          {Array.from({ length: size }).map((_, i) => (
            <Skeleton key={i} className={viewMode === 'grid' ? "h-64 rounded-xl" : "h-24 rounded-xl"} />
          ))}
        </div>
      ) : displayItems.length === 0 ? (
        <div className="text-center py-20 bg-white dark:bg-zinc-950 rounded-xl border border-gray-200 dark:border-zinc-800">
          <Building2 size={48} className="mx-auto text-gray-300 dark:text-gray-600 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">No companies found</h3>
          <p className="text-gray-500 dark:text-gray-400 mt-2">Try adjusting your search or clearing filters.</p>
          {hasActiveFilters && (
            <button onClick={clearFilters} className="mt-4 px-4 py-2 bg-gray-100 dark:bg-zinc-800 hover:bg-gray-200 dark:hover:bg-zinc-700 text-gray-800 dark:text-gray-200 rounded-md text-sm transition-colors">
              Clear Filters
            </button>
          )}
        </div>
      ) : (
        <div className={viewMode === 'grid' ? "grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4" : "space-y-4"}>
          {displayItems.map((company) => (
            <Link to={`/companies/${company.slug}`} key={company.id} className="block group">
              <Card className="h-full hover:shadow-md transition-all dark:hover:bg-zinc-900/50 border-gray-200 dark:border-zinc-800">
                <CardHeader className="pb-3">
                  <div className="flex justify-between items-start gap-2">
                    <CardTitle className="text-lg font-bold group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors line-clamp-2">
                      {company.name}
                    </CardTitle>
                    <div className="flex gap-2 items-center">
                      <button 
                        onClick={(e) => toggleFollow(e, company)}
                        className="p-1.5 text-gray-400 hover:text-yellow-500 hover:bg-yellow-50 rounded-full transition-colors"
                      >
                        <Star size={16} className={company.is_followed ? "fill-yellow-500 text-yellow-500" : ""} />
                      </button>
                      {company.maturity && (
                        <Badge variant={company.maturity >= 4 ? 'default' : 'secondary'} className={`shrink-0 ${company.maturity >= 4 ? 'bg-blue-600' : 'bg-gray-100 text-gray-600 dark:bg-zinc-800 dark:text-gray-400'}`}>
                          L{company.maturity}
                        </Badge>
                      )}
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2 text-sm text-gray-600 dark:text-gray-300">
                    <div className="flex items-center gap-2">
                      <MapPin size={14} className="text-gray-400 shrink-0" />
                      <span className="truncate">{company.country || 'Unknown'}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Target size={14} className="text-gray-400 shrink-0" />
                      <span className="truncate">{company.ai_category || 'Uncategorized'}</span>
                    </div>
                    {company.company_type && (
                      <div className="flex items-center gap-2">
                        <Building2 size={14} className="text-gray-400 shrink-0" />
                        <span className="truncate">{company.company_type}</span>
                      </div>
                    )}
                  </div>
                  
                  {company.segment_tags && company.segment_tags.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {company.segment_tags.slice(0, 3).map(tag => (
                        <Badge key={tag} variant="outline" className="text-[11px] px-1.5 py-0 font-normal bg-gray-50/50 dark:bg-zinc-800/50 border-gray-200 dark:border-zinc-700">
                          {tag}
                        </Badge>
                      ))}
                      {company.segment_tags.length > 3 && (
                        <span className="text-xs text-gray-500 px-1 py-0.5">+{company.segment_tags.length - 3}</span>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}

      {/* Pagination */}
      {data && data.total > size && (() => {
        const totalPages = Math.ceil(data.total / size);
        return (
          <div className="flex items-center justify-center gap-4 pt-6 border-t border-gray-100 dark:border-zinc-800">
            <button 
              disabled={page === 1}
              onClick={() => setPage(p => Math.max(1, p - 1))}
              className="px-4 py-2 rounded-md border border-gray-200 dark:border-zinc-700 bg-white dark:bg-zinc-900 disabled:opacity-40 text-sm font-medium hover:bg-gray-50 dark:hover:bg-zinc-800 transition-colors"
            >
              Previous
            </button>
            <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
              Page {page} of {totalPages}
            </span>
            <button 
              disabled={!data.has_next}
              onClick={() => setPage(p => p + 1)}
              className="px-4 py-2 rounded-md border border-gray-200 dark:border-zinc-700 bg-white dark:bg-zinc-900 disabled:opacity-40 text-sm font-medium hover:bg-gray-50 dark:hover:bg-zinc-800 transition-colors"
            >
              Next
            </button>
          </div>
        );
      })()}
    </div>
  );
}
