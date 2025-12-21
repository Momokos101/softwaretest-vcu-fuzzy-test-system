import { LayoutDashboard, FlaskConical, BarChart3, FileText, Settings } from 'lucide-react';

interface SidebarProps {
  currentView: string;
  onNavigate: (view: 'dashboard' | 'tests' | 'analysis' | 'reports' | 'settings') => void;
}

export function Sidebar({ currentView, onNavigate }: SidebarProps) {
  const menuItems = [
    { id: 'dashboard', label: '概览', icon: LayoutDashboard },
    { id: 'tests', label: '测试管理', icon: FlaskConical },
    { id: 'analysis', label: '结果分析', icon: BarChart3 },
    { id: 'reports', label: '报告中心', icon: FileText },
    { id: 'settings', label: '系统配置', icon: Settings },
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
              onClick={() => onNavigate(item.id as any)}
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
      <div className="absolute bottom-8 left-0 right-0 px-6">
        <div className="bg-white rounded-lg p-4 border border-slate-200 shadow-sm">
          <div className="text-sm text-slate-700 mb-1">系统版本</div>
          <div className="text-xs text-slate-500">v2.0 Beta</div>
        </div>
      </div>
    </aside>
  );
}