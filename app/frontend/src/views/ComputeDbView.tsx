import React, { useEffect, useState } from 'react';
import { finopsApi } from '../services/api';
import { OptimisationsResponse, AudienceView } from '../types/finops';
import {
  Cpu, Database, ShieldAlert, CheckCircle, Clock, Zap,
  Lock, AlertTriangle, ArrowRight
} from 'lucide-react';

interface ComputeDbViewProps {
  audience: AudienceView;
}

export const ComputeDbView: React.FC<ComputeDbViewProps> = ({ audience }) => {
  const [data, setData] = useState<OptimisationsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [phaseFilter, setPhaseFilter] = useState<string>('');
  const [effortFilter, setEffortFilter] = useState<string>('');

  useEffect(() => {
    finopsApi.getOptimisations()
      .then(res => setData(res))
      .catch(err => console.error('Failed to load optimisations:', err))
      .finally(() => setLoading(false));
  }, []);

  if (loading || !data) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  const { recommendations, compliance_locks, recommendations_by_phase } = data;

  const filtered = recommendations.filter(r => {
    if (phaseFilter && !r.phase.includes(phaseFilter)) return false;
    if (effortFilter && r.effort !== effortFilter) return false;
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-bold text-white tracking-tight">Compute & Database Optimisation</h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              18 Prioritised Initiatives
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Graviton3 migration, EC2 fleet downsizing, RDS cluster rightsizing, Karpenter spot adoption, and strict compliance ring-fences.
          </p>
        </div>

        {/* Phase Counts */}
        <div className="flex items-center space-x-2">
          {Object.entries(recommendations_by_phase).map(([phase, count]) => (
            <div key={phase} className="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs">
              <span className="text-slate-400 mr-1.5">{phase.split('—')[0].trim()}:</span>
              <span className="text-white font-bold">{count}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Compliance Ring-Fence Guardrails Banner */}
      <div className="glass-panel p-5 rounded-2xl border-l-4 border-l-amber-500 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <ShieldAlert className="w-5 h-5 text-amber-400" />
            <h3 className="font-semibold text-white">Compliance Ring-Fence Guardrails (Immutable Constraints)</h3>
          </div>
          <span className="text-xs font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
            $16,300 Protected Budget
          </span>
        </div>
        <p className="text-xs text-slate-300">
          The following microservices are locked against aggressive downscaling. Any optimization proposal targeting these services must preserve high-availability minimums:
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          {compliance_locks.map((lock, i) => (
            <div key={i} className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800/80 space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-white">{lock.service}</span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300">
                  {lock.framework}
                </span>
              </div>
              <p className="text-[11px] text-slate-400">{lock.rule}</p>
              {lock.protected_budget_usd > 0 && (
                <div className="text-[11px] text-emerald-400 font-mono font-medium">
                  Protected: ${lock.protected_budget_usd.toLocaleString()}/mo
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-2 bg-slate-900 p-1 rounded-xl border border-slate-800 text-xs">
          <button
            onClick={() => setPhaseFilter('')}
            className={`px-3 py-1.5 rounded-lg transition-all ${
              phaseFilter === '' ? 'bg-indigo-600 text-white font-medium' : 'text-slate-400 hover:text-white'
            }`}
          >
            All Phases (18)
          </button>
          <button
            onClick={() => setPhaseFilter('Step 1')}
            className={`px-3 py-1.5 rounded-lg transition-all ${
              phaseFilter === 'Step 1' ? 'bg-indigo-600 text-white font-medium' : 'text-slate-400 hover:text-white'
            }`}
          >
            Step 1: Eliminate (6)
          </button>
          <button
            onClick={() => setPhaseFilter('Step 2')}
            className={`px-3 py-1.5 rounded-lg transition-all ${
              phaseFilter === 'Step 2' ? 'bg-indigo-600 text-white font-medium' : 'text-slate-400 hover:text-white'
            }`}
          >
            Step 2: Right-Size (7)
          </button>
          <button
            onClick={() => setPhaseFilter('Step 3')}
            className={`px-3 py-1.5 rounded-lg transition-all ${
              phaseFilter === 'Step 3' ? 'bg-indigo-600 text-white font-medium' : 'text-slate-400 hover:text-white'
            }`}
          >
            Step 3: Commitments (5)
          </button>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-xs text-slate-400">Effort:</span>
          {['', 'LOW', 'MEDIUM', 'HIGH'].map((eff) => (
            <button
              key={eff}
              onClick={() => setEffortFilter(eff)}
              className={`px-2.5 py-1 rounded-lg text-xs font-mono transition-all ${
                effortFilter === eff
                  ? 'bg-slate-700 text-white font-bold'
                  : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
              }`}
            >
              {eff || 'ALL'}
            </button>
          ))}
        </div>
      </div>

      {/* 18 Recommendations Cards */}
      <div className="grid grid-cols-1 gap-3">
        {filtered.map((item) => (
          <div
            key={item.id}
            className="glass-panel p-5 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4 hover:border-slate-700 transition-all group"
          >
            <div className="flex items-start space-x-4 min-w-0">
              <div className="w-8 h-8 rounded-xl bg-slate-800/80 border border-slate-700/60 flex items-center justify-center text-xs font-bold text-slate-300 font-mono shrink-0">
                #{item.rank}
              </div>

              <div className="min-w-0">
                <div className="flex items-center space-x-2 flex-wrap gap-y-1">
                  <h4 className="font-semibold text-white text-base group-hover:text-indigo-300 transition-colors">
                    {item.title}
                  </h4>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-slate-800 text-slate-400 border border-slate-700">
                    {item.appendix_a}
                  </span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                    {item.category}
                  </span>
                  {item.compliance_locked && (
                    <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20 flex items-center space-x-1">
                      <Lock className="w-3 h-3" />
                      <span>{item.compliance_impact}</span>
                    </span>
                  )}
                </div>

                <p className="text-xs text-slate-300 mt-1.5 leading-relaxed">
                  {item.action}
                </p>

                <div className="flex items-center space-x-4 mt-2.5 text-[11px] text-slate-400 font-mono">
                  <span className="flex items-center space-x-1">
                    <Clock className="w-3.5 h-3.5 text-slate-500" />
                    <span>Impl: {item.implementation_days}d</span>
                  </span>
                  <span className="flex items-center space-x-1">
                    <Zap className="w-3.5 h-3.5 text-slate-500" />
                    <span>Payback: {item.payback_days}d</span>
                  </span>
                  <span>Effort: <strong className="text-slate-300">{item.effort}</strong></span>
                  <span>Risk: <strong className="text-slate-300">{item.risk}</strong></span>
                </div>
              </div>
            </div>

            {/* Savings Badge */}
            <div className="text-right shrink-0 border-t md:border-t-0 md:border-l border-slate-800 pt-3 md:pt-0 md:pl-6">
              <div className="text-[10px] uppercase font-bold text-slate-400">Monthly Run-Rate</div>
              <div className="text-xl font-bold text-emerald-400 font-mono mt-0.5">
                +${item.estimated_monthly_savings_usd.toLocaleString()}
              </div>
              <div className="text-[10px] text-slate-500 font-mono">
                ${(item.estimated_monthly_savings_usd * 12).toLocaleString()}/yr
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
