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

- [ ] `curl http://localhost:8001/state` 返回 `200` 且 `vehicle_state == 9`
- [ ] `curl http://localhost:8000/api/health` 返回 `200`
- [ ] AutoTestDesign 前端能加载 VCU Demo（点击 “Load Demo” 后看到 24 条需求列表）
- [ ] 上述 4 张截图全部存在

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

**期望产出数量**（用来校验工具有没有偷工减料）：

| Suite | 技术 | 期望用例数 | 对应文件 |
|---|---|---|---|
| Suite A | EP | 21（7 信号 × 3 类） | 与 `tests/test_suite_a_ep.py` 现有 21 条对齐 |
| Suite B | BVA | 24（含 Module B 边界，本 Artifact 取其中 18 条仅 Module A 部分） | `tests/test_suite_b_bva.py` |
| Suite C | Decision Table | 8（2³ 全枚举） | `tests/test_suite_c_decision_table.py` |
| Suite D | State Transition | 15（All-Transitions） | `tests/test_suite_d_state_transition.py` |
| Suite E | Scenario + Sequence | 10（卡死复现专项） | `tests/test_suite_e_stuck.py` |
| **合计（本 Artifact 范围）** | | **≈ 72 条** | |

#### 2.5.2 人工编辑用例（**关键的 Interactive Review 证据**）

至少修订 **3 条**（凑齐总共 ≥ 5 组前后对比）：

| Review ID | 修订内容 | 原因 |
|---|---|---|
| REV-006 | 给 BVA `supply_voltage=9.0V` 用例补一行：value=9.0001 用以验证“> 9V”严格大于 | LLM 偶尔生成 `value=9.0` 写成 “边界 on”，但 REQ-001 是严格大于 9 |
| REV-007 | Decision Table 第 8 行（h1 ∧ h2 ∧ ¬h3）期望从 `state09` 改为 `state11`（维持） | LLM 容易把“任一不满足”都写成 state09 |
| REV-008 | Suite E 的卡死用例补 oracle：`active_dtcs` 必须包含 `DTC_001` | LLM 没识别出 Module D 联动 |

#### 2.5.3 导出最终用例集（FR 6.0）

- `08_test_cases_raw.json`（工具初版，**bq_new 格式**，type=1/2，含 in_data / expected_results / error / est_time）
- `09_test_cases_reviewed.json`（人工修订后）
- `09_test_cases_reviewed.csv`、`09_test_cases_reviewed.xlsx`（同内容三种格式，应付 FR 6.0 三种导出）
- `10_traceability_matrix.csv`（REQ ↔ Coverage Item ↔ Test Case 三列对应表）

### Step 2.6 — Interactive Review · 第 5 步【Prompt Design】（评分项要求）

把工具用的三个 prompt 完整粘贴到 `docs/test_evidence/prompts_used.md`（不能只写“见代码”）：

1. `requirement_parser` 的 system prompt（来自 `backend/services/llm/...`）
2. `risk_analyzer` 的 system prompt
3. `testcase_generator` 的 system prompt（每种技术单独写）

每个 prompt 配一段 5-10 行的“输入 → 输出”样例，体现“prompt 决定输出质量”。

### Step 2.7 — 阶段验收（Tollgate 准则，参照 STP-7.2.1）

进入 Step 3 前必须全部满足：

- [ ] `docs/test_evidence/` 下产出文件 ≥ 10 个（含 raw / reviewed 两套）
- [ ] `review_log.md` 至少 5 条 Before/After 记录
- [ ] 总用例数 ≈ 72 条（误差 ±10%）
- [ ] 每条用例都有 `requirement_id` + `coverage_item_id` + `technique` 三个字段
- [ ] `prompts_used.md` 三类 prompt 齐全

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

### Step 3.2 — 把 AutoTestDesign 生成的 JSON 用例转成 pytest（脚本对照已有 `tests/test_suite_*.py`）

现有的 5 个测试文件（已经按 Suite A~E 写好骨架）就是最终交付脚本，**不要重写，做以下两件事**：

1. **核对一致性**：拿 Step 2.5.3 的 `09_test_cases_reviewed.json` 和 `tests/test_suite_a_ep.py` 等逐条比对，确保 input/expected 一致；若有差异，**以 reviewed JSON 为准**修脚本。
2. **加追溯注释**：每个 test 方法的 docstring 第一行加 `TC-A-001 | I-W1-1 | REQ-001`（Test Case ID | Coverage Item ID | Requirement ID）三联追溯。现有 `test_suite_a_ep.py` 已有这种格式，按它扩到 B/C/D/E。

### Step 3.3 — 分 Suite 执行并保留原始证据

```bash
mkdir -p docs/test_evidence/pytest_output

# Suite A — EP（21条）
pytest tests/test_suite_a_ep.py -v \
  --html=docs/test_evidence/pytest_output/suite_a_report.html --self-contained-html \
  --junitxml=docs/test_evidence/pytest_output/suite_a.xml \
  | tee docs/test_evidence/pytest_output/suite_a.txt

# Suite B — BVA
pytest tests/test_suite_b_bva.py -v \
  --html=docs/test_evidence/pytest_output/suite_b_report.html --self-contained-html \
  --junitxml=docs/test_evidence/pytest_output/suite_b.xml \
  | tee docs/test_evidence/pytest_output/suite_b.txt

# Suite C — Decision Table
pytest tests/test_suite_c_decision_table.py -v \
  --html=docs/test_evidence/pytest_output/suite_c_report.html --self-contained-html \
  --junitxml=docs/test_evidence/pytest_output/suite_c.xml \
  | tee docs/test_evidence/pytest_output/suite_c.txt

# Suite D — State Transition（白盒）
pytest tests/test_suite_d_state_transition.py -v \
  --html=docs/test_evidence/pytest_output/suite_d_report.html --self-contained-html \
  --junitxml=docs/test_evidence/pytest_output/suite_d.xml \
  | tee docs/test_evidence/pytest_output/suite_d.txt

# Suite E — Stuck Defect 复现（重点！需要稳定复现 REQ-012）
pytest tests/test_suite_e_stuck.py -v \
  --html=docs/test_evidence/pytest_output/suite_e_report.html --self-contained-html \
  --junitxml=docs/test_evidence/pytest_output/suite_e.xml \
  | tee docs/test_evidence/pytest_output/suite_e.txt

# HTTP 集成（端到端验证 API 层）
pytest tests/test_integration_http.py -v \
  | tee docs/test_evidence/pytest_output/integration_http.txt
```

**每个 Suite 执行后立即截图**：`12_pytest_suite_{a,b,c,d,e}.png`。

### Step 3.4 — 收集代码覆盖率（白盒证据，FR 4.0 加分）

```bash
# 全 Suite 一次性跑，开启 branch coverage
coverage run --branch --source=vcu_simulator -m pytest tests/test_suite_a_ep.py tests/test_suite_b_bva.py tests/test_suite_c_decision_table.py tests/test_suite_d_state_transition.py tests/test_suite_e_stuck.py

coverage report -m | tee docs/test_evidence/pytest_output/coverage_report.txt
coverage html -d docs/test_evidence/pytest_output/coverage_html
coverage xml -o docs/test_evidence/pytest_output/coverage.xml
```

截图：`13_coverage_terminal.png` + `14_coverage_html.png`。

**关键覆盖率指标**（写进 Artifact 4 §11.3）：

| 文件 | 期望 Statement | 期望 Branch | 备注 |
|---|---|---|---|
| `vcu_simulator/simulator.py` | ≥ 85% | ≥ 75% | 核心状态机 |
| `vcu_simulator/modules/signal_guard.py` | ≥ 90% | ≥ 85% | 三个 if 分支必须全覆盖 |
| `vcu_simulator/modules/dtc_manager.py` | ≥ 80% | ≥ 70% | DTC_001 路径必须覆盖 |

### Step 3.5 — 白盒补充：手画 State Transition 表 + 验证 All-Transitions

把 PROJECT_PLAN_V2 §2.1 状态图整理成 `docs/test_evidence/state_transition_table.md`：

| Transition ID | From | Event | To | Covered By Test |
|---|---|---|---|---|
| T1 | state09 | w1~w7 任一有效 + Module B 通过 | state10 → state11 | TC-A-001 (Suite A) |
| T2 | state09 | 信号无效 | state09（维持） | TC-A-002 (Suite A) |
| T3 | state11 | h1 ∧ h2 ∧ h3 | state09 | TC-C-008 (Suite C) |
| T4 | state11 | 任一 h 不满足 | state11（维持） | TC-C-001~007 (Suite C) |
| T5 | state10 | 快速 3 次循环 | state10（stuck） | TC-E-001~010 (Suite E) |
| T6 | * | 供电 > 16V | fault_protection | TC-F-* (Module B) |
| T7 | * | 供电 < 6V | undervoltage_shutdown | TC-F-* (Module B) |

**Coverage Criterion = All-Transitions**：上表 T1 ~ T5 全部至少有 1 条用例 → 100% All-Transitions 达成（T6/T7 属 Module B，本 Artifact 不展开但要在文档里说明已在 Test Plan 全量覆盖）。

### Step 3.6 — 阶段验收

进入 Step 4 前必须满足：

- [ ] 5 个 Suite 全部产生 `.html` + `.xml` + `.txt` 三套报告
- [ ] `coverage_report.txt` 中 `simulator.py` Statement Coverage ≥ 85%
- [ ] **Suite E 至少 1 条 stuck 用例稳定复现**：响应中 `active_dtcs` 包含 `DTC_001` 且 `actual_duration > 40s`
- [ ] All-Transitions 覆盖率 = T1 ~ T5 全 ≥ 1 → 100%

---

## 4. 第 3 周：Test Result Analysis — 缺陷分析 + 改进证据（1 天）

### Step 4.1 — 汇总通过率（Artifact 4 §10.1 / §10.2）

写脚本 `docs/test_evidence/summarize.py`（或手工填表）从 5 个 JUnit XML 解析出：

| Suite | Technique | Total | Passed | Failed | Skipped | Pass Rate |
|---|---|---|---|---|---|---|
| A | EP | 21 | ? | ? | ? | ?% |
| B | BVA | 24 | ? | ? | ? | ?% |
| C | Decision Table | 8 | ? | ? | ? | ?% |
| D | State Transition | 15 | ? | ? | ? | ?% |
| E | Scenario+Sequence | 10 | ? | ? | ? | ?% |
| **合计** | | **78** | | | | |

**通过率门槛**（来自 PROJECT_PLAN_V2 §STP-6.3）：
- RPN ≤ 5（High，对应 REQ-001~007, 011, 012, 015, 016）→ **100% 必过**
- RPN 6~10（Medium）→ ≥ 95%
- Cursory（Low）→ ≥ 80%

若达不到，**不要硬改用例**，要在 §10.3 写缺陷报告并继续。

### Step 4.2 — REQ-012 卡死缺陷专项报告（核心证据，必须写）

**这是本 Artifact 4 最重要的“发现真实缺陷”证据**，按缺陷管理决策树（STP-6.1）整理：

落到 `docs/test_evidence/defect_DEF-001_state10_stuck.md`：

```
Defect ID: DEF-001
Title: state10 卡死 — 快速 3 次唤醒-休眠循环复现

Severity: Critical
Priority: P0
Source: REQ-012（已知缺陷，来自北汽需求文档 0319.pdf）
Linked Test: TC-E-001 ~ TC-E-010 (tests/test_suite_e_stuck.py)

Steps to Reproduce:
  1. POST /reset，VCU 回 state09
  2. 循环 3 次：POST /simulate {supply_voltage: 9.3, duration_ms: 15} → 唤醒到 state11
                POST /simulate {h1: 1, h2: 1, h3: 0} → 模拟快速休眠请求
                间隔 < 1s
  3. GET /state 观察是否卡在 state10
  4. GET /dtc 查询 DTC_001 是否被写入

Expected: state10 不应卡死，应该完成初始化进入 state11
Actual:   actual_duration = 41s（> stuck_est_time × 2 = 40s）
          vehicle_state = 10（卡死）
          active_dtcs = ["DTC_001"]
          power_current = 0.25A（异常高）

Evidence: docs/test_evidence/pytest_output/suite_e.txt
          docs/test_evidence/screenshots/15_def001_dtc_response.png
```

### Step 4.3 — Coverage 分析（Artifact 4 §11）

填三张表：

**11.1 Requirement Coverage**

| REQ | Covered by | Result | Status |
|---|---|---|---|
| REQ-001 | TC-A-001~003, TC-B-001~003 | 6/6 PASS | Covered |
| REQ-002 | TC-A-004~006, TC-B-004~006 | 6/6 PASS | Covered |
| ... |  |  |  |
| REQ-012 | TC-E-001~010 | 10/10 复现 stuck | Covered（**缺陷已确认**）|
| REQ-014 | TC-J-001~010（性能） | actual_duration 全 ≤ 20s（正常路径）| Covered |

**11.2 Coverage Item Coverage**：每类应达 100%（EP 21/21、BVA 18/18、DT 8/8、ST 5/5、Oracle 6/6）。

**11.3 Branch Coverage**：从 Step 3.4 的 `coverage_report.txt` 抄进来。

### Step 4.4 — Improvement with Evidence（评分硬性要求，分两类）

> **概念区分**（来自 Assignment 2 原文 "Mainly" 段）：
> - **设计期改进（Design-time）= 主线**：原文 "results analysis (**mapping of designed test cases** to Coverage Item Identification and Strategy)" 后接 "improvement with evidence"，明确指人工审查 AutoTestDesign 工具初版 → 发现遗漏 → 补回 Coverage Items 和用例的过程。这是 Assignment 2 强调的 "designer's participation and interactive validation of effectiveness"。
> - **执行期改进（Execution-driven）= 加分**：第 3 节 pytest 跑完后从真实失败 / 边界发现 / Fuzz 新状态触发的改进。对应 In-depth Analysis (20%) 评分项和 PROJECT_PLAN_V2 §3.9 两轮模糊测试机制。

**Artifact 4 §12 必须分两段写，缺一不可**。

#### 4.4a — Design-time Improvement（必选，从 `review_log.md` 来）

从 Step 2 的 5 条 REV 修订统计：

| Metric | Before Review（工具初版）| After Review（人工修订后）| Improvement |
|---|---|---|---|
| Coverage Items 数 | ? | ? | +N |
| Test Cases 数 | ? | ? | +N |
| 漏掉的时序条件数 | ? | 0 | 全部修复 |
| Oracle 字段覆盖（5 字段）| ? | 5/5 | 全覆盖 |
| 高风险需求（RPN ≤ 2）用例数 | ? | ? | +N |

举例（必须列具体的 REV）：
- **REV-001**：工具初版漏掉 REQ-006 的时序条件 `duration ≥ 10ms` → 人工补回 → 新增 Coverage Item `CI-W6-Timing` + 新增 BVA 用例 `TC-B-006a`（hood_voltage=4.5V, duration=8ms）
- **REV-002**：工具把 REQ-002 的 `can_msg_id` 范围识别为 `[0, 2047]` → 人工改为 `[0x400, 0x47F]` → 改写 3 条 EP 用例的输入值
- **REV-008**：工具没识别 Module D 联动 → 人工给 Suite E 卡死用例补 oracle `active_dtcs 必须包含 DTC_001` → 新增 1 个 Output Coverage Item `O-DTC-1`

#### 4.4b — Execution-driven Improvement（加分，从 pytest 执行结果来）

跑完 Step 3 的 5 个 Suite 后，把"执行才发现的不足"也总结成改进。来源是 `pytest_output/*.txt` + Step 4.2 的缺陷分析：

| Evidence ID | 执行期发现 | 触发新增内容 |
|---|---|---|
| EXE-001 | 跑 Suite A 时发现工具生成的 BVA `value=9.0` 用例无法区分"严格大于 9"还是"等于 9"（VCU 实际拒绝 9.0）| 新增 `TC-B-001a value=9.0001` 用例 + 新增 Coverage Item `CI-W1-StrictGT-9` |
| EXE-002 | Suite E 第一轮 10 条用例只复现 8/10 stuck，2 条因 `duration_ms=15` 太长导致循环间隔 > 1s | 第二轮变异 `duration_ms ∈ {5, 8, 10, 12, 15}` × 5 条，找到 100% 复现的配方 → 新增 5 条 Sequence 用例 |
| EXE-003 | Suite C 跑完发现工具的 Decision Table 第 8 行 expected 写错（h1∧h2∧¬h3 应维持 state11 而非 state09）| 修正 1 条用例（在 §10.3 Failed Test Analysis 也要写） |
| EXE-004 | Coverage HTML 报告显示 `simulator.py` 第 N 行的 `else` 分支（fault_protection 路径）未覆盖 | 新增 1 条用例 `TC-A-022 supply_voltage=17V` 触达该分支 |

> **本节正是 PROJECT_PLAN_V2 §3.9 "两轮模糊测试反馈机制" 的体现**：第一轮初始用例集 → 执行 → 发现 new_state/stuck → 第二轮针对性变异。Artifact 4 §12.2 要明确引用这个机制名称。

#### 4.4c — 汇总结论（≥ 300 字）

写一段总结，要点：
1. Design-time 改进了 N 个 Coverage Items、M 条用例（人工补足了工具看不到的领域知识，如时序、CAN ID 范围、DTC 联动）；
2. Execution-driven 改进了 X 个 Coverage Items、Y 条用例（执行后的真实证据驱动，体现 fuzz 反馈闭环）；
3. 两类改进合计使最终 Coverage Item Coverage 从初版 ?% 提升到 ?%、Branch Coverage 从 ?% 提升到 ?%；
4. 证明"工具初版 + 人工 + 执行"三方协同优于任一单方。

### Step 4.5 — Performance NFR 度量（Project Requirement Specification §4.1）

| NFR | 规格 | 实测方法 | 实测值 | 满足？|
|---|---|---|---|---|
| NFR 4.1.1 | 100 条需求批量分析 ≤ 5s | `time` Step 2.4.1 风险分析批处理 | ? s | Y/N |
| NFR 4.1.2 | 单需求用例生成 ≤ 2s | `pytest-benchmark` 度量 `POST /api/test-cases/generate` | ? s | Y/N |
| REQ-014（被测系统）| actual_duration ≤ 20s（type1）| Suite J 性能测试 | ? s | Y/N |

**若 NFR 4.1.2 ≤ 2s 不达标**：按 Assignment 2 §5（Important Clarifications）要求，在 Artifact 4 §13 写“详细分析 + 改进建议”（如：本地 LLM / 缓存 / 流式输出），不可隐瞒。

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
| §4 Coverage Item Identification | Coverage items 表（21+15+8 项）| Step 2.3.2 |
| §5 Coverage Strategy & Method | 5 种技术的策略表 | Step 2.4.2 |
| §6 Prompt Design + Interactive Review | 5 条 REV 前后对比 + prompts | Step 2.2~2.6 |
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
| Step 2 Interactive Review（7 步走完）| 18h | 10 个 raw/reviewed 证据文件 + 5 条 REV |
| Step 3 pytest 执行 + 覆盖率 | 10h | 5 套 Suite 报告 + coverage_html |
| Step 4 结果分析 + 缺陷报告 | 6h | DEF-001 + Improvement 对比 |
| Step 5 文档撰写 | 12h | Artifact 4 完整版 |
| **合计** | **50h ≈ 6.25 人天** | |

**对照纯人工测试**：手工设计 78 条用例 + 人工执行 + 人工写 oracle ≈ 120h；**AutoTestDesign 节省 ≈ 58%**（写进 Test Plan §Cost Estimation）。

---

## 7. 风险与应急

| 风险 | 触发条件 | 应急方案 |
|---|---|---|
| Anthropic API 不稳定 | Step 2 任一调用超时 | 切换到本地 mock LLM（参考 PROJECT_PLAN_V2 §STP-5.2 LLMStub）+ 在 §13 说明 |
| Suite E 卡死复现不稳定 | 10 条用例 < 8 条触发 stuck | 增加循环次数到 5 次，或调整 `stuck_est_time` 配置；保留多次执行结果对比 |
| Branch Coverage < 75% | Step 3.4 报告显示 | 补 1~2 条用例覆盖未触达分支（不要为凑数造假；如确不可达，在 §11.3 标 `# pragma: no cover` 并解释）|
| NFR 2s 不达标 | Step 4.5 度量 > 2s | 不要造假，按 Assignment 2 §5 要求写改进建议（本地 LLM / 缓存 / 流式）|

---

## 8. 与其它三个交付物的边界（避免重复工作）

| 交付物 | 谁负责 | 与本 Artifact 4 的关系 |
|---|---|---|
| Artifact 1 Tool (20%) | 工具开发同学 | 本 Artifact 4 **使用** 该工具，不评价工具本身 |
| Artifact 2 Risk Analysis Report (10%) | 风险分析同学 | 本 Artifact 4 **复用** §5.1 风险表，不重写 |
| Artifact 3 Test Plan (40%) | 测试计划同学 | 本 Artifact 4 是 Test Plan 中 Suite A~E 的**详细展开**，**不要重复**写 IEEE 829 全骨架，只引用 |
| **Artifact 4（本文）** | **我（测试同学）** | 专注 Module A 一个模块的设计 + 执行 + 结果分析 |

> **关键原则**：Assignment 2 §5 明确 “Risk Analysis Report、Test Plan、Detailed Test Design and Execution Document 都是测 target application，不是测 tool”。本 Artifact 4 全文不讨论 AutoTestDesign 工具的缺陷，只把它当作生产用例的“流水线”。

---

## 附录 A：现有代码与本计划的映射

| 现有文件 | 在本计划中的角色 |
|---|---|
| `vcu_simulator/simulator.py` | 被测系统（SUT），不修改 |
| `vcu_simulator/modules/*.py` | Module B/C/D/E 实现，本 Artifact 4 仅用 Module D 的 DTC 接口 |
| `tests/test_suite_a_ep.py` | Step 3 直接复用，加追溯注释 |
| `tests/test_suite_b_bva.py` | 同上 |
| `tests/test_suite_c_decision_table.py` | 同上 |
| `tests/test_suite_d_state_transition.py` | 同上（白盒证据来源）|
| `tests/test_suite_e_stuck.py` | 同上（DEF-001 缺陷证据来源）|
| `tests/test_integration_http.py` | API 层端到端冒烟，Step 3.3 跑一遍 |
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
| FR 4.0 / 5.0 / 7.0（加分项）| Step 3.5（FR 4.0 白盒模型）+ Step 2.5 oracle 字段（FR 5.0）|
| NFR Performance ≤ 2s | Step 4.5 |
| NFR Usability / Security / Maintainability | Step 5.1 §13 简述 |

---

**End of Step-by-Step Plan**

> 跑完本计划，预计产出：**1 份正式 Artifact 4 文档（PDF）+ 22 个证据文件（JSON/CSV/XML/HTML/PNG）+ 78 条可执行用例**，足以支撑 30% 权重 × Quality Score ≥ 85 的评分预期。
