# 快速启动指南

## 🚀 启动前后端项目

### 步骤1: 安装前端依赖

```bash
cd frontend
npm install
```

如果遇到问题，可以尝试：
```bash
npm install --legacy-peer-deps
```

### 步骤2: 启动后端服务器

打开第一个终端窗口：

```bash
cd backend
python3 run_server.py
```

后端将在 `http://localhost:8000` 运行

### 步骤3: 启动前端开发服务器

打开第二个终端窗口：

```bash
cd frontend
npm run dev
```

前端将在 `http://localhost:3000` 运行

### 步骤4: 访问应用

打开浏览器访问: `http://localhost:3000`

## ✅ 验证连接

### 检查后端

访问 `http://localhost:8000/docs` 查看API文档

### 检查前端

访问 `http://localhost:3000` 查看前端界面

### 测试API连接

打开浏览器开发者工具（F12），查看Network标签，应该能看到API请求。

## 🔧 常见问题

### 1. 端口被占用

如果3000端口被占用，Vite会自动使用下一个可用端口（如3001）。

### 2. 后端连接失败

确保：
- 后端服务器正在运行
- 后端在 `http://localhost:8000`
- 检查后端日志是否有错误

### 3. 依赖安装失败

尝试：
```bash
rm -rf node_modules package-lock.json
npm install
```

### 4. TypeScript错误

如果遇到TypeScript错误，可以：
- 检查 `tsconfig.json` 配置
- 确保所有类型定义正确

## 📝 下一步

1. 在组件中连接API（参考 `INTEGRATION_COMPLETE.md`）
2. 实现实时监控功能
3. 测试所有功能

## 🎉 完成！

前后端已成功整合，可以开始开发了！

