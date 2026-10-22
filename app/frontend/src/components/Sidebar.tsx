import React from 'react';
import {
  LayoutDashboard, Search, Cpu, HardDrive, ArrowLeftRight,
  Tags, AlertTriangle, Calculator, FileCheck, Swords
} from 'lucide-react';

export type ViewId =
  | 'executive'
  | 'explorer'
  | 'compute-db'
  | 'storage'
  | 'transfer'
  | 'tags'
  | 'anomalies'
  | 'simulator'
  | 'governance'
  | 'war-room';

interface SidebarProps {
  currentView: ViewId;
  onSelectView: (view: ViewId) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentView, onSelectView }) => {
  const navItems = [
    {
      id: 'executive' as ViewId,
      label: 'Executive / CFO',
      desc: 'KPIs, $60k target, unit economics',
      icon: LayoutDashboard,
      badge: 'Core'
    },
    {
      id: 'explorer' as ViewId,
      label: 'Cost Explorer',
      desc: 'Multidimensional cost drilldowns',
      icon: Search,
    },
    {
      id: 'compute-db' as ViewId,
      label: 'Compute & DB',
      desc: 'Graviton, RDS & PCI/RBI locks',
      icon: Cpu,
      badge: 'Ring-fenced'
    },
    {
      id: 'storage' as ViewId,
      label: 'Storage & EBS',
      desc: 'Lifecycle & SOC 2 audit WORM',
      icon: HardDrive,
    },
    {
      id: 'transfer' as ViewId,
      label: 'Data Transfer',
      desc: 'Top 10 paths & AZ-aware routing',
      icon: ArrowLeftRight,
    },
    {
      id: 'tags' as ViewId,
      label: 'Tag Governance',
      desc: '10 mandatory tags & dark spend',
      icon: Tags,
    },
    {
      id: 'anomalies' as ViewId,
      label: 'Anomaly Centre',
      desc: 'P1-P4 SLAs & Z-score alerts',
      icon: AlertTriangle,
      badge: 'P1-P4'
    },
    {
      id: 'simulator' as ViewId,
      label: 'Savings Simulator',
      desc: 'Interactive zero-double-counting waterfall',
      icon: Calculator,
      highlight: true
    },
    {
      id: 'governance' as ViewId,
      label: 'Governance & RACI',
      desc: 'RACI matrix & review cadences',
      icon: FileCheck,
    },
    {
      id: 'war-room' as ViewId,
      label: 'FinOps War Room',
      desc: '4 interactive crisis scenarios',
      icon: Swords,
      badge: 'Game'
    },
  ];

  return (
    <aside className="w-64 border-r border-slate-800 bg-slate-900/60 backdrop-blur-md flex flex-col justify-between py-4 shrink-0">
      <div className="space-y-1 px-3">
        <div className="px-3 pb-2 text-[10px] font-bold uppercase tracking-wider text-slate-500">
          Navigation Modules
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectView(item.id)}
              className={`w-full text-left px-3 py-2.5 rounded-xl transition-all flex items-center justify-between group ${
                isActive
                  ? 'bg-gradient-to-r from-indigo-600 to-indigo-700 text-white shadow-lg shadow-indigo-600/20 font-medium'
                  : 'text-slate-300 hover:bg-slate-800/70 hover:text-white'
              }`}
            >
              <div className="flex items-center space-x-3 min-w-0">
                <Icon
                  className={`w-4 h-4 shrink-0 transition-colors ${
                    isActive ? 'text-white' : 'text-slate-400 group-hover:text-indigo-400'
                  }`}
                />
                <div className="truncate">
                  <div className="text-sm truncate">{item.label}</div>
                  <div className={`text-[10px] truncate ${isActive ? 'text-indigo-100/80' : 'text-slate-500'}`}>
                    {item.desc}
                  </div>
                </div>
              </div>

              {item.badge && (
                <span
                  className={`ml-1 text-[10px] font-semibold px-1.5 py-0.5 rounded ${
                    isActive
                      ? 'bg-white/20 text-white'
                      : 'bg-slate-800 text-slate-400 border border-slate-700'
                  }`}
                >
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Footer Info */}
      <div className="px-4 py-3 mx-3 rounded-xl bg-slate-950/60 border border-slate-800/80 text-[11px] text-slate-400 space-y-1">
        <div className="flex justify-between items-center text-slate-300 font-medium">
          <span>Target Savings</span>
          <span className="text-emerald-400 font-bold">$60,000/mo</span>
        </div>
        <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
          <div className="bg-gradient-to-r from-indigo-500 to-emerald-400 h-full w-[100%]"></div>
        </div>
        <div className="text-[10px] text-slate-500 flex justify-between">
          <span>Current: $180k</span>
          <span>Goal: &le; $120k</span>
        </div>
      </div>
    </aside>
  );
};
