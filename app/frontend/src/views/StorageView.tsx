import React, { useEffect, useState } from 'react';
import { finopsApi } from '../services/api';
import { StorageResponse, AudienceView } from '../types/finops';
import { HardDrive, Archive, ShieldCheck, Database, ArrowRight, CheckCircle2 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts';

interface StorageViewProps {
  audience: AudienceView;
}

const COLORS = ['#6366F1', '#10B981', '#F59E0B', '#3B82F6', '#EC4899'];

export const StorageView: React.FC<StorageViewProps> = ({ audience }) => {
  const [data, setData] = useState<StorageResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    finopsApi.getStorage()
      .then(res => setData(res))
      .catch(err => console.error('Storage error:', err))
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
          <h1 className="text-2xl font-bold text-white tracking-tight">Storage & EBS Lifecycle Optimisation</h1>
          <p className="text-sm text-slate-400 mt-1">
            S3 Intelligent-Tiering, Glacier archiving, EBS rightsizing, gp2 &rarr; gp3 volume migrations, and SOC 2 immutable audit log protection.
          </p>
        </div>
        <div className="text-right">
          <div className="text-xs text-slate-400 font-mono">POTENTIAL SAVINGS</div>
          <div className="text-xl font-bold text-emerald-400 font-mono">
            +${data.total_potential_savings_usd.toLocaleString()}/mo
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="glass-panel p-5 rounded-2xl">
          <div className="text-xs text-slate-400 uppercase font-bold">Total Storage Spend</div>
          <div className="text-2xl font-bold text-white mt-1 font-mono">
            ${data.total_storage_monthly_cost_usd.toLocaleString()}
          </div>
          <p className="text-xs text-slate-500 mt-2 font-mono">{data.total_storage_gb.toLocaleString()} GB managed</p>
        </div>

        <div className="glass-panel p-5 rounded-2xl">
          <div className="text-xs text-slate-400 uppercase font-bold">S3 Wrong-Tier Buckets</div>
          <div className="text-2xl font-bold text-amber-400 mt-1 font-mono">
            {data.s3_wrong_tier_count}
          </div>
          <p className="text-xs text-amber-400/80 mt-2">&gt;90 days unaccessed in STANDARD</p>
        </div>

        <div className="glass-panel p-5 rounded-2xl">
          <div className="text-xs text-slate-400 uppercase font-bold">EBS Over-Provisioned</div>
          <div className="text-2xl font-bold text-rose-400 mt-1 font-mono">
            {data.ebs_over_provisioned_count}
          </div>
          <p className="text-xs text-rose-400/80 mt-2">&gt;1TB provisioned with &lt;100GB used</p>
        </div>

        <div className="glass-panel p-5 rounded-2xl">
          <div className="text-xs text-slate-400 uppercase font-bold">gp2 &rarr; gp3 Candidates</div>
          <div className="text-2xl font-bold text-indigo-400 mt-1 font-mono">
            {data.gp2_to_gp3_candidates_count}
          </div>
          <p className="text-xs text-indigo-300 mt-2">20% direct price reduction</p>
        </div>
      </div>

      {/* SOC 2 Immutable Audit Banner */}
      <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs font-bold text-white">SOC 2 Type II WORM Compliance Protection Active</div>
            <div className="text-xs text-slate-400">
              lendflow-audit bucket retains 12-month immutable Object Lock. Tiering to Glacier preserves compliance checksums.
            </div>
          </div>
        </div>
        <span className="text-xs font-mono px-3 py-1 rounded bg-slate-800 text-emerald-400 border border-slate-700">
          PROTECTED
        </span>
      </div>

      {/* Storage Class Breakdown Chart */}
      <div className="glass-panel p-6 rounded-2xl">
        <h3 className="font-semibold text-white mb-1">Storage Class Spend Distribution</h3>
        <p className="text-xs text-slate-400 mb-4">Total monthly dollar spend grouped by storage tier</p>

        <div className="h-60">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data.storage_class_breakdown} margin={{ top: 10, right: 10, left: 0, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="storage_class" stroke="#64748b" fontSize={11} />
              <YAxis
                stroke="#64748b"
                fontSize={11}
                tickFormatter={(v) => `$${v}`}
              />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem' }}
                formatter={(val: any, _: any, item: any) => [
                  `$${Number(val).toLocaleString()} (${item.payload.total_size_gb.toLocaleString()} GB, ${item.payload.resource_count} items)`,
                  'Spend'
                ]}
              />
              <Bar dataKey="total_monthly_cost_usd" radius={[6, 6, 0, 0]}>
                {data.storage_class_breakdown.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* S3 Candidates Table */}
      <div className="glass-panel p-6 rounded-2xl space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-white">S3 Lifecycle Tiering Candidates (Sample)</h3>
          <span className="text-xs text-slate-400 font-mono">Action: Move to Standard-IA / Glacier</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 text-slate-400 uppercase font-mono text-[10px] border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-3">Bucket ID</th>
                <th className="py-2.5 px-3">Service</th>
                <th className="py-2.5 px-3">Size (GB)</th>
                <th className="py-2.5 px-3">Unaccessed</th>
                <th className="py-2.5 px-3">Current &rarr; Target</th>
                <th className="py-2.5 px-3">Current Cost</th>
                <th className="py-2.5 px-3 text-right">Monthly Savings</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 font-mono">
              {data.s3_candidates.map((c, i) => (
                <tr key={i} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-2 px-3 text-white font-medium">{c.resource_id}</td>
                  <td className="py-2 px-3 text-indigo-400">{c.service}</td>
                  <td className="py-2 px-3 text-slate-300">{c.size_gb.toLocaleString()}</td>
                  <td className="py-2 px-3 text-amber-400">{c.days_since_access} days</td>
                  <td className="py-2 px-3 text-slate-300">
                    <span className="text-rose-400">{c.current_storage_class}</span> &rarr;{' '}
                    <span className="text-emerald-400">{c.target_storage_class}</span>
                  </td>
                  <td className="py-2 px-3 text-slate-400">${c.current_monthly_cost_usd.toFixed(2)}</td>
                  <td className="py-2 px-3 text-right text-emerald-400 font-bold">
                    +${c.monthly_savings_usd.toFixed(2)}
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
