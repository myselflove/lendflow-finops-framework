import React, { useEffect, useState } from 'react';
import { finopsApi } from '../services/api';
import { ExplorerResponse, AudienceView } from '../types/finops';
import { Filter, Layers, Database, Calendar, Globe, Shield, RefreshCw } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell
} from 'recharts';

interface ExplorerViewProps {
  audience: AudienceView;
}

const COLORS = ['#6366F1', '#10B981', '#F59E0B', '#3B82F6', '#EC4899', '#8B5CF6', '#14B8A6'];

export const ExplorerView: React.FC<ExplorerViewProps> = ({ audience }) => {
  const [data, setData] = useState<ExplorerResponse | null>(null);
  const [loading, setLoading] = useState(true);

  // Filters state
  const [month, setMonth] = useState<string>('');
  const [service, setService] = useState<string>('');
  const [environment, setEnvironment] = useState<string>('');
  const [region, setRegion] = useState<string>('');
  const [complianceScope, setComplianceScope] = useState<string>('');
  const [groupBy, setGroupBy] = useState<string>('service');

  const fetchExplorerData = () => {
    setLoading(true);
    const params: Record<string, string | number> = { group_by: groupBy };
    if (month) params.month = Number(month);
    if (service) params.service = service;
    if (environment) params.environment = environment;
    if (region) params.region = region;
    if (complianceScope) params.compliance_scope = complianceScope;

    finopsApi.getExplorer(params)
      .then(res => setData(res))
      .catch(err => console.error('Explorer error:', err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchExplorerData();
  }, [month, service, environment, region, complianceScope, groupBy]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Infrastructure Cost Explorer</h1>
          <p className="text-sm text-slate-400 mt-1">
            Multidimensional drilldown across 10,800 daily resource line items by service, environment, region, and compliance scope.
          </p>
        </div>
        <button
          onClick={fetchExplorerData}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition-all"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Data</span>
        </button>
      </div>

      {/* Filter Toolbar */}
      <div className="glass-panel p-4 rounded-2xl grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {/* Month */}
        <div>
          <label className="text-[10px] uppercase font-bold text-slate-400 block mb-1">Month</label>
          <select
            value={month}
            onChange={(e) => setMonth(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500"
          >
            <option value="">All Months (6 mo)</option>
            <option value="1">Month 1 (Jul)</option>
            <option value="2">Month 2 (Aug)</option>
            <option value="3">Month 3 (Sep)</option>
            <option value="4">Month 4 (Oct)</option>
            <option value="5">Month 5 (Nov)</option>
            <option value="6">Month 6 (Dec Baseline)</option>
          </select>
        </div>

        {/* Environment */}
        <div>
          <label className="text-[10px] uppercase font-bold text-slate-400 block mb-1">Environment</label>
          <select
            value={environment}
            onChange={(e) => setEnvironment(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500"
          >
            <option value="">All Envs</option>
            <option value="production">Production</option>
            <option value="staging">Staging (Waste)</option>
            <option value="development">Development (Waste)</option>
          </select>
        </div>

        {/* Region */}
        <div>
          <label className="text-[10px] uppercase font-bold text-slate-400 block mb-1">Region</label>
          <select
            value={region}
            onChange={(e) => setRegion(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500"
          >
            <option value="">All Regions</option>
            <option value="ap-south-1">ap-south-1 (Mumbai)</option>
            <option value="eu-west-1">eu-west-1 (Ireland)</option>
            <option value="eu-central-1">eu-central-1 (Frankfurt)</option>
          </select>
        </div>

        {/* Compliance Scope */}
        <div>
          <label className="text-[10px] uppercase font-bold text-slate-400 block mb-1">Compliance Scope</label>
          <select
            value={complianceScope}
            onChange={(e) => setComplianceScope(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500"
          >
            <option value="">All Compliance</option>
            <option value="pci-dss">PCI DSS (Payments)</option>
            <option value="soc2">SOC 2 (Audit & Ledger)</option>
            <option value="rbi-it">RBI IT Framework</option>
            <option value="gdpr">GDPR</option>
          </select>
        </div>

        {/* Service */}
        <div>
          <label className="text-[10px] uppercase font-bold text-slate-400 block mb-1">Service</label>
          <select
            value={service}
            onChange={(e) => setService(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500"
          >
            <option value="">All 12 Services</option>
            <option value="lendflow-gateway">lendflow-gateway</option>
            <option value="lendflow-auth">lendflow-auth</option>
            <option value="lendflow-ingestion">lendflow-ingestion</option>
            <option value="lendflow-credit-scoring">lendflow-credit-scoring</option>
            <option value="lendflow-underwriting">lendflow-underwriting</option>
            <option value="lendflow-doc-verify">lendflow-doc-verify</option>
            <option value="lendflow-payments">lendflow-payments (PCI)</option>
            <option value="lendflow-ledger">lendflow-ledger</option>
            <option value="lendflow-notifications">lendflow-notifications</option>
            <option value="lendflow-analytics">lendflow-analytics</option>
            <option value="lendflow-audit">lendflow-audit (SOC2)</option>
            <option value="lendflow-collections">lendflow-collections</option>
          </select>
        </div>

        {/* Group By */}
        <div>
          <label className="text-[10px] uppercase font-bold text-slate-400 block mb-1">Group By</label>
          <select
            value={groupBy}
            onChange={(e) => setGroupBy(e.target.value)}
            className="w-full bg-slate-900 border border-indigo-700/60 rounded-lg px-2.5 py-1.5 text-xs text-indigo-300 font-medium focus:outline-none focus:border-indigo-500"
          >
            <option value="service">Group by Service</option>
            <option value="environment">Group by Environment</option>
            <option value="region">Group by Region</option>
            <option value="resource_type">Group by Resource Type</option>
          </select>
        </div>
      </div>

      {loading || !data ? (
        <div className="flex items-center justify-center h-64">
          <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : (
        <>
          {/* Summary Strip */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="glass-panel p-4 rounded-xl">
              <div className="text-xs text-slate-400">Total Filtered Spend</div>
              <div className="text-xl font-bold text-white mt-1 font-mono">
                ${data.total_spend_usd.toLocaleString()}
              </div>
            </div>
            <div className="glass-panel p-4 rounded-xl">
              <div className="text-xs text-slate-400">Filtered Line Items</div>
              <div className="text-xl font-bold text-indigo-400 mt-1 font-mono">
                {data.filtered_records_count.toLocaleString()} / {data.total_records.toLocaleString()}
              </div>
            </div>
            <div className="glass-panel p-4 rounded-xl">
              <div className="text-xs text-slate-400">Group Dimension</div>
              <div className="text-xl font-bold text-slate-200 mt-1 capitalize font-mono">
                {data.group_by}
              </div>
            </div>
            <div className="glass-panel p-4 rounded-xl">
              <div className="text-xs text-slate-400">Categories Formed</div>
              <div className="text-xl font-bold text-emerald-400 mt-1 font-mono">
                {data.grouped_data.length}
              </div>
            </div>
          </div>

          {/* Grouped Bar Chart */}
          <div className="glass-panel p-6 rounded-2xl">
            <h3 className="font-semibold text-white mb-1 capitalize">
              Spend Aggregated by {data.group_by.replace('_', ' ')}
            </h3>
            <p className="text-xs text-slate-400 mb-4">Click to inspect service concentrations and distribution percentages</p>

            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.grouped_data} margin={{ top: 10, right: 10, left: 0, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis
                    dataKey="name"
                    stroke="#64748b"
                    fontSize={10}
                    angle={-20}
                    textAnchor="end"
                    interval={0}
                  />
                  <YAxis
                    stroke="#64748b"
                    fontSize={11}
                    tickFormatter={(v) => `$${v / 1000}k`}
                  />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem' }}
                    formatter={(val: any, _: any, item: any) => [
                      `$${Number(val).toLocaleString()} (${item.payload.percentage}%)`,
                      'Spend'
                    ]}
                  />
                  <Bar dataKey="total_cost_usd" radius={[6, 6, 0, 0]}>
                    {data.grouped_data.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Sample Line Items Table */}
          <div className="glass-panel p-6 rounded-2xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-white">Line Item Audit Sample ({data.sample_records.length} records)</h3>
              <span className="text-xs text-slate-400 font-mono">daily_cost_detail.csv</span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-900/80 text-slate-400 uppercase font-mono text-[10px] border-b border-slate-800">
                  <tr>
                    <th className="py-2.5 px-3">Date</th>
                    <th className="py-2.5 px-3">Service</th>
                    <th className="py-2.5 px-3">Type</th>
                    <th className="py-2.5 px-3">Resource ID</th>
                    <th className="py-2.5 px-3">Env</th>
                    <th className="py-2.5 px-3">Region</th>
                    <th className="py-2.5 px-3 text-right">Daily Cost</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800 font-mono">
                  {data.sample_records.map((r, i) => (
                    <tr key={i} className="hover:bg-slate-800/40 transition-colors">
                      <td className="py-2 px-3 text-slate-400">{r.date}</td>
                      <td className="py-2 px-3 text-white font-medium">{r.service}</td>
                      <td className="py-2 px-3 text-indigo-400">{r.resource_type}</td>
                      <td className="py-2 px-3 text-slate-400 truncate max-w-[150px]">{r.resource_id}</td>
                      <td className="py-2 px-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                          r.environment === 'production'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                        }`}>
                          {r.environment}
                        </span>
                      </td>
                      <td className="py-2 px-3 text-slate-400">{r.region}</td>
                      <td className="py-2 px-3 text-right text-emerald-400 font-semibold">
                        ${r.cost.toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
