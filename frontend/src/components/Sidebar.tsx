import React from 'react';
import { FileText, AlertTriangle, Code2, Download, Workflow } from 'lucide-react';

type View = 'autotest-v2' | 'requirements' | 'risk-analysis' | 'test-design' | 'export';

interface SidebarProps {
  currentView: string;
  onNavigate: (view: View) => void;
}

export function Sidebar({ currentView, onNavigate }: SidebarProps) {
  const menuItems: { id: View; label: string; icon: React.ElementType }[] = [
    { id: 'autotest-v2', label: 'V2向导', icon: Workflow },
    { id: 'requirements', label: '需求管理', icon: FileText },
    { id: 'risk-analysis', label: '风险分析', icon: AlertTriangle },
    { id: 'test-design', label: '测试设计', icon: Code2 },
    { id: 'export', label: '导出中心', icon: Download },
  ];

  return (
    <aside className="w-[240px] bg-slate-50 h-screen fixed left-0 top-[56px] pt-6 shadow-sm border-r border-slate-200">
      <nav className="px-3">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`w-full text-left px-4 py-3 mb-1.5 flex items-center gap-3 rounded-lg transition-all duration-200 relative group ${
                isActive
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'text-slate-700 hover:bg-slate-100 hover:text-slate-900'
              }`}
            >
              <Icon className={`w-5 h-5 transition-transform duration-200 ${isActive ? '' : 'group-hover:scale-110'}`} />
              <span className="relative z-10 font-medium">{item.label}</span>
              {isActive && (
                <div className="absolute right-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-blue-800 rounded-l-full" />
              )}
            </button>
          );
        })}
      </nav>
      
      {/* Version Info */}
      <div className="absolute bottom-16 left-0 right-0 px-6">
        <div className="bg-white rounded-lg p-4 border border-slate-200 shadow-sm">
          <div className="text-sm text-slate-700 mb-1">AutoTestDesign</div>
          <div className="text-xs text-slate-500">v2.0</div>
        </div>
      </div>
    </aside>
  );
}
