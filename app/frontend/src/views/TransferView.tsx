import React, { useEffect, useState } from 'react';
import { finopsApi } from '../services/api';
import { TransferResponse, AudienceView } from '../types/finops';
import { ArrowLeftRight, Network, Zap, CheckCircle2, AlertOctagon } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

interface TransferViewProps {
  audience: AudienceView;
}

const COLORS = ['#F43F5E', '#6366F1', '#10B981', '#F59E0B', '#3B82F6', '#8B5CF6'];

export const TransferView: React.FC<TransferViewProps> = ({ audience }) => {
  const [data, setData] = useState<TransferResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    finopsApi.getTransfer()
      .then(res => setData(res))
      .catch(err => console.error('Transfer error:', err))
      .finally(() => setLoading(false));
  }, []);

  if (loading || !data) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Data Transfer & Networking Analysis</h1>
          <p className="text-sm text-slate-400 mt-1">
            Cross-AZ traffic analysis, VPC Gateway Endpoint optimization, inter-region transfer containment, and AZ-aware pod affinity.
          </p>
        </div>
        <div className="text-right">
          <div className="text-xs text-slate-400 font-mono">CROSS-AZ COST IMPACT</div>
          <div className="text-xl font-bold text-rose-400 font-mono">
            ${data.cross_az_cost_usd.toLocaleString()} ({data.cross_az_percentage}%)
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass-panel p-5 rounded-2xl">
          <div className="text-xs text-slate-400 uppercase font-bold">Total Network Transfer Spend</div>
          <div className="text-2xl font-bold text-white mt-1 font-mono">
            ${data.total_transfer_cost_usd.toLocaleString()}
          </div>
          <p className="text-xs text-slate-500 mt-2 font-mono">{data.total_transfer_gb.toLocaleString()} GB transferred</p>
        </div>

        <div className="glass-panel p-5 rounded-2xl border-l-4 border-l-rose-500">
          <div className="text-xs text-slate-400 uppercase font-bold">Cross-AZ Waste Component</div>
          <div className="text-2xl font-bold text-rose-400 mt-1 font-mono">
            ${data.cross_az_cost_usd.toLocaleString()}
          </div>
          <p className="text-xs text-rose-400/90 mt-2 font-medium">60% of all transfer events span availability zones</p>
        </div>

        <div className="glass-panel p-5 rounded-2xl">
          <div className="text-xs text-slate-400 uppercase font-bold">Potential Endpoint Savings</div>
          <div className="text-2xl font-bold text-emerald-400 mt-1 font-mono">
            +$2,450 / mo
          </div>
          <p className="text-xs text-emerald-400 mt-2 font-medium">Via VPC Gateway Endpoints + Pod Colocation</p>
        </div>
      </div>

      {/* Transfer Distribution & Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Pie Chart Breakdown */}
        <div className="glass-panel p-6 rounded-2xl lg:col-span-1">
          <h3 className="font-semibold text-white mb-1">Transfer Cost by Type</h3>
          <p className="text-xs text-slate-400 mb-4">Percentage share of total networking spend</p>

          <div className="h-52">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.transfer_type_breakdown}
                  dataKey="total_cost_usd"
                  nameKey="transfer_type"
                  cx="50%"
                  cy="50%"
                  outerRadius={70}
                  innerRadius={40}
                  paddingAngle={3}
                >
                  {data.transfer_type_breakdown.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem' }}
                  formatter={(val: any) => [`$${Number(val).toLocaleString()}`, 'Cost']}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="space-y-1.5 mt-2">
            {data.transfer_type_breakdown.map((t, i) => (
              <div key={i} className="flex justify-between items-center text-xs">
                <div className="flex items-center space-x-2">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: COLORS[i % COLORS.length] }}></span>
                  <span className="text-slate-300 font-mono text-[11px]">{t.transfer_type}</span>
                </div>
                <span className="font-mono text-slate-400">{t.cost_percentage}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* Actionable Engineering Recommendations */}
        <div className="glass-panel p-6 rounded-2xl lg:col-span-2 space-y-4">
          <h3 className="font-semibold text-white">Targeted Network Architecture Recommendations</h3>
          <div className="space-y-3">
            {data.recommendations.map((rec, i) => (
              <div key={i} className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-2">
                <div className="flex justify-between items-start">
                  <div className="flex items-center space-x-2">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                      {rec.priority}
                    </span>
                    <h4 className="font-semibold text-white text-sm">{rec.title}</h4>
                  </div>
                  <span className="text-emerald-400 font-bold font-mono text-sm">
                    +${rec.estimated_monthly_savings_usd}/mo
                  </span>
                </div>
                <p className="text-xs text-slate-300">{rec.impact}</p>
                <div className="text-[11px] text-slate-500 font-mono">
                  Complexity: <strong className="text-slate-400">{rec.complexity}</strong>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Top 10 Costliest Transfer Paths Table */}
      <div className="glass-panel p-6 rounded-2xl space-y-4">
        <h3 className="font-semibold text-white">Top 10 Costliest Data Transfer Paths</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 text-slate-400 uppercase font-mono text-[10px] border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-3">Source &rarr; Destination</th>
                <th className="py-2.5 px-3">Transfer Type</th>
                <th className="py-2.5 px-3">Total Volume (GB)</th>
                <th className="py-2.5 px-3">Optimisation Recommendation</th>
                <th className="py-2.5 px-3 text-right">Total Cost</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 font-mono">
              {data.top_10_costliest_paths.map((p, i) => (
                <tr key={i} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-2 px-3 text-white font-medium">
                    <span className="text-indigo-400">{p.source_service}</span> &rarr;{' '}
                    <span className="text-emerald-400">{p.destination_service}</span>
                  </td>
                  <td className="py-2 px-3 text-slate-400">{p.transfer_type}</td>
                  <td className="py-2 px-3 text-slate-300">{p.total_gb_transferred.toLocaleString()} GB</td>
                  <td className="py-2 px-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                      p.is_wasteful
                        ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                        : 'bg-slate-800 text-slate-400'
                    }`}>
                      {p.optimization}
                    </span>
                  </td>
                  <td className="py-2 px-3 text-right text-rose-400 font-bold">
                    ${p.total_cost_usd.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
