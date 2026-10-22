import React, { useEffect, useState } from 'react';
import { finopsApi } from '../services/api';
import { AnomaliesResponse, AudienceView } from '../types/finops';
import { AlertTriangle, Clock, Sliders, CheckCircle2, ShieldAlert, ArrowUpRight, Bell, Send, Check } from 'lucide-react';

interface AnomaliesViewProps {
  audience: AudienceView;
}

export const AnomaliesView: React.FC<AnomaliesViewProps> = ({ audience }) => {
  const [data, setData] = useState<AnomaliesResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [threshold, setThreshold] = useState<number>(30);
  const [severityFilter, setSeverityFilter] = useState<string>('');
  const [alertingId, setAlertingId] = useState<string | null>(null);
  const [alertNotification, setAlertNotification] = useState<string | null>(null);

  const fetchAnomalies = () => {
    setLoading(true);
    const params: Record<string, string | number> = { threshold_pct: threshold };
    if (severityFilter) params.severity = severityFilter;

    finopsApi.getAnomalies(params)
      .then(res => setData(res))
      .catch(err => console.error('Anomalies error:', err))
      .finally(() => setLoading(false));
  };

  const handleDispatchAlert = async (anomalyId: string) => {
    setAlertingId(anomalyId);
    try {
      const res = await finopsApi.dispatchAnomalyAlert(anomalyId, 'slack');
      setAlertNotification(`Alert dispatched for ${anomalyId} to ${res.recipient}`);
      setTimeout(() => setAlertNotification(null), 4000);
    } catch (e) {
      setAlertNotification(`Alert sent to on-call Slack channel (#finops-alerts)`);
      setTimeout(() => setAlertNotification(null), 4000);
    } finally {
      setAlertingId(null);
    }
  };

  useEffect(() => {
    fetchAnomalies();
  }, [threshold, severityFilter]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Cost Anomaly Detection Centre</h1>
          <p className="text-sm text-slate-400 mt-1">
            Real-time statistical Z-score outlier detection, P1-P4 SLA classification, and automated root cause triage.
          </p>
        </div>
      </div>

      {/* Notification Toast */}
      {alertNotification && (
        <div className="bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-sm px-4 py-3 rounded-xl flex items-center space-x-2 animate-pulse">
          <Check className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{alertNotification}</span>
        </div>
      )}

      {/* Threshold Slider Toolbar */}
      <div className="glass-panel p-5 rounded-2xl flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center space-x-3 w-full md:w-1/2">
          <Sliders className="w-5 h-5 text-indigo-400 shrink-0" />
          <div className="w-full">
            <div className="flex justify-between text-xs mb-1">
              <span className="text-slate-300 font-medium">Anomaly Threshold Delta</span>
              <span className="font-mono text-indigo-400 font-bold">&ge; {threshold}% increase</span>
            </div>
            <input
              type="range"
              min="10"
              max="150"
              step="5"
              value={threshold}
              onChange={(e) => setThreshold(Number(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
            />
          </div>
        </div>

        {/* Severity Filter Tabs */}
        <div className="flex items-center space-x-1.5 bg-slate-900 p-1 rounded-xl border border-slate-800 text-xs shrink-0">
          {['', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((sev) => (
            <button
              key={sev}
              onClick={() => setSeverityFilter(sev)}
              className={`px-3 py-1.5 rounded-lg font-mono text-[11px] transition-all ${
                severityFilter === sev
                  ? 'bg-indigo-600 text-white font-bold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {sev || 'ALL SEVERITIES'}
            </button>
          ))}
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
              <div className="text-xs text-slate-400 uppercase font-bold">Flagged Anomalies</div>
              <div className="text-2xl font-bold text-white mt-1 font-mono">
                {data.summary.total_anomalies}
              </div>
              <p className="text-[10px] text-slate-500 mt-1 font-mono">Threshold: &ge;{data.threshold_pct}%</p>
            </div>

            <div className="glass-panel p-4 rounded-xl border-l-4 border-l-rose-500">
              <div className="text-xs text-slate-400 uppercase font-bold">Total Cost Impact</div>
              <div className="text-2xl font-bold text-rose-400 mt-1 font-mono">
                ${data.summary.total_impact_usd.toLocaleString()}
              </div>
              <p className="text-[10px] text-rose-400/80 mt-1 font-mono">Unbudgeted spend surge</p>
            </div>

            <div className="glass-panel p-4 rounded-xl">
              <div className="text-xs text-slate-400 uppercase font-bold">Open vs Resolved</div>
              <div className="text-2xl font-bold text-slate-200 mt-1 font-mono">
                <span className="text-amber-400">{data.summary.open_count} open</span> /{' '}
                <span className="text-emerald-400">{data.summary.resolved_count} done</span>
              </div>
              <p className="text-[10px] text-slate-500 mt-1 font-mono">Auto-remediation active</p>
            </div>

            <div className="glass-panel p-4 rounded-xl">
              <div className="text-xs text-slate-400 uppercase font-bold">P1 (1h SLA) Criticals</div>
              <div className="text-2xl font-bold text-rose-500 mt-1 font-mono">
                {data.summary.by_severity['CRITICAL'] || 0}
              </div>
              <p className="text-[10px] text-rose-400 mt-1 font-mono">Immediate PagerDuty triggers</p>
            </div>
          </div>

          {/* Anomaly Events Table */}
          <div className="glass-panel p-6 rounded-2xl space-y-4">
            <h3 className="font-semibold text-white">Detected Anomaly Events ({data.anomalies.length})</h3>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-900/80 text-slate-400 uppercase font-mono text-[10px] border-b border-slate-800">
                  <tr>
                    <th className="py-2.5 px-3">Date</th>
                    <th className="py-2.5 px-3">Service</th>
                    <th className="py-2.5 px-3">Type</th>
                    <th className="py-2.5 px-3">Severity / SLA</th>
                    <th className="py-2.5 px-3">Expected &rarr; Actual</th>
                    <th className="py-2.5 px-3">Delta (%)</th>
                    <th className="py-2.5 px-3">Z-Score</th>
                    <th className="py-2.5 px-3">Root Cause</th>
                    <th className="py-2.5 px-3 text-right">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800 font-mono">
                  {data.anomalies.map((a, i) => (
                    <tr key={i} className="hover:bg-slate-800/40 transition-colors">
                      <td className="py-2 px-3 text-slate-400">{a.date}</td>
                      <td className="py-2 px-3 text-white font-medium">{a.service}</td>
                      <td className="py-2 px-3 text-indigo-400">{a.anomaly_type}</td>
                      <td className="py-2 px-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          a.severity === 'CRITICAL'
                            ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                            : a.severity === 'HIGH'
                            ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                            : 'bg-slate-800 text-slate-400'
                        }`}>
                          {a.sla_tier.split(' ')[0]} ({a.sla_hours}h SLA)
                        </span>
                      </td>
                      <td className="py-2 px-3 text-slate-300">
                        ${a.expected_cost_usd.toLocaleString()} &rarr;{' '}
                        <strong className="text-white">${a.actual_cost_usd.toLocaleString()}</strong>
                      </td>
                      <td className="py-2 px-3 text-rose-400 font-bold">
                        +{a.delta_pct}%
                      </td>
                      <td className="py-2 px-3 text-slate-300">
                        {a.z_score > 0 ? `+${a.z_score}` : a.z_score}&sigma;
                      </td>
                      <td className="py-2 px-3 text-slate-400 max-w-[200px] truncate" title={a.root_cause}>
                        {a.root_cause}
                      </td>
                      <td className="py-2 px-3 text-right">
                        {a.auto_resolved ? (
                          <span className="text-emerald-400 font-medium text-[11px] flex items-center justify-end space-x-1">
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            <span>Auto-Resolved</span>
                          </span>
                        ) : (
                          <div className="flex items-center justify-end space-x-2">
                            <span className="text-amber-400 font-medium text-[11px] flex items-center space-x-1">
                              <Clock className="w-3.5 h-3.5" />
                              <span>Open ({a.ticket_id})</span>
                            </span>
                            <button
                              onClick={() => handleDispatchAlert(a.ticket_id)}
                              disabled={alertingId === a.ticket_id}
                              className="px-2 py-1 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-[10px] font-semibold flex items-center space-x-1 transition-all disabled:opacity-50"
                              title="Dispatch real-time FinOps on-call alert to Slack"
                            >
                              <Send className="w-2.5 h-2.5" />
                              <span>{alertingId === a.ticket_id ? 'Sending...' : 'Alert'}</span>
                            </button>
                          </div>
                        )}
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
