import React from 'react';
import { AudienceView } from '../types/finops';
import { FileCheck, Users, Calendar, ShieldCheck, Trophy, GitPullRequest, AlertCircle } from 'lucide-react';

interface GovernanceViewProps {
  audience: AudienceView;
}

export const GovernanceView: React.FC<GovernanceViewProps> = ({ audience }) => {
  const raciData = [
    {
      activity: 'Tag Compliance & Hygiene Enforcement',
      finops: 'Accountable',
      cfo: 'Informed',
      vpEng: 'Consulted',
      sre: 'Responsible',
      techLeads: 'Responsible'
    },
    {
      activity: 'Savings Plans & RI Purchasing ($50k+)',
      finops: 'Responsible',
      cfo: 'Accountable',
      vpEng: 'Consulted',
      sre: 'Informed',
      techLeads: 'Informed'
    },
    {
      activity: 'Graviton3 Architecture Migration',
      finops: 'Consulted',
      cfo: 'Informed',
      vpEng: 'Accountable',
      sre: 'Responsible',
      techLeads: 'Responsible'
    },
    {
      activity: 'Non-Production Weekend Scheduling Policy',
      finops: 'Accountable',
      cfo: 'Informed',
      vpEng: 'Consulted',
      sre: 'Responsible',
      techLeads: 'Consulted'
    },
    {
      activity: 'P1 Cost Anomaly Triaging & Root Cause Analysis',
      finops: 'Accountable',
      cfo: 'Informed',
      vpEng: 'Informed',
      sre: 'Responsible',
      techLeads: 'Responsible'
    },
    {
      activity: 'PCI DSS / RBI Ring-Fence Verification',
      finops: 'Consulted',
      cfo: 'Informed',
      vpEng: 'Accountable',
      sre: 'Responsible',
      techLeads: 'Responsible'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">FinOps Governance & RACI Framework</h1>
          <p className="text-sm text-slate-400 mt-1">
            Organizational accountability, review cadences, CI/CD budget guardrails, and behavioral cultural gamification.
          </p>
        </div>
      </div>

      {/* Review Cadences Strip */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="glass-panel p-5 rounded-2xl">
          <div className="flex items-center space-x-2 text-indigo-400 mb-2">
            <Calendar className="w-4 h-4" />
            <h4 className="font-bold text-xs uppercase tracking-wider text-slate-300">Daily Standup</h4>
          </div>
          <p className="text-sm font-semibold text-white">Cost Anomaly Triage</p>
          <p className="text-xs text-slate-400 mt-1">15-min daily check on P1/P2 spend spikes and automated ticketing.</p>
        </div>

        <div className="glass-panel p-5 rounded-2xl">
          <div className="flex items-center space-x-2 text-indigo-400 mb-2">
            <Calendar className="w-4 h-4" />
            <h4 className="font-bold text-xs uppercase tracking-wider text-slate-300">Weekly Sprint</h4>
          </div>
          <p className="text-sm font-semibold text-white">Engineering Showback</p>
          <p className="text-xs text-slate-400 mt-1">Service-level unit cost tracking and PR Infracost impact reviews.</p>
        </div>

        <div className="glass-panel p-5 rounded-2xl">
          <div className="flex items-center space-x-2 text-indigo-400 mb-2">
            <Calendar className="w-4 h-4" />
            <h4 className="font-bold text-xs uppercase tracking-wider text-slate-300">Monthly Board</h4>
          </div>
          <p className="text-sm font-semibold text-white">CFO Variance Deck</p>
          <p className="text-xs text-slate-400 mt-1">Waterfall progress audit vs. $60k target and margin expansion tracking.</p>
        </div>

        <div className="glass-panel p-5 rounded-2xl">
          <div className="flex items-center space-x-2 text-indigo-400 mb-2">
            <Calendar className="w-4 h-4" />
            <h4 className="font-bold text-xs uppercase tracking-wider text-slate-300">Quarterly Cadence</h4>
          </div>
          <p className="text-sm font-semibold text-white">Commitment Rebalancing</p>
          <p className="text-xs text-slate-400 mt-1">Savings Plans & RI expirations review (72% target portfolio coverage).</p>
        </div>
      </div>

      {/* RACI Matrix Table */}
      <div className="glass-panel p-6 rounded-2xl space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-white flex items-center space-x-2">
            <Users className="w-5 h-5 text-indigo-400" />
            <span>FinOps RACI Responsibility Assignment Matrix</span>
          </h3>
          <div className="flex space-x-3 text-[11px] font-mono">
            <span className="text-emerald-400">R: Responsible</span>
            <span className="text-indigo-400">A: Accountable</span>
            <span className="text-amber-400">C: Consulted</span>
            <span className="text-slate-400">I: Informed</span>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 text-slate-400 uppercase font-mono text-[10px] border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-3">FinOps Decision / Activity</th>
                <th className="py-2.5 px-3 text-center">FinOps Lead</th>
                <th className="py-2.5 px-3 text-center">CFO</th>
                <th className="py-2.5 px-3 text-center">VP Engineering</th>
                <th className="py-2.5 px-3 text-center">SRE / DevOps</th>
                <th className="py-2.5 px-3 text-center">Tech Leads</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 font-mono">
              {raciData.map((row, i) => (
                <tr key={i} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-2.5 px-3 text-white font-sans font-medium">{row.activity}</td>
                  <td className="py-2.5 px-3 text-center">
                    <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                      {row.finops}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-center">
                    <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-slate-800 text-slate-300">
                      {row.cfo}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-center">
                    <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                      {row.vpEng}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-center">
                    <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      {row.sre}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-center">
                    <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      {row.techLeads}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* CI/CD Guardrails & Cultural Gamification Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* CI/CD Guardrails */}
        <div className="glass-panel p-6 rounded-2xl space-y-3">
          <div className="flex items-center space-x-2">
            <GitPullRequest className="w-5 h-5 text-indigo-400" />
            <h3 className="font-semibold text-white">CI/CD Budget Gates & Admission Controllers</h3>
          </div>
          <p className="text-xs text-slate-400">
            Automated circuit breakers integrated into GitHub Actions and Kubernetes admission controllers:
          </p>

          <div className="space-y-2.5 text-xs">
            <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
              <div>
                <div className="font-bold text-white">Infracost Pull Request Check</div>
                <div className="text-slate-400 text-[11px]">Fails build if Terraform change adds &gt;$500/mo without FinOps signoff</div>
              </div>
              <span className="text-emerald-400 font-mono text-xs">ACTIVE</span>
            </div>

            <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
              <div>
                <div className="font-bold text-white">OPA Gatekeeper Admission Webhook</div>
                <div className="text-slate-400 text-[11px]">Rejects pods missing Owner, Environment, or ComplianceScope tags</div>
              </div>
              <span className="text-emerald-400 font-mono text-xs">ENFORCED</span>
            </div>

            <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
              <div>
                <div className="font-bold text-white">Nightly Non-Prod Auto-Shutdown</div>
                <div className="text-slate-400 text-[11px]">Lambda shuts down non-prod nodes at 20:00 IST weekdays and weekends</div>
              </div>
              <span className="text-emerald-400 font-mono text-xs">SCHEDULED</span>
            </div>
          </div>
        </div>

        {/* Gamification Showback Leaderboard */}
        <div className="glass-panel p-6 rounded-2xl space-y-3">
          <div className="flex items-center space-x-2">
            <Trophy className="w-5 h-5 text-amber-400" />
            <h3 className="font-semibold text-white">Team Efficiency Leaderboard (Month 6)</h3>
          </div>
          <p className="text-xs text-slate-400">
            Monthly showback recognition for engineering squads based on unit cost reduction & tag hygiene:
          </p>

          <div className="space-y-2 text-xs">
            <div className="p-3 rounded-xl bg-gradient-to-r from-amber-500/10 to-transparent border border-amber-500/20 flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <span className="font-bold text-amber-400 font-mono text-base">#1</span>
                <div>
                  <div className="font-bold text-white">Core Financials (lendflow-ledger)</div>
                  <div className="text-slate-400 text-[11px]">98.2% Tag Compliance &bull; 0 Idle Waste</div>
                </div>
              </div>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 font-mono">
                GOLD SQUAD
              </span>
            </div>

            <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <span className="font-bold text-slate-300 font-mono text-base">#2</span>
                <div>
                  <div className="font-bold text-white">Data Platform (lendflow-ingestion)</div>
                  <div className="text-slate-400 text-[11px]">94.5% Tag Compliance &bull; -18% unit cost</div>
                </div>
              </div>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-300 font-mono">
                SILVER SQUAD
              </span>
            </div>

            <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <span className="font-bold text-amber-600 font-mono text-base">#3</span>
                <div>
                  <div className="font-bold text-white">Customer Engagement (notifications)</div>
                  <div className="text-slate-400 text-[11px]">91.0% Tag Compliance &bull; Lambda tuning done</div>
                </div>
              </div>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-600/10 text-amber-600 font-mono">
                BRONZE SQUAD
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
