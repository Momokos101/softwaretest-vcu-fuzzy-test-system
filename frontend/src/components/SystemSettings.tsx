import { useState } from 'react';
import { Save, RefreshCw, Cpu, Sliders, Shield, Database, Users, History, ChevronDown } from 'lucide-react';
import { Toggle } from './Toggle';

export function SystemSettings() {
  const [activeTab, setActiveTab] = useState('engine');
  const [showPermissionMatrix, setShowPermissionMatrix] = useState(false);
  const [showConfigHistory, setShowConfigHistory] = useState(false);
  const [settings, setSettings] = useState({
    // Engine Settings
    traditionalEngineEnabled: true,
    ganEngineEnabled: true,
    maxConcurrentTests: 5,
    defaultTimeout: 60,
    maxRetries: 3,
    
    // GAN Model Settings
    ganModelVersion: 'v2.0',
    ganFidThreshold: 40,
    
    // Constraint Settings
    enableConstraints: true,
    safetyBlacklist: true,
    rangeCheck: true,
  });

  const handleSave = () => {
    alert('系统配置已保存成功！');
  };

  const handleReset = () => {
    if (confirm('确定要重置为默认设置吗？')) {
      alert('已重置为默认设置');
    }
  };

  const tabs = [
    { id: 'engine', label: '引擎配置', icon: Cpu },
    { id: 'gan', label: 'GAN模型', icon: Sliders },
    { id: 'constraints', label: '约束器', icon: Shield },
    { id: 'data', label: '数据资产', icon: Database },
    { id: 'rbac', label: '权限管理', icon: Users },
  ];

  return (
    <div className="p-6 mt-[56px]">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="mb-1">系统配置</h2>
          <p className="text-sm text-gray-500">引擎 · 模型 · 约束 · 数据</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleReset}
            className="flex items-center gap-2 px-5 py-2.5 border-2 border-gray-300 rounded-xl hover:bg-gray-50 transition-all"
          >
            <RefreshCw className="w-5 h-5" />
            重置
          </button>
          <button
            onClick={handleSave}
            className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:shadow-lg hover:shadow-blue-600/30 transition-all"
          >
            <Save className="w-5 h-5" />
            保存
          </button>
        </div>
      </div>

      <div className="grid grid-cols-5 gap-6">
        {/* Tabs Sidebar */}
        <div className="col-span-1">
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-3 sticky top-6">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3.5 rounded-xl transition-all mb-2 ${
                    activeTab === tab.id
                      ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg'
                      : 'text-gray-700 hover:bg-blue-50'
                  }`}
                >
                  <Icon className={`w-5 h-5 ${activeTab === tab.id ? '' : 'text-gray-500'}`} />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Content Area */}
        <div className="col-span-4">
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8 animate-fade-in">
            {activeTab === 'engine' && (
              <div className="space-y-6">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center">
                    <Cpu className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-xl">双模引擎配置</h3>
                    <p className="text-sm text-gray-500">传统变异 + GAN智能生成</p>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="p-5 bg-gradient-to-br from-blue-50 to-blue-100/50 rounded-xl border border-blue-200">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="font-medium text-blue-900 mb-1">传统模糊测试引擎</div>
                        <div className="text-sm text-blue-700">基于规则的变异算法</div>
                      </div>
                      <Toggle
                        checked={settings.traditionalEngineEnabled}
                        onChange={(e) =>
                          setSettings({ ...settings, traditionalEngineEnabled: e.target.checked })
                        }
                      />
                    </div>
                  </div>

                  <div className="p-5 bg-gradient-to-br from-green-50 to-green-100/50 rounded-xl border border-green-200">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="font-medium text-green-900 mb-1 flex items-center gap-2">
                          GAN智能引擎
                          <span className="px-2 py-0.5 bg-gradient-to-r from-blue-500 to-blue-600 text-white text-xs rounded-full">AI</span>
                        </div>
                        <div className="text-sm text-green-700">条件GAN生成 · 智能边界探索</div>
                      </div>
                      <Toggle
                        checked={settings.ganEngineEnabled}
                        onChange={(e) => setSettings({ ...settings, ganEngineEnabled: e.target.checked })}
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 bg-gray-50 rounded-xl border border-gray-200">
                      <label className="block mb-3 text-gray-700 font-medium">最大并发测试数</label>
                      <input
                        type="number"
                        value={settings.maxConcurrentTests}
                        onChange={(e) =>
                          setSettings({ ...settings, maxConcurrentTests: parseInt(e.target.value) })
                        }
                        className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-blue-400 transition-colors"
                      />
                    </div>

                    <div className="p-4 bg-gray-50 rounded-xl border border-gray-200">
                      <label className="block mb-3 text-gray-700 font-medium">默认超时 (分钟)</label>
                      <input
                        type="number"
                        value={settings.defaultTimeout}
                        onChange={(e) => setSettings({ ...settings, defaultTimeout: parseInt(e.target.value) })}
                        className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-blue-400 transition-colors"
                      />
                    </div>

                    <div className="p-4 bg-gray-50 rounded-xl border border-gray-200">
                      <label className="block mb-3 text-gray-700 font-medium">最大重试次数</label>
                      <input
                        type="number"
                        value={settings.maxRetries}
                        onChange={(e) =>
                          setSettings({ ...settings, maxRetries: parseInt(e.target.value) || 0 })
                        }
                        className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-blue-400 transition-colors"
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'gan' && (
              <div className="space-y-6">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl flex items-center justify-center">
                    <Sliders className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-xl">GAN模型配置</h3>
                    <p className="text-sm text-gray-500">条件GAN · 性能指标</p>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="p-4 bg-gradient-to-br from-blue-50 to-blue-100/50 rounded-xl border border-blue-200">
                    <label className="block mb-3 text-blue-900 font-medium">模型版本</label>
                    <select
                      value={settings.ganModelVersion}
                      onChange={(e) => setSettings({ ...settings, ganModelVersion: e.target.value })}
                      className="w-full px-4 py-3 border-2 border-blue-200 rounded-xl focus:outline-none focus:border-blue-400 transition-colors bg-white"
                    >
                      <option value="v1.0">Conditional GAN v1.0</option>
                      <option value="v2.0">Conditional GAN v2.0 (推荐)</option>
                      <option value="v2.1-beta">Conditional GAN v2.1-beta</option>
                    </select>
                  </div>

                  <div className="p-4 bg-gray-50 rounded-xl border border-gray-200">
                    <label className="block mb-3 text-gray-700 font-medium">FID阈值</label>
                    <input
                      type="number"
                      value={settings.ganFidThreshold}
                      onChange={(e) => setSettings({ ...settings, ganFidThreshold: parseInt(e.target.value) })}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-blue-400 transition-colors"
                    />
                    <div className="mt-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
                      <div className="text-sm text-blue-800 mb-2">当前性能指标：</div>
                      <div className="grid grid-cols-3 gap-2 text-xs">
                        <div className="text-blue-700">FID: 35.2</div>
                        <div className="text-blue-700">KL: 0.15</div>
                        <div className="text-blue-700">JS: 0.08</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'constraints' && (
              <div className="space-y-6">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl flex items-center justify-center">
                    <Shield className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-xl">统一约束器</h3>
                    <p className="text-sm text-gray-500">系统安全护栏 · 合规性校验</p>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="p-5 bg-gradient-to-br from-green-50 to-green-100/50 rounded-xl border border-green-200">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex-1">
                        <div className="font-medium text-green-900 mb-1">启用约束器</div>
                        <div className="text-sm text-green-700">对所有生成用例进行安全校验</div>
                      </div>
                      <Toggle
                        checked={settings.enableConstraints}
                        onChange={(e) => setSettings({ ...settings, enableConstraints: e.target.checked })}
                      />
                    </div>
                  </div>

                  <div className="p-4 bg-gray-50 rounded-xl border border-gray-200">
                    <h4 className="font-medium mb-3">约束规则</h4>
                    <div className="space-y-3">
                      <label className="flex items-center gap-3 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={settings.safetyBlacklist}
                          onChange={(e) => setSettings({ ...settings, safetyBlacklist: e.target.checked })}
                          className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                        />
                        <div>
                          <div className="font-medium text-sm">功能安全禁发列表</div>
                          <div className="text-xs text-gray-500">禁止发送刹车、转向等安全信号</div>
                        </div>
                      </label>
                      <label className="flex items-center gap-3 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={settings.rangeCheck}
                          onChange={(e) => setSettings({ ...settings, rangeCheck: e.target.checked })}
                          className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                        />
                        <div>
                          <div className="font-medium text-sm">数值物理范围检查</div>
                          <div className="text-xs text-gray-500">验证信号值在合法范围内</div>
                        </div>
                      </label>
                    </div>
                  </div>

                  <div className="p-4 bg-blue-50 rounded-xl border border-blue-200">
                    <div className="text-sm text-blue-800 mb-2">今日拦截统计：</div>
                    <div className="grid grid-cols-3 gap-4 text-center">
                      <div>
                        <div className="text-2xl font-medium text-blue-700">2,450</div>
                        <div className="text-xs text-blue-600">拦截总数</div>
                      </div>
                      <div>
                        <div className="text-2xl font-medium text-green-700">73.5%</div>
                        <div className="text-xs text-green-600">通过率</div>
                      </div>
                      <div>
                        <div className="text-2xl font-medium text-orange-700">0.8ms</div>
                        <div className="text-xs text-orange-600">平均延</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'data' && (
              <div className="space-y-6">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl flex items-center justify-center">
                    <Database className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-xl">数据资产管理</h3>
                    <p className="text-sm text-gray-500">DBC · 训练数据 · 模型版本</p>
                  </div>
                </div>

                <div className="space-y-4">
                  {/* DBC Files */}
                  <div className="p-5 bg-gradient-to-br from-blue-50 to-blue-100/50 rounded-xl border border-blue-200">
                    <div className="flex items-center gap-3 mb-3">
                      <FileCode className="w-5 h-5 text-blue-700" />
                      <h4 className="font-medium text-blue-900">DBC文件</h4>
                    </div>
                    <div className="space-y-2 text-sm text-blue-800">
                      <div className="flex justify-between">
                        <span>VCU_CAN_v2.3.dbc</span>
                        <span className="px-2 py-0.5 bg-green-100 text-green-700 rounded text-xs">使用中</span>
                      </div>
                      <div className="text-xs text-blue-600">信号: 156 · 报文: 42</div>
                    </div>
                  </div>

                  {/* Training Data */}
                  <div className="p-5 bg-gradient-to-br from-green-50 to-green-100/50 rounded-xl border border-green-200">
                    <div className="flex items-center gap-3 mb-3">
                      <Database className="w-5 h-5 text-green-700" />
                      <h4 className="font-medium text-green-900">训练数据集</h4>
                    </div>
                    <div className="space-y-2 text-sm text-green-800">
                      <div>VCU正常通信日志 (BLF, 2.3GB)</div>
                      <div>VCU异常案例集 (CSV, 156MB)</div>
                      <div className="text-xs text-green-600">总样本: 128,200</div>
                    </div>
                  </div>

                  {/* Model Versions */}
                  <div className="p-5 bg-gradient-to-br from-blue-50 to-blue-100/50 rounded-xl border border-blue-200">
                    <div className="flex items-center gap-3 mb-3">
                      <GitBranch className="w-5 h-5 text-blue-700" />
                      <h4 className="font-medium text-blue-900">GAN模型版本</h4>
                    </div>
                    <div className="space-y-2 text-sm text-blue-800">
                      <div className="flex justify-between">
                        <span>Conditional GAN v2.0</span>
                        <span className="px-2 py-0.5 bg-green-100 text-green-700 rounded text-xs">生产</span>
                      </div>
                      <div className="text-xs text-blue-600">FID: 35.2 · 训练: 2025-11-15</div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'rbac' && (
              <div className="space-y-6">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl flex items-center justify-center">
                    <Users className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-xl">RBAC权限管理</h3>
                    <p className="text-sm text-gray-500">角色定义 · 权限矩阵 · 用户分配</p>
                  </div>
                </div>

                <div className="space-y-4">
                  {/* 角色定义 - 默认展开 */}
                  <div className="p-5 bg-gradient-to-br from-blue-50 to-blue-100/50 rounded-xl border border-blue-200">
                    <div className="font-medium text-blue-900 mb-3">角色定义（7个专业角色）</div>
                    <div className="grid grid-cols-2 gap-3">
                      <div className="flex items-center justify-between p-3 bg-white rounded-lg">
                        <div className="flex items-center gap-3">
                          <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                          <div>
                            <div className="font-medium">系统管理员</div>
                            <div className="text-xs text-gray-500">全局配置 · 用户管理 · 系统维护</div>
                          </div>
                        </div>
                        <span className="px-3 py-1 bg-red-100 text-red-700 rounded-lg text-sm">2人</span>
                      </div>
                      
                      <div className="flex items-center justify-between p-3 bg-white rounded-lg">
                        <div className="flex items-center gap-3">
                          <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                          <div>
                            <div className="font-medium">测试负责人</div>
                            <div className="text-xs text-gray-500">测试计划 · 资源分配 · 进度管控</div>
                          </div>
                        </div>
                        <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-lg text-sm">1人</span>
                      </div>
                      
                      <div className="flex items-center justify-between p-3 bg-white rounded-lg">
                        <div className="flex items-center gap-3">
                          <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                          <div>
                            <div className="font-medium">测试工程师</div>
                            <div className="text-xs text-gray-500">创建测试 · 执行测试 · 查看结果</div>
                          </div>
                        </div>
                        <span className="px-3 py-1 bg-green-100 text-green-700 rounded-lg text-sm">5人</span>
                      </div>
                      
                      <div className="flex items-center justify-between p-3 bg-white rounded-lg">
                        <div className="flex items-center gap-3">
                          <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                          <div>
                            <div className="font-medium">分析工程师</div>
                            <div className="text-xs text-gray-500">结果分析 · 报告生成 · 趋势预测</div>
                          </div>
                        </div>
                        <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-lg text-sm">3人</span>
                      </div>
                      
                      <div className="flex items-center justify-between p-3 bg-white rounded-lg">
                        <div className="flex items-center gap-3">
                          <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                          <div>
                            <div className="font-medium">配置管理员</div>
                            <div className="text-xs text-gray-500">DBC管理 · GAN模型 · 约束配置</div>
                          </div>
                        </div>
                        <span className="px-3 py-1 bg-orange-100 text-orange-700 rounded-lg text-sm">2人</span>
                      </div>
                      
                      <div className="flex items-center justify-between p-3 bg-white rounded-lg">
                        <div className="flex items-center gap-3">
                          <div className="w-2 h-2 bg-cyan-500 rounded-full"></div>
                          <div>
                            <div className="font-medium">开发人员</div>
                            <div className="text-xs text-gray-500">查看缺陷 · 下载日志 · 复现问题</div>
                          </div>
                        </div>
                        <span className="px-3 py-1 bg-cyan-100 text-cyan-700 rounded-lg text-sm">4人</span>
                      </div>
                      
                      <div className="flex items-center justify-between p-3 bg-white rounded-lg col-span-2">
                        <div className="flex items-center gap-3">
                          <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                          <div>
                            <div className="font-medium">审计员/查看者</div>
                            <div className="text-xs text-gray-500">只读权限 · 审计日志 · 合规检查</div>
                          </div>
                        </div>
                        <span className="px-3 py-1 bg-gray-100 text-gray-700 rounded-lg text-sm">3人</span>
                      </div>
                    </div>
                  </div>

                  {/* 权限矩阵 - 可折叠 */}
                  <div className="p-5 bg-gray-50 rounded-xl border border-gray-200">
                    <button
                      onClick={() => setShowPermissionMatrix(!showPermissionMatrix)}
                      className="w-full flex items-center justify-between"
                    >
                      <div className="flex items-center gap-2">
                        <ChevronDown className={`w-5 h-5 text-gray-600 transition-transform ${showPermissionMatrix ? 'rotate-180' : ''}`} />
                        <span className="font-medium text-gray-900">权限矩阵</span>
                        <span className="text-sm text-gray-500">(7个角色 × 10项权限)</span>
                      </div>
                      <span className="text-sm text-blue-600">点击{showPermissionMatrix ? '收起' : '展开'}</span>
                    </button>
                    
                    {showPermissionMatrix && (
                      <div className="mt-4 overflow-x-auto">
                        <table className="w-full text-xs">
                          <thead>
                            <tr className="border-b-2 border-gray-300">
                              <th className="text-left py-2 px-2 font-medium">权限项</th>
                              <th className="text-center py-2 px-2 font-medium">系统<br/>管理员</th>
                              <th className="text-center py-2 px-2 font-medium">测试<br/>负责人</th>
                              <th className="text-center py-2 px-2 font-medium">测试<br/>工程师</th>
                              <th className="text-center py-2 px-2 font-medium">分析<br/>工程师</th>
                              <th className="text-center py-2 px-2 font-medium">配置<br/>管理员</th>
                              <th className="text-center py-2 px-2 font-medium">开发<br/>人员</th>
                              <th className="text-center py-2 px-2 font-medium">审计员</th>
                            </tr>
                          </thead>
                          <tbody>
                            {[
                              { name: '系统配置', roles: [true, false, false, false, false, false, false] },
                              { name: '用户管理', roles: [true, false, false, false, false, false, false] },
                              { name: 'RBAC管理', roles: [true, true, false, false, false, false, false] },
                              { name: '创建测试', roles: [true, true, true, false, false, false, false] },
                              { name: '执行测试', roles: [true, true, true, false, false, false, false] },
                              { name: '暂停/终止', roles: [true, true, true, false, false, false, false] },
                              { name: 'DBC配置', roles: [true, false, false, false, true, false, false] },
                              { name: 'GAN模型', roles: [true, false, false, false, true, false, false] },
                              { name: '结果分析', roles: [true, true, true, true, false, true, true] },
                              { name: '报告导出', roles: [true, true, true, true, false, true, false] },
                              { name: '查看日志', roles: [true, true, true, true, true, true, true] },
                              { name: '审计追溯', roles: [true, true, false, false, false, false, true] },
                            ].map((perm, idx) => (
                              <tr key={idx} className="border-b border-gray-200 hover:bg-blue-50/30">
                                <td className="py-2 px-2 font-medium">{perm.name}</td>
                                {perm.roles.map((hasPermission, roleIdx) => (
                                  <td key={roleIdx} className="py-2 px-2 text-center">
                                    {hasPermission ? (
                                      <span className="text-green-600 font-bold text-base">✓</span>
                                    ) : (
                                      <span className="text-gray-300">–</span>
                                    )}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>

                  {/* 配置变更历史 - 可折叠 */}
                  <div className="p-5 bg-gray-50 rounded-xl border border-gray-200">
                    <button
                      onClick={() => setShowConfigHistory(!showConfigHistory)}
                      className="w-full flex items-center justify-between"
                    >
                      <div className="flex items-center gap-2">
                        <ChevronDown className={`w-5 h-5 text-gray-600 transition-transform ${showConfigHistory ? 'rotate-180' : ''}`} />
                        <span className="font-medium text-gray-900">配置变更历史</span>
                        <span className="text-sm text-gray-500">(基线版本管理)</span>
                      </div>
                      <span className="text-sm text-blue-600">最近5次变更</span>
                    </button>
                    
                    {showConfigHistory && (
                      <div className="mt-4 space-y-2">
                        {[
                          { version: 'v2.0', time: '2025-11-21 09:30', user: '张工(系统管理员)', action: '启用GAN引擎', type: 'update' },
                          { version: 'v1.9', time: '2025-11-20 14:15', user: '李工(配置管理员)', action: '更新DBC文件v2.3', type: 'update' },
                          { version: 'v1.9', time: '2025-11-20 11:20', user: '王工(测试负责人)', action: '新增测试工程师权限', type: 'rbac' },
                          { version: 'v1.8', time: '2025-11-19 16:45', user: '赵工(配置管理员)', action: '调整约束器阈值', type: 'update' },
                          { version: 'v1.8', time: '2025-11-19 10:00', user: '张工(系统管理员)', action: '创建审计员角色', type: 'rbac' },
                        ].map((log, idx) => (
                          <div key={idx} className="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-200">
                            <div className="flex items-center gap-3">
                              <div className="flex flex-col items-center">
                                <History className="w-5 h-5 text-blue-600" />
                                <span className="text-xs text-gray-500 mt-1">{log.version}</span>
                              </div>
                              <div>
                                <div className="font-medium text-sm flex items-center gap-2">
                                  {log.action}
                                  {log.type === 'rbac' && (
                                    <span className="px-2 py-0.5 bg-purple-100 text-purple-700 rounded text-[10px]">RBAC</span>
                                  )}
                                </div>
                                <div className="text-xs text-gray-500">
                                  {log.user} · {log.time}
                                </div>
                              </div>
                            </div>
                            <button className="px-3 py-1 text-xs border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                              回滚
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* 权限拦截统计 */}
                  <div className="p-4 bg-blue-50 rounded-xl border border-blue-200">
                    <div className="text-sm text-blue-800 mb-2">今日权限拦截统计：</div>
                    <div className="grid grid-cols-4 gap-4 text-center">
                      <div>
                        <div className="text-2xl font-medium text-blue-700">2</div>
                        <div className="text-xs text-blue-600">拦截次数</div>
                      </div>
                      <div>
                        <div className="text-2xl font-medium text-green-700">100%</div>
                        <div className="text-xs text-green-600">准确率</div>
                      </div>
                      <div>
                        <div className="text-2xl font-medium text-orange-700">20</div>
                        <div className="text-xs text-orange-600">活跃用户</div>
                      </div>
                      <div>
                        <div className="text-2xl font-medium text-purple-700">7</div>
                        <div className="text-xs text-purple-600">角色类型</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}