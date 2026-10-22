import React from 'react';
import { AudienceView } from '../types/finops';
import { Shield, Sparkles, UserCheck, Briefcase, Users, Cloud } from 'lucide-react';

interface NavbarProps {
  audience: AudienceView;
  onAudienceChange: (audience: AudienceView) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ audience, onAudienceChange }) => {
  return (
    <header className="h-16 border-b border-slate-800 bg-slate-900/90 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-40">
      {/* Brand & Platform */}
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-emerald-400 flex items-center justify-center shadow-lg shadow-indigo-500/20">
          <Cloud className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <span className="font-bold text-lg tracking-tight text-white">LendFlow</span>
            <span className="px-2 py-0.5 text-xs font-semibold rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              FinOps
            </span>
          </div>
          <p className="text-xs text-slate-400">Enterprise Cloud Cost Optimisation & Governance</p>
        </div>
      </div>

      {/* Compliance & Region Status */}
      <div className="hidden lg:flex items-center space-x-3 text-xs">
        <div className="flex items-center space-x-1.5 px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700/60 text-slate-300">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>ap-south-1 (Mumbai)</span>
        </div>
        <div className="flex items-center space-x-1 px-3 py-1 rounded-full bg-indigo-950/40 border border-indigo-800/40 text-indigo-300 font-medium">
          <Shield className="w-3.5 h-3.5 text-indigo-400" />
          <span>PCI DSS & RBI Ring-Fenced</span>
        </div>
      </div>

      {/* Audience View Switcher */}
      <div className="flex items-center space-x-1 bg-slate-950 p-1 rounded-xl border border-slate-800">
        <button
          onClick={() => onAudienceChange('executive')}
          className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
            audience === 'executive'
              ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
          }`}
          title="Executive & CFO View: High-level financial KPIs, margin expansion, 90-day targets"
        >
          <Briefcase className="w-3.5 h-3.5" />
          <span>Executive / CFO</span>
        </button>

        <button
          onClick={() => onAudienceChange('engineering-manager')}
          className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
            audience === 'engineering-manager'
              ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
          }`}
          title="Engineering Manager View: Rightsizing, Kubernetes, architectural trade-offs"
        >
          <UserCheck className="w-3.5 h-3.5" />
          <span>Eng Manager</span>
        </button>

        <button
          onClick={() => onAudienceChange('team')}
          className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
            audience === 'team'
              ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
          }`}
          title="Team View: Microservice showback, tag hygiene, team showback leaderboard"
        >
          <Users className="w-3.5 h-3.5" />
          <span>Team Showback</span>
        </button>
      </div>
    </header>
  );
};
