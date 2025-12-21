import { useState } from 'react';
import { FileCode, Upload, Download, Eye, Tag, Calendar, Folder, GitBranch } from 'lucide-react';

export function DataAssetManagement() {
  const [activeTab, setActiveTab] = useState('dbc');

  // DBC文件管理
  const dbcFiles = [
    {
      id: 'DBC-001',
      name: 'VCU_CAN_v2.3.dbc',
      version: 'v2.3',
      uploadDate: '2025-11-15',
      signals: 156,
      messages: 42,
      usedBy: 12,
      status: 'active',
    },
    {
      id: 'DBC-002',
      name: 'VCU_CAN_v2.2.dbc',
      version: 'v2.2',
      uploadDate: '2025-10-20',
      signals: 142,
      messages: 38,
      usedBy: 8,
      status: 'archived',
    },
  ];

  // 训练数据集
  const trainingDatasets = [
    {
      id: 'DS-001',
      name: 'VCU正常通信日志_20251115',
      type: 'BLF',
      size: '2.3 GB',
      samples: 125000,
      uploadDate: '2025-11-15',
      usedByModel: 'GAN v2.0',
      tags: ['正常样本', '休眠唤醒'],
    },
    {
      id: 'DS-002',
      name: 'VCU异常案例集_20251110',
      type: 'CSV',
      size: '156 MB',
      samples: 3200,
      uploadDate: '2025-11-10',
      usedByModel: 'GAN v2.0',
      tags: ['异常样本', '历史Bug'],
    },
    {
      id: 'DS-003',
      name: 'VCU多域并发场景_20251105',
      type: 'ASC',
      size: '1.8 GB',
      samples: 98000,
      uploadDate: '2025-11-05',
      usedByModel: 'GAN v1.0',
      tags: ['并发场景', '高负载'],
    },
  ];

  // GAN模型版本
  const modelVersions = [
    {
      id: 'MODEL-001',
      name: 'Conditional GAN v2.0',
      trainDate: '2025-11-15',
      trainingData: 'DS-001 + DS-002',
      fid: 35.2,
      kl: 0.15,
      js: 0.08,
      status: 'production',
      usageCount: 45,
    },
    {
      id: 'MODEL-002',
      name: 'Conditional GAN v1.0',
      trainDate: '2025-10-20',
      trainingData: 'DS-003',
      fid: 42.8,
      kl: 0.22,
      js: 0.12,
      status: 'archived',
      usageCount: 128,
    },
  ];

  return (
    <div className="p-6 mt-[56px]">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="mb-1">数据资产管理</h2>
          <p className="text-sm text-gray-500">版本控制 · 数据溯源 · 资产复用</p>
        </div>
        <button className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:shadow-lg transition-all">
          <Upload className="w-5 h-5" />
          上传数据资产
        </button>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 mb-6">
        <div className="flex border-b border-gray-200">
          <button
            onClick={() => setActiveTab('dbc')}
            className={`pb-3 px-2 transition-colors ${
              activeTab === 'dbc'
                ? 'border-b-2 border-blue-600 text-blue-600 font-medium'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <FileCode className="w-5 h-5" />
            DBC文件管理
          </button>
          <button
            onClick={() => setActiveTab('training')}
            className={`pb-3 px-2 transition-colors ${
              activeTab === 'training'
                ? 'border-b-2 border-blue-600 text-blue-600 font-medium'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Folder className="w-5 h-5" />
            训练数据集
          </button>
          <button
            onClick={() => setActiveTab('models')}
            className={`pb-3 px-2 transition-colors ${
              activeTab === 'models'
                ? 'border-b-2 border-blue-600 text-blue-600 font-medium'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <GitBranch className="w-5 h-5" />
            模型版本管理
          </button>
        </div>

        <div className="p-6">
          {activeTab === 'dbc' && (
            <div className="space-y-4 animate-fade-in">
              <div className="mb-4">
                <h3 className="text-lg mb-2">DBC文件列表</h3>
                <p className="text-sm text-gray-500">CAN信号定义 · 版本追踪 · 使用情况</p>
              </div>

              {dbcFiles.map((file) => (
                <div
                  key={file.id}
                  className="p-6 bg-gradient-to-br from-blue-50 to-blue-100/50 rounded-xl border border-blue-200 hover:border-blue-300 transition-all"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4 flex-1">
                      <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center">
                        <FileCode className="w-6 h-6 text-white" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="font-medium">{file.name}</h3>
                          <span className="px-2 py-1 bg-blue-200 text-blue-800 rounded text-sm">{file.version}</span>
                          <span className={`px-2 py-1 rounded text-sm ${
                            file.status === 'active' 
                              ? 'bg-green-100 text-green-700' 
                              : 'bg-gray-100 text-gray-700'
                          }`}>
                            {file.status === 'active' ? '使用中' : '已归档'}
                          </span>
                        </div>
                        <div className="grid grid-cols-4 gap-4 text-sm text-blue-800">
                          <div>
                            <span className="text-blue-600">信号数: </span>
                            <span className="font-medium">{file.signals}</span>
                          </div>
                          <div>
                            <span className="text-blue-600">报文数: </span>
                            <span className="font-medium">{file.messages}</span>
                          </div>
                          <div>
                            <span className="text-blue-600">使用次数: </span>
                            <span className="font-medium">{file.usedBy}</span>
                          </div>
                          <div>
                            <span className="text-blue-600">上传日期: </span>
                            <span className="font-medium">{file.uploadDate}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button className="p-2 hover:bg-blue-200 rounded-lg transition-colors">
                        <Eye className="w-5 h-5 text-blue-700" />
                      </button>
                      <button className="p-2 hover:bg-blue-200 rounded-lg transition-colors">
                        <Download className="w-5 h-5 text-blue-700" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'training' && (
            <div className="space-y-4 animate-fade-in">
              <div className="mb-4">
                <h3 className="text-lg mb-2">训练数据集管理</h3>
                <p className="text-sm text-gray-500">正常样本 · 异常样本 · 数据溯源</p>
              </div>

              {trainingDatasets.map((dataset) => (
                <div
                  key={dataset.id}
                  className="p-6 bg-gradient-to-br from-green-50 to-green-100/50 rounded-xl border border-green-200 hover:border-green-300 transition-all"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4 flex-1">
                      <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-green-600 rounded-xl flex items-center justify-center">
                        <Folder className="w-6 h-6 text-white" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="font-medium">{dataset.name}</h3>
                          <span className="px-2 py-1 bg-green-200 text-green-800 rounded text-sm">{dataset.type}</span>
                        </div>
                        <div className="grid grid-cols-5 gap-4 text-sm text-green-800 mb-3">
                          <div>
                            <span className="text-green-600">大小: </span>
                            <span className="font-medium">{dataset.size}</span>
                          </div>
                          <div>
                            <span className="text-green-600">样本数: </span>
                            <span className="font-medium">{dataset.samples.toLocaleString()}</span>
                          </div>
                          <div>
                            <span className="text-green-600">上传日期: </span>
                            <span className="font-medium">{dataset.uploadDate}</span>
                          </div>
                          <div className="col-span-2">
                            <span className="text-green-600">用于模型: </span>
                            <span className="font-medium">{dataset.usedByModel}</span>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {dataset.tags.map((tag, index) => (
                            <span key={index} className="px-2 py-1 bg-green-200 text-green-800 rounded text-sm flex items-center gap-1">
                              <Tag className="w-3 h-3" />
                              {tag}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button className="p-2 hover:bg-green-200 rounded-lg transition-colors">
                        <Eye className="w-5 h-5 text-green-700" />
                      </button>
                      <button className="p-2 hover:bg-green-200 rounded-lg transition-colors">
                        <Download className="w-5 h-5 text-green-700" />
                      </button>
                    </div>
                  </div>

                  {/* Data Card Info */}
                  <div className="mt-4 pt-4 border-t border-green-300">
                    <div className="text-sm text-green-700">
                      <span className="font-medium">数据卡: </span>
                      记录数据来源、处理版本、特征提取方法和质量指标
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'models' && (
            <div className="space-y-4 animate-fade-in">
              <div className="mb-4">
                <h3 className="text-lg mb-2">GAN模型版本管理</h3>
                <p className="text-sm text-gray-500">版本追踪 · 性能指标 · 只读管理</p>
              </div>

              {modelVersions.map((model) => (
                <div
                  key={model.id}
                  className="p-6 bg-gradient-to-br from-blue-50 to-blue-100/50 rounded-xl border border-blue-200 hover:border-blue-300 transition-all"
                >
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-4 flex-1">
                      <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl flex items-center justify-center">
                        <GitBranch className="w-6 h-6 text-white" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="font-medium">{model.name}</h3>
                          <span className={`px-2 py-1 rounded text-sm ${
                            model.status === 'production' 
                              ? 'bg-green-100 text-green-700' 
                              : 'bg-gray-100 text-gray-700'
                          }`}>
                            {model.status === 'production' ? '生产环境' : '已归档'}
                          </span>
                        </div>
                        <div className="grid grid-cols-3 gap-4 text-sm text-blue-800">
                          <div>
                            <span className="text-blue-600">训练日期: </span>
                            <span className="font-medium">{model.trainDate}</span>
                          </div>
                          <div>
                            <span className="text-blue-600">训练数据: </span>
                            <span className="font-medium">{model.trainingData}</span>
                          </div>
                          <div>
                            <span className="text-blue-600">使用次数: </span>
                            <span className="font-medium">{model.usageCount}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button className="px-4 py-2 bg-blue-200 text-blue-800 rounded-lg hover:bg-blue-300 transition-colors">
                        查看详情
                      </button>
                    </div>
                  </div>

                  {/* Performance Metrics */}
                  <div className="grid grid-cols-3 gap-4 p-4 bg-white rounded-lg border border-blue-200">
                    <div className="text-center">
                      <div className="text-xs text-gray-600 mb-1">FID Score</div>
                      <div className="text-2xl font-medium text-blue-700">{model.fid}</div>
                      <div className="text-xs text-gray-500">越低越好</div>
                    </div>
                    <div className="text-center border-l border-r border-blue-200">
                      <div className="text-xs text-gray-600 mb-1">KL Divergence</div>
                      <div className="text-2xl font-medium text-blue-700">{model.kl}</div>
                      <div className="text-xs text-gray-500">分布相似度</div>
                    </div>
                    <div className="text-center">
                      <div className="text-xs text-gray-600 mb-1">JS Distance</div>
                      <div className="text-2xl font-medium text-blue-700">{model.js}</div>
                      <div className="text-xs text-gray-500">对称度量</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}