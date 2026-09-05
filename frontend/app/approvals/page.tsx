'use client';

import { useState, useEffect } from 'react';
import { ShieldCheck, RefreshCw, CheckCircle, XCircle, Clock, AlertTriangle, ArrowLeft, Zap } from 'lucide-react';
import { api, Approval } from '@/lib/api';

export default function ApprovalsPage() {
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [deciding, setDeciding] = useState<string | null>(null);

  const fetchApprovals = async () => {
    setLoading(true);
    try {
      const res = await api.getPendingApprovals();
      setApprovals(res.approvals);
    } catch {
      setError('Failed to fetch approvals');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchApprovals(); }, []);

  const handleDecision = async (threadId: string, decision: string, notes?: string) => {
    setDeciding(threadId);
    try {
      await api.decideApproval(threadId, decision, { notes });
      fetchApprovals();
    } catch {
      setError('Failed to submit decision');
    } finally {
      setDeciding(null);
    }
  };

  const statusColor = (s: string) => {
    const c: Record<string, string> = {
      PENDING:  'bg-amber-50 text-amber-700 border-amber-200',
      APPROVED: 'bg-emerald-50 text-emerald-700 border-emerald-200',
      REJECTED: 'bg-red-50 text-red-700 border-red-200',
      EXECUTED: 'bg-blue-50 text-blue-700 border-blue-200',
    };
    return c[s] || 'bg-gray-50 text-gray-600 border-gray-200';
  };

  const statusIcon = (s: string) => {
    const icons: Record<string, typeof Clock> = { PENDING: Clock, APPROVED: CheckCircle, REJECTED: XCircle, EXECUTED: Zap };
    const Icon = icons[s] || Clock;
    return <Icon className="w-3.5 h-3.5" />;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-amber-50/20">
      <header className="relative bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 text-white shadow-lg">
        <div className="max-w-6xl mx-auto px-6 py-5 flex items-center gap-4">
          <a href="/" className="w-9 h-9 bg-white/10 hover:bg-white/20 rounded-lg flex items-center justify-center transition-colors">
            <ArrowLeft className="w-4 h-4" />
          </a>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-amber-500 to-orange-600 rounded-xl flex items-center justify-center shadow-lg">
              <ShieldCheck className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-semibold tracking-tight">Approvals</h1>
              <p className="text-xs text-white/50">Human-in-the-loop decisions</p>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8 animate-slide-up">
          <div className="flex items-center gap-3">
            <h2 className="text-xl font-bold text-gray-900">Pending Approvals</h2>
            {approvals.length > 0 && (
              <span className="px-2.5 py-0.5 bg-amber-100 text-amber-700 rounded-full text-xs font-bold border border-amber-200">{approvals.length}</span>
            )}
          </div>
          <button onClick={fetchApprovals} disabled={loading}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-600 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 transition-all shadow-sm disabled:opacity-50">
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />Refresh
          </button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl mb-6 text-sm animate-slide-down flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 flex-shrink-0" />{error}
          </div>
        )}

        {loading ? (
          <div className="space-y-4">
            {[1, 2].map((i) => (
              <div key={i} className="glass-strong rounded-2xl p-6 space-y-3">
                <div className="skeleton h-5 w-40" />
                <div className="skeleton h-4 w-56" />
                <div className="skeleton h-12 w-full" />
              </div>
            ))}
          </div>
        ) : approvals.length === 0 ? (
          <div className="glass-strong rounded-2xl p-12 text-center animate-fade-in">
            <div className="w-16 h-16 bg-emerald-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="w-8 h-8 text-emerald-500" />
            </div>
            <p className="text-gray-700 font-semibold text-lg">All caught up!</p>
            <p className="text-sm text-gray-400 mt-1">No pending approvals at the moment</p>
          </div>
        ) : (
          <div className="space-y-4">
            {approvals.map((a, idx) => (
              <div key={a.thread_id}
                className="glass-strong rounded-2xl overflow-hidden shadow-md shadow-gray-200/30 card-hover animate-slide-up"
                style={{ animationDelay: `${idx * 60}ms` }}>
                <div className="flex">
                  <div className="w-1.5 flex-shrink-0 bg-gradient-to-b from-amber-400 to-orange-500" />
                  <div className="flex-1 p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-bold text-gray-900 text-base">{a.action_type} Request</h3>
                          <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${statusColor(a.status)}`}>
                            {statusIcon(a.status)}{a.status}
                          </span>
                        </div>
                        <p className="text-sm text-gray-500 mt-1">
                          Customer: <span className="font-mono font-medium text-gray-700">{a.customer_id}</span>
                          {a.order_id && <span> &middot; Order: <span className="font-mono font-medium text-gray-700">{a.order_id}</span></span>}
                        </p>
                      </div>
                    </div>
                    {a.requested_amount && <p className="text-3xl font-extrabold text-gradient mb-4">₹{a.requested_amount.toLocaleString()}</p>}
                    <p className="text-sm text-gray-700 mb-4 leading-relaxed">{a.requested_reason}</p>
                    {a.ai_reasoning_summary && (
                      <div className="bg-gradient-to-br from-brand-50 to-indigo-50 border border-brand-100 rounded-xl p-4 mb-4">
                        <div className="flex items-center gap-2 mb-2">
                          <Zap className="w-4 h-4 text-brand-500" />
                          <p className="text-xs font-semibold text-brand-700 uppercase tracking-wide">AI Reasoning</p>
                        </div>
                        <p className="text-sm text-brand-800/80 leading-relaxed">{a.ai_reasoning_summary}</p>
                      </div>
                    )}
                    {a.status === 'PENDING' && (
                      <div className="flex items-center gap-3 pt-4 border-t border-gray-100">
                        <button onClick={() => handleDecision(a.thread_id, 'approve')} disabled={deciding === a.thread_id}
                          className="flex items-center gap-2 px-5 py-2.5 btn-success-gradient text-white text-sm rounded-xl font-medium disabled:opacity-50">
                          {deciding === a.thread_id ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <CheckCircle className="w-4 h-4" />}
                          Approve
                        </button>
                        <button onClick={() => handleDecision(a.thread_id, 'reject', 'Rejected by support agent')} disabled={deciding === a.thread_id}
                          className="flex items-center gap-2 px-5 py-2.5 btn-danger-gradient text-white text-sm rounded-xl font-medium disabled:opacity-50">
                          <XCircle className="w-4 h-4" />Reject
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}