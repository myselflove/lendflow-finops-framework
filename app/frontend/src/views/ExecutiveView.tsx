import React, { useEffect, useState } from 'react';
import { finopsApi } from '../services/api';
import { SummaryResponse, AudienceView } from '../types/finops';
import {
  DollarSign, TrendingDown, Percent, ShieldCheck,
  CheckCircle2, AlertCircle, ArrowUpRight, BarChart3, Layers
} from 'lucide-react';
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer,
  LineChart, Line, CartesianGrid, Legend
} from 'recharts';

interface ExecutiveViewProps {
  audience: AudienceView;
}

export const ExecutiveView: React.FC<ExecutiveViewProps> = ({ audience }) => {
  const [data, setData] = useState<SummaryResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    finopsApi.getSummary()
      .then(res => setData(res))
      .catch(err => {
        console.error('Failed to load summary:', err);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading || !data) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  const { kpis, spend_trend, unit_economics, forecast_90_day, ri_coverage } = data;

  return (
    <div className="space-y-6">
      {/* View Header with Audience Context Banner */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-bold text-white tracking-tight">Executive & CFO Dashboard</h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Target Achieved: $102k/mo
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            {audience === 'executive' && 'High-level financial KPIs, margin expansion, and 90-day board commitments.'}
            {audience === 'engineering-manager' && 'Engineering impact: node rightsizing, Graviton3 migration, and cluster capacity.'}
            {audience === 'team' && 'Team showback context: service attribution and efficiency targets.'}
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="text-right">
            <div className="text-xs text-slate-400 font-mono">ANNUALIZED VALUE</div>
            <div className="text-lg font-bold text-emerald-400 font-mono">
              ${(kpis.annualized_run_rate_savings_usd / 1_000_000).toFixed(2)}M / yr
            </div>
          </div>
        </div>
      </div>

      {/* Primary KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Baseline Spend */}
        <div className="glass-panel p-5 rounded-2xl relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Month 6 Baseline</p>
              <h3 className="text-2xl font-bold text-white mt-1 font-mono">
                ${kpis.baseline_monthly_spend_usd.toLocaleString()}
              </h3>
            </div>
            <div className="p-2.5 rounded-xl bg-slate-800 text-slate-300">
              <DollarSign className="w-5 h-5" />
            </div>
          </div>
          <p className="text-xs text-rose-400 flex items-center mt-3 font-medium">
            <ArrowUpRight className="w-3.5 h-3.5 mr-1" />
            +$108k trajectory over 6 months
          </p>
        </div>

        {/* Projected Monthly Spend */}
        <div className="glass-panel p-5 rounded-2xl relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Post-Optimisation Spend</p>
              <h3 className="text-2xl font-bold text-emerald-400 mt-1 font-mono">
                ${kpis.projected_monthly_spend_usd.toLocaleString()}
              </h3>
            </div>
            <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <TrendingDown className="w-5 h-5" />
            </div>
          </div>
          <p className="text-xs text-emerald-400 flex items-center mt-3 font-medium">
            <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
            Well below &le;$120k threshold
          </p>
        </div>

        {/* Monthly Savings & % */}
        <div className="glass-panel-glow p-5 rounded-2xl relative overflow-hidden">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-medium text-indigo-300 uppercase tracking-wider">Net Monthly Savings</p>
              <h3 className="text-2xl font-bold text-white mt-1 font-mono">
                ${kpis.total_monthly_savings_usd.toLocaleString()}
              </h3>
            </div>
            <div className="p-2.5 rounded-xl bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
              <Percent className="w-5 h-5" />
            </div>
          </div>
          <p className="text-xs text-indigo-300 flex items-center mt-3 font-medium">
            <span className="font-bold mr-1">{kpis.savings_pct}% cut</span> (Target: &ge;33.3%)
          </p>
        </div>

        {/* Gross Margin Impact */}
        <div className="glass-panel p-5 rounded-2xl relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Gross Margin Expansion</p>
              <h3 className="text-2xl font-bold text-white mt-1 font-mono">
                {kpis.projected_gross_margin_pct}%
              </h3>
            </div>
            <div className="p-2.5 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <BarChart3 className="w-5 h-5" />
            </div>
          </div>
          <p className="text-xs text-amber-400 flex items-center mt-3 font-medium">
            +10.25% margin gain on $1M revenue
          </p>
        </div>
      </div>

      {/* Unit Economics Highlight Banner */}
      <div className="p-5 rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-indigo-900/40 grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <div className="text-xs text-slate-400">Monthly Loan Ingestion Volume</div>
          <div className="text-xl font-bold text-white mt-0.5 font-mono">
            {unit_economics.monthly_loan_applications.toLocaleString()} loans
          </div>
        </div>

        <div>
          <div className="text-xs text-slate-400">Current Cost per Loan App</div>
          <div className="text-xl font-bold text-rose-400 mt-0.5 font-mono">
            ${unit_economics.current_cost_per_application_usd.toFixed(4)}
          </div>
          <div className="text-[10px] text-slate-500">${unit_economics.current_cost_per_1k_loans_usd.toFixed(2)} per 1,000</div>
        </div>

        <div>
          <div className="text-xs text-slate-400">Target Cost per Loan App</div>
          <div className="text-xl font-bold text-emerald-400 mt-0.5 font-mono">
            ${unit_economics.projected_cost_per_application_usd.toFixed(4)}
          </div>
          <div className="text-[10px] text-slate-500">${unit_economics.projected_cost_per_1k_loans_usd.toFixed(2)} per 1,000</div>
        </div>

        <div>
          <div className="text-xs text-slate-400">Unit Cost Reduction</div>
          <div className="text-xl font-bold text-indigo-300 mt-0.5 font-mono">
            -${unit_economics.savings_per_1k_loans_usd.toFixed(2)} / 1k
          </div>
          <div className="text-[10px] text-emerald-400 font-semibold">56.9% cloud efficiency gain</div>
        </div>
      </div>

      {/* Charts Grid: Historical Spend Growth & 90-Day Forecast */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Historical Spend Trend */}
        <div className="glass-panel p-6 rounded-2xl">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-semibold text-white">6-Month Historical Spend Trajectory</h3>
              <p className="text-xs text-slate-400">Rapid growth from $72,000 (Month 1) to $180,000 (Month 6 baseline)</p>
            </div>
            <span className="text-xs font-mono px-2 py-1 rounded bg-slate-800 text-slate-300">
              EC2 + EKS = 41.6%
            </span>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={spend_trend} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="spendGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366F1" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#6366F1" stopOpacity={0.0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="month_name" stroke="#64748b" fontSize={11} />
                <YAxis
                  stroke="#64748b"
                  fontSize={11}
                  tickFormatter={(v) => `$${v / 1000}k`}
                />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem' }}
                  formatter={(value: any) => [`$${Number(value).toLocaleString()}`, 'Total Cost']}
                />
                <Area type="monotone" dataKey="total_cost_usd" stroke="#6366F1" strokeWidth={2.5} fillOpacity={1} fill="url(#spendGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 90-Day Implementation Forecast */}
        <div className="glass-panel p-6 rounded-2xl">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-semibold text-white">90-Day Optimisation Forecast</h3>
              <p className="text-xs text-slate-400">Unmanaged trajectory vs. Step 1 &rarr; 2 &rarr; 3 execution</p>
            </div>
            <span className="text-xs font-mono px-2 py-1 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Goal: Day 90
            </span>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={forecast_90_day} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="month_label" stroke="#64748b" fontSize={11} />
                <YAxis
                  stroke="#64748b"
                  fontSize={11}
                  tickFormatter={(v) => `$${v / 1000}k`}
                />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem' }}
                  formatter={(val: any) => [`$${Number(val).toLocaleString()}`]}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                <Line
                  type="monotone"
                  dataKey="unmanaged_spend_usd"
                  name="Unmanaged Spend (Trajectory)"
                  stroke="#f43f5e"
                  strokeWidth={2}
                  strokeDasharray="4 4"
                />
                <Line
                  type="monotone"
                  dataKey="optimised_spend_usd"
                  name="Optimised Cloud Spend"
                  stroke="#10b981"
                  strokeWidth={2.5}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* RI Coverage & Compliance Ring-Fence Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* RI/SP Strategy */}
        <div className="glass-panel p-6 rounded-2xl">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-white flex items-center space-x-2">
              <Layers className="w-4 h-4 text-indigo-400" />
              <span>Commitment Portfolio Target (72% Coverage)</span>
            </h3>
            <span className="text-xs px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 font-mono">
              Current: 0% RI
            </span>
          </div>
          <p className="text-xs text-slate-400 mb-4">
            Shift from 100% On-Demand to a 3-tier commitment strategy applied strictly to post-rightsized baseline:
          </p>

          <div className="space-y-3">
            {Object.entries(ri_coverage.recommended_split).map(([title, pct]) => (
              <div key={title} className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-300">{title}</span>
                  <span className="font-mono text-indigo-400 font-semibold">{pct}%</span>
                </div>
                <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                  <div
                    className="bg-indigo-500 h-full rounded-full"
                    style={{ width: `${pct}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Compliance Ring-Fence Guarantee */}
        <div className="glass-panel p-6 rounded-2xl border-l-4 border-l-emerald-500">
          <div className="flex items-center space-x-2 mb-2">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            <h3 className="font-semibold text-white">Compliance Ring-Fence Protection</h3>
          </div>
          <p className="text-xs text-slate-300 mb-4">
            A non-negotiable <strong className="text-white">${kpis.compliance_ring_fenced_usd.toLocaleString()}/month</strong> budget is strictly locked against hazardous downscaling to guarantee regulatory licensing:
          </p>

          <div className="grid grid-cols-3 gap-3 text-center">
            <div className="p-3 rounded-xl bg-slate-900/90 border border-slate-800">
              <div className="text-[10px] text-slate-400 uppercase font-semibold">PCI DSS v4.0</div>
              <div className="text-sm font-bold text-white mt-1 font-mono">$8,000/mo</div>
              <div className="text-[10px] text-emerald-400 mt-1">3 AZ Dedicated</div>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/90 border border-slate-800">
              <div className="text-[10px] text-slate-400 uppercase font-semibold">SOC 2 Type II</div>
              <div className="text-sm font-bold text-white mt-1 font-mono">$3,500/mo</div>
              <div className="text-[10px] text-emerald-400 mt-1">WORM Object Lock</div>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/90 border border-slate-800">
              <div className="text-[10px] text-slate-400 uppercase font-semibold">RBI IT Framework</div>
              <div className="text-sm font-bold text-white mt-1 font-mono">$5,000/mo</div>
              <div className="text-[10px] text-emerald-400 mt-1">India Residency</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
