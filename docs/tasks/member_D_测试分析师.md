# 成员 D — 测试分析师 任务书

---

## 你的定位

你主要负责**两个最高分值的文档交付物**：Risk Analysis Report（10%）和 Test Plan 的主体部分（40% 里的核心章节）。你的工作产出决定了整个项目"站不站得住脚"——老师会仔细阅读你的文档来判断团队对软件测试概念的理解深度。

你不是主力写代码的人，但你需要**理解系统**，因为你写的内容必须和代码实际做的事完全一致。

---

## 你依赖谁

| 你需要的 | 来自 | 时间 |
|---------|-----|-----|
| `simulator_spec_for_doc.md`（仿真器5信号说明） | 成员 A | 第1周末 |
| `API_reference_for_frontend.md`（了解系统架构） | 成员 A | 第1周末 |
| 10条 VCU 需求的最终版本 | 成员 A/B 确认后 | 第1周末 |
| `pytest_results.txt`（测试执行结果） | 成员 B | 第3周初 |
| `detailed_test_case_design.md`（成员 B 写的用例设计） | 成员 B | 第3周初 |

**在等代码的同时，你可以先写 Risk Analysis Report 和 Test Plan 前三节**——这些内容主要依赖对系统的理解，不需要代码跑起来。

---

## 你的任务清单

### 任务 1：Artifact 2 — Risk Analysis Report（完整）

**文件位置：** `docs/Risk_Analysis_Report.md`（成员 E 负责排版成 PDF）

**章节结构（按照 Assignment 要求）：**

#### 1.1 目标应用概述
- VCU 唤醒-休眠控制模块是什么（用外行能看懂的语言说）
- 它在汽车系统中的位置（充电场景下的 ECU 上下电管理）
- 为什么用仿真器而不是真实硬件（SIL 测试是汽车行业标准流程，老师了解项目背景）
- 仿真器的 API 架构（引用成员 A 提供的 `simulator_spec_for_doc.md`）

#### 1.2 测试范围与边界
- 测试对象：5 个输入信号（CC2电压、CC电压值、CP幅值、供电电压、网络唤醒报文使能状态）
- 不在测试范围内：VCU 内部固件逻辑、CAN 总线物理层
- 测试边界：每个信号的有效/无效区间（直接从 `simulator_spec_for_doc.md` 取数据）

#### 1.3 需求列表
列出全部 10 条 VCU 需求（从 DESIGN_PLAN.md 第二节 2.5 的 CSV 取），每条包含：
- ID / Title / Description / Category

#### 1.4 风险评估方法
解释 5 维度评分算法：
- 每个维度的名称、权重、评分说明
- 优先级映射规则（≥7.0=High，4.0~6.9=Medium，<4.0=Low）
- 为什么这 5 个维度（对应 ISTQB Risk-Based Testing 原则）

#### 1.5 风险分析结果
完整的风险分析表格：

| 需求ID | 类别 | Criticality | Boundary | Complexity | State | Testability | 总分 | 优先级 | 分析依据 |
|--------|-----|------------|---------|-----------|-------|------------|------|-------|---------|
| REQ-001 | Input Validation | 6 | 10 | 4 | 6 | 10 | 7.35 | High | CC2电压有精确的[4.8,7.7]V边界，越界直接导致状态失败 |
| REQ-002 | Input Validation | 6 | 8 | 2 | 4 | 10 | 6.40 | Medium | ... |
| REQ-003 | Input Validation | 6 | 6 | 2 | 4 | 10 | 6.00 | Medium | ... |
| REQ-004 | State Transition | 8 | 10 | 2 | 10 | 10 | 8.50 | High | ... |
| REQ-005 | State Control | 7 | 10 | 4 | 10 | 10 | 8.30 | High | ... |
| REQ-006 | Safety | 10 | 8 | 4 | 8 | 8 | 8.40 | High | ... |
| REQ-007 | Safety | 10 | 8 | 4 | 8 | 8 | 8.40 | High | ... |
| REQ-008 | Safety | 10 | 4 | 2 | 6 | 10 | 7.30 | High | ... |
| REQ-009 | State Control | 7 | 4 | 4 | 10 | 10 | 7.25 | High | ... |
| REQ-010 | Timing | 4 | 6 | 2 | 4 | 8 | 4.60 | Medium | ... |

> 注：具体各维度分值请根据每条需求的实际特征计算，上表仅为参考框架。

#### 1.6 风险矩阵图
- 手绘或用工具生成一张气泡图（X=Boundary Sensitivity，Y=Criticality，气泡大小=总分，颜色=优先级）
- 可以截工具（RiskAnalysis.tsx 页面）的图，或用 Excel/PPT 制作

#### 1.7 测试优先级建议
根据风险分析结果，给出推荐的测试执行顺序，解释为什么高风险需求要先测。

---

### 任务 2：Artifact 3 — Test Plan（你负责的三节）

**文件位置：** `docs/Test_Plan.md`（成员 E 汇总所有人的章节）

#### 2.1 Project Scope（项目范围）

内容：
- **背景**：使用 AutoTestDesign 工具对 VCU 唤醒-休眠行为仿真器进行系统性软件测试
- **测试目标**：验证 VCU 仿真器在 5 种输入信号下的响应行为符合软件需求规格
- **整体目标**：证明 AutoTestDesign 工具能够从需求出发，自动生成、执行并报告测试结果
- **测试范围**：
  - 功能测试：5 个信号的 EP/BVA/决策表测试
  - AI 补充测试：GAN 生成的 CC2 电压时序序列测试
  - 非功能测试：响应时间（actual_duration < 120s）
- **不在范围内**：VCU 物理硬件测试、CAN 总线协议底层

大约 500 字。

#### 2.2 Test Items（测试项）

内容：

**功能特性（按 5 个信号分）：**

| 测试项 | 描述 | 相关需求 |
|-------|-----|---------|
| CC2 电压唤醒触发 | 验证[4.8,7.7]V范围内成功唤醒，越界失败 | REQ-001/002/003 |
| CC2 电压休眠触发 | 验证 12.0V 精确触发休眠 | REQ-004 |
| CC 接触电压检测 | 验证[0.1,3.9]V范围导致失败 | REQ-005 |
| CP 幅值异常检测 | 验证[9.1,12.9]V范围导致失败 | REQ-006 |
| 供电电压异常检测 | 验证[9.1,15.9]V范围导致失败 | REQ-007 |
| 网络唤醒冲突检测 | 验证使能=1时导致失败 | REQ-008 |
| READY 标志一致性 | 验证 vehicle_state 与 ready_flag 始终同步 | REQ-009 |

**非功能特性：**

| 测试项 | 描述 | 相关需求 |
|-------|-----|---------|
| 响应时间 | actual_duration < 120s | REQ-010 |
| API 可用性 | 仿真器健康检查正常 | — |

**系统架构描述：**
画一个简单的框图：
```
AutoTestDesign Tool (Port 8000)
    前端 React (Port 3000)  ↔  后端 FastAPI (Port 8000)
                                      ↓ HTTP POST /simulate
                          VCU 仿真器 (Port 8001)
```

#### 2.3 High-level Test Suite Design（高层测试套件设计）

| 测试套件 | 技术 | 覆盖需求 | 优先级 | 理由 |
|---------|-----|---------|-------|-----|
| TS-01：CC2 电压边界测试 | BVA | REQ-001/002/003/004 | High | CC2 是主唤醒信号，边界最关键 |
| TS-02：CC2 等价划分 | EP | REQ-001/002/003 | High | — |
| TS-03：辅助信号异常注入 | EP + BVA | REQ-005/006/007/008 | High | 安全性需求 |
| TS-04：多信号条件组合 | Decision Table | REQ-001~009 | High | — |
| TS-05：READY 一致性验证 | EP | REQ-009 | Medium | — |
| TS-06：GAN 序列补充测试 | GAN-based | REQ-001/003 | Medium | CC2 动态边界穿越 |
| TS-07：响应时间测试 | Boundary Value | REQ-010 | Low | 非功能性 |

**为每个套件写 1~2 句理由**，说明为什么选这个技术对应这组需求（这是"Understanding of Concepts 10%"的得分点）。

---

## 你不用写的内容（其他人负责）

- Test Plan: Testing Framework and Rationale → 成员 A
- Test Plan: Cost Estimation → 成员 A
- Test Plan: Schedule → 成员 A
- Test Plan: Organization Chart → 成员 E
- Detailed Test Design 全部 → 成员 B + E

---

## 你需要交付给谁

| 交付物 | 交给谁 | 时间节点 |
|-------|-------|---------|
| `Risk_Analysis_Report.md` 草稿 | 成员 E（汇总+排版） | 第2周末 |
| Test Plan: Project Scope 章节 | 成员 E | 第2周末 |
| Test Plan: Test Items 章节 | 成员 E | 第2周末 |
| Test Plan: High-level Suite Design 章节 | 成员 E | 第3周初 |
| Risk Report 的风险矩阵图文件 | 成员 E（用于 PPT） | 第3周初 |
