import { useState } from "react";
import { AutoTestDesignV2 } from "./components/AutoTestDesignV2";
import { ExportCenter } from "./components/ExportCenter";
import { RequirementInput } from "./components/RequirementInput";
import { RiskAnalysis } from "./components/RiskAnalysis";
import { TestCaseDesign } from "./components/TestCaseDesign";
import { TopNav } from "./components/TopNav";
import { Sidebar } from "./components/Sidebar";

type View = "autotest-v2" | "requirements" | "risk-analysis" | "test-design" | "export";

export default function App() {
  const [currentView, setCurrentView] = useState<View>("autotest-v2");

  const renderView = () => {
    switch (currentView) {
      case "autotest-v2":
        return <AutoTestDesignV2 />;
      case "requirements":
        return <RequirementInput />;
      case "risk-analysis":
        return <RiskAnalysis />;
      case "test-design":
        return <TestCaseDesign />;
      case "export":
        return <ExportCenter />;
      default:
        return <AutoTestDesignV2 />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-slate-50/30">
      <TopNav />
      <div className="flex pt-[56px]">
        <Sidebar currentView={currentView} onNavigate={setCurrentView} />
        <main className="flex-1 ml-[240px]">
          {renderView()}
        </main>
      </div>
    </div>
  );
}
