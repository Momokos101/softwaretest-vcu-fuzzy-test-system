# 成员 E — 统筹负责人 任务书

---

## 你的定位

你是团队的**整合者和对外接口**。你不需要负责一个独立的代码模块，但你需要对每个人的工作都有足够的理解，因为：
1. 你负责把所有人的文档章节**汇总成完整的 Artifact 3（Test Plan）和 Artifact 4（Detailed Test Design）**
2. 你负责制作 **PPT** 并协调 **15 分钟答辩**
3. 你负责**校对所有文档的一致性**——确保 Risk Report、Test Plan、Detailed Test Design 里描述的 VCU 需求、边界值、状态码完全一致

你的工作开始时间最晚，但收尾任务最重，不能拖延。

---

## 你依赖谁

| 你需要的 | 来自 | 时间节点 |
|---------|-----|---------|
| Test Plan: Framework + Cost + Schedule 章节 | 成员 A | 第3周初 |
| Test Plan: Project Scope + Test Items + Suite Design 章节 | 成员 D | 第3周初 |
| `detailed_test_case_design.md`（用例设计） | 成员 B | 第3周初 |
| `test_result_analysis.md`（执行结果） | 成员 B | 第3周末 |
| `Risk_Analysis_Report.md` 草稿 | 成员 D | 第2周末 |
| 工具各页面截图（约8~10张） | 成员 C | 第3周末 |
| `AutoTestDesign_Demo.mp4` | 成员 C | 第4周初 |
| 更新后的 README.md | 成员 C | 第3周末 |

**你可以提前开始的事情（不依赖其他人）：**
- 准备 PPT 模板和风格
- 写 Organization Chart（就是这 5 份分工文件的图表化）
- 准备 Q&A 问题库（列出预期问题，留空答案，等各成员填写）

---

## 你的任务清单

### 任务 1：汇总 Artifact 3 — Test Plan（完整版）

**文件位置：** `docs/Test_Plan.md`

按以下顺序汇总各章节（各来源人见下表），确保风格统一、前后引用一致：

| 章节 | 来源 | 你的加工工作 |
|-----|-----|-----------|
| 1. Project Scope | 成员 D | 统一标题格式，检查是否引用了正确的需求编号 |
| 2. Test Items | 成员 D | 检查架构图是否与实际代码一致（端口号、服务名称） |
| 3. High-level Test Suite Design | 成员 D | 检查7个套件对应的需求编号是否正确 |
| 4. Schedule / Checklist | 成员 A | 日期替换为实际周次 |
| 5. Organization Chart | **你写** | 见下方说明 |
| 6. Chosen Testing Framework | 成员 A | 格式统一 |
| 7. Cost Estimation | 成员 A | 检查数字合理性 |

**你负责写的：Organization Chart**

用文字+表格描述 5 人职责，画出简单的分工图：

```
项目组织结构：

成员 A（后端架构师）      成员 B（测试算法工程师）
  ├── VCU 仿真器             ├── FR2.0 风险评分算法
  ├── FR1.0/1.1 后端         ├── FR3.0 EP/BVA/决策表
  └── Test Plan（技术节）   ├── FR6.0 导出服务
                             └── Detailed Test Design（用例+结果）

成员 C（前端工程师）       成员 D（测试分析师）
  ├── 4个新前端页面           ├── Risk Analysis Report
  ├── Sidebar/App 修改        └── Test Plan（主体章节）
  └── 视频 Demo

成员 E（统筹负责人）
  ├── Test Plan 汇总与校对
  ├── Detailed Test Design 汇总
  ├── PPT 制作
  └── 答辩协调
```

写清楚每个成员在"测试活动"中的角色（参考 ISTQB 的角色定义：Test Manager、Test Designer、Test Executor 等）。

---

### 任务 2：汇总 Artifact 4 — Detailed Test Design（完整版）

**文件位置：** `docs/Detailed_Test_Design.md`

**你负责写的内容：Test Tool Implementation 章节**

成员 B 提供了 pytest 脚本，你来描述这个测试工具的使用方式：

```markdown
## Test Tool Implementation

### Testing Framework
- **pytest 3.x** with **httpx** as the HTTP client
- **pytest-parametrize** for data-driven test execution

### How the Tool Works
1. AutoTestDesign Tool generates test cases (EP/BVA/Decision Table)
2. Each test case is represented as a `(signal_name, value, expected_status, expected_state)` tuple
3. pytest executes each tuple by calling `POST http://localhost:8001/simulate`
4. The Test Oracle compares actual `vehicle_state` and `test_status` against expected values
5. Results are recorded in `pytest_results.txt`

### Running the Tests
```bash
cd /path/to/project
source backend/venv/bin/activate
pip install pytest httpx
pytest tests/test_vcu_simulator.py -v --tb=short
```

### Test Oracle Logic
（从成员B的脚本里摘录 assert 部分，解释判定逻辑）
```

**汇总成员 B 提供的两个文档：**
- 从 `detailed_test_case_design.md` 复制 Test Case Design 章节
- 从 `test_result_analysis.md` 复制 Test Result Analysis 章节

**对整体进行的加工：**
- 添加引言和结论（约 200 字）
- 确保测试用例 ID 在三份文档中一致（比如 "BVA-CC2-2" 在 Test Plan、Detailed Test Design、pytest 脚本里是同一个）
- 添加追踪矩阵（需求 × 测试用例），如成员 B 没有输出，你来制作

---

### 任务 3：文档整体一致性校对（重要）

收到所有人的文档后，统一检查以下内容：

**数值一致性：**
- [ ] CC2 有效范围：全文统一写 [4.8, 7.7]V（不出现 4.9 或 7.8 作为边界，除非有注释）
- [ ] CC2=4.8V 对应的预期结果：全文统一写 vehicle_state=170（VCU 成功唤醒）
- [ ] 所有越界情况的 vehicle_state：全文统一写 30（不出现 12/46 作为测试预期）
- [ ] test_status 代码：全文统一用 1/3/4（不混用 PASS/FAIL 字母和数字）
- [ ] CC2=7.8V 的说明：加注"灰色边界，多数 FAIL"

**需求编号一致性：**
- [ ] 10 条 VCU 需求（REQ-001~010）在所有文档中描述一致
- [ ] Test Plan 的 Suite Design 中引用的需求编号与 Detailed Test Design 中一致
- [ ] pytest 脚本注释中的需求引用与文档一致

**逻辑一致性：**
- [ ] Risk Analysis Report 中的高风险需求，在 Test Plan 中也被列为高优先级测试套件
- [ ] Test Plan 中的 Cost Estimation 与实际工作量分配吻合
- [ ] Detailed Test Design 的 Result Analysis 中提到的缺陷（如果有），要能追溯到具体测试用例

---

### 任务 4：PPT 制作

**文件命名：** `AutoTestDesign_Presentation.pptx`

**幻灯片结构（建议 18~22 页）：**

| 页码 | 内容 | 素材来源 |
|-----|-----|---------|
| 1 | 封面（项目名、组员、日期） | — |
| 2 | 项目概述（工具 + 目标应用的双层架构图） | DESIGN_PLAN.md §1.1 |
| 3 | 目标应用：VCU 仿真器（5个信号一览表） | DESIGN_PLAN.md §2.1 |
| 4 | FR 1.0/1.1：需求导入与解析（界面截图） | 成员 C |
| 5 | FR 2.0：风险分析（界面截图 + 风险矩阵图） | 成员 C + 成员 D |
| 6 | 测试数据生成策略（5信号分层表 + GAN定位） | DESIGN_PLAN.md §1.3 |
| 7 | FR 3.0：EP 测试用例（表格） | 成员 B |
| 8 | FR 3.0：BVA 测试用例（表格，重点展示CC2边界） | 成员 B |
| 9 | FR 3.0：决策表（8条规则） | 成员 B |
| 10 | FR 3.0：界面截图（TestCaseDesign 页面） | 成员 C |
| 11 | FR 5.0：测试执行（PASS/FAIL 实时截图） | 成员 C |
| 12 | FR 6.0：导出（Excel截图，展示追踪矩阵） | 成员 C |
| 13 | Risk Analysis Report 摘要 | 成员 D |
| 14 | Test Plan 摘要（7节结构） | 成员 D + A |
| 15 | Detailed Test Design：用例统计（37条分布图） | 成员 B |
| 16 | Detailed Test Design：测试结果（Pass/Fail/Coverage） | 成员 B |
| 17 | 工具泛化性（为什么不只能测 VCU） | 你来写 |
| 18 | 数据驱动的发现（db_15 CC2 扩展范围等真实洞察） | 来自数据分析 |
| 19 | 总结与贡献 | — |
| 20 | Q&A | — |

**设计要求：**
- 使用统一配色（推荐蓝灰色系，简洁专业）
- 每页不超过 6 行文字，多用图表和截图
- 第 17 页（工具泛化性）是"In-depth Analysis 20%"的得分点，认真写

---

### 任务 5：答辩准备

#### 5.1 Q&A 问题库（发给所有人准备）

文件：`docs/tasks/QA_preparation.md`

整理以下预期问题及参考答案：

| 问题 | 答案要点 | 谁最适合回答 |
|-----|---------|-----------|
| 1. 你们的工具和 Jira/TestRail 有什么区别？ | 我们的工具负责"设计"（从需求到用例），Jira 负责"管理"（执行追踪）。| E |
| 2. 为什么 CC2=7.8V 有时 PASS 有时 FAIL？ | 5个数据库中该值出现两种结果，db_10有PASS，db_11/db等均为FAIL。这正是测试工具价值所在——识别灰色边界。 | A |
| 3. GAN 模型在测试中具体生成了什么？ | 生成 CC2 电压时序序列（8步），测试电压连续变化时VCU状态转变的位置是否正确。 | B |
| 4. 你们的工具能测其他系统吗？ | 是的。只要目标系统有：①可量化的输入信号 ②清晰的有效/无效区间 ③可调用的 API，就能用我们的工具测。举例：登录系统的密码长度，计算器的输入范围。| E |
| 5. 你们如何保证仿真器行为与真实 VCU 一致？ | 仿真器的所有边界值来自对5个真实 HIL 测试数据库（9615条记录）的分析，老师也了解这个项目背景。 | A |
| 6. Decision Table 和 EP 的区别是什么？ | EP 针对单信号划分等价类；决策表组合多个信号的条件，测试信号间的相互影响（比如CC2有效时其他信号异常的影响）。| B or D |
| 7. Interactive Review 怎么实现的？ | 前端每个阶段（需求解析/风险分析/测试用例）都支持内联编辑，修改后调用 PUT API 持久化。 | C |
| 8. 为什么用 Python/FastAPI 而不是 Java？ | 与 GAN 模型（PyTorch）同生态，API 开发效率高，成员 A 在技术选型文档中有详细说明。 | A |

#### 5.2 答辩分工脚本（15 分钟）

| 时间 | 内容 | 主讲人 |
|-----|-----|-------|
| 0:00~2:00 | 项目概述 + 目标应用介绍 | E |
| 2:00~5:00 | 工具 Demo（播放视频或现场演示） | C |
| 5:00~8:00 | 测试用例设计（EP/BVA/决策表原理和结果） | B |
| 8:00~10:00 | 风险分析报告 + Test Plan 摘要 | D |
| 10:00~12:00 | 测试结果分析 + 工具泛化性 | E |
| 12:00~15:00 | Q&A | 全员按职能分工回答 |

**每人需要准备自己负责部分的 2~3 句话精炼表述**，在答辩前一起排练一遍。

---

## 你需要交付给谁

| 交付物 | 交给谁 | 时间节点 |
|-------|-------|---------|
| `Test_Plan.md`（汇总完整版） | 提交 Artifact 3 | 第4周初 |
| `Detailed_Test_Design.md`（汇总完整版） | 提交 Artifact 4 | 第4周初 |
| `AutoTestDesign_Presentation.pptx` | 全组答辩用 | 第4周初 |
| `QA_preparation.md` | 全组练习 | 第3周末（提前发，让大家有时间准备） |
| 文档一致性校对报告（内部用） | 成员 A/B/D（让他们修改） | 第3周末 |
