# 从Figma获取前端代码完整指南

## 📋 目录
1. [方法概览](#方法概览)
2. [方法1: 使用Figma插件（推荐）](#方法1-使用figma插件推荐)
3. [方法2: 使用Figma Dev Mode](#方法2-使用figma-dev-mode)
4. [方法3: 手动提取设计规范](#方法3-手动提取设计规范)
5. [方法4: 分享Figma链接](#方法4-分享figma链接)
6. [整合代码到项目](#整合代码到项目)

---

## 方法概览

Figma本身不直接导出完整代码，但有几种方法可以获取前端代码：

| 方法 | 适用场景 | 难度 | 推荐度 |
|------|---------|------|--------|
| Figma插件 | 有插件访问权限 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Figma Dev Mode | 有专业版账号 | ⭐ | ⭐⭐⭐⭐ |
| 手动提取 | 任何情况 | ⭐⭐⭐ | ⭐⭐⭐ |
| 分享链接 | 需要协助 | ⭐ | ⭐⭐⭐⭐ |

---

## 方法1: 使用Figma插件（推荐）

### 步骤1: 安装插件

1. 在Figma中打开你的设计文件
2. 点击左侧菜单的 **"插件"** 图标（或按快捷键 `Cmd/Ctrl + /`）
3. 搜索并安装以下插件之一：

#### 推荐插件：

**A. Figma to Code** (最常用)
- 支持导出 React、Vue、HTML
- 可以导出CSS样式
- 免费使用

**B. Anima**
- 功能强大，支持React、Vue、Angular
- 可以导出完整组件
- 部分功能需要付费

**C. Figma to React**
- 专门针对React
- 导出代码质量较高

### 步骤2: 使用插件导出

1. **选择要导出的组件/页面**
   - 在Figma中选择要导出的Frame或组件
   - 可以多选多个组件

2. **运行插件**
   - 点击插件图标启动
   - 选择导出格式（React/Vue/HTML）
   - 选择代码风格（函数式组件/类组件）

3. **复制代码**
   - 插件会生成代码
   - 复制生成的代码
   - 保存到项目对应位置

### 步骤3: 提取设计规范

从Figma中提取以下信息：

#### 颜色
1. 在Figma中选择任意元素
2. 查看右侧面板的"Fill"部分
3. 记录所有使用的颜色值（HEX或RGB）

#### 字体
1. 选择文本元素
2. 查看右侧面板的"Text"部分
3. 记录：
   - 字体族（Font Family）
   - 字号（Font Size）
   - 行高（Line Height）
   - 字重（Font Weight）

#### 间距
1. 使用Figma的测量工具
2. 记录常用间距：4px, 8px, 16px, 24px, 32px等

#### 圆角
1. 选择有圆角的元素
2. 查看右侧面板的"Corner Radius"
3. 记录圆角值

---

## 方法2: 使用Figma Dev Mode

如果你有Figma专业版，可以使用Dev Mode：

1. **切换到Dev Mode**
   - 点击右上角的"Dev Mode"按钮
   - 或使用快捷键

2. **查看CSS属性**
   - 选择元素
   - 右侧面板会显示CSS属性
   - 可以直接复制CSS代码

3. **导出设计规范**
   - 在Dev Mode中可以导出设计规范
   - 包括颜色、字体、间距等

---

## 方法3: 手动提取设计规范

如果无法使用插件，可以手动提取：

### 提取颜色
```javascript
// 在Figma中记录颜色，然后创建颜色配置文件
// frontend/src/styles/colors.js
export const colors = {
  primary: '#1890ff',      // 主色调
  secondary: '#52c41a',    // 辅助色
  text: '#000000',         // 文字颜色
  textSecondary: '#666666', // 次要文字
  background: '#ffffff',   // 背景色
  border: '#d9d9d9',       // 边框色
  // ... 更多颜色
}
```

### 提取字体
```javascript
// frontend/src/styles/typography.js
export const typography = {
  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto',
  fontSize: {
    small: '12px',
    normal: '14px',
    medium: '16px',
    large: '18px',
    xlarge: '24px',
  },
  lineHeight: {
    tight: 1.2,
    normal: 1.5,
    relaxed: 1.8,
  },
}
```

### 提取间距
```javascript
// frontend/src/styles/spacing.js
export const spacing = {
  xs: '4px',
  sm: '8px',
  md: '16px',
  lg: '24px',
  xl: '32px',
  xxl: '48px',
}
```

---

## 方法4: 分享Figma链接

如果你希望我帮你提取设计规范：

1. **获取Figma链接**
   - 在Figma中点击右上角的"Share"按钮
   - 选择"Copy link"
   - 确保链接权限设置为"Anyone with the link can view"

2. **分享给我**
   - 将链接发给我
   - 我可以指导你提取设计规范
   - 或者根据设计稿帮你实现组件

---

## 整合代码到项目

### 步骤1: 安装前端依赖

```bash
cd frontend
npm install
```

### 步骤2: 将Figma导出的代码整合

#### 如果是组件代码：
1. 将组件代码保存到 `frontend/src/components/` 目录
2. 根据需要进行调整和优化

#### 如果是样式代码：
1. 将样式保存到 `frontend/src/styles/` 目录
2. 在组件中导入使用

#### 如果是设计规范：
1. 创建配置文件（如上面的颜色、字体、间距文件）
2. 在组件中使用

### 步骤3: 调整代码

Figma导出的代码通常需要调整：

1. **导入路径**
   ```javascript
   // 调整相对路径
   import Button from './components/Button'
   ```

2. **样式**
   ```javascript
   // 使用CSS模块或styled-components
   import styles from './Component.module.css'
   ```

3. **组件结构**
   ```javascript
   // 确保组件符合React规范
   function Component() {
     return <div>...</div>
   }
   export default Component
   ```

### 步骤4: 连接后端API

我已经创建了API服务文件 `frontend/src/services/api.js`，你可以：

1. 在组件中导入API方法
   ```javascript
   import { testPlanAPI } from '../services/api'
   ```

2. 调用API
   ```javascript
   const plans = await testPlanAPI.getAll()
   ```

---

## 📁 项目结构说明

我已经为你创建了完整的前端项目结构：

```
frontend/
├── src/
│   ├── components/      # 可复用组件（将Figma组件放这里）
│   ├── pages/          # 页面组件
│   ├── services/       # API服务（已配置好）
│   ├── utils/         # 工具函数
│   ├── styles/         # 样式文件（放Figma样式）
│   └── assets/         # 静态资源（图片、图标等）
├── package.json        # 依赖配置
└── vite.config.js      # Vite配置（已配置代理）
```

---

## 🚀 快速开始

### 1. 安装依赖
```bash
cd frontend
npm install
```

### 2. 启动开发服务器
```bash
npm run dev
```

前端将在 `http://localhost:3000` 启动

### 3. 确保后端运行
```bash
cd backend
python3 run_server.py
```

后端在 `http://localhost:8000` 运行

---

## 📝 下一步

1. **从Figma导出代码**
   - 使用插件导出组件代码
   - 或手动提取设计规范

2. **整合到项目**
   - 将组件代码放到 `components/` 目录
   - 将样式放到 `styles/` 目录

3. **连接后端**
   - 使用已配置的API服务
   - 实现数据交互

4. **测试**
   - 确保前后端正常通信
   - 测试所有功能

---

## 💡 提示

- Figma导出的代码可能需要调整才能使用
- 建议先导出单个组件测试
- 样式可能需要手动调整以匹配设计
- 可以使用Ant Design组件库加速开发

---

## ❓ 需要帮助？

如果你遇到问题：
1. 分享Figma链接，我可以帮你提取设计规范
2. 告诉我具体遇到的问题
3. 我可以帮你调整和优化代码
