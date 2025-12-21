# VCU智能模糊测试系统 - 前端

## 📋 项目说明

这是基于GAN的唤醒-休眠场景智能模糊测试系统的前端部分。

## 🚀 快速开始

### 1. 安装依赖

```bash
cd frontend
npm install
# 或
yarn install
# 或
pnpm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

前端将在 `http://localhost:3000` 启动

### 3. 构建生产版本

```bash
npm run build
```

## 📁 项目结构

```
frontend/
├── src/
│   ├── components/      # 可复用组件
│   │   └── Layout.jsx    # 布局组件
│   ├── pages/           # 页面组件
│   │   ├── HomePage.jsx
│   │   ├── TestPlanPage.jsx
│   │   ├── TestTaskPage.jsx
│   │   ├── MonitoringPage.jsx
│   │   └── ReportPage.jsx
│   ├── services/        # API服务
│   │   └── api.js       # API调用封装
│   ├── utils/           # 工具函数
│   │   └── websocket.js # WebSocket管理
│   ├── styles/          # 样式文件
│   │   └── index.css
│   ├── assets/          # 静态资源
│   ├── App.jsx          # 主应用组件
│   └── main.jsx         # 入口文件
├── public/              # 公共资源
├── package.json
├── vite.config.js
└── index.html
```

## 🔗 后端API集成

前端已配置代理，所有 `/api` 请求会自动转发到后端服务器 (`http://localhost:8000`)

## 📝 从Figma获取代码

请参考项目根目录的 `FIGMA_TO_CODE_GUIDE.md` 文件，了解如何从Figma获取设计代码。

## 🎨 技术栈

- **React 18** - UI框架
- **Vite** - 构建工具
- **Ant Design 5** - UI组件库
- **React Router** - 路由管理
- **Axios** - HTTP客户端
- **ECharts** - 数据可视化

## 📚 下一步

1. 从Figma导出设计代码
2. 根据设计稿实现页面组件
3. 连接后端API
4. 实现实时监控功能

