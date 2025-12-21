# VCU智能模糊测试系统

基于GAN的唤醒-休眠场景智能模糊测试系统

## 📋 项目简介

本系统为汽车电子硬件在HIL（Hardware-in-the-Loop）或仿真测试环境中的VCU/域控制器，构建一套专注于"唤醒—握手—Ready—休眠"关键流程的双模式智能模糊测试系统。

系统支持传统模糊测试方式与基于GAN的智能模糊测试方式两种模式，可在统一的测试框架下独立运行或进行结果对比。

## 🏗️ 系统架构

- **后端**: Python + FastAPI
- **前端**: React + Vite + TypeScript
- **GAN模型**: TensorFlow/Keras
- **数据库**: SQLite

## 🚀 快速开始

### 后端启动

```bash
cd backend
pip3 install -r requirements.txt
python3 run_server.py
```

后端服务运行在: http://localhost:8000
API文档: http://localhost:8000/docs

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

前端服务运行在: http://localhost:3000

## 📦 当前版本

**版本**: v1.0 - 稳定版本（角色分离重构前）

**包含功能**:
- ✅ 完整的后端API服务（22个接口）
- ✅ 完整的前端界面（所有功能模块）
- ✅ 前后端已连接
- ✅ 所有接口支持模拟数据
- ✅ 测试计划管理
- ✅ 测试任务管理
- ✅ 实时监控
- ✅ 结果分析
- ✅ 报告生成
- ✅ 约束管理

## 🔄 版本控制

- **main分支**: 当前稳定版本
- **feature/role-based-redesign**: 角色分离重构分支（开发中）

## 📚 文档

- [API测试清单](./API_TEST_CHECKLIST.md)
- [后端API完成报告](./BACKEND_API_COMPLETE.md)
- [前端重组建议](./FRONTEND_ROLE_BASED_REDESIGN.md)
- [Git设置指南](./GIT_SETUP.md)

## 👥 角色说明

系统设计支持三种角色：

1. **测试工程师**: 测试执行与分析
2. **工艺工程师**: 安全与规则管理
3. **台架维护工程师**: 系统部署与联调

当前版本所有功能都在测试工程师界面，角色分离功能正在开发中。

## 📝 许可证

本项目为课程项目，仅供学习和研究使用。

## 📞 联系方式

如有问题，请查看项目文档或提交Issue。

