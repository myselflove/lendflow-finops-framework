import React, { useEffect, useState } from 'react';
import { finopsApi } from '../services/api';
import { TagsResponse, AudienceView } from '../types/finops';
import { Tags, ShieldCheck, AlertCircle, BarChart2, EyeOff, CheckCircle } from 'lucide-react';

interface TaggingViewProps {
  audience: AudienceView;
}

export const TaggingView: React.FC<TaggingViewProps> = ({ audience }) => {
  const [data, setData] = useState<TagsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    finopsApi.getTags()
      .then(res => setData(res))
      .catch(err => console.error('Tagging error:', err))
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
          <h1 className="text-2xl font-bold text-white tracking-tight">Tag Governance & Dark Spend Heatmap</h1>
          <p className="text-sm text-slate-400 mt-1">
            Tracking compliance across 10 mandatory FinOps tags, unallocated dark spend detection, and team accountability.
          </p>
        </div>
        <div className="text-right">
          <div className="text-xs text-slate-400 font-mono">OVERALL COMPLIANCE</div>
          <div className="text-xl font-bold text-emerald-400 font-mono">
            {data.overall_compliance_rate_pct}%
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass-panel p-5 rounded-2xl">
          <div className="text-xs text-slate-400 uppercase font-bold">Total Resources Analyzed</div>
          <div className="text-2xl font-bold text-white mt-1 font-mono">
            {data.total_resources_analyzed.toLocaleString()}
          </div>
          <p className="text-xs text-slate-500 mt-2 font-mono">Audit across EC2, RDS, EKS, S3, EBS</p>
        </div>

        <div className="glass-panel p-5 rounded-2xl border-l-4 border-l-rose-500">
          <div className="text-xs text-slate-400 uppercase font-bold">Dark (Unallocated) Spend</div>
          <div className="text-2xl font-bold text-rose-400 mt-1 font-mono">
            ${data.dark_spend_monthly_usd.toLocaleString()} / mo
          </div>
          <p className="text-xs text-rose-400/90 mt-2 font-medium">
            {data.dark_spend_percentage}% of cloud spend missing Owner or CostCenter
          </p>
        </div>

        <div className="glass-panel p-5 rounded-2xl">
          <div className="text-xs text-slate-400 uppercase font-bold">Mandatory Tags Required</div>
          <div className="text-2xl font-bold text-indigo-400 mt-1 font-mono">
            10 Tags
          </div>
          <p className="text-xs text-indigo-300 mt-2">5 Core FinOps + 5 Extended Governance</p>
        </div>
      </div>

      {/* 10 Mandatory Tags Metrics Grid */}
      <div className="glass-panel p-6 rounded-2xl space-y-4">
        <h3 className="font-semibold text-white">10 Mandatory FinOps Tag Compliance Rates</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data.mandatory_tags_metrics.map((tag, i) => (
            <div key={i} className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
              <div className="flex justify-between items-center text-xs">
                <div className="flex items-center space-x-2">
                  <span className="font-mono font-bold text-white text-sm">{tag.tag_name}</span>
                  <span className={`px-1.5 py-0.5 rounded text-[10px] font-mono ${
                    tag.is_core ? 'bg-indigo-500/20 text-indigo-300' : 'bg-slate-800 text-slate-400'
                  }`}>
                    {tag.is_core ? 'Core Tag' : 'Governance Tag'}
                  </span>
                </div>
                <span className={`font-mono font-bold text-sm ${
                  tag.compliance_rate_pct >= 85 ? 'text-emerald-400' : 'text-amber-400'
                }`}>
                  {tag.compliance_rate_pct}%
                </span>
              </div>

              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all ${
                    tag.compliance_rate_pct >= 85 ? 'bg-emerald-500' : 'bg-amber-500'
                  }`}
                  style={{ width: `${tag.compliance_rate_pct}%` }}
                ></div>
              </div>

              <div className="flex justify-between text-[10px] text-slate-500 font-mono">
                <span>{tag.compliant_resources.toLocaleString()} compliant</span>
                <span>{tag.non_compliant_resources.toLocaleString()} missing</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Team / Service Compliance Heatmap Table */}
      <div className="glass-panel p-6 rounded-2xl space-y-4">
        <h3 className="font-semibold text-white">Service & Environment Tag Compliance Heatmap</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 text-slate-400 uppercase font-mono text-[10px] border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-3">Service</th>
                <th className="py-2.5 px-3">Environment</th>
                <th className="py-2.5 px-3">Total Resources</th>
                <th className="py-2.5 px-3">Compliant Resources</th>
                <th className="py-2.5 px-3">Common Missing Tags</th>
                <th className="py-2.5 px-3 text-right">Compliance Rate</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 font-mono">
              {data.service_heatmap.map((row, i) => (
                <tr key={i} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-2 px-3 text-white font-medium">{row.service_or_team}</td>
                  <td className="py-2 px-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                      row.environment === 'production'
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                    }`}>
                      {row.environment}
                    </span>
                  </td>
                  <td className="py-2 px-3 text-slate-400">{row.total_resources}</td>
                  <td className="py-2 px-3 text-slate-300">{row.compliant_resources}</td>
                  <td className="py-2 px-3">
                    {row.missing_tags.length > 0 ? (
                      <span className="text-amber-400/90 text-[11px]">
                        {row.missing_tags.join(', ')}
                      </span>
                    ) : (
                      <span className="text-emerald-400 text-[11px]">None (100% compliant)</span>
                    )}
                  </td>
                  <td className="py-2 px-3 text-right font-bold">
                    <span className={row.compliance_rate_pct >= 80 ? 'text-emerald-400' : 'text-rose-400'}>
                      {row.compliance_rate_pct}%
                    </span>
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
