# Figma代码整合指南

## 📋 整合步骤

当你从Figma导出代码后，按以下步骤整合：

### 步骤1: 确定代码位置

根据代码类型，放到对应目录：

- **页面组件** → `frontend/src/pages/`
- **可复用组件** → `frontend/src/components/`
- **样式文件** → `frontend/src/styles/`
- **静态资源** → `frontend/src/assets/` 或 `frontend/public/`

### 步骤2: 调整导入路径

Figma导出的代码可能需要调整导入路径：

```jsx
// 调整前（Figma导出）
import Button from './Button'
import styles from './Component.module.css'

// 调整后（项目结构）
import Button from '../components/Button'
import styles from './Component.module.css'
```

### 步骤3: 连接后端API

使用已配置的API服务：

```jsx
import { testPlanAPI, testTaskAPI, ganAPI } from '../services/api'

// 在组件中使用
const plans = await testPlanAPI.getAll()
```

### 步骤4: 使用设计规范

如果导出了设计规范，使用主题配置：

```jsx
import { colors, typography, spacing } from '../styles/design-tokens'

// 在组件中使用
<div style={{ color: colors.primary, padding: spacing.md }}>
```

## 🔧 常见问题处理

### 问题1: 样式不生效

**解决**：
- 检查CSS文件路径
- 确保样式文件被正确导入
- 使用CSS模块或styled-components

### 问题2: 组件导入错误

**解决**：
- 检查文件路径是否正确
- 确保组件已导出
- 使用相对路径或绝对路径

### 问题3: 图片资源找不到

**解决**：
- 将图片放到 `frontend/src/assets/` 或 `frontend/public/`
- 使用正确的导入路径
- 或使用URL路径

## 📝 代码示例

### 页面组件示例

```jsx
// frontend/src/pages/TestPlanPage.jsx
import { useState, useEffect } from 'react'
import { testPlanAPI } from '../services/api'
import { Button, Table } from 'antd'

function TestPlanPage() {
  const [plans, setPlans] = useState([])

  useEffect(() => {
    loadPlans()
  }, [])

  const loadPlans = async () => {
    const data = await testPlanAPI.getAll()
    setPlans(data)
  }

  return (
    <div>
      <h1>测试计划</h1>
      <Table dataSource={plans} />
    </div>
  )
}

export default TestPlanPage
```

### 组件示例

```jsx
// frontend/src/components/CustomButton.jsx
import { Button } from 'antd'
import './CustomButton.css'

function CustomButton({ children, onClick }) {
  return (
    <Button className="custom-button" onClick={onClick}>
      {children}
    </Button>
  )
}

export default CustomButton
```

## 🚀 快速整合

如果你导出了代码，可以直接：

1. **粘贴代码给我**
   - 我会帮你调整和整合

2. **或告诉我文件位置**
   - 我会读取并整合

3. **我会帮你**：
   - 调整代码结构
   - 修复导入路径
   - 连接API
   - 确保可以运行

---

**准备好代码了吗？发给我吧！** 🎉

