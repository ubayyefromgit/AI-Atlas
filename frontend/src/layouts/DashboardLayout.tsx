import React, { useState } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  Menu, X, Search, Moon, Sun, Monitor, 
  Home, Building2, MessageSquare, ShieldAlert, Activity,
  ChevronRight, Newspaper, Bell, Check
} from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { useAuth } from '../contexts/AuthContext';
import { useAskAIContext } from '../contexts/AskAIContext';
import { AskAIPanel } from '../components/AskAIPanel';
import { useDebounce } from '../hooks/useDebounce';
import { useCompanies, useQuickDiscover, useCreateCompany } from '../hooks/useCompanies';
import { useNotifications, useMarkAsRead, useMarkAllAsRead } from '../hooks/useNotifications';
import { Globe, Plus } from 'lucide-react';

export function DashboardLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { theme, setTheme } = useTheme();
  const { isAuthenticated } = useAuth();
  const { toggle: toggleAskAI } = useAskAIContext();
  const location = useLocation();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearchFocused, setIsSearchFocused] = useState(false);
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
  
  const debouncedSearch = useDebounce(searchQuery, 300);
  const { data: searchResults, isLoading: searchLoading } = useCompanies({ 
    search: debouncedSearch, 
    size: 5 
  });
  
  const { mutate: quickDiscover, data: discoveredCompany, isPending: isDiscovering, reset: resetDiscover } = useQuickDiscover();
  const { mutate: createCompany, isPending: isCreating } = useCreateCompany();

  const { data: notifications } = useNotifications();
  const { mutate: markAsRead } = useMarkAsRead();
  const { mutate: markAllAsRead } = useMarkAllAsRead();

  const unreadCount = notifications?.filter(n => !n.is_read).length || 0;

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      setIsSearchFocused(false);
      navigate(`/companies?search=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  const handleResultClick = (slug: string) => {
    setSearchQuery('');
    setIsSearchFocused(false);
    navigate(`/companies/${slug}`);
  };

  const navigation = [
    { name: 'Dashboard', href: '/', icon: Home },
    { name: 'Company Directory', href: '/companies', icon: Building2 },
    { name: 'Global News', href: '/news', icon: Newspaper },
    // Ask AI is triggered via the Top Nav or here as an action, we'll keep it as a button
    { name: 'Ask AI', action: toggleAskAI, icon: MessageSquare },
    { name: 'Admin Discovery', href: '/admin', icon: ShieldAlert },
    { name: 'System Evaluation', href: '/evaluation', icon: Activity },
  ];

  const cycleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  const ThemeIcon = theme === 'dark' ? Sun : Moon;

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-zinc-950 text-gray-900 dark:text-gray-100 overflow-hidden">
      
      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-zinc-900 border-r border-gray-200 dark:border-zinc-800 
        transform transition-transform duration-200 ease-in-out lg:relative lg:translate-x-0
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="h-16 flex items-center justify-between px-4 border-b border-gray-200 dark:border-zinc-800">
          <Link to="/" className="text-xl font-bold tracking-tight text-blue-600 dark:text-blue-500">
            AI Atlas
          </Link>
          <button onClick={() => setSidebarOpen(false)} className="lg:hidden p-2 text-gray-500">
            <X size={20} />
          </button>
        </div>

        <nav className="p-4 space-y-1">
          {navigation.map((item) => {
            const Icon = item.icon;
            const isActive = item.href && location.pathname === item.href;
            
            return item.href ? (
              <Link
                key={item.name}
                to={item.href}
                className={`flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${
                  isActive 
                    ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 font-medium' 
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-zinc-800'
                }`}
              >
                <Icon size={18} />
                {item.name}
              </Link>
            ) : (
              <button
                key={item.name}
                onClick={item.action}
                className="w-full flex items-center gap-3 px-3 py-2 rounded-md transition-colors text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-zinc-800"
              >
                <Icon size={18} />
                {item.name}
              </button>
            )
          })}
        </nav>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Navigation */}
        <header className="h-16 flex items-center justify-between px-4 sm:px-6 lg:px-8 bg-white dark:bg-zinc-900 border-b border-gray-200 dark:border-zinc-800 z-30">
          <div className="flex items-center gap-4">
            <button 
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-2 -ml-2 text-gray-500 hover:bg-gray-100 dark:hover:bg-zinc-800 rounded-md"
            >
              <Menu size={20} />
            </button>
            
            {/* Breadcrumbs (Simplistic for now) */}
            <div className="hidden sm:flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400 capitalize">
              <span>{location.pathname === '/' ? 'Dashboard' : location.pathname.split('/')[1]}</span>
            </div>
          </div>

          <div className="flex items-center gap-2 sm:gap-4">
            <form onSubmit={handleSearch} className="relative hidden sm:block">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
              <input 
                type="text" 
                placeholder="Global search..." 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onFocus={() => setIsSearchFocused(true)}
                onBlur={() => setTimeout(() => setIsSearchFocused(false), 200)}
                className="w-64 pl-9 pr-4 py-2 bg-gray-100 dark:bg-zinc-800 border-transparent focus:bg-white dark:focus:bg-zinc-900 rounded-full text-sm outline-none focus:ring-2 focus:ring-blue-500 transition-all"
              />
              
              {/* Search Dropdown */}
              {isSearchFocused && searchQuery.length > 1 && (
                <div className="absolute top-full mt-2 w-full min-w-[300px] bg-white dark:bg-zinc-900 rounded-lg shadow-lg border border-gray-200 dark:border-zinc-800 overflow-hidden z-50">
                  {searchLoading || isDiscovering ? (
                    <div className="p-4 text-sm text-center text-gray-500">
                      {isDiscovering ? 'Searching the web...' : 'Searching...'}
                    </div>
                  ) : discoveredCompany ? (
                    <div className="p-4">
                      <div className="flex items-center gap-2 mb-2 text-blue-600 dark:text-blue-400 text-xs font-semibold uppercase tracking-wider">
                        <Globe size={14} />
                        Web Result
                      </div>
                      <h4 className="font-semibold text-gray-900 dark:text-gray-100">{discoveredCompany.name}</h4>
                      <p className="text-xs text-gray-500 mt-1">{discoveredCompany.ai_category || discoveredCompany.industry || 'AI Company'}</p>
                      {discoveredCompany.website && (
                        <a href={discoveredCompany.website} target="_blank" rel="noopener noreferrer" className="text-xs text-blue-500 hover:underline mt-1 inline-block">
                          {discoveredCompany.website}
                        </a>
                      )}
                      <div className="mt-4 flex gap-2">
                        <button
                          type="button"
                          disabled={isCreating}
                          onClick={() => {
                            // Build a clean payload with only the fields the API accepts
                            const payload = {
                              name: discoveredCompany.name,
                              country: discoveredCompany.country || null,
                              ai_category: discoveredCompany.ai_category || null,
                              segment_tags: discoveredCompany.segment_tags || [],
                              use_cases: discoveredCompany.use_cases || [],
                              website: discoveredCompany.website || null,
                              source: 'web_discovery',
                              status: 'approved',
                            };
                            createCompany(payload, {
                              onSuccess: (newCompany) => {
                                resetDiscover();
                                setIsSearchFocused(false);
                                setSearchQuery('');
                                navigate(`/companies/${newCompany.slug}`);
                              }
                            });
                          }}
                          className="flex-1 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium py-1.5 px-3 rounded-md transition-colors disabled:opacity-50 flex items-center justify-center gap-1"
                        >
                          {isCreating ? 'Saving...' : <><Plus size={14} /> Save to Directory</>}
                        </button>
                        <button
                          type="button"
                          onClick={() => resetDiscover()}
                          className="px-3 py-1.5 text-sm text-gray-500 hover:bg-gray-100 dark:hover:bg-zinc-800 rounded-md transition-colors"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : searchResults?.items && searchResults.items.length > 0 ? (
                    <ul className="py-2 max-h-80 overflow-auto">
                      {searchResults.items.map(company => (
                        <li key={company.id}>
                          <button
                            type="button"
                            onClick={() => handleResultClick(company.slug)}
                            className="w-full text-left px-4 py-2 hover:bg-gray-50 dark:hover:bg-zinc-800 transition-colors flex flex-col"
                          >
                            <span className="text-sm font-medium text-gray-900 dark:text-gray-100">{company.name}</span>
                            <span className="text-xs text-gray-500 truncate">{company.ai_category || company.industry || 'Unknown Sector'}</span>
                          </button>
                        </li>
                      ))}
                      <li className="border-t border-gray-100 dark:border-zinc-800 mt-1 pt-1">
                        <button
                          type="button"
                          onClick={handleSearch}
                          className="w-full text-center px-4 py-2 text-xs text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 font-medium"
                        >
                          View all results
                        </button>
                      </li>
                    </ul>
                  ) : (
                    <div className="p-4 text-center">
                      <p className="text-sm text-gray-500 mb-3">No local companies found for "{searchQuery}"</p>
                      <button
                        type="button"
                        onClick={() => quickDiscover(searchQuery)}
                        className="inline-flex items-center justify-center gap-2 w-full px-4 py-2 text-sm font-medium text-blue-700 bg-blue-50 hover:bg-blue-100 dark:text-blue-400 dark:bg-blue-900/20 dark:hover:bg-blue-900/40 rounded-md transition-colors"
                      >
                        <Globe size={16} />
                        Search the web for "{searchQuery}"
                      </button>
                    </div>
                  )}
                </div>
              )}
            </form>

            {/* Notification Bell */}
            <div className="relative">
              <button 
                onClick={() => setIsNotificationsOpen(!isNotificationsOpen)}
                className="p-2 text-gray-500 hover:text-blue-600 dark:hover:text-blue-400 transition-colors relative"
                title="Notifications"
              >
                <Bell size={20} />
                {unreadCount > 0 && (
                  <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
                )}
              </button>

              {isNotificationsOpen && (
                <div className="absolute right-0 top-full mt-2 w-80 bg-white dark:bg-zinc-900 rounded-lg shadow-xl border border-gray-200 dark:border-zinc-800 overflow-hidden z-50">
                  <div className="p-3 border-b border-gray-100 dark:border-zinc-800 flex justify-between items-center">
                    <h3 className="font-semibold text-sm">Notifications</h3>
                    {unreadCount > 0 && (
                      <button onClick={() => markAllAsRead()} className="text-xs text-blue-600 hover:underline">
                        Mark all as read
                      </button>
                    )}
                  </div>
                  <div className="max-h-96 overflow-y-auto">
                    {!notifications || notifications.length === 0 ? (
                      <div className="p-4 text-center text-sm text-gray-500">No new notifications</div>
                    ) : (
                      <ul className="divide-y divide-gray-100 dark:divide-zinc-800">
                        {notifications.map(notif => (
                          <li key={notif.id} className={`p-4 ${notif.is_read ? 'opacity-60' : 'bg-blue-50/50 dark:bg-blue-900/10'} relative group`}>
                            <div className="flex justify-between items-start gap-2">
                              <div>
                                <span className="text-xs text-gray-500 block mb-1">{new Date(notif.created_at).toLocaleDateString()}</span>
                                <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{notif.message}</p>
                              </div>
                              {!notif.is_read && (
                                <button 
                                  onClick={() => markAsRead(notif.id)}
                                  className="text-gray-400 hover:text-green-500 opacity-0 group-hover:opacity-100 transition-opacity"
                                  title="Mark as read"
                                >
                                  <Check size={16} />
                                </button>
                              )}
                            </div>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                </div>
              )}
            </div>

            <button 
              onClick={toggleAskAI}
              className="p-2 text-gray-500 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
              title="Ask AI"
            >
              <MessageSquare size={20} />
            </button>

            <button 
              onClick={cycleTheme}
              className="p-2 text-gray-500 hover:bg-gray-100 dark:hover:bg-zinc-800 rounded-full transition-colors"
            >
              <ThemeIcon size={20} />
            </button>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto p-4 sm:p-6 lg:p-8">
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>

      {/* Ask AI Side Panel */}
      <AskAIPanel />

    </div>
  );
}
