# Artifact 4 — 详细测试设计与执行 · 一步步执行计划

> **作业出处**：Assignment 2 第 4 项交付物（权重 30%）— *Detailed Test Design and Execution Document for one major feature/module*。
>
> **本文档定位**：写给“测试同学”自己看的 **执行手册**（procedure manual），不是最终交付的 Artifact 4 文档本身。按本文步骤跑完，得到的所有产物（用例 JSON / pytest 输出 / 截图 / 覆盖率报告）会再喂给 `Artifact4_Detailed_Test_Design_Execution_Outline.md` 完成正式撰写。
>
> **依据文件（严格遵循，不可自创）**：
> - `Assignment 2 .pdf`（最新 8th May 2026 版） — 交付物范围与评分标准
> - `Project Requirement Specification.docx` — 工具 FR/NFR 规范
> - `docs/PROJECT_PLAN_V2.md` — VCU 仿真器 5 模块 24 条需求 + 10 个 Test Suite 设计
> - `docs/Requests_to_Testing_Teammate_for_Artifact4.md` — 文档同学开出的证据清单
> - `docs/Artifact4_Detailed_Test_Design_Execution_Outline.md` — 文档同学已经写好的 Artifact 4 大纲，留出空槽给本计划产出的证据
>
> **更新日期**：2026-05-24

---

## 0. 任务定位与边界

### 0.1 Assignment 2 第 4 项原文要求（必须命中的三个子项）

| 子项 | 原文要求 | 我们要产出什么 |
|---|---|---|
| **Test Case Design** | Design test cases for the selected feature/module using the AutoTestDesign tool, and explain test coverage. Use **multiple black-box** testing techniques **and also white-box** techniques. | 用 AutoTestDesign 生成 + 人工审查后的 EP / BVA / Decision Table / State Transition 用例集，每条带 REQ 追溯和 coverage item ID |
| **Test Tool Implementation** | Choose a testing framework for executing the tests on the target application; ideally develop test scripts based on the detailed test cases above. | 选定 **pytest + httpx**；将设计阶段的用例落到 `tests/test_suite_*.py` 真实可跑脚本 |
| **Test Result Analysis** | Summary based on the test results. | pytest 输出 + 覆盖率 + 缺陷分析（REQ-012 卡死复现） + Before/After Interactive Review 对比 |

### 0.2 自选模块

| 项 | 取值 | 依据 |
|---|---|---|
| Target Application | **VCU Wake-Sleep Behavior Simulator v1.0** | Assignment 2 第 5 节明确要求 target application 与 tool 分离；PROJECT_PLAN_V2 §1.1 |
| Selected Feature/Module | **Module A — 电源状态管理（Wake-Sleep Decision Module）** | PROJECT_PLAN_V2 §2.2；该模块需求最多（14 条）、风险最高（含 REQ-012 已知缺陷 RPN=1）、5 大 ISO 9126 特性都覆盖 |
| 覆盖需求范围 | REQ-001 ~ REQ-014（共 14 条）| PROJECT_PLAN_V2 §2.8 |
| 选定理由（必须写进 Artifact 4） | ① 该模块包含 **已知 state10 卡死缺陷**（RPN=1，最高优先级），是“真实工程缺陷复现”的最佳载体；② 7 路唤醒 × 3 条休眠 × 状态机三态，**天然覆盖 ISO 29119-4 的 EP / BVA / Decision Table / State Transition 四种技术**，单一模块即可同时演示多种黑盒 + 白盒；③ 接口 (`POST /simulate`、`POST /simulate/sleep`、`GET /state`、`GET /dtc`) 已实现，可端到端执行 | 见 PROJECT_PLAN_V2 §5.2 + 现有代码 |

### 0.3 范围声明（写进 Artifact 4 §1.3）

| In Scope | Out of Scope（必须写排除理由） |
|---|---|
| Module A 状态机 state09 / state10 / state11 完整迁移路径 | 真实 HIL 台架与物理 CAN 总线（仿真器为 SIL，无硬件） |
| 7 路唤醒触发（w1 ~ w7） | 多 VCU 网络拓扑（项目不涉及） |
| 3 路休眠条件（h1 AND h2 AND h3） | 安全启动 / 固件加密（仿真器不实现 HSM） |
| 时序边界（duration ≥ 10ms） | dSPACE/SCALEXIO 物理接口 |
| 已知 state10 卡死缺陷复现（REQ-012） | 1 kHz 物理采样 |
| 输出字段一致性（REQ-013） | 生产环境压力测试 |
| 时序合规（REQ-014, actual_duration ≤ 20s） | Module B/C/D/E 单独测试（在 Test Plan 全量覆盖，但本 Artifact 4 不展开） |

---

## 1. 第 0 周：环境准备与基线确认（0.5 天）

### Step 1.1 — 拉取并启动三套服务

```bash
# 1) VCU 仿真器（target application），端口 8001
cd /Users/hby/Documents/GitHub/softwaretest-vcu-fuzzy-test-system
python -m uvicorn vcu_simulator.main:app --host 0.0.0.0 --port 8001 --reload

# 2) AutoTestDesign 后端（the tool），端口 8000
cd backend && python run_server.py

# 3) AutoTestDesign 前端，端口 3000
cd frontend && npm run dev
```

### Step 1.2 — 记录环境基线（Artifact 4 §9.2 要用）

执行以下命令把版本号 / commit hash / 依赖列表落到 `docs/test_evidence/env_baseline.txt`：

```bash
mkdir -p docs/test_evidence
{
  echo "=== Date ===" && date
  echo "=== OS ===" && uname -a
  echo "=== Python ===" && python --version
  echo "=== pytest ===" && pytest --version
  echo "=== Git branch / commit ===" && git rev-parse --abbrev-ref HEAD && git rev-parse HEAD
  echo "=== Dependencies ===" && pip freeze | grep -E "fastapi|uvicorn|httpx|pytest|anthropic"
  echo "=== VCU /state ===" && curl -s http://localhost:8001/state
  echo "=== VCU /config ===" && curl -s http://localhost:8001/config
} > docs/test_evidence/env_baseline.txt
```

### Step 1.3 — 截图（必须截，文档同学会要）

| 文件名（保存到 `docs/test_evidence/screenshots/`）| 内容 |
|---|---|
| `01_three_services_running.png` | 三个终端窗口都跑起来的全局截图 |
| `02_vcu_swagger.png` | 浏览器打开 `http://localhost:8001/docs`，展开 `POST /simulate` 的截图 |
| `03_tool_frontend_home.png` | `http://localhost:3000` 主页截图 |
| `04_simulate_sample_response.png` | 在 Swagger 里执行一次 `POST /simulate {"supply_voltage": 9.3, "duration_ms": 15}`，截响应体 |

### Step 1.4 — 验收准则（必须全过才进入 Step 2）

- [x] `curl http://localhost:8001/state` 返回 `200` 且 `vehicle_state == 9`
- [x] `curl http://localhost:8000/api/health` 返回 `200`
- [x] AutoTestDesign 前端能加载 VCU Demo（点击 “Load Demo” 后看到 24 条需求列表）
- [x] 上述 4 张截图全部存在

---

## 2. 第 1 周：Test Case Design — 用 AutoTestDesign 跑完 7 步 Interactive Review（3 天）

> 本阶段对应 Assignment 2 “**Mainly**” 段：Concept → Coverage Item Identification → Coverage Strategy & Method → Test Cases → Prompt Design → Results Analysis → Improvement。
> **强制要求**：每一步都要 **保留工具初版输出 + 人工修订后版本 + 修改原因说明**，否则丢“Interactive Review”这条评分项。

### Step 2.1 — 准备需求基线（FR 1.0 / 1.1）

#### 2.1.1 用 Module A 的 14 条需求作为输入

把 `docs/PROJECT_PLAN_V2.md` §2.8 表中 **REQ-001 ~ REQ-014** 抠出来，落到一个新文件 `docs/test_evidence/module_A_requirements_input.txt`，**逐字照抄不要改写**。示例（前 3 条，全文按这个格式补完）：

```
REQ-001 硬线供电唤醒 w1
    供电电压 > 9V 持续 ≥ 10ms 时唤醒，输出 pdcu_wake_reason=1, vehicle_state=11。
    Priority: High

REQ-002 CAN 网络唤醒 w2
    CAN 总线收到 ID ∈ [0x400, 0x47F] 报文时唤醒，pdcu_wake_reason=2, vehicle_state=11。
    Priority: High

REQ-003 CP 信号唤醒 w3
    CP 幅值 > 9V 上升沿触发唤醒，pdcu_wake_reason=3。
    Priority: Medium
```

> **不要用 `docs/demo_vcu_requirements.csv`**：那个是 CC2 旧版需求，与当前 Module A 状态机口径不一致；本 Artifact 4 用 PROJECT_PLAN_V2 §2.8 表作为唯一基线。

#### 2.1.2 三种输入方式都要演示一遍（FR 1.0 要求）

| 输入方式 | 操作 | 证据文件名 |
|---|---|---|
| ① 文本粘贴 | 复制 `module_A_requirements_input.txt` 内容到前端 textarea，点 Parse | `05_input_paste.png` |
| ② CSV 上传 | 把同样内容转成 CSV（id,title,requirement,priority），上传 | `06_input_csv_upload.png` |
| ③ Demo 加载 | 点击 “Load VCU Demo” 按钮 | `07_input_demo_load.png` |

#### 2.1.3 LLM 结构化结果导出（FR 1.1）

工具解析完成后：
- 点击 `Export → Parsed Requirements (JSON)`，保存为 `docs/test_evidence/01_parsed_requirements_raw.json`
- **截图保留工具初版**：`08_parsed_requirements_raw.png`

### Step 2.2 — Interactive Review · 第 1 步【Concept】（FR 1.1 + 人工审查）

#### 2.2.1 人工逐条检查 LLM 解析结果

打开 `01_parsed_requirements_raw.json`，对照原文校验：
- `input_fields[*].name` 是否齐全？（如 REQ-001 应识别出 `供电电压` + `duration_ms` 两个字段）
- `conditions[*].threshold` 数值是否正确？（如 9.0、10）
- `expected_actions[*].expected_value` 是否对（如 `vehicle_state=11`, `pdcu_wake_reason=1`）

#### 2.2.2 在前端编辑并保存（**必须留 Before / After 对比**）

至少修订 **3 条**（文档同学要求 ≥ 5 组前后对比，配合后面 Step 2.3 ~ 2.5 一共凑够）：

| Review ID | 典型修订内容（按实际工具输出选） | 修订原因 |
|---|---|---|
| REV-001 | 给 REQ-006 补回 LLM 漏掉的 `duration_ms ≥ 10` 时序条件 | LLM 偶尔会把时序识别为可选字段 |
| REV-002 | 把 REQ-002 `can_msg_id` 的 `valid_range` 从 `[0, 2047]` 改为 `[0x400, 0x47F]` | 与 PROJECT_PLAN_V2 §2.2 表对齐 |
| REV-003 | 给 REQ-012 补 `expected_actions: [{output_field: actual_duration, operator: gt, expected_value: 40}]` | LLM 没识别出“超时 2 倍”的 oracle |

每条修订都要：
- 改前截图：`09_rev001_before.png`
- 改后截图：`09_rev001_after.png`
- 在 `docs/test_evidence/review_log.md` 写一行：`REV-001 | REQ-006 | 补回时序条件 | 原因：... | 证据：09_rev001_*.png`

#### 2.2.3 导出修订后的结构化需求

- `02_parsed_requirements_reviewed.json`

### Step 2.3 — Interactive Review · 第 2 步【Coverage Item Identification】

#### 2.3.1 工具自动生成 Coverage Items

调用 `GET /api/coverage-items`（或前端对应页面），把工具初版结果导出到 `docs/test_evidence/03_coverage_items_raw.json`。

#### 2.3.2 人工对照 PROJECT_PLAN_V2 §5.8 表 Coverage Items 分类

工具初版很可能只有 Input 类等价项，**手动补足** Output / Behavior / Environment 类（这正是 Chapter 4 Workshop 的标准做法）。最少要有：

| Class ID | 类型 | 描述 |
|---|---|---|
| I-W1-1 ~ I-W7-3 | Input（21 个） | 7 路信号 × 有效/无效值/无效时序 |
| O-STATE-1 / 2 | Output | `vehicle_state` 唤醒成功 / 失败两类 |
| O-REASON-1 | Output | `pdcu_wake_reason` 1~7 vs 0 |
| O-BUSFLAG-1 | Output | `bus_message_flag` 一致性（REQ-013） |
| O-DURATION-1 | Output | `actual_duration ≤ 20s`（REQ-014） |
| B-NORM-1 | Behavior | state09 → state10 → state11 完整正常序列 |
| B-STUCK-1 | Behavior | 快速 3 次循环触发 state10 卡死（REQ-012） |
| E-SIM-1 | Environment | VCU v1.0 / port 8001 / SIL |

#### 2.3.3 保存证据

- 改前：`03_coverage_items_raw.json` + `10_coverage_raw.png`
- 改后：`04_coverage_items_reviewed.json` + `10_coverage_reviewed.png`
- review_log.md 追加 REV-004（补 Output 类）、REV-005（补 Behavior 类）

### Step 2.4 — Interactive Review · 第 3 步【Coverage Strategy & Method】（FR 2.0 + FR 3.0）

#### 2.4.1 风险评分（FR 2.0）

调用 `POST /api/requirements/analyze-risk`，让 LLM 按 ISO 9126 × Tech×Business Risk 框架给每条需求打分。导出 `05_risk_analysis_raw.csv`。

**人工校验 RPN 关键三项**（必须与 PROJECT_PLAN_V2 §5.1 一致）：

| REQ | 期望 RPN | 期望 Extent |
|---|---|---|
| REQ-001 ~ 007 | 2（Tech 2 × Bus 1） | Extensive |
| REQ-008 ~ 011 | 2 | Extensive |
| **REQ-012** | **1**（Tech 1 × Bus 1，最高优先级） | Extensive |
| REQ-013 / 014 | 6 | Broad |

若 LLM 给的分数与上表偏差超过 ±2，调用 `PUT /api/requirements/{id}/risk` 手动覆写。

- 改前：`05_risk_analysis_raw.csv` + `11_risk_matrix_raw.png`
- 改后：`06_risk_analysis_reviewed.csv` + `11_risk_matrix_reviewed.png`

#### 2.4.2 测试技术选择（每条需求绑定技术，写进 Artifact 4 §3.2 / §5）

按 PROJECT_PLAN_V2 §STP-5.8 的映射：

| 需求 | 技术（Black-Box / White-Box）| 选择理由（Chapter 4） |
|---|---|---|
| REQ-001 ~ 007 | **EP**（7 路 × 有效/无效/时序无效 3 个等价类） | 输入域有清晰等价类划分；EP 是覆盖输入域最系统的方法 |
| REQ-001 / 006 / 007（带时序）| **BVA**（每边界 below/on/above 三点）| 数值边界处缺陷率最高（off-by-one）|
| REQ-008 ~ 011（h1 AND h2 AND h3）| **Decision Table** | 3 个布尔条件 2³=8 种组合，决策表能系统枚举避免遗漏 |
| REQ-001 ~ 012（状态机迁移）| **State Transition Testing（白盒 All-Transitions）** | VCU 核心是 FSM；All-Transitions 准则确保每条迁移至少执行一次 |
| REQ-012（已知缺陷复现）| **Scenario Testing + Sequence**（补充技术）| 卡死由特定操作序列触发，场景测试最对口 |
| REQ-014（时序非功能）| **Performance Testing** | actual_duration 是 ISO 9126 Efficiency 子特性 |

调用 `PUT /api/strategies/{req_id}` 把上表写进工具，导出 `07_strategy_assignment.csv`。

### Step 2.5 — Interactive Review · 第 4 步【Test Case Generation】（FR 3.0 + FR 4.0）

#### 2.5.1 让 AutoTestDesign 批量生成用例

```bash
# 一键全生成
curl -X POST http://localhost:8000/api/test-cases/generate-all \
  -H "Content-Type: application/json" \
  -d '{"req_ids": ["REQ-001","REQ-002","REQ-003","REQ-004","REQ-005","REQ-006","REQ-007","REQ-008","REQ-009","REQ-010","REQ-011","REQ-012","REQ-013","REQ-014"]}'
```

**实际产出**（仅 Module A，REQ-001~014；不含 Module B/C/D/E）：工具按每条需求的策略技术批量生成，经两轮人工审查后定稿 **96 条**，技术分布：

| 技术 | 条数 | 说明 |
|---|---|---|
| EP 等价类 | 27 | 7 路唤醒有效/无效类 + 休眠条件等价类 |
| BVA 边界值 | 33 | 含 invalid-too-low/on/above 三点（如 8.9/9.0/9.1V）|
| DT 决策表 | 13 | h1∧h2∧h3 组合枚举（休眠）|
| ST 状态迁移 | 18 | state09↔11、↔09、→10 迁移（All-Transitions）|
| SC 场景/序列 | 5 | REQ-012 卡死快速循环复现 |
| **合计** | **96** | 14/14 需求全覆盖；**负向 47 / 正向 49**（负向=预期 VCU 报错/拒绝/卡死/维持）|

> 数据 = `09_test_cases_reviewed.json`（最终版）。版本链全程保留：v0 88 条 → v1 raw 94（工具初版，含臆造字段）→ v2 设计期审查 96 → v3 取值语义重生成 99 → v4 最终 96。

#### 2.5.2 人工审查用例（**关键的 Interactive Review 证据**，对照课件标准）

实际进行了**两轮**审查（详见 `review_log.md` Phase 5 设计期 + Phase 6 执行期），共 REV-012~016：

| Review ID | 修订内容 | 课件依据 |
|---|---|---|
| REV-012 | REQ-014 ×6：oracle 用 `is_compliant`（VCU 无此字段）→ 改真实字段 `actual_duration lte/gt` | Inspection P9 Untestability |
| REV-013 | REQ-012 ×2：标题"不触发卡死"却写 `result_type=stuck` → 改 `ne stuck`/`vehicle_state ne 10` | Part1 P5 条件不完整 |
| REV-014 | REQ-001 补 8.9V invalid-too-low 用例（不唤醒→state9）| Part1 P35-40 BVA 必含无效类 |
| REV-015 | 改进 testcase prompt（字段白名单）+ regenerate REQ-008/009/010，消除臆造字段 21→0 | Prompt Design / Untestability |
| REV-016 | 执行期：改 3（REQ-010 输入矛盾/阈值、REQ-014 时序违规走卡死）+ 删 4（畸形/重复）+ 加 1 | 执行 96 条暴露的 oracle 缺陷 |

#### 2.5.3 导出最终用例集（FR 6.0）

- `08_test_cases_raw.json`（工具初版，**bq_new 格式**，type=1/2，含 in_data / expected_results / error / est_time）
- `09_test_cases_reviewed.json`（人工修订后）
- `09_test_cases_reviewed.csv`、`09_test_cases_reviewed.xlsx`（同内容三种格式，应付 FR 6.0 三种导出）
- `10_traceability_matrix.csv`（REQ ↔ Coverage Item ↔ Test Case 三列对应表）

### Step 2.6 — Interactive Review · 第 5 步【Prompt Design】（评分项要求）

把工具实际使用的 **5 个 prompt** 完整粘贴到 `docs/test_evidence/prompts_used.md`（不能只写“见代码”）：`parse`（需求解析）、`risk`（风险分析）、`coverage`（覆盖项）、`testcase`（用例+oracle 生成）、`improve`（第二轮 LLM 用例增广）。每个配真实“输入→输出”样例。

**testcase prompt 的两轮迭代改进（Prompt Design 核心证据）**——designer 不是一次写死，而是依审查/执行反馈两次回炉、改**工具(prompt)**而非手工补用例：

| 版本 | 改进 | 修复 | 效果 | 存档 |
|---|---|---|---|---|
| v1 原始 | 仅字段列表 | — | 含臆造字段+取值错误 | `prompt_testcase_before.json` |
| v2 (REV-015) | + 字段名白名单 | Untestability：臆造字段 21→0 | — | `prompt_testcase_v2_fieldwhitelist.json` |
| v3 (TOOL-FIX-007) | + VCU 输出取值语义 | 系统性 oracle 取值错（state0/维持态/result_type）| 执行通过率 48/96→80/99 | `prompt_testcase_v3_value_semantics.json` |

### Step 2.7 — 阶段验收（Tollgate 准则，参照 STP-7.2.1）

进入 Step 3 前必须全部满足（实测均已达成）：

- [x] `docs/test_evidence/` 产出文件 ≥ 10 个（实际 25+，含 raw/reviewed 全版本链）
- [x] `review_log.md` ≥ 5 条 Before/After（实际 REV-001~016 共 16 条 + TOOL-FIX-001~008）
- [x] 总用例数 96 条（仅 Module A，14/14 需求覆盖）
- [x] 每条用例都有 `requirement_id` + `coverage_item_id` + `technique` 三联追溯
- [x] `prompts_used.md` 5 个 prompt 齐全（含 testcase v1→v3 演进）

---

## 3. 第 2 周：Test Tool Implementation — pytest 脚本与执行（2 天）

### Step 3.1 — 选定执行框架并写理由（Artifact 4 §9.1）

| 项 | 选型 | 选型理由（要写进 Artifact 4） |
|---|---|---|
| Test framework | **pytest** | 参数化、装饰器、丰富插件生态；社区标准；ISO 29119 兼容 |
| HTTP client | **httpx** | 同步 + 异步双模式，与 FastAPI 同源，类型友好 |
| 覆盖率工具 | **coverage.py** | 业界标准，支持 statement + branch |
| 性能基准 | **pytest-benchmark** | 用于 REQ-014 actual_duration NFR 度量 |
| 报告 | **pytest-html** + JUnit XML | 同时满足人工阅读和 CI 解析 |

### Step 3.2 — 把 96 条设计用例落成可执行 pytest（数据驱动，单一事实源）

交付脚本是 **`tests/test_suite_from_design.py`**（旧的按技术硬编码的 5 个 `test_suite_a~e.py` 已删除——它们脱离 96 条设计、违反 Assignment "scripts **based on** the detailed test cases"）。该脚本把 `09_test_cases_reviewed.json` 的 **96 条 reviewed 设计用例逐条参数化执行**：

1. **每个 pytest 参数 == 一条设计用例**，参数 id = `uuid | REQ | RPN | title`（全追溯，便于回映射）。
2. **输入适配器**：把设计 in_data 的抽象字段名（voltage / h1 / can_bus_idle …）翻译成 VCU 真实接口（supply_voltage / VCUO_bDIAG_VCUIdle_flg / can_stopped …）；休眠测试先唤醒到 state11 再施加条件、卡死走快速循环序列。
3. **IEEE 829 生命周期**：setup（新建 VCUSimulator）/ 测试（驱动）/ 断言 oracle（measure）/ teardown（reset）；用例按 **RPN 风险排序**（REQ-012 卡死 RPN=1 最先）。
4. **追溯矩阵**：`docs/test_evidence/10_traceability_matrix.csv`（96 行，列含 Test Case ID / **Design Case UUID**（可 join 到 `execution_details.json`）/ Coverage Item ID / Requirement ID / Technique / RPN / **Polarity 正负向**（negative 47 / positive 49）/ **Result**（PASS/FAIL），按 pytest 执行顺序排列）。

### Step 3.3 — 执行 pytest 并保留 html / xml / txt 证据

```bash
mkdir -p docs/test_evidence/pytest_output

# 数据驱动套件（96 条设计用例，按技术分 EP/BVA/DT/ST/SC 五个类）
python -m pytest tests/test_suite_from_design.py -v \
  --html=docs/test_evidence/pytest_output/design_suite_report.html --self-contained-html \
  --junitxml=docs/test_evidence/pytest_output/design_suite.xml \
  | tee docs/test_evidence/pytest_output/design_suite.txt

# API 端到端集成（HTTP 层）
python -m pytest tests/test_integration_http.py -v \
  --junitxml=docs/test_evidence/pytest_output/integration_http.xml \
  | tee docs/test_evidence/pytest_output/integration_http.txt
```

**实测结果**：design_suite **96 passed**、integration_http **11 passed**。

**工具内执行（TOOL-FIX-008）**：前端 Results 标签「执行全部」(`POST /api/execute`) 已接到上面这套 pytest——点击即在后端跑 `test_suite_from_design.py`、解析 JUnit XML、按 uuid 把每条用例标记 pass/fail 并回填 **VCU 实际输出（actual_output）**。Results 顶部 Summary 显示 96/96，逐条可展开看 VCU 响应。截图：`Results_summary_96pass.png`。

### Step 3.4 — Module A 代码覆盖率（白盒证据，coverage.py）

> **范围铁律**：Artifact 4 只测 Module A，覆盖率只统计 **Module A 被测代码 `vcu_simulator/simulator.py`**，不含 `modules/`（B/C/D/E 故障逻辑）、不含 `main.py`/`models.py`（HTTP/schema 层）。

```bash
coverage run --branch --source=vcu_simulator -m pytest tests/test_suite_from_design.py
coverage report -m --include="*/vcu_simulator/simulator.py" | tee docs/test_evidence/pytest_output/coverage_report.txt
coverage html -d docs/test_evidence/pytest_output/coverage_html --include="*/vcu_simulator/simulator.py"
coverage xml  -o docs/test_evidence/pytest_output/coverage.xml
coverage json -o docs/test_evidence/pytest_output/coverage.json --include="*/vcu_simulator/simulator.py"
```

`simulator.py` 是多模块共享文件（文件级 79.6% 语句 / 70.4% 分支），需剔除其中混入的非-Module-A 行：infra getter（get_state/config/performance）、legacy 兼容（_normalize_legacy_payload/simulate_sleep/simulate_batch）、Module B 过压欠压处理（_handle_guard_rejection）、Module C CAN 错误注入、Module D DTC 清除。剔除后即**纯 Module A 决策逻辑**覆盖率：

| 指标 | 纯 Module A | 目标 | 实测 |
|---|---|---|---|
| 语句覆盖 | 160/167 | ≥ 80% | **95.8%** ✓ |
| 分支覆盖 | 73/82 | ≥ 70% | **89.0%** ✓ |

分类与可复现度量方法见 `docs/test_evidence/pytest_output/coverage_analysis.md`。截图：`coverage_html.png`。

### Step 3.5 — 白盒补充：State Transition 表 + All-Transitions（仅 Module A 三态）

Module A 状态机只有 **state09(休眠) / state10(卡死) / state11(唤醒)** 三态（呼应 Chp4TestTechPart2 的 0-switch / All-Transitions 覆盖）。整理成 `docs/test_evidence/state_transition_table.md`：

| Transition | From | Event/Cond | To | Covered By（技术）|
|---|---|---|---|---|
| T1 | state09 | w1~w7 任一有效（电压+时序满足）| state11 | EP / ST 唤醒用例（REQ-001~007）|
| T2 | state09 | 信号无效 / 时序不足 | state09（维持）| EP / BVA 负向用例 |
| T3 | state11 | h1 ∧ h2 ∧ h3 同时满足 | state09 | DT / ST 休眠用例（REQ-011）|
| T4 | state11 | 任一 h 不满足 | state11（维持）| DT 用例（REQ-008~011）|
| T5 | state09 | Wake[有效] 且**连续 ≥3 次快速(间隔<1s)唤醒-休眠循环已累计**（rapid≥3）| state10（卡死）| SC 卡死用例（REQ-012）|

**Coverage Criterion = All-Transitions（0-switch）**：T1~T5 每条均有 ≥1 条 Module A 用例覆盖 → **100% All-Transitions**。
> T5 源态精确性：REQ-012 经 `(唤醒→休眠)×3` 后状态停在 **state09** 且循环计数=3，第 4 次唤醒从 state09 触发卡死（`simulator.py:164-176`，此时 `self.state==STATE_SLEEP`）。完整状态转换表（slide p26 四字段 + Undefined 行）+ All-States/All-Transitions/1-switch 证据见 `docs/test_evidence/state_transition_table.md`。
> 过压(>16V)→fault_protection、欠压(<6V)→undervoltage_shutdown 等迁移属 **Module B，不在本 Artifact 4 范围**，状态图与覆盖均不纳入。

### Step 3.6 — 阶段验收

进入 Step 4 前必须满足（实测均已达成）：

- [x] `design_suite` 产生 html + xml + txt（**96 passed**）
- [x] Module A 被测代码 `simulator.py` 语句 ≥80%、分支 ≥70% —— 实测 **95.8% / 89.0%**
- [x] **REQ-012 卡死稳定复现**：响应 `active_dtcs` 含 `DTC_001` 且 `actual_duration = 41s`（> stuck_est_time×2 = 40s）
- [x] All-Transitions 覆盖率 = T1~T5 全 ≥1 → **100%**

---

## 4. 第 3 周：Test Result Analysis — 缺陷分析 + 改进证据（1 天）

### Step 4.1 — 汇总通过率（Artifact 4 §10.1 / §10.2）

从 `design_suite.xml`（JUnit）按技术统计（仅 Module A 96 条）：

| 技术 | Total | Passed | Failed | Pass Rate |
|---|---|---|---|---|
| EP | 27 | 27 | 0 | 100% |
| BVA | 33 | 33 | 0 | 100% |
| DT | 13 | 13 | 0 | 100% |
| ST | 18 | 18 | 0 | 100% |
| SC | 5 | 5 | 0 | 100% |
| **合计** | **96** | **96** | **0** | **100%** |

> 集成测试 `integration_http` 11/11 通过（API 端到端）。
> 完整汇总（按技术 / 按需求+RPN / 正负向构成）见 `docs/test_evidence/pass_rate_summary.md`，数字由脚本从 `execution_details.json` 重算。

**通过率门槛**（仅 Module A 需求，REQ-001~014）：
- RPN ≤ 5（High，对应 REQ-001/003/008~012）→ **100% 必过** —— 实测 **47/47 = 100%**
- RPN 6~10（Medium，REQ-002/004/005/006/007/013/014）→ ≥ 95% —— 实测 **49/49 = 100%**

**通过 ≠ 仿真器全 success**：96 条里 **47 条负向**（预期 VCU 报错/拒绝/卡死/维持，含 46 条 result_type=error + 1 条卡死 state10），**49 条正向**（期望成功唤醒→11 / 休眠→9）。负向用例通过 = 确认 VCU 正确报错/暴露缺陷。若有用例失败且非 oracle 缺陷，则 §10.3 写缺陷报告（不硬改用例）。本轮 oracle 缺陷均已在 REV-016 执行期审查修正。

### Step 4.2 — REQ-012 卡死缺陷专项报告（核心证据，必须写）

**这是本 Artifact 4 最重要的“发现真实缺陷”证据**。已落到 `docs/test_evidence/defect_DEF-001_state10_stuck.md`，按课件 `Chap5Congfig Anatomy of a Perfect Bug Report.docx`「完美缺陷报告」**三阶段法**组织：
- **Phase 1 Investigation**：用 REQ-012 的 6 条用例做**双维度边界隔离**——次数边界（2 不触发 / 3、4 触发 → 阈值=3）+ 间隔边界（0.5/0.9s 触发 / **1.0s 边界不触发** / 1.1s 不触发 → 阈值 <1.0s）；Reproduce / Isolate / Generalize / Compare 齐全。
- **Phase 2 Synthesis**：技术摘要 + 整车/客户影响。
- **Phase 3 Polish**：下方结构化字段（Identifier / Severity / Steps / Expected / Actual / Root Cause / Impact）。

核心字段（Actual 取自 `execution_details.json`）：

```
Defect ID: DEF-001
Title: state10 卡死 — 快速 3 次唤醒-休眠循环复现

Severity: Critical
Priority: P0
Source: REQ-012（已知缺陷，来自客户需求文档 0319.pdf）
Linked Test: tests/test_suite_from_design.py 中 REQ-012 的 SC/ST 卡死用例（6 条，含
             "连续3次快速唤醒休眠循环触发卡死"）

Steps to Reproduce（适配器 _run 对 REQ-012 的执行序列）:
  1. sim.reset() → VCU 回 state09
  2. 循环 3 次（相邻间隔 < 1s）：
       simulate(supply_voltage=9.3, duration_ms=15)              → 唤醒到 state11
       simulate(VCUO_bDIAG_VCUIdle_flg=1, AuthComplete_flg=1, can_stopped=True) → 休眠（快速）
  3. 第 4 次 simulate(supply_voltage=9.3, duration_ms=15) → 触发卡死

Expected（按设计应当）: 不卡死，正常进入 state11
Actual（实测，缺陷复现）:
          vehicle_state = 10（卡死，STATE_INIT）
          result_type   = "error"
          active_dtcs    = ["DTC_001"]
          actual_duration = 41s（= stuck_est_time × 2 + 1，> 40s）

Evidence: docs/test_evidence/pytest_output/design_suite.txt
          docs/test_evidence/pytest_output/execution_details.json（REQ-012 各条 VCU 实际输出）
```

### Step 4.3 — Coverage 分析（Artifact 4 §11）

填三张表：

三张表已落到 `docs/test_evidence/coverage_tables.md`（数字由脚本重算）：

**11.1 Requirement Coverage**（14/14 需求全覆盖，96 条全 PASS）：

| REQ | 技术 | 用例数 | Result | Status |
|---|---|---|---|---|
| REQ-001~007（7 路唤醒）| EP+BVA+ST | **57** | 全 PASS | Covered |
| REQ-008~011（休眠条件）| EP+BVA+DT+ST | 24 | 全 PASS | Covered |
| REQ-012（卡死缺陷）| SC+ST | 6 | 复现 stuck（state10+DTC_001）| Covered（**DEF-001 已确认**）|
| REQ-013（输出一致性）| EP+DT+ST | **4** | 全 PASS | Covered |
| REQ-014（时序合规）| BVA | **5** | actual_duration 正常；违规由卡死 41s 体现 | Covered |

**11.2 Coverage Item Coverage**：22 个 Module A Coverage Item（`coverage_items.json`），按 (需求+技术) 映射 **22/22 全覆盖**，技术 EP/BVA/DT/ST/SC 五种齐全（黑盒 EP/BVA/DT/SC + 白盒 ST）。
> 追溯小缺口（已披露）：1 个 CI 在 v3 regenerate 丢失 UUID 链但功能仍被 REQ-012 卡死用例覆盖；16 条用例 CI 字段为占位串。不影响覆盖结论，列为流程改进项。

**11.3 Branch Coverage（Module A 被测代码 simulator.py）**：语句 **95.8%** / 分支 **89.0%**（剔除非-Module-A 行后；见 `coverage_analysis.md`）。

### Step 4.4 — Improvement with Evidence（评分硬性要求，分两类）

> **概念区分**（来自 Assignment 2 原文 "Mainly" 段）：
> - **设计期改进（Design-time）= 主线**：原文 "results analysis (**mapping of designed test cases** to Coverage Item Identification and Strategy)" 后接 "improvement with evidence"，明确指人工审查 AutoTestDesign 工具初版 → 发现遗漏 → 补回 Coverage Items 和用例的过程。这是 Assignment 2 强调的 "designer's participation and interactive validation of effectiveness"。
> - **执行期改进（Execution-driven）= 加分**：第 3 节 pytest 跑完后从真实失败 / 边界发现 / 执行反馈触发的改进。对应 In-depth Analysis (20%) 评分项和 PROJECT_PLAN_V2 §3.9 两轮反馈机制（工具内由 `/api/improve` 的 LLM 第二轮用例增广实现；非 fuzz，Assignment 2 无 fuzz FR）。

**Artifact 4 §12 必须分两段写，缺一不可**。完整汇总（含量化 Before/After + REV/TOOL-FIX 索引 + §C 汇总结论）已落到 `docs/test_evidence/improvement_evidence.md`。

#### 4.4a — Design-time Improvement（必选，从 `review_log.md` 来）

从 `review_log.md` Phase 1~5 的设计期 REV 统计（对照课件审查工具初版）：

| Metric | Before（工具初版 v1，94 条）| After（设计期审查后）| Improvement |
|---|---|---|---|
| 引用 VCU 不存在字段的用例（Untestable）| 21 | 0 | 全部消除 |
| oracle 字段是否限于 VCU 真实输出 | 否 | 是（白名单约束）| 工具级修复 |
| BVA 无效等价类（invalid-too-low）| 缺 | 补齐 8.9V | +1 |
| 测试技术覆盖 | 偏单一 | EP/BVA/DT/ST/SC 五种 | 黑盒+白盒齐全 |

举例（具体 REV，详见 review_log）：
- **REV-014**：工具初版 BVA 漏 invalid-too-low（只有 9.0/9.1）→ 人工补 8.9V→state9 用例（参考 Chp4Part1 P35-40）
- **REV-015**：工具把 oracle 字段写成 VCU 不返回的 `is_compliant`/`sleep_sub_condition_*`（Untestable）→ 改 testcase prompt 加字段白名单 + regenerate → 臆造字段 21→0
- **REV-012/013**：REQ-014 `is_compliant`→`actual_duration`、REQ-012 反转的 stuck oracle 修正

#### 4.4b — Execution-driven Improvement（加分，从 pytest 执行结果来）

把 96 条做成数据驱动 pytest 真正执行后，暴露了设计期审查没抓到的缺陷（来源 `design_suite.txt` + `coverage_analysis.md` + `review_log.md` Phase 6）：

| Evidence ID | 执行期发现 | 触发的改进 |
|---|---|---|
| EXE-001 | 首次执行 96 条仅 **48/96 通过**——失败的 48 条是 LLM 系统性 oracle 取值错误（vehicle_state=0 幻觉、维持态写 10、no-wake 写 expected、卡死写 stuck）| **TOOL-FIX-007**：testcase prompt 加“VCU 输出取值语义”→ regenerate → **48/96→80/99**（一次工具修复，非手工补 48 条）|
| EXE-002 | 诊断剩余失败，发现 13 条是**测试脚本 harness bug**（休眠测试需先唤醒 state11 再施加条件），非设计缺陷 | 修适配器（先唤醒前置）→ **80/99→92/99**；正确区分工具/脚本/用例三类问题 |
| EXE-003 | 7 条残留为真·设计缺陷（REQ-013 输出当输入、REQ-010 标题/输入矛盾、REQ-014 超时不可复现）| **REV-016**：改 3 删 4 加 1 → **92→96/96** |

> **本节即 PROJECT_PLAN_V2 §3.9 “两轮反馈机制” 的体现**：设计 96 → 执行暴露缺陷 → 改进（prompt/适配器/用例）→ 重执行通过。Artifact 4 §12.2 明确引用此机制。关键诚实点：根因优先（改工具 prompt 一次顶 48 次手工补丁）、三类问题分清（工具/脚本/用例）。

#### 4.4c — 汇总结论（≥ 300 字）

写一段总结，要点：
1. Design-time 改进了 N 个 Coverage Items、M 条用例（人工补足了工具看不到的领域知识，如时序、CAN ID 范围、DTC 联动）；
2. Execution-driven 改进了 X 个 Coverage Items、Y 条用例（执行后的真实证据驱动，体现执行反馈闭环）；
3. 两类改进合计使**执行通过率从首次 48/96（50%）提升到 96/96（100%）**、臆造字段从 21 条降到 0、Module A 分支覆盖达 89.0%；
4. 证明"工具初版 + 人工审查 + 真实执行"三方协同优于任一单方（设计期审查抓不到 oracle-vs-SUT 偏差，只有执行能；根因在 prompt 则改工具一次顶手工补几十条）。

### Step 4.5 — Performance NFR 度量（Project Requirement Specification §4.1）

数据来源：工具 `/api/performance`（Results 页底部 LLM 调用性能日志，model=qwen3.7-max 百炼云端）。

| NFR（工具）| 规格 | 实测 | 满足？|
|---|---|---|---|
| 单需求用例生成（NFR 4.1.2）| ≤ 2s | `testcase.generate` 约 **60~113s/需求** | ❌ 严重超标 |
| 风险分析 | — | `risk.analyze` 约 **75s/批** | — |
| **被测系统 REQ-014**：actual_duration（type1）| ≤ 20s | 正常 **14.7s** ≤ 20 ✓；卡死时 **41s**（缺陷）| ✓（正常路径）|

**NFR 4.1.2 严重不达标**（云端 qwen3.7-max + reasoning 导致每需求数十秒 vs 目标 2s）。按 Assignment 2 §5（不可隐瞒），在 Artifact 4 §13 写**分析 + 改进建议**：本地小模型 / 关闭 reasoning（LLM_ENABLE_THINKING=false 已部分缓解）/ 结果缓存 / 并发批量生成 / 流式输出。

---

## 5. 第 4 周：文档撰写与交付（1.5 天）

### Step 5.1 — 按 Artifact 4 大纲填空

打开 `docs/Artifact4_Detailed_Test_Design_Execution_Outline.md`，逐节把 `[TBD]`、`[INSERT ...]` 替换成 Step 1 ~ 4 产出的真实证据：

| Outline 节 | 填什么 | 数据来源 |
|---|---|---|
| §0 Cover | 团队信息 + commit hash | Step 1.2 |
| §1 Introduction | 范围 + 模块 + 接口截图 | Step 1.3、§0.2 / §0.3 |
| §2 Test Basis | REQ-001~014 表 + 来源 | Step 2.1 |
| §3 Concept & Rationale | EP/BVA/DT/ST 选择理由 | Step 2.4.2 |
| §4 Coverage Item Identification | Coverage items 表（22 项 Module A）| Step 2.3.2 |
| §5 Coverage Strategy & Method | 5 种技术的策略表 | Step 2.4.2 |
| §6 Prompt Design + Interactive Review | REV-001~016 前后对比 + 5 prompts（testcase v1→v3）| Step 2.2~2.6 |
| §7 Test Case Design | 全部用例表 + JSON 链接 | Step 2.5.3 |
| §8 Traceability Matrix | 三列追溯表 | Step 2.5.3 |
| §9 Test Tool Implementation | pytest + 脚本结构 + 命令 | Step 3.1~3.3 |
| §10 Test Execution Results | 通过率 + Failed 分析 + DEF-001 | Step 4.1~4.2 |
| §11 Coverage Analysis | 三张覆盖率表 | Step 4.3 |
| §12 Evidence-based Improvement | Before/After 对比表 | Step 4.4 |
| §13 Limitations / Residual Risks | NFR 不达标 + Out of Scope 说明 | Step 4.5 + §0.3 |
| Appendix A/B/C | Prompts + 文件列表 + 截图 | Step 1.3、2.6 |

### Step 5.2 — 自检 Checklist（按 Assignment 2 评分项）

| 评分项（10 / 20 / 40 / 20 / 10）| 自检问题 | 我们的证据 |
|---|---|---|
| Concept Understanding (10%) | EP / BVA / DT / ST / Risk-based / Traceability 概念是否准确？ | §3 + §6 + §8 |
| Coherence of Design & Implementation (20%) | 设计的用例 = 实际跑的用例？ Coverage Items 都有用例覆盖？ | §4 ↔ §7 ↔ §10 一致 |
| Coverage & Effectiveness (40%) | 多种黑盒技术 ✓ + 白盒技术 ✓ + 覆盖率指标 ✓ | EP/BVA/DT 三种黑盒 + State Transition 白盒 + Branch Coverage |
| In-depth Analysis (20%) | DEF-001 缺陷分析 + Before/After + NFR 分析 | §10.3 + §12 + §13 |
| Presentation (10%) | 排版 / 截图清晰 / 引用规范 | 全文 |

### Step 5.3 — 交付清单（最终上交给文档同学）

把以下文件打包发给文档同学：

```
docs/
  Artifact4_Detailed_Test_Design_Execution_Outline.md  ← 填好的 Artifact 4 主文档
  test_evidence/
    env_baseline.txt
    module_A_requirements_input.txt
    review_log.md
    prompts_used.md
    state_transition_table.md
    defect_DEF-001_state10_stuck.md
    01_parsed_requirements_raw.json
    02_parsed_requirements_reviewed.json
    03_coverage_items_raw.json
    04_coverage_items_reviewed.json
    05_risk_analysis_raw.csv
    06_risk_analysis_reviewed.csv
    07_strategy_assignment.csv
    08_test_cases_raw.json
    09_test_cases_reviewed.{json,csv,xlsx}
    10_traceability_matrix.csv
    pytest_output/
      suite_{a,b,c,d,e}.{txt,xml,html}
      integration_http.txt
      coverage_report.txt
      coverage.xml
      coverage_html/
    screenshots/
      01 ~ 15_*.png（≥ 15 张）
```

---

## 6. 时间与成本估算（写进 Test Plan §Cost Estimation，本计划同步给文档同学）

| 阶段 | 工时（人时）| 关键交付 |
|---|---|---|
| Step 1 环境准备 | 4h | 三服务运行 + 环境基线 |
| Step 2 Interactive Review（7 步走完）| 18h | 25+ 证据文件（全版本链）+ REV-001~016 + 8 个 TOOL-FIX |
| Step 3 pytest 执行 + 覆盖率 | 10h | 5 套 Suite 报告 + coverage_html |
| Step 4 结果分析 + 缺陷报告 | 6h | DEF-001 + Improvement 对比 |
| Step 5 文档撰写 | 12h | Artifact 4 完整版 |
| **合计** | **50h ≈ 6.25 人天** | |

**对照纯人工测试**：手工设计 96 条用例 + 人工执行 + 人工写 oracle ≈ 120h；**AutoTestDesign 节省 ≈ 58%**（写进 Test Plan §Cost Estimation）。

---

## 7. 风险与应急

| 风险 | 触发条件 | 应急方案 |
|---|---|---|
| Anthropic API 不稳定 | Step 2 任一调用超时 | 切换到本地 mock LLM（参考 PROJECT_PLAN_V2 §STP-5.2 LLMStub）+ 在 §13 说明 |
| REQ-012 卡死复现不稳定 | 快速循环间隔 ≥1s 时不触发 stuck | 适配器用 `time.sleep(interval)` 精确控制循环间隔（<1s 触发、≥1s 不触发），保证稳定复现 |
| Branch Coverage < 75% | Step 3.4 报告显示 | 补 1~2 条用例覆盖未触达分支（不要为凑数造假；如确不可达，在 §11.3 标 `# pragma: no cover` 并解释）|
| NFR 2s 不达标 | Step 4.5 度量 > 2s | 不要造假，按 Assignment 2 §5 要求写改进建议（本地 LLM / 缓存 / 流式）|

---

## 8. 与其它三个交付物的边界（避免重复工作）

| 交付物 | 谁负责 | 与本 Artifact 4 的关系 |
|---|---|---|
| Artifact 1 Tool (20%) | 工具开发同学 | 本 Artifact 4 **使用** 该工具，不评价工具本身 |
| Artifact 2 Risk Analysis Report (10%) | 风险分析同学 | 本 Artifact 4 **复用** §5.1 风险表，不重写 |
| Artifact 3 Test Plan (40%) | 测试计划同学 | 本 Artifact 4 是 Test Plan 中 **Module A** 部分的**详细展开**，**不要重复**写 IEEE 829 全骨架，只引用 |
| **Artifact 4（本文）** | **我（测试同学）** | 专注 Module A 一个模块的设计 + 执行 + 结果分析 |

> **关键原则**：Assignment 2 §5 明确 “Risk Analysis Report、Test Plan、Detailed Test Design and Execution Document 都是测 target application，不是测 tool”。本 Artifact 4 全文不讨论 AutoTestDesign 工具的缺陷，只把它当作生产用例的“流水线”。

---

## 附录 A：现有代码与本计划的映射

| 现有文件 | 在本计划中的角色 |
|---|---|
| `vcu_simulator/simulator.py` | **Module A 被测系统（SUT）**，覆盖率只算它，不修改 |
| `vcu_simulator/modules/*.py` | 共享基础设施（含 B/C/D/E 故障逻辑）；Module A 仅经 `dtc_manager` 记录卡死 DTC_001。**不计入 Module A 覆盖率** |
| `tests/test_suite_from_design.py` | **唯一测试套件**：数据驱动执行 96 条设计用例（含输入适配器、IEEE 829 生命周期、RPN 排序）。旧的 test_suite_a~e.py 已删除 |
| `tests/test_integration_http.py` | API 层端到端冒烟（11 条），Step 3.3 跑一遍 |
| `backend/api/services/pytest_runner.py` | 把前端「执行全部」接到上面的 pytest（TOOL-FIX-008）|
| `backend/` | AutoTestDesign 后端，Step 2 调它的 API |
| `docs/PROJECT_PLAN_V2.md` | 唯一需求基线来源 |
| `docs/Artifact4_Detailed_Test_Design_Execution_Outline.md` | Step 5 要填的目标文档 |
| `docs/Requests_to_Testing_Teammate_for_Artifact4.md` | Step 1~4 收集证据的清单依据 |

---

## 附录 B：评分项映射（自检用）

| Assignment 2 评分维度 | 本计划落点 |
|---|---|
| Test Case Design — multiple black-box (≥3) | Step 2.4.2 + Step 2.5：EP + BVA + Decision Table 三种 |
| Test Case Design — white-box | Step 2.4.2 + Step 3.5：State Transition + Branch Coverage |
| Test Case Design — using AutoTestDesign tool | Step 2 全程 |
| Test Case Design — interactive review | Step 2.2 / 2.3 / 2.5 各 ≥ 3 条 REV |
| Test Tool Implementation — framework rationale | Step 3.1 |
| Test Tool Implementation — scripts based on test cases | Step 3.2~3.3 |
| Test Result Analysis — summary | Step 4.1 |
| Test Result Analysis — defect / improvement | Step 4.2 + 4.4 |
| FR 1.0 / 1.1 / 2.0 / 3.0 / 6.0 + Interactive Review（必须项）| 全在 Step 2 |
| FR 4.0 / 5.0 / 7.0（加分项）| Step 3.5（FR 4.0 白盒模型）+ Step 2.5 oracle 字段（FR 5.0）+ **FR 7.0 = Optimize 页（风险优先级排序 + 覆盖最小化 96→65），见 `fr7_optimization.md`** |
| NFR Performance ≤ 2s | Step 4.5 |
| NFR Usability / Security / Maintainability | Step 5.1 §13 简述 |

---

**End of Step-by-Step Plan**

> 跑完本计划，预计产出：**1 份正式 Artifact 4 文档（PDF）+ 25+ 个证据文件（JSON/CSV/XML/HTML/MD/PNG）+ 96 条可执行用例（仅 Module A，96/96 通过）**，足以支撑 30% 权重 × Quality Score ≥ 85 的评分预期。
