# 前端项目设置指南

## ✅ 已完成的工作

我已经为你创建了完整的前端项目结构，包括：

- ✅ React + Vite 项目框架
- ✅ Ant Design UI组件库
- ✅ 路由配置（React Router）
- ✅ API服务封装（已连接后端）
- ✅ WebSocket工具（实时监控）
- ✅ 基础页面结构
- ✅ 开发环境配置

## 🚀 快速开始

### 步骤1: 安装依赖

```bash
cd frontend
npm install
```

如果还没有安装Node.js，请先安装：
- 访问 https://nodejs.org/
- 下载并安装LTS版本

### 步骤2: 启动开发服务器

```bash
npm run dev
```

前端将在 `http://localhost:3000` 启动

### 步骤3: 确保后端运行

在另一个终端窗口：

```bash
cd backend
python3 run_server.py
```

后端在 `http://localhost:8000` 运行

## 📋 从Figma获取代码的步骤

### 方法A: 使用Figma插件（最简单）

1. **打开Figma设计文件**
   - 在Figma中打开你的设计

2. **安装插件**
   - 点击左侧菜单的"插件"图标
   - 搜索 "Figma to Code" 或 "Anima"
   - 点击"安装"

3. **导出代码**
   - 选择要导出的组件/页面
   - 运行插件
   - 选择"React"格式
   - 复制生成的代码

4. **保存到项目**
   - 将组件代码保存到 `frontend/src/components/`
   - 将样式保存到 `frontend/src/styles/`

### 方法B: 手动提取设计规范

如果无法使用插件，可以：

1. **提取颜色**
   - 在Figma中选择元素
   - 查看右侧面板的颜色值
   - 记录所有颜色

2. **提取字体**
   - 选择文本元素
   - 记录字体、字号、行高等

3. **提取间距**
   - 使用Figma测量工具
   - 记录常用间距值

4. **创建配置文件**
   - 在 `frontend/src/styles/` 创建配置文件
   - 我可以在你提取后帮你创建

### 方法C: 分享Figma链接

如果你希望我帮你提取：

1. **获取分享链接**
   - 在Figma中点击"Share"
   - 选择"Copy link"
   - 确保权限设置为"Anyone can view"

2. **发给我**
   - 将链接发给我
   - 我可以指导你提取或帮你实现

## 📁 项目结构

```
frontend/
├── src/
│   ├── components/      # 组件目录（放Figma导出的组件）
│   │   └── Layout.jsx   # 布局组件（已创建）
│   ├── pages/          # 页面目录
│   │   ├── HomePage.jsx
│   │   ├── TestPlanPage.jsx
│   │   ├── TestTaskPage.jsx
│   │   ├── MonitoringPage.jsx
│   │   └── ReportPage.jsx
│   ├── services/       # API服务（已配置好）
│   │   └── api.js      # 后端API调用
│   ├── utils/          # 工具函数
│   │   └── websocket.js # WebSocket管理
│   ├── styles/         # 样式文件（放Figma样式）
│   │   └── index.css
│   ├── assets/         # 静态资源（图片、图标）
│   ├── App.jsx         # 主应用
│   └── main.jsx        # 入口文件
├── public/             # 公共资源
├── package.json        # 依赖配置
├── vite.config.js      # Vite配置（已配置代理）
└── index.html          # HTML模板
```

## 🔗 后端API集成

前端已配置好API调用，所有 `/api` 请求会自动转发到后端：

```javascript
// 示例：调用后端API
import { testPlanAPI } from './services/api'

// 获取所有测试计划
const plans = await testPlanAPI.getAll()

// 创建测试计划
const newPlan = await testPlanAPI.create({
  name: '测试计划1',
  description: '描述'
})
```

## 📝 下一步操作

### 1. 从Figma获取代码

选择以下方式之一：
- [ ] 使用Figma插件导出代码
- [ ] 手动提取设计规范
- [ ] 分享Figma链接给我

### 2. 整合代码

- [ ] 将组件代码放到 `components/` 目录
- [ ] 将样式放到 `styles/` 目录
- [ ] 调整代码以符合项目结构

### 3. 实现页面功能

- [ ] 实现测试计划页面
- [ ] 实现测试任务页面
- [ ] 实现实时监控页面
- [ ] 实现报告页面

### 4. 测试

- [ ] 测试前后端连接
- [ ] 测试API调用
- [ ] 测试WebSocket实时更新

## 💡 提示

1. **Figma插件推荐**：
   - Figma to Code（免费，支持React）
   - Anima（功能强大，部分付费）

2. **代码调整**：
   - Figma导出的代码可能需要调整
   - 确保导入路径正确
   - 样式可能需要手动调整

3. **使用Ant Design**：
   - 项目已集成Ant Design
   - 可以直接使用组件库加速开发
   - 参考：https://ant.design/

4. **API调用**：
   - 所有API方法已在 `services/api.js` 中定义
   - 直接导入使用即可

## ❓ 需要帮助？

如果你遇到问题：
1. 告诉我具体问题
2. 分享Figma链接（如果需要）
3. 我可以帮你调整代码

## 📚 相关文档

- [Figma代码获取详细指南](./FIGMA_TO_CODE_GUIDE.md)
- [前端README](./frontend/README.md)
- [后端API文档](./backend/API_CONNECTION_TEST.md)

