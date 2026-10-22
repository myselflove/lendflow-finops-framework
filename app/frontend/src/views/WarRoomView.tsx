import React, { useEffect, useState } from 'react';
import { finopsApi } from '../services/api';
import { WarRoomResponse, WarRoomScenario, WarRoomActionResponse, AudienceView } from '../types/finops';
import {
  Swords, AlertTriangle, ShieldCheck, CheckCircle2,
  XCircle, Clock, DollarSign, Play, RotateCcw
} from 'lucide-react';

interface WarRoomViewProps {
  audience: AudienceView;
}

export const WarRoomView: React.FC<WarRoomViewProps> = ({ audience }) => {
  const [data, setData] = useState<WarRoomResponse | null>(null);
  const [selectedScenarioId, setSelectedScenarioId] = useState<string>('cfo-90-day-ultimatum');
  const [selectedActionIds, setSelectedActionIds] = useState<string[]>([]);
  const [simResult, setSimResult] = useState<WarRoomActionResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [evaluating, setEvaluating] = useState(false);

  useEffect(() => {
    finopsApi.getWarRoom()
      .then(res => {
        setData(res);
        if (res.scenarios.length > 0) {
          setSelectedScenarioId(res.scenarios[0].id);
        }
      })
      .catch(err => console.error('War room error:', err))
      .finally(() => setLoading(false));
  }, []);

  const currentScenario = data?.scenarios.find(s => s.id === selectedScenarioId);

  const toggleAction = (actionId: string) => {
    const updated = selectedActionIds.includes(actionId)
      ? selectedActionIds.filter(id => id !== actionId)
      : [...selectedActionIds, actionId];
    setSelectedActionIds(updated);
    setSimResult(null);
  };

  const runSimulation = () => {
    if (!currentScenario) return;
    setEvaluating(true);
    finopsApi.simulateWarRoomAction(currentScenario.id, selectedActionIds)
      .then(res => setSimResult(res))
      .catch(err => console.error('Action simulation error:', err))
      .finally(() => setEvaluating(false));
  };

  const handleScenarioChange = (id: string) => {
    setSelectedScenarioId(id);
    setSelectedActionIds([]);
    setSimResult(null);
  };

  if (loading || !data || !currentScenario) {
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
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-bold text-white tracking-tight">FinOps War Room Simulator</h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
              Interactive Decision Game
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Solve 4 executive and regulatory crisis challenges by evaluating stakeholder trade-offs, financial targets, and compliance guardrails.
          </p>
        </div>
      </div>

      {/* Scenario Selector Tabs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {data.scenarios.map((sc) => {
          const isSelected = sc.id === selectedScenarioId;
          return (
            <button
              key={sc.id}
              onClick={() => handleScenarioChange(sc.id)}
              className={`p-4 rounded-2xl text-left border transition-all ${
                isSelected
                  ? 'bg-slate-900 border-indigo-500 shadow-lg shadow-indigo-950/40'
                  : 'bg-slate-950/60 border-slate-800/80 hover:border-slate-700 opacity-70 hover:opacity-100'
              }`}
            >
              <div className="flex items-center justify-between text-xs mb-1">
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono ${
                  sc.urgency === 'CRITICAL' ? 'bg-rose-500/20 text-rose-400' : 'bg-amber-500/20 text-amber-400'
                }`}>
                  {sc.urgency}
                </span>
                <span className="font-mono text-emerald-400 font-bold">
                  ${(sc.financial_stake_usd / 1000).toFixed(0)}k Stake
                </span>
              </div>
              <h4 className="font-bold text-white text-sm mt-2 line-clamp-1">{sc.title}</h4>
              <p className="text-[11px] text-slate-400 mt-1 line-clamp-2">{sc.description}</p>
            </button>
          );
        })}
      </div>

      {/* Active Scenario Overview */}
      <div className="glass-panel p-6 rounded-2xl space-y-4 border-l-4 border-l-indigo-500">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-2">
          <div>
            <h3 className="text-lg font-bold text-white">{currentScenario.title}</h3>
            <p className="text-xs text-indigo-300 font-mono mt-0.5">Objective: Achieve ${currentScenario.financial_stake_usd.toLocaleString()} Target Safely</p>
          </div>
          <div className="text-xs px-3 py-1 rounded-xl bg-slate-900 border border-slate-800 text-slate-300">
            {selectedActionIds.length} of {currentScenario.available_actions.length} Actions Selected
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs pt-2 border-t border-slate-800/80">
          <div>
            <span className="font-bold text-slate-400 block mb-1">BUSINESS CONTEXT</span>
            <p className="text-slate-300 leading-relaxed">{currentScenario.context}</p>
          </div>

          <div>
            <span className="font-bold text-slate-400 block mb-1">PRIMARY CHALLENGE</span>
            <p className="text-slate-300 leading-relaxed">{currentScenario.primary_challenge}</p>
          </div>

          <div>
            <span className="font-bold text-slate-400 block mb-1">COMPLIANCE GUARDRAIL</span>
            <p className="text-amber-400/90 leading-relaxed font-mono text-[11px]">{currentScenario.compliance_guardrail}</p>
          </div>
        </div>
      </div>

      {/* Available Actions Checklist */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-white text-base">Select Your Tactical Actions</h3>
          <span className="text-xs text-slate-400">Click to arm initiatives for execution</span>
        </div>

        <div className="grid grid-cols-1 gap-3">
          {currentScenario.available_actions.map((act) => {
            const isArmed = selectedActionIds.includes(act.action_id);
            return (
              <div
                key={act.action_id}
                onClick={() => toggleAction(act.action_id)}
                className={`p-4 rounded-xl border cursor-pointer transition-all ${
                  isArmed
                    ? 'bg-slate-900 border-indigo-500 shadow-md shadow-indigo-950/20'
                    : 'bg-slate-950/50 border-slate-800/80 hover:border-slate-700'
                }`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start space-x-3">
                    <div className={`mt-0.5 w-5 h-5 rounded-md flex items-center justify-center border transition-all ${
                      isArmed ? 'bg-indigo-600 border-indigo-500 text-white' : 'border-slate-700 bg-slate-900'
                    }`}>
                      {isArmed && <CheckCircle2 className="w-4 h-4" />}
                    </div>

                    <div>
                      <div className="flex items-center space-x-2 flex-wrap">
                        <h4 className="font-bold text-white text-sm">{act.title}</h4>
                        {!act.compliance_approved && (
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30">
                            COMPLIANCE RISK
                          </span>
                        )}
                        <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-400">
                          Risk: {act.risk_level}
                        </span>
                      </div>
                      <p className="text-xs text-slate-300 mt-1">{act.description}</p>
                      <p className="text-[11px] text-slate-400 mt-1 italic">
                        Stakeholder Impact: {act.stakeholder_impact}
                      </p>
                    </div>
                  </div>

                  <div className="text-right shrink-0">
                    <div className="text-sm font-bold text-emerald-400 font-mono">
                      +${act.immediate_savings_usd.toLocaleString()}/mo
                    </div>
                    <div className="text-[10px] text-slate-500 font-mono">
                      {act.implementation_time_days} days to deploy
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Execute Button */}
        <div className="pt-2 flex justify-end">
          <button
            onClick={runSimulation}
            disabled={selectedActionIds.length === 0 || evaluating}
            className={`flex items-center space-x-2 px-6 py-2.5 rounded-xl font-bold text-sm transition-all shadow-lg ${
              selectedActionIds.length > 0 && !evaluating
                ? 'bg-gradient-to-r from-indigo-600 to-emerald-500 hover:from-indigo-500 hover:to-emerald-400 text-white shadow-indigo-600/30'
                : 'bg-slate-800 text-slate-500 cursor-not-allowed'
            }`}
          >
            <Play className="w-4 h-4 fill-current" />
            <span>{evaluating ? 'Simulating Impact...' : 'Evaluate War Room Plan'}</span>
          </button>
        </div>
      </div>

      {/* Simulation Result Modal / Card */}
      {simResult && (
        <div className={`glass-panel p-6 rounded-2xl border-2 space-y-4 animate-in fade-in slide-in-from-bottom-2 ${
          simResult.compliance_passed && simResult.risk_score.includes('OPTIMAL')
            ? 'border-emerald-500/80 bg-slate-900'
            : simResult.compliance_passed
            ? 'border-amber-500/80 bg-slate-900'
            : 'border-rose-500/80 bg-rose-950/20'
        }`}>
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-slate-800 pb-3">
            <div>
              <span className="text-[10px] uppercase font-bold text-slate-400 font-mono">DECISION OUTCOME EVALUATION</span>
              <h3 className="text-xl font-bold text-white mt-0.5">{simResult.cfo_approval_status}</h3>
            </div>
            <div className="flex items-center space-x-3 text-xs font-mono">
              <div>
                <span className="text-slate-400">Total Savings:</span>{' '}
                <strong className="text-emerald-400">${simResult.total_savings_achieved_usd.toLocaleString()}/mo</strong>
              </div>
              <div>
                <span className="text-slate-400">Impl Time:</span>{' '}
                <strong className="text-white">{simResult.implementation_days_total} days</strong>
              </div>
            </div>
          </div>

          <p className="text-sm text-slate-200 leading-relaxed font-sans">
            {simResult.outcome_summary}
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2 text-xs">
            <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
              <span className="text-slate-400 block mb-0.5">COMPLIANCE VERDICT</span>
              <span className={`font-bold flex items-center space-x-1 ${
                simResult.compliance_passed ? 'text-emerald-400' : 'text-rose-400'
              }`}>
                {simResult.compliance_passed ? (
                  <>
                    <CheckCircle2 className="w-4 h-4" />
                    <span>PASSED — 100% Regulatory Integrity Maintained</span>
                  </>
                ) : (
                  <>
                    <XCircle className="w-4 h-4" />
                    <span>FAILED — Violation of PCI DSS / RBI Mandate</span>
                  </>
                )}
              </span>
            </div>

            <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
              <span className="text-slate-400 block mb-0.5">RISK SCORE</span>
              <span className="font-bold text-white font-mono">{simResult.risk_score}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
