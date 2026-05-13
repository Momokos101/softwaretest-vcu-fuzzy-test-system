import { Zap } from 'lucide-react';

export function TopNav() {
  return (
    <nav className="bg-white text-slate-900 px-6 py-3 flex items-center justify-between fixed top-0 left-0 right-0 z-50 shadow-sm border-b border-slate-200">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg flex items-center justify-center shadow-sm">
          <Zap className="w-5 h-5 text-white" />
        </div>
        <h1 className="text-xl tracking-wide">AutoTestDesign</h1>
        <span className="px-3 py-1 bg-blue-50 rounded-full text-xs border border-blue-200 text-blue-700">VCU Wake-Sleep</span>
      </div>
      <div className="flex items-center gap-2 text-sm text-slate-500">
        <span>AI-Driven Test Design Tool</span>
      </div>
    </nav>
  );
}
