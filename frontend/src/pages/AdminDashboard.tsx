import React, { useState, useEffect } from 'react';
import { useDiscoveryCandidates, useRunDiscovery, useApproveCandidate, useRejectCandidate, useUpdateCandidate, useBulkApproveCandidates, useBulkRejectCandidates } from '../hooks/useDiscovery';
import { useCreateCompany, useUpdateCompany } from '../hooks/useCompanies';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { ShieldAlert, Play, CheckCircle2, XCircle, Globe, LayoutList, Check, AlertTriangle, X, LogOut, Edit, Plus } from 'lucide-react';
import { Skeleton } from '../components/ui/skeleton';
import { AdminLogin } from './AdminLogin';

export function AdminDashboard() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    setIsAuthenticated(!!localStorage.getItem('adminToken'));
  }, []);

  const { data: candidates, isLoading } = useDiscoveryCandidates();
  const { mutate: runDiscovery, isPending: isRunning } = useRunDiscovery();
  const { mutate: approveCandidate } = useApproveCandidate();
  const { mutate: rejectCandidate } = useRejectCandidate();
  const { mutate: updateCandidate, isPending: isUpdating } = useUpdateCandidate();
  const { mutate: createCompany, isPending: isCreating } = useCreateCompany();
  const { mutate: updateCompany, isPending: isUpdatingCompany } = useUpdateCompany();
  const { mutate: bulkApprove, isPending: isBulkApproving } = useBulkApproveCandidates();
  const { mutate: bulkReject, isPending: isBulkRejecting } = useBulkRejectCandidates();

  const [processingId, setProcessingId] = useState<number | null>(null);
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());

  const [sector, setSector] = useState('');
  const [country, setCountry] = useState('Germany');

  const [editingCandidateId, setEditingCandidateId] = useState<number | null>(null);
  const [editForm, setEditForm] = useState({ name: '', website: '', ai_category: '', country: '' });

  const [showAddCompany, setShowAddCompany] = useState(false);
  const [addForm, setAddForm] = useState({ name: '', website: '', ai_category: '', country: '', description: '', segment_tags: '', use_cases: '' });
  const [upsertMode, setUpsertMode] = useState(false);
  const [upsertSlug, setUpsertSlug] = useState('');

  const [pipelineStep, setPipelineStep] = useState(0);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isRunning) {
      setPipelineStep(0);
      interval = setInterval(() => {
        setPipelineStep((prev) => (prev < 4 ? prev + 1 : prev));
      }, 10000);
    } else {
      setPipelineStep(0);
    }
    return () => clearInterval(interval);
  }, [isRunning]);

  const pipelineSteps = [
    "Collecting Evidence (Web Search)",
    "LLM Data Extraction",
    "URL & Fact Validation",
    "Confidence Scoring",
    "Database Deduplication"
  ];

  const pendingCandidates = candidates?.filter(c => c.status?.toUpperCase() === 'PENDING') || [];

  const handleRunDiscovery = (e: React.FormEvent) => {
    e.preventDefault();
    if (!sector || !country) return;
    runDiscovery({ sector, country });
  };

  const toggleSelection = (id: number) => {
    const newSelection = new Set(selectedIds);
    if (newSelection.has(id)) {
      newSelection.delete(id);
    } else {
      newSelection.add(id);
    }
    setSelectedIds(newSelection);
  };

  const handleApprove = (id: number) => {
    setProcessingId(id);
    approveCandidate(id, { onSettled: () => setProcessingId(null) });
  };

  const handleReject = (id: number) => {
    setProcessingId(id);
    rejectCandidate(id, { onSettled: () => setProcessingId(null) });
  };

  const handleBulkApprove = () => {
    bulkApprove(Array.from(selectedIds), {
      onSettled: () => setSelectedIds(new Set())
    });
  };

  const handleBulkReject = () => {
    bulkReject(Array.from(selectedIds), {
      onSettled: () => setSelectedIds(new Set())
    });
  };

  const handleLogout = () => {
    localStorage.removeItem('adminToken');
    setIsAuthenticated(false);
  };

  const startEditing = (candidate: any) => {
    setEditingCandidateId(candidate.id);
    setEditForm({
      name: candidate.name,
      website: candidate.website || '',
      ai_category: candidate.ai_category || '',
      country: candidate.country || '',
    });
  };

  const saveEdit = (id: number) => {
    updateCandidate({ id, data: editForm }, {
      onSuccess: () => setEditingCandidateId(null)
    });
  };

  const handleAddCompany = (e: React.FormEvent) => {
    e.preventDefault();
    const payload = {
      ...addForm,
      segment_tags: addForm.segment_tags ? addForm.segment_tags.split(',').map(t => t.trim()).filter(Boolean) : [],
      use_cases: addForm.use_cases ? addForm.use_cases.split(',').map(t => t.trim()).filter(Boolean) : [],
    };

    if (upsertMode && upsertSlug) {
      updateCompany({ slug: upsertSlug, data: payload }, {
        onSuccess: () => {
          setShowAddCompany(false);
          setUpsertMode(false);
          setUpsertSlug('');
          setAddForm({ name: '', website: '', ai_category: '', country: '', description: '', segment_tags: '', use_cases: '' });
        }
      });
      return;
    }

    createCompany(payload, {
      onSuccess: () => {
        setShowAddCompany(false);
        setAddForm({ name: '', website: '', ai_category: '', country: '', description: '', segment_tags: '', use_cases: '' });
      },
      onError: (error: any) => {
        const msg = error?.response?.data?.detail || '';
        if (msg.includes('already exists')) {
          const slug = addForm.name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
          setUpsertSlug(slug);
          setUpsertMode(true);
        }
      }
    });
  };

  if (!isAuthenticated) {
    return <AdminLogin onLogin={() => setIsAuthenticated(true)} />;
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-500 pb-20">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-900 dark:text-gray-100 flex items-center gap-3">
            <ShieldAlert className="text-red-500" />
            Admin Dashboard
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-2">Manage the AI Discovery Pipeline and approve candidates.</p>
        </div>
        <button
          onClick={handleLogout}
          className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-red-600 hover:text-red-700 bg-red-50 hover:bg-red-100 rounded-md transition-colors"
        >
          <LogOut size={16} />
          Logout
        </button>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        <div className="md:col-span-1 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Run Discovery</CardTitle>
              <CardDescription>Launch the automated intelligence pipeline.</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleRunDiscovery} className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Target Sector</label>
                  <input
                    type="text"
                    value={sector}
                    onChange={e => setSector(e.target.value)}
                    placeholder="e.g. Food & Beverage"
                    required
                    className="w-full px-3 py-2 border border-gray-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 rounded-md text-sm outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Target Country</label>
                  <input
                    type="text"
                    value={country}
                    onChange={e => setCountry(e.target.value)}
                    required
                    className="w-full px-3 py-2 border border-gray-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 rounded-md text-sm outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                  />
                </div>
                <button
                  type="submit"
                  disabled={isRunning}
                  className="w-full flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring bg-blue-600 text-white shadow hover:bg-blue-700 h-9 px-4 py-2 disabled:opacity-50"
                >
                  <Play size={16} className={`mr-2 ${isRunning ? 'animate-pulse' : ''}`} />
                  {isRunning ? 'Pipeline Running...' : 'Launch Pipeline'}
                </button>
              </form>

              {isRunning && (
                <div className="mt-6 space-y-3 p-4 bg-gray-50 dark:bg-zinc-900/50 rounded-lg border border-gray-100 dark:border-zinc-800">
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-gray-500">Execution Progress</h4>
                  <div className="space-y-3">
                    {pipelineSteps.map((step, idx) => {
                      const isCompleted = pipelineStep > idx;
                      const isCurrent = pipelineStep === idx;
                      return (
                        <div key={idx} className="flex items-center gap-3 text-sm">
                          {isCompleted ? (
                            <CheckCircle2 size={16} className="text-green-500 shrink-0" />
                          ) : isCurrent ? (
                            <div className="w-4 h-4 rounded-full border-2 border-blue-500 border-t-transparent animate-spin shrink-0" />
                          ) : (
                            <div className="w-4 h-4 rounded-full border-2 border-gray-200 dark:border-zinc-700 shrink-0" />
                          )}
                          <span className={`${isCompleted ? 'text-gray-900 dark:text-gray-100 font-medium' : isCurrent ? 'text-blue-600 dark:text-blue-400 font-medium animate-pulse' : 'text-gray-400 dark:text-gray-500'}`}>
                            {step}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Manual Add</CardTitle>
              <CardDescription>Manually add a new company directly.</CardDescription>
            </CardHeader>
            <CardContent>
              {!showAddCompany ? (
                <button
                  onClick={() => {
                    setShowAddCompany(true);
                    setUpsertMode(false);
                  }}
                  className="w-full flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring border border-gray-200 bg-white hover:bg-gray-100 text-gray-900 h-9 px-4 py-2"
                >
                  <Plus size={16} className="mr-2" /> Add Company
                </button>
              ) : (
                <form onSubmit={handleAddCompany} className="space-y-4">
                  {upsertMode && (
                    <div className="p-3 bg-blue-50 dark:bg-blue-900/20 text-blue-800 dark:text-blue-300 rounded-md text-sm flex items-start gap-2">
                      <AlertTriangle size={16} className="mt-0.5 shrink-0 text-blue-600 dark:text-blue-400" />
                      <div>
                        <strong>Company already exists.</strong> Would you like to update its details instead?
                      </div>
                    </div>
                  )}
                  <input
                    type="text"
                    value={addForm.name}
                    onChange={e => setAddForm({...addForm, name: e.target.value})}
                    placeholder="Company Name"
                    required
                    className="w-full px-3 py-2 border border-gray-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 text-gray-900 dark:text-gray-100 rounded-md text-sm outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <input
                    type="url"
                    value={addForm.website}
                    onChange={e => setAddForm({...addForm, website: e.target.value})}
                    placeholder="Website URL"
                    className="w-full px-3 py-2 border border-gray-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 text-gray-900 dark:text-gray-100 rounded-md text-sm outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <input
                    type="text"
                    value={addForm.ai_category}
                    onChange={e => setAddForm({...addForm, ai_category: e.target.value})}
                    placeholder="AI Category"
                    className="w-full px-3 py-2 border border-gray-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 text-gray-900 dark:text-gray-100 rounded-md text-sm outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <input
                    type="text"
                    value={addForm.country}
                    onChange={e => setAddForm({...addForm, country: e.target.value})}
                    placeholder="Country"
                    className="w-full px-3 py-2 border border-gray-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 text-gray-900 dark:text-gray-100 rounded-md text-sm outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <input
                    type="text"
                    value={addForm.segment_tags}
                    onChange={e => setAddForm({...addForm, segment_tags: e.target.value})}
                    placeholder="Segment Tags (comma separated)"
                    className="w-full px-3 py-2 border border-gray-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 text-gray-900 dark:text-gray-100 rounded-md text-sm outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <input
                    type="text"
                    value={addForm.use_cases}
                    onChange={e => setAddForm({...addForm, use_cases: e.target.value})}
                    placeholder="Use Cases (comma separated)"
                    className="w-full px-3 py-2 border border-gray-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 text-gray-900 dark:text-gray-100 rounded-md text-sm outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <div className="flex gap-3 pt-2">
                    <button type="submit" disabled={isCreating || isUpdatingCompany} className="flex-1 bg-blue-600 hover:bg-blue-700 text-white rounded-md py-2 text-sm font-medium transition-colors disabled:opacity-50">
                      {upsertMode ? (isUpdatingCompany ? 'Updating...' : 'Update Existing') : (isCreating ? 'Adding...' : 'Add Company')}
                    </button>
                    <button type="button" onClick={() => {
                      setShowAddCompany(false);
                      setUpsertMode(false);
                    }} className="flex-1 bg-gray-100 hover:bg-gray-200 dark:bg-zinc-800 dark:hover:bg-zinc-700 text-gray-700 dark:text-gray-300 rounded-md py-2 text-sm transition-colors">Cancel</button>
                  </div>
                </form>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="md:col-span-2 space-y-6">
          <Card className="h-full border border-orange-200 dark:border-orange-900/50 shadow-sm">
            <CardHeader className="bg-orange-50/50 dark:bg-orange-900/10 border-b border-orange-100 dark:border-orange-900/30 flex flex-row items-center justify-between py-3">
              <CardTitle className="flex items-center gap-2 text-orange-700 dark:text-orange-400 m-0">
                <LayoutList size={20} />
                Pending Candidates ({pendingCandidates.length})
              </CardTitle>
              {selectedIds.size > 0 && (
                <div className="flex gap-2">
                  <button
                    onClick={handleBulkApprove}
                    disabled={isBulkApproving || isBulkRejecting}
                    className="flex items-center bg-green-600 hover:bg-green-700 text-white text-xs px-3 py-1.5 rounded transition-colors disabled:opacity-50"
                  >
                    {isBulkApproving ? <div className="w-3 h-3 rounded-full border-2 border-white border-t-transparent animate-spin mr-1" /> : <CheckCircle2 size={14} className="mr-1" />}
                    Approve Selected ({selectedIds.size})
                  </button>
                  <button
                    onClick={handleBulkReject}
                    disabled={isBulkRejecting || isBulkApproving}
                    className="flex items-center border border-gray-300 dark:border-zinc-700 hover:bg-gray-100 dark:hover:bg-zinc-800 text-red-600 text-xs px-3 py-1.5 rounded transition-colors disabled:opacity-50"
                  >
                    {isBulkRejecting ? <div className="w-3 h-3 rounded-full border-2 border-red-600 border-t-transparent animate-spin mr-1" /> : <XCircle size={14} className="mr-1" />}
                    Reject Selected ({selectedIds.size})
                  </button>
                </div>
              )}
            </CardHeader>
            <CardContent className="p-0">
              {isLoading ? (
                <div className="p-6 space-y-4">
                  <Skeleton className="h-40 w-full" />
                  <Skeleton className="h-40 w-full" />
                </div>
              ) : pendingCandidates.length > 0 ? (
                <div className="divide-y divide-gray-100 dark:divide-zinc-800">
                  {pendingCandidates.map(candidate => (
                    <div key={candidate.id} className="p-6 hover:bg-gray-50 dark:hover:bg-zinc-900/50 transition-colors">
                      {editingCandidateId === candidate.id ? (
                        <div className="space-y-4">
                          <h3 className="text-sm font-semibold">Edit Candidate</h3>
                          <div className="grid sm:grid-cols-2 gap-4">
                            <input
                              value={editForm.name}
                              onChange={e => setEditForm({...editForm, name: e.target.value})}
                              className="px-3 py-2 border border-gray-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 text-gray-900 dark:text-gray-100 rounded-md text-sm outline-none focus:ring-2 focus:ring-blue-500"
                              placeholder="Name"
                            />
                            <input
                              value={editForm.website}
                              onChange={e => setEditForm({...editForm, website: e.target.value})}
                              className="px-3 py-2 border border-gray-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 text-gray-900 dark:text-gray-100 rounded-md text-sm outline-none focus:ring-2 focus:ring-blue-500"
                              placeholder="Website"
                            />
                            <input
                              value={editForm.ai_category}
                              onChange={e => setEditForm({...editForm, ai_category: e.target.value})}
                              className="px-3 py-2 border border-gray-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 text-gray-900 dark:text-gray-100 rounded-md text-sm outline-none focus:ring-2 focus:ring-blue-500"
                              placeholder="Category"
                            />
                            <input
                              value={editForm.country}
                              onChange={e => setEditForm({...editForm, country: e.target.value})}
                              className="px-3 py-2 border border-gray-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 text-gray-900 dark:text-gray-100 rounded-md text-sm outline-none focus:ring-2 focus:ring-blue-500"
                              placeholder="Country"
                            />
                          </div>
                          <div className="flex gap-2">
                            <button onClick={() => saveEdit(candidate.id)} disabled={isUpdating} className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm transition-colors">Save</button>
                            <button onClick={() => setEditingCandidateId(null)} className="bg-gray-100 hover:bg-gray-200 dark:bg-zinc-800 dark:hover:bg-zinc-700 text-gray-700 dark:text-gray-300 px-4 py-2 rounded-md text-sm transition-colors">Cancel</button>
                          </div>
                        </div>
                      ) : (
                        <div className="flex flex-col xl:flex-row justify-between gap-6">
                          <div className="flex-1 space-y-4">
                            <div className="flex justify-between items-start">
                              <div className="flex items-start gap-3">
                                <input 
                                  type="checkbox" 
                                  checked={selectedIds.has(candidate.id)}
                                  onChange={() => toggleSelection(candidate.id)}
                                  className="mt-1.5 w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                />
                                <div>
                                  <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
                                    {candidate.name}
                                    <button onClick={() => startEditing(candidate)} className="text-gray-400 hover:text-blue-500">
                                      <Edit size={16} />
                                    </button>
                                  </h3>
                                <a href={candidate.website || '#'} target="_blank" rel="noopener noreferrer" className="flex items-center text-sm text-blue-600 dark:text-blue-400 hover:underline mt-1">
                                  <Globe size={14} className="mr-1" /> {candidate.website || 'No website'}
                                </a>
                              </div>
                            </div>
                            <div className="text-right">
                                <Badge variant={candidate.confidence_score >= 0.7 ? 'default' : 'secondary'} className={candidate.confidence_score >= 0.7 ? 'bg-green-600' : ''}>
                                  {Math.round(candidate.confidence_score * 100)}% Confidence
                                </Badge>
                              </div>
                            </div>

                            <div className="grid sm:grid-cols-2 gap-4 text-sm text-gray-600 dark:text-gray-400">
                              <div>
                                <span className="font-medium text-gray-900 dark:text-gray-300">Category:</span> {candidate.ai_category || 'N/A'}
                              </div>
                              <div>
                                <span className="font-medium text-gray-900 dark:text-gray-300">Country:</span> {candidate.country}
                              </div>
                            </div>
                            
                            <div className="space-y-2">
                              <span className="text-xs font-semibold uppercase tracking-wider text-gray-500">Confidence Breakdown</span>
                              <div className="flex flex-wrap gap-2 text-xs">
                                {candidate.confidence_explanation.website_verified ? (
                                  <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200 dark:bg-green-900/20 dark:text-green-400 dark:border-green-900/50">
                                    <Check size={12} className="mr-1" /> Site Verified
                                  </Badge>
                                ) : (
                                  <Badge variant="outline" className="bg-yellow-50 text-yellow-700 border-yellow-200 dark:bg-yellow-900/20 dark:text-yellow-400 dark:border-yellow-900/50">
                                    <AlertTriangle size={12} className="mr-1" /> Unverified Site
                                  </Badge>
                                )}
                                <Badge variant="outline">
                                  {candidate.confidence_explanation.evidence_count} Evidence Sources
                                </Badge>
                                <Badge variant="outline">
                                  {Math.round(candidate.confidence_explanation.field_completeness * 100)}% Complete
                                </Badge>
                                {candidate.confidence_explanation.duplicate_penalty > 0 && (
                                  <Badge variant="destructive">
                                    Duplicate Detected
                                  </Badge>
                                )}
                              </div>
                            </div>
                          </div>

                          <div className="flex xl:flex-col gap-3 shrink-0 self-start w-full xl:w-auto">
                            <button
                              onClick={() => handleApprove(candidate.id)}
                              disabled={processingId !== null || isBulkApproving || isBulkRejecting}
                              className="flex-1 flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring bg-green-600 text-white shadow hover:bg-green-700 h-9 px-4 py-2 disabled:opacity-50"
                            >
                              {processingId === candidate.id ? (
                                <div className="w-4 h-4 rounded-full border-2 border-white border-t-transparent animate-spin mr-2" />
                              ) : (
                                <CheckCircle2 size={16} className="mr-2" />
                              )}
                              {processingId === candidate.id ? 'Approving...' : 'Approve'}
                            </button>
                            <button
                              onClick={() => handleReject(candidate.id)}
                              disabled={processingId !== null || isBulkApproving || isBulkRejecting}
                              className="flex-1 flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring border border-gray-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 shadow-sm hover:bg-gray-100 dark:hover:bg-zinc-900 h-9 px-4 py-2 text-red-600 disabled:opacity-50"
                            >
                              {processingId === candidate.id ? (
                                <div className="w-4 h-4 rounded-full border-2 border-red-600 border-t-transparent animate-spin mr-2" />
                              ) : (
                                <XCircle size={16} className="mr-2" />
                              )}
                              {processingId === candidate.id ? 'Rejecting...' : 'Reject'}
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-20 px-4">
                  <CheckCircle2 size={48} className="mx-auto text-green-500 mb-4 opacity-50" />
                  <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">Inbox Zero</h3>
                  <p className="text-gray-500 dark:text-gray-400">All discovery candidates have been processed.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
