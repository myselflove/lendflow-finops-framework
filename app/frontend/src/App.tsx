import React, { useState } from 'react';
import { AudienceView } from './types/finops';
import { Navbar } from './components/Navbar';
import { Sidebar, ViewId } from './components/Sidebar';
import { ExecutiveView } from './views/ExecutiveView';
import { ExplorerView } from './views/ExplorerView';
import { ComputeDbView } from './views/ComputeDbView';
import { StorageView } from './views/StorageView';
import { TransferView } from './views/TransferView';
import { TaggingView } from './views/TaggingView';
import { AnomaliesView } from './views/AnomaliesView';
import { SimulatorView } from './views/SimulatorView';
import { GovernanceView } from './views/GovernanceView';
import { WarRoomView } from './views/WarRoomView';

export const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<ViewId>('executive');
  const [audience, setAudience] = useState<AudienceView>('executive');

  const renderActiveView = () => {
    switch (currentView) {
      case 'executive':
        return <ExecutiveView audience={audience} />;
      case 'explorer':
        return <ExplorerView audience={audience} />;
      case 'compute-db':
        return <ComputeDbView audience={audience} />;
      case 'storage':
        return <StorageView audience={audience} />;
      case 'transfer':
        return <TransferView audience={audience} />;
      case 'tags':
        return <TaggingView audience={audience} />;
      case 'anomalies':
        return <AnomaliesView audience={audience} />;
      case 'simulator':
        return <SimulatorView audience={audience} />;
      case 'governance':
        return <GovernanceView audience={audience} />;
      case 'war-room':
        return <WarRoomView audience={audience} />;
      default:
        return <ExecutiveView audience={audience} />;
    }
  };

  return (
    <div className="min-h-screen bg-[#0B0F17] flex flex-col font-sans selection:bg-indigo-600 selection:text-white">
      {/* Top Navbar */}
      <Navbar audience={audience} onAudienceChange={setAudience} />

      {/* Main Content Area with Sidebar */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar Navigation */}
        <Sidebar currentView={currentView} onSelectView={setCurrentView} />

        {/* Dynamic View Body */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8 bg-[#0B0F17]">
          <div className="max-w-7xl mx-auto">
            {renderActiveView()}
          </div>
        </main>
      </div>
    </div>
  );
};

export default App;
