# 成员 5 — PPT 与文档统筹 任务书

---

## 你在答辩中讲什么

**你讲"我们的工具有什么价值、能推广吗"**——做整个答辩的开场总览和收尾深度分析。你负责让评委从整体上理解这个项目的意义，以及工具的可推广性。这部分对应评分标准里的"In-depth Analysis（20%）"，是很多团队忽视但分值很高的部分。

答辩时间：约 3 分钟（开场 1 min + 收尾 2 min）

---

## 你依赖谁

你几乎依赖所有人，因此要从第 1 周起就开始协调收集材料：

| 你需要的 | 来自 | 截止时间 |
|---------|-----|---------|
| `simulator_spec_for_tester.md` | 成员 1 | 第 1 周末（了解系统） |
| Risk Report 完整版 | 成员 1+4 | 第 3 周初 |
| Test Plan: Test Items | 成员 1 | 第 2 周末 |
| Test Plan: Testing Framework + Cost | 成员 2 | 第 3 周初 |
| Demo 视频 | 成员 2 | 第 4 周初 |
| 工具界面截图（约 8 张） | 成员 2 | 第 3 周末 |
| `Detailed_Test_Design.md` | 成员 3 | 第 3 周末 |
| `pytest_results.txt` | 成员 3 | 第 3 周末 |
| Test Plan 三节（Scope/Schedule/Org） | 成员 3 | 第 3 周初 |
| Test Plan: High-level Suite Design | 成员 4 | 第 3 周初 |
| 风险矩阵图 | 成员 4 | 第 2 周末 |

---

## 你负责的工作

### 你不写代码，你负责"把所有人的工作拼成一个完整项目"

---

## 你需要写的文档

### 文档 1：Test Plan 完整版（Artifact 3，40 分）

**文件路径：** `docs/Test_Plan.md`

**你的职责：汇总所有章节 + 写 Organization Chart + 做全文校对**

Test Plan 7 个章节来源：

| 章节 | 来源 | 你需要做的加工 |
|-----|-----|-------------|
| Project Scope | 成员 3 | 统一格式，检查需求编号是否正确 |
| Test Items | 成员 1 | 检查架构图端口号是否与实际一致 |
| High-level Test Suite Design | 成员 4 | 检查 7 套测试套件的需求编号 |
| Schedule / Checklist | 成员 3 | 替换为实际完成时间 |
| Organization Chart | **你来写** | 见下方说明 |
| Chosen Testing Framework | 成员 2 | 格式统一 |
| Cost Estimation | 成员 2 | 检查数字合理性 |

**你来写：Organization Chart（约 200 字 + 结构图）**

```markdown
## Organization Chart

本次测试活动由 5 名团队成员共同承担，各自角色如下：

| 成员 | 测试角色 | 主要职责 |
|-----|---------|---------|
| 成员 1 | Test Environment Engineer | 搭建 VCU 仿真器（被测系统），撰写 Risk Analysis Report |
| 成员 2 | Test Tool Developer | 开发 AutoTestDesign 工具（前端 + 后端），录制 Demo 视频 |
| 成员 3 | Test Designer & Executor | 使用工具设计测试用例，执行 pytest 脚本，撰写 Detailed Test Design |
| 成员 4 | Test Analyst | 完成风险分析评分，设计高层测试套件 |
| 成员 5 | Test Manager | 汇总所有文档，制作 PPT，协调答辩 |

（画出简单的组织结构图）
```

**全文校对清单（收到所有章节后逐项检查）：**

- [ ] 10 条 VCU 需求（REQ-001~010）在所有文档中描述一致
- [ ] CC2 有效范围：全文统一写 [4.8, 7.7]V
- [ ] CC2=4.8V：全文统一写 vehicle_state=170（VCU 成功唤醒）
- [ ] 越界 vehicle_state：全文统一写 30（不写 12/46）
- [ ] test_status：全文统一用 1/3/4，含义一致
- [ ] 测试套件 ID（TS-01~07）在 Test Plan 和 Detailed Test Design 中一致
- [ ] 用例 ID（EP-XX / BVA-XX / DT-RX）在 Detailed Test Design 和 pytest 脚本中一致

---

### 文档 2：Detailed Test Design 完整版（Artifact 4，30 分）

**文件路径：** `docs/Detailed_Test_Design.md`

**你的职责：汇总成员 3 的两节 + 补写 Test Tool Implementation + 写引言和结论**

文档结构：

**引言（你来写，约 150 字）：**
- 本文档是对 VCU 仿真器一个主要功能模块的详细测试设计与执行记录
- 使用 AutoTestDesign 工具生成测试用例，使用 pytest + httpx 执行
- 选取 CC2 电压范围（REQ-001）和辅助信号检测（REQ-005~008）作为重点模块

**Test Case Design**：来自成员 3，直接复制

**Test Tool Implementation（你来写，约 400 字）：**

```markdown
## Test Tool Implementation

### 测试框架选择
- **AutoTestDesign Tool（前端 React + 后端 FastAPI）**
  - 用于需求导入、解析、风险分析、测试用例生成
  - 访问：http://localhost:3000
  - 选择理由：本项目自研工具，实现了 EP/BVA/决策表的自动化生成，
    并能直接调用 VCU 仿真器 API 执行测试

- **pytest + httpx**
  - 用于参数化执行测试用例，直接调用 POST /simulate 接口
  - 选择理由：Python 生态，与后端同语言，支持参数化和详细报告生成

### 测试执行方式
1. 启动 VCU 仿真器（python vcu_simulator/main.py）
2. 启动后端（python backend/run_server.py）
3. 在 AutoTestDesign 工具中导入需求、生成用例（截图见上节）
4. 执行 pytest：
   pytest tests/test_vcu_simulator.py -v --tb=short

### Test Oracle 判定逻辑
每条用例执行后，对比以下三项：
1. test_status：实际值 vs 预期值（1=PASS / 3=SLEEP / 4=FAIL）
2. vehicle_state：实际值 vs 预期值（170 or 30）
3. ready_flag：实际值 vs 预期值（1 or 0）
三项全部匹配 → 测试通过（PASS）
任一不匹配 → 测试失败（FAIL），记录差异

REQ-009 一致性验证：额外检查 vehicle_state=170 时 ready_flag 必须=1
```

**Test Result Analysis**：来自成员 3，直接复制

**结论（你来写，约 100 字）：**
- 总结测试覆盖情况
- 工具的效果评价（节省了多少时间）

---

### 文档 3：PPT（`docs/AutoTestDesign_启动会.pptx` 已有，答辩 PPT 另做）

> 注意：`docs/generate_ppt.py` 生成的是**启动会 PPT**。答辩用 PPT 是另一份，结构不同。

**文件路径：** `docs/AutoTestDesign_答辩.pptx`

**答辩 PPT 结构（建议 20 页，15 分钟）：**

| 页码 | 内容 | 主讲人 | 时间 |
|-----|-----|-------|-----|
| 1 | 封面 | — | — |
| 2 | 项目概述（两个系统关系图） | **你**（开场） | 1 min |
| 3 | 目标应用：VCU 仿真器 + 5个信号表 | **成员 1** | 1.5 min |
| 4 | 真实数据发现（3个重要发现） | **成员 1** | 1.5 min |
| 5 | 工具架构（前后端 + GAN 角色） | **成员 2** | 0.5 min |
| 6 | 工具 Demo（播放视频或截图展示） | **成员 2** | 2 min |
| 7 | 需求与解析界面截图 | **成员 2** | 0.5 min |
| 8 | 风险分析：方法说明 | **成员 4** | 1 min |
| 9 | 风险分析：矩阵图 + 结果表 | **成员 4** | 1 min |
| 10 | 高层测试套件设计（7套表格） | **成员 4** | 1 min |
| 11 | 测试用例设计：EP 表格 | **成员 3** | 0.5 min |
| 12 | 测试用例设计：BVA 表格（CC2重点）| **成员 3** | 0.5 min |
| 13 | 测试用例设计：决策表 | **成员 3** | 0.5 min |
| 14 | 测试执行：pytest 截图 + PASS/FAIL | **成员 3** | 1 min |
| 15 | 测试结果：追踪矩阵 + 覆盖率 | **成员 3** | 0.5 min |
| 16 | 工具泛化性（不只能测 VCU） | **你** | 1 min |
| 17 | 工具 vs 手动测试对比（Cost节省）| **你** | 0.5 min |
| 18 | Improvement with Evidence | **你** | 0.5 min |
| 19 | 总结 | **你** | 0.5 min |
| 20 | Q&A | 全员 | 3 min |

---

### 文档 4：Q&A 问题库

**文件路径：** `docs/tasks/QA_preparation.md`

**第 3 周末发给所有人，让大家提前准备：**

| # | 问题 | 参考答案要点 | 最适合回答的人 |
|--|-----|------------|-------------|
| 1 | 你们的工具和 Jira/TestRail 有什么区别？ | 我们的工具负责"设计"（从需求自动生成用例），Jira 负责"管理"（追踪执行）| 你 |
| 2 | 为什么 CC2=7.8V 有时 PASS 有时 FAIL？ | 真实数据库中 db_10 有 PASS 也有 FAIL，这是真实的灰色边界，测试工具识别了这个不确定性 | 成员 1 |
| 3 | GAN 生成的电压序列具体用在哪？ | 测试 CC2 电压连续变化时 VCU 状态转变的位置是否正确 | 成员 2 |
| 4 | 你们的工具能测其他系统吗？ | 可以。任何有数值边界输入和可调用 API 的系统都适用。举例：登录系统的密码长度、计算器的输入范围 | 你 |
| 5 | 仿真器和真实 VCU 有什么差异？ | 仿真器基于 9615 条真实数据建立，但未模拟时序效应和温度变化，老师也了解项目背景 | 成员 1 |
| 6 | 为什么 BVA 选 CC2 电压而不是其他信号？ | CC2 有明确的双侧 PASS/FAIL 边界（4.8V 和 7.7V），其他信号只有单侧失效区间 | 成员 4 |
| 7 | Interactive Review 是怎么实现的？ | 前端每个阶段都支持内联编辑，修改后调用 PUT API 持久化，不需要刷新页面 | 成员 2 |
| 8 | 测试结果中有 FAIL 的用例吗？如何处理？ | （等执行完后填写真实情况）| 成员 3 |

---

## 你的时间安排

| 周次 | 任务 |
|-----|-----|
| 第 1 周 | 阅读 DESIGN_PLAN.md，建立共享文档空间，开始 PPT 模板，准备 Q&A 框架 |
| 第 2 周 | 收到风险矩阵图（成员 4），开始答辩 PPT 制作，协调各成员进度 |
| 第 3 周 | 汇总 Test Plan 所有章节，校对一致性，汇总 Detailed Test Design |
| 第 4 周 | 完成答辩 PPT，发 Q&A 问题库，组织全员答辩排练（至少 1 次） |

---

## 答辩讲稿要点（约 3 分钟，分开场 + 收尾）

**开场（约 1 分钟）：**
> "我们这个项目分为两个部分：AutoTestDesign 工具，和它的目标应用 VCU 行为仿真器。工具负责从需求出发，自动生成测试用例并执行；仿真器是我们基于 9615 条真实数据建立的被测软件。接下来我们5个人分别介绍各自的工作。"

**收尾——工具价值和可推广性（约 2 分钟）：**

1. **工具效率对比**（30s）
   > "与手动测试相比，我们的工具将用例设计时间从约 49 小时减少到 9 小时，节省了 82%。这来自自动化的 EP/BVA/决策表生成，以及直接调用仿真器执行的一键测试能力。"

2. **可推广性**（60s）
   > "我们的工具不是只能测 VCU。它的核心能力是：读取需求文本 → 识别数值范围 → 生成 EP/BVA 用例 → 调用目标系统 API 执行。任何有以下特征的系统都适用：
   > - 有明确的输入信号和数值范围（比如登录系统的密码长度）
   > - 有可以调用的 REST API
   > - 有预期的输出状态
   > 把仿真器换成任何其他系统的 API，工具完全不需要修改。"

3. **Improvement with Evidence**（30s）
   > "在第一轮执行后，我们发现 CC2=7.8V 的 BVA 边界用例揭示了 5 个真实数据库中 PASS/FAIL 同时存在的不确定性。我们增加了重复测试用例来量化这个边界的稳定性，这正是自动化工具能发现而手工测试容易忽视的灰色地带。"
