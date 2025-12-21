# 前端基于角色的功能重组建议

## 📊 当前问题分析

### 当前功能分布（都在测试工程师界面）
- ✅ Dashboard（概览）
- ✅ TestManagement（测试管理）
- ✅ TestMonitoring（监控执行）
- ✅ ResultAnalysis（结果分析）
- ✅ ReportCenter（报告中心）
- ✅ ConstraintManager（约束管理）- **应该属于工艺工程师**
- ✅ SystemSettings（系统配置）- **应该属于台架维护工程师**

### 用例图要求的功能分布

#### 1. 测试执行与分析模块（测试工程师）
- ✅ 配置测试任务 → TestManagement
- ✅ 监控执行过程 → TestMonitoring
- ✅ 分析测试报告 → ResultAnalysis + ReportCenter

#### 2. 安全与规则模块（工艺工程师）
- ❌ 执行双重安全校验 → ConstraintManager（需要增强）
- ❌ 维护工艺规则库 → ConstraintManager（需要增强为规则库管理）

#### 3. 系统部署与联调模块（台架维护工程师）
- ❌ HIL联调与接口验证 → **需要新建组件**
- ⚠️ 系统部署与监控 → SystemSettings（需要拆分和增强）

---

## 🎯 修改建议

### 方案一：角色切换模式（推荐）

#### 1. 添加角色选择/切换功能
- 在 TopNav 添加角色切换下拉菜单
- 支持三种角色：测试工程师、工艺工程师、台架维护工程师
- 根据角色显示不同的侧边栏菜单

#### 2. 重新组织侧边栏菜单

**测试工程师侧边栏：**
```
- 概览 (Dashboard)
- 测试管理 (TestManagement)
- 实时监控 (TestMonitoring)
- 结果分析 (ResultAnalysis)
- 报告中心 (ReportCenter)
```

**工艺工程师侧边栏：**
```
- 规则库管理 (RuleLibrary) - 新建
- 安全校验配置 (SecurityCheck) - 新建/增强ConstraintManager
- 约束统计 (ConstraintStats) - ConstraintManager的统计部分
```

**台架维护工程师侧边栏：**
```
- 系统部署 (SystemDeployment) - 新建
- HIL联调 (HILDebugging) - 新建
- 接口验证 (InterfaceVerification) - 新建
- 系统监控 (SystemMonitoring) - SystemSettings的监控部分
- 系统配置 (SystemSettings) - 保留部分配置功能
```

#### 3. 新建组件

**工艺工程师模块：**
- `RuleLibrary.tsx` - 工艺规则库管理
  - 规则列表（增删改查）
  - 规则分类（白名单、黑名单、范围检查等）
  - 规则导入/导出
  - 规则版本管理

- `SecurityCheck.tsx` - 双重安全校验配置
  - 第一重校验配置（DBC检查、白名单等）
  - 第二重校验配置（范围检查、CRC等）
  - 校验流程可视化
  - 校验日志查看

**台架维护工程师模块：**
- `HILDebugging.tsx` - HIL联调
  - HIL设备连接状态
  - 联调测试用例
  - 联调日志
  - 联调结果分析

- `InterfaceVerification.tsx` - 接口验证
  - 接口列表（CAN、LIN等）
  - 接口测试用例
  - 接口响应验证
  - 接口性能监控

- `SystemDeployment.tsx` - 系统部署
  - 部署配置
  - 部署历史
  - 部署状态监控
  - 回滚功能

#### 4. 修改现有组件

**ConstraintManager.tsx：**
- 拆分为两个组件：
  - `ConstraintStats.tsx` - 约束统计（测试工程师可查看）
  - `RuleLibrary.tsx` - 规则库管理（工艺工程师专用）

**SystemSettings.tsx：**
- 保留系统配置部分（台架维护工程师）
- 移除测试相关配置（移到测试工程师模块）

---

### 方案二：多标签页模式

在现有界面基础上，添加角色标签页：
- 测试工程师标签页
- 工艺工程师标签页
- 台架维护工程师标签页

每个标签页显示对应的功能模块。

---

### 方案三：权限控制模式

添加用户登录和权限管理：
- 用户登录时选择角色
- 根据角色权限显示/隐藏功能
- 后端API添加权限验证

---

## 📋 推荐实施方案（方案一）

### 实施步骤

1. **第一步：添加角色管理**
   - 创建 `RoleContext.tsx` 管理当前角色
   - 在 TopNav 添加角色切换器
   - 修改 App.tsx 根据角色显示不同菜单

2. **第二步：重组侧边栏**
   - 创建三个角色的菜单配置
   - 根据角色动态渲染菜单项
   - 添加角色标识

3. **第三步：新建组件**
   - RuleLibrary.tsx（工艺工程师）
   - SecurityCheck.tsx（工艺工程师）
   - HILDebugging.tsx（台架维护工程师）
   - InterfaceVerification.tsx（台架维护工程师）
   - SystemDeployment.tsx（台架维护工程师）

4. **第四步：拆分现有组件**
   - ConstraintManager → ConstraintStats + RuleLibrary
   - SystemSettings → 保留核心配置，移除测试相关

5. **第五步：后端API支持**
   - 添加规则库管理API
   - 添加HIL联调API
   - 添加接口验证API
   - 添加系统部署API

---

## 🎨 UI/UX 建议

1. **角色切换器位置**：TopNav 右侧，显示当前角色和切换按钮
2. **角色标识**：不同角色使用不同颜色主题
   - 测试工程师：蓝色
   - 工艺工程师：绿色
   - 台架维护工程师：橙色
3. **权限提示**：访问无权限功能时显示友好提示
4. **数据隔离**：不同角色看到的数据范围不同

---

## 📊 功能映射表

| 用例图功能 | 当前组件 | 建议归属 | 新建/修改 |
|----------|---------|---------|----------|
| 配置测试任务 | TestManagement | 测试工程师 | ✅ 保持 |
| 监控执行过程 | TestMonitoring | 测试工程师 | ✅ 保持 |
| 分析测试报告 | ResultAnalysis + ReportCenter | 测试工程师 | ✅ 保持 |
| 执行双重安全校验 | ConstraintManager | 工艺工程师 | 🔨 增强为SecurityCheck |
| 维护工艺规则库 | ConstraintManager | 工艺工程师 | 🆕 新建RuleLibrary |
| HIL联调与接口验证 | 无 | 台架维护工程师 | 🆕 新建HILDebugging + InterfaceVerification |
| 系统部署与监控 | SystemSettings | 台架维护工程师 | 🔨 拆分为SystemDeployment + SystemMonitoring |

---

## ✅ 实施优先级

**高优先级（核心功能）：**
1. 添加角色切换功能
2. 重组侧边栏菜单
3. 新建RuleLibrary组件（工艺工程师）
4. 新建HILDebugging组件（台架维护工程师）

**中优先级（增强功能）：**
5. 新建SecurityCheck组件
6. 新建InterfaceVerification组件
7. 新建SystemDeployment组件
8. 拆分ConstraintManager

**低优先级（优化功能）：**
9. 添加权限验证
10. 添加数据隔离
11. UI主题切换

---

## 💡 实施建议

建议采用**渐进式重构**：
1. 先实现角色切换和菜单重组（不影响现有功能）
2. 逐步新建组件并迁移功能
3. 最后添加权限控制和数据隔离

这样可以在不破坏现有功能的前提下，逐步完成角色分离。

