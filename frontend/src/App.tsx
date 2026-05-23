import { useState } from "react";
import { Dashboard } from "./components/Dashboard";
import { TestMonitoring } from "./components/TestMonitoring";
import { TestManagement } from "./components/TestManagement";
import { ResultAnalysis } from "./components/ResultAnalysis";
import { ReportCenter } from "./components/ReportCenter";
import { SystemSettings } from "./components/SystemSettings";
import { TopNav } from "./components/TopNav";
import { Sidebar } from "./components/Sidebar";
import { RequirementInput } from "./components/RequirementInput";
import { RiskAnalysis } from "./components/RiskAnalysis";
import { TestCaseDesign } from "./components/TestCaseDesign";
import { ExportCenter } from "./components/ExportCenter";
import { AutoTestDesignV2 } from "./components/AutoTestDesignV2";

export default function App() {
  const [currentView, setCurrentView] = useState<
    | "dashboard"
    | "tests"
    | "analysis"
    | "reports"
    | "settings"
    | "monitoring"
    | "requirements"
    | "autotest-v2"
    | "risk-analysis"
    | "test-design"
    | "export"
  >("dashboard");
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null);

  const renderView = () => {
    switch (currentView) {
      case "dashboard":
        return (
          <Dashboard
            onCreateTest={() => setCurrentView("tests")}
            onViewMonitoring={(taskId: string) => {
              setCurrentTaskId(taskId);
              setCurrentView("monitoring");
            }}
          />
        );
      case "tests":
        return (
          <TestManagement
            onCreateTest={() => setCurrentView("tests")}
            onViewMonitoring={(taskId: string) => {
              setCurrentTaskId(taskId);
              setCurrentView("monitoring");
            }}
          />
        );
      case "analysis":
        return <ResultAnalysis taskId={currentTaskId || undefined} />;
      case "reports":
        return <ReportCenter />;
      case "settings":
        return <SystemSettings />;
      case "monitoring":
        return (
          <TestMonitoring
            taskId={currentTaskId || ""}
            onBack={() => setCurrentView("dashboard")}
          />
        );
      case "requirements":
        return <RequirementInput />;
      case "autotest-v2":
        return <AutoTestDesignV2 />;
      case "risk-analysis":
        return <RiskAnalysis />;
      case "test-design":
        return <TestCaseDesign />;
      case "export":
        return <ExportCenter />;
      default:
        return (
          <Dashboard
            onCreateTest={() => setCurrentView("tests")}
            onViewMonitoring={(taskId: string) => {
              setCurrentTaskId(taskId);
              setCurrentView("monitoring");
            }}
          />
        );
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-slate-50/30">
      <TopNav />
      <div className="flex">
        <Sidebar
          currentView={currentView}
          onNavigate={setCurrentView}
        />
        <main className="flex-1 ml-[240px]">
          {renderView()}
        </main>
      </div>
    </div>
  );
}
