# Interactive Review Log — AutoTestDesign Tool 人工审查记录

> **文档定位**：Artifact 4 §6（Prompt Design + Interactive Review）的核心证据来源。
> 记录每条由 LLM 生成的 raw 内容（Coverage Items / Test Cases / Risk）与人工修订后的 reviewed 内容的 **Before / After + Why**。
>
> **更新规则**：每发起一次修订，追加一条记录；REV-ID 全局递增；保留 raw 文件路径 + reviewed 文件路径 + 截图路径，三件证据缺一不可。

---

## Phase 1 — Requirements Parsing 审查（FR 1.1）

**输入**：`docs/test_evidence/module_A_requirements_input.txt`（14 条 Module A 需求）
**LLM 原始输出**：`docs/test_evidence/01_parsed_requirements_raw.json`（80.6s, qwen3.7-max via DashScope）

### 通读发现的 6 处 LLM 错误 / 遗漏

下表给出每处问题的 **REQ-ID / 字段路径 / LLM 现状 / 应改成什么 / 依据**。人工 tester 从中至少选 3 条做 Before/After 编辑（其它放到 Coverage Item / Test Case 审查阶段补足，凑到 ≥ 5 条总数）。

| REV 候选 | REQ | 字段 | LLM 输出（Before）| 应改成（After）| 依据 |
|---|---|---|---|---|---|
| **REV-001** | REQ-005 | `input_fields[1].name = ubr_threshold` | LLM 把 `ubr_threshold` 当成 test input field | **删除该字段**（它是 `/config` 里的配置参数，不是每次 test 的输入）| PROJECT_PLAN_V2 §2.2 表里 ubr_threshold 是阈值常量，调整通过 `PUT /config`，不是 simulate 入参 |
| **REV-002** | REQ-006 + REQ-007 | `input_fields[0].has_timing = False` | LLM 把 hood_voltage / door_voltage 的 has_timing 标为 False | **改为 True** | REQ-006/007 是"电压 + 时序"双重判断（参考 PROJECT_PLAN_V2 §2.2 时序双条件判断表），电压字段必须标 has_timing 才能让 BVA 生成器知道要生成时序边界用例 |
| **REV-003** | REQ-011 | `expected_actions` 只有 `vehicle_state eq 9` | LLM 只写了"三条件都满足→进入 state09"的正向 oracle | **补一条 alternative_action**：任一条件不满足 → vehicle_state 维持原值（state==11 或 state==10）| REQ-011 原文明确写："任一条件不满足，VCU 维持当前状态"，LLM 漏掉了负向分支，决策表 8 行里 7 行会判错 |
| **REV-004** | REQ-012 | `conditions[0]` 把两个条件合成一个 threshold | LLM 把 `consecutive_wake_sleep_cycles >= 3 AND interval < 1s` 塞进单个 condition 用 threshold=3 | **拆成两条 conditions**：①  threshold cycles>=3 ②  timing interval<1s | 这是"卡死缺陷"的复合触发条件，合并后无法独立测试，且 BVA 生成器看不到 interval 边界（0.9s/1.0s/1.1s）会漏关键用例 |
| **REV-005** | REQ-013 | `expected_actions` 同时有 `bus_message_flag eq 1` 和 `bus_message_flag eq 0` | LLM 产生了**互斥**的 oracle（同字段两个相反值）| **改为条件式 oracle**：when vehicle_state==11 → bus_message_flag==1；when vehicle_state==9 → bus_message_flag==0 | LLM 受 schema 限制无法表达 conditional output，必须人工补；否则 Test Case 生成时不知道两个值各对应哪种输入 |
| **REV-006** | REQ-014 | 同 REV-005 的问题 | `actual_duration lte 20.0` 和 `lte 60.0` 同时存在，但没绑定 test_case_type | **改为条件式 oracle**：when test_case_type==1 → ≤20.0s；when ==2 → ≤60.0s | 同上，是 type1/type2 两种用例的不同时序门槛，需要 condition-bound |

### 还可以加分项（非错误，但增强覆盖度）

| 补充候选 | 内容 | 依据 |
|---|---|---|
| **REV-007**（可选）| REQ-002 把 `threshold` 从字符串 `"0x400-0x47F"` 改成两个数值 `lower_bound=0x400, upper_bound=0x47F`，便于 BVA 生成 below/on/above 边界 | LLM 把范围塞成字符串，BVA 生成器无法直接取数 |
| **REV-008**（可选）| REQ-010 在 conditions 里补 CAN ID 过滤（`only IDs in [0x400, 0x47F]`），LLM 写成泛化的"can_bus_idle"丢了 ID 范围信息 | REQ-010 原文有 "0x400 ~ 0x47F" 限定，模糊后影响 Test Case 精度 |

---

## Phase 2 — Coverage Items 审查（FR 3.0 准备）

**LLM 原始输出**：`docs/test_evidence/03_coverage_items_raw.json`（40.8s, qwen3.7-max via DashScope，14 条 / 每 REQ 1 条 / 全部 Input 类）
**人工修订后**：`docs/test_evidence/04_coverage_items_reviewed.json`（**22 条** = 14 raw + 8 new）

### LLM 初版的核心缺陷

LLM 只生成 **Input 类** 14 条（每 REQ 1 条），完全跳过 ISO 29119 / Chapter 4 Workshop 推荐的 **Output / Behavior / Environment** 三个类别。

| 类别 | LLM 初版 | Chapter 4 应有 | 补全 |
|---|---|---|---|
| Input | 14 | ~14 | 0 |
| Output | **0** ❌ | 5 | **+5** |
| Behavior | **0** ❌ | 2 | **+2** |
| Environment | **0** ❌ | 1 | **+1** |
| **小计** | **14** | **22** | **+8** |

### Phase 2 三组 REV 详情

| REV-ID | 修订内容 | Why | 新增 CI 数 |
|---|---|---|---|
| **REV-006** | 补 Output 类 5 条：`vehicle_state oracle` (REQ-001)、`pdcu_wake_reason oracle` (REQ-001)、`bus_message_flag↔state 一致性` (REQ-013)、`actual_duration 时序边界` (REQ-014)、`active_dtcs 含 DTC_001` (REQ-012)| LLM 只关心输入边界，完全忽略响应体字段的 oracle 维度。但 Test Oracle 是 ISO 29119 §6.2 必备元素，没有 Output CI 等于"不知道怎么判定通过/失败" | 5 |
| **REV-007** | 补 Behavior 类 2 条：`正常唤醒序列 state09→state10→state11` (REQ-001, technique=ST)、`卡死序列 6 步` (REQ-012, technique=SC) | 状态机的"行为"不是单点输入，而是序列。LLM 初版 14 条没有任何序列类 CI，State Transition 和 Scenario Testing 两种技术失去"覆盖目标" | 2 |
| **REV-008** | 补 Environment 类 1 条：`VCU v1.0 SIL 环境基线 (FastAPI / port 8001 / 无物理 HIL)` (REQ-001) | Chapter 4 Workshop 明确要求把环境约束作为独立 CI，便于在 Artifact 4 §13 Limitations 章节准确陈述"哪些测试因环境而做不到"（例如真实 HIL 时序、CAN 物理层）| 1 |

### Phase 2 修订执行记录

| REV-ID | Before 文件 | After 文件 | 修订内容 | Why | Before 截图 | After 截图 | 操作人 / 时间 |
|---|---|---|---|---|---|---|---|
| REV-006 | `03_coverage_items_raw.json` | `04_coverage_items_reviewed.json` | 5 条 Output 类 Coverage Items POST 入库（CI 总数 14 → 19） | LLM 忽略响应体 oracle 维度，导致 Test Case 生成无法判定通过/失败 | `screenshots/Phase2_CoverageItems_before.png` | `screenshots/Phase2_CoverageItems_after.png`（待截）| 测试同学 / 2026-05-24 |
| REV-007 | 同上 | 同上 | 2 条 Behavior 类 Coverage Items 入库（CI 总数 19 → 21） | LLM 没生成任何序列/场景类 CI，状态机测试和卡死复现场景找不到"覆盖目标" | 同上 | 同上 | 测试同学 / 2026-05-24 |
| REV-008 | 同上 | 同上 | 1 条 Environment 类 Coverage Item 入库（CI 总数 21 → 22） | 把"SIL 环境约束"显式 CI 化，便于 Artifact 4 §13 Limitations 准确陈述未测项的环境根因 | 同上 | 同上 | 测试同学 / 2026-05-24 |

### Phase 2 最终覆盖率分布（After）

- **总 CI 数**：22（vs Before 14）→ +57.1%
- **技术分布**：BVA 9 / EP 6 / SC 3 / DT 2 / ST 2（5 种技术全用上，符合 Assignment 2 "≥ 3 种黑盒 + 白盒" 要求）
- **ISO 9126 分布**：Functionality 17 / Reliability 3 / Efficiency 2（三大特性都覆盖，Reliability 含卡死和 DTC，Efficiency 含时序）

---

---

## Phase 3 — Risk Analysis 审查（FR 2.0）

**LLM 原始输出**：`docs/test_evidence/05_risk_analysis_raw.json` + `.csv`（75.5s, qwen3.7-max；ISO 9126 × Tech×Business Risk → RPN）
**人工修订后**：`docs/test_evidence/06_risk_analysis_reviewed.json` + `.csv`

### 关键发现：LLM 评分比 PROJECT_PLAN_V2 §5.1 更自洽

LLM 独立评估的 RPN 与计划 §5.1 有 9 处不一致，但深入分析后发现 **多数情况下 LLM 是对的**：

- 计划 §5.1 把 REQ-001~011 全标 RPN=2（Extensive），但 §2.8 优先级列里 REQ-006/007 明明是 **Low**、REQ-003/004/005 是 **Medium** —— §5.1 与 §2.8 自相矛盾。
- LLM 修正了这个矛盾：给 Low 优先级的 REQ-006（RPN=9）/REQ-007（RPN=6）更高 RPN（=更低测试优先级），给 Medium 的 REQ-003/004/005（RPN=4~6）中等优先级。
- 最关键的 **REQ-012 卡死缺陷，LLM 精准给 RPN=1**（tech=1×bus=1，最高优先级），与计划完全一致。

→ **决策：只 override 2 处真正需要修正的**（REQ-008/009 休眠条件），其余保留 LLM 评分（尊重 AI 风险分析器的合理判断，符合 FR 2.0 定位）。

### Phase 3 修订执行记录

| REV-ID | Before 文件 | After 文件 | 修订内容 | Why | Before 截图 | After 截图 | 操作人 / 时间 |
|---|---|---|---|---|---|---|---|
| REV-009 | `05_risk_analysis_raw.json`（REQ-008）| `06_risk_analysis_reviewed.json`（REQ-008）| REQ-008 RPN 从 **8（tech=4,bus=2,Broad）** 改为 **2（tech=2,bus=1,Extensive）** | h1 (VCUIdle_flg) 是进入休眠的必要条件之一，PROJECT_PLAN_V2 §2.8 标 **High** 优先级。休眠逻辑出错会导致 VCU 该休眠不休眠（电池耗尽）或不该休眠却休眠（行车中断电），业务风险应为 Very High。LLM 把 tech 评 4（过于乐观）+ bus 评 2，低估了这条 High 需求，需提到 Extensive 测试深度 | `screenshots/Phase3_RiskAnalysis_before.png` | `screenshots/Phase3_RiskAnalysis_after.png`（待截）| 测试同学 / 2026-05-25 |
| REV-010 | `05_risk_analysis_raw.json`（REQ-009）| `06_risk_analysis_reviewed.json`（REQ-009）| REQ-009 RPN 从 **6（tech=3,bus=2,Broad）** 改为 **2（tech=2,bus=1,Extensive）** | h2 (AuthComplete_flg) 同 h1，是休眠三必要条件之一，§2.8 标 **High**。与 REQ-008 同理，必须与 REQ-010/011 享同等 Extensive 测试深度，否则休眠 AND 逻辑的决策表覆盖会出现优先级断层 | 同上 | 同上 | 测试同学 / 2026-05-25 |

### Phase 3 最终 RPN 分布（After Review）

| Extent | RPN | REQ |
|---|---|---|
| **Extensive** | 1 | REQ-012（卡死缺陷，最高）|
| **Extensive** | 2 | REQ-001, REQ-008, REQ-009, REQ-010, REQ-011（核心唤醒+休眠条件）|
| **Extensive** | 4 | REQ-003 |
| **Broad** | 6 | REQ-002, REQ-004, REQ-005, REQ-007, REQ-014 |
| **Broad** | 8 | REQ-013 |
| **Broad** | 9 | REQ-006 |

合计 Extensive 7 条 / Broad 7 条；High 风险需求（RPN ≤ 2）= 6 条，将获得 100% 通过率要求（见 PROJECT_PLAN_V2 §STP-6.3）。

---

## Phase 4 — Test Cases 审查（待 Test Case 生成阶段后填）

（占位）

---

## 修订执行记录

每完成一次"在前端/API 上真实改一条 + 截图 + 保存修订后文件"，在下表追加一行：

| REV-ID | Before 文件 | After 文件 | 修订内容 | Why | Before 截图 | After 截图 | 操作人 / 时间 |
|---|---|---|---|---|---|---|---|
| REV-001 | `01_parsed_requirements_raw.json`（REQ-005 段）| `REV-001_REQ-005_after.json` | REQ-005 删除 `ubr_threshold` input_field：input_fields 由 2 → 1，data_ranges 同步从 2 个 key 减到 1 个 | `ubr_threshold` 是 `/config` 配置参数（默认 4.4V，调整通过 `PUT /config` 修改），不是每次 simulate 调用的输入；LLM 误把它当 test input 会污染 EP/BVA — 会出现 `ubr_threshold=14.5V` 这种纯噪声用例 | `screenshots/REV-001_REQ-005_before.png` | `screenshots/REV-001_REQ-005_after.png`（待截）| 测试同学 / 2026-05-24 |
| REV-002 | `01_parsed_requirements_raw.json`（REQ-006/007 段）| `REV-002_REQ-006_007_after.json` | REQ-006 / REQ-007 把 `hood_voltage` / `door_voltage` 的 `has_timing` **False → True**（duration_ms 维持 True 不变）| REQ-006/007 是"电压 + 时序"双重判断（PROJECT_PLAN_V2 §2.2 时序双条件判断表）：电压满足且 duration ≥ 10ms 才唤醒。LLM 只把 duration_ms 标了 has_timing=True，电压字段标 False，下游 BVA 生成器只会生成电压一维边界（3.9/4.0/4.1V），漏掉"电压有效但 duration<10ms"等二维边界用例 | `screenshots/REV-002_REQ-006_007_before.png`（或拆为 `_006/_007_before.png` 两张）| `screenshots/REV-002_REQ-006_007_after.png`（待截）| 测试同学 / 2026-05-24 |
| REV-003 | `01_parsed_requirements_raw.json`（REQ-011 段）| `REV-003_REQ-011_after.json` | REQ-011 ① 把 conditions 从 1 条拆为 2 条：「ALL satisfied → state09」和「ANY false → MAINTAIN」；② expected_actions 从 1 条扩为 2 条：`vehicle_state eq 9`（休眠分支）+ `vehicle_state gt 9`（维持分支，即 state10 或 state11）| 原文 "h1 AND h2 AND h3 三条件同时满足时... 任一条件不满足，VCU 维持当前状态" 明确有两条分支，LLM 只写了正向。Decision Table 8 行中 7 行（任一不满足）按 LLM 初版会被判错。注：backend schema `operator` 不支持 `ne`，所以用 `gt 9` 表达"非 9"——因为 vehicle_state 只可能是 9/10/11，gt 9 ⟺ {10,11} = 维持状态 | `screenshots/REV-003_REQ-011_before.png` | `screenshots/REV-003_REQ-011_after.png`（待截）| 测试同学 / 2026-05-24 |
| REV-004 | `01_parsed_requirements_raw.json`（REQ-012 段）| `REV-004_REQ-012_after.json` | REQ-012 把唯一一条 condition `consecutive_wake_sleep_cycles >= 3 AND interval < 1s` (threshold=3) 拆为 2 条独立 conditions：① `threshold` cycles>=3；② `timing` interval<1.0s | 这是已知缺陷 REQ-012（RPN=1）的复合触发条件，LLM 把 AND 压平成单 threshold 后：① BVA 生成器看不到 interval 边界（0.9/1.0/1.1s），漏掉关键时序边界用例；② 测试用例无法独立验证两个条件单独不满足时是否还会触发卡死 | `screenshots/REV-004_REQ-012_before.png` | `screenshots/REV-004_REQ-012_after.png`（待截）| 测试同学 / 2026-05-24 |
| REV-005 | `01_parsed_requirements_raw.json`（REQ-013 段）| `REV-005_REQ-013_after.json` | REQ-013 把 conditions 从 1 条 `state == 11 or state == 9` 拆为 2 条 state condition：① `WHEN state==11 (normal)`；② `WHEN state==9 (sleeping)`。expected_actions 仍是 `bus_message_flag eq 1` 和 `bus_message_flag eq 0`，但现在 conditions 里的 description 明确了 oracle 与 state 的对应关系 | LLM 原 oracle 是「bus_message_flag eq 1」 + 「bus_message_flag eq 0」两条互斥，没有任何 state 上下文，Test Case 生成器根本不知道哪条对应哪种输入。注：backend ExpectedAction schema 不支持 `condition` 这种 condition-binding 字段（试过 PUT 时 pydantic 静默丢弃），所以条件绑定只能在 conditions.description 里用 `WHEN ...` 暗示——这是工具 schema 设计限制，应在 §13 Limitations 章节记录 | `screenshots/REV-005_REQ-013_before.png` | `screenshots/REV-005_REQ-013_after.png`（待截）| 测试同学 / 2026-05-24 |

---

## 附录：工具自身缺陷修复（Tool Bug Fixes，作为 Improvement 加分项）

不是 REV，但属于"工具初版有问题，由人工修复后增强了 Interactive Review 体验"的附加证据。

### TOOL-FIX-001 — RequirementInput.tsx 的 parsed 编辑器对结构化字段渲染错误

**症状**：`Input Fields` 和 `Conditions` 在前端显示为 `[object Object]`，无法编辑。

**根因**：`frontend/src/components/RequirementInput.tsx` 行 268/270 `toEditableParsed()` 把对象数组 `.join('\n')` 转字符串，每个对象变成 `"[object Object]"` 字面值；保存路径行 130/131 又用 `splitLines()` 把字符串拆回，结构信息（data_type/valid_range/unit/has_timing）全部丢失。

**修复**：把这两个字段对齐 `data_ranges` 的处理方式 — 用 `JSON.stringify(arr, null, 2)` 渲染、`JSON.parse(str)` 保存；并加 try/catch 在用户输入非法 JSON 时 alert 提示。

**影响**：使 Interactive Review 真正可用（之前用户无法在 UI 上看清字段内容，更别说编辑）。

**证据**：`git diff frontend/src/components/RequirementInput.tsx`（commit hash 待提交后填入）。

### TOOL-FIX-002（**已修复**）— 给 Coverage tab 补全 Add / Edit / Delete UI

**症状（修复前）**：`Coverage` tab 的 Coverage Items 列表只支持**查看**和"LLM 一次性重生成"（会清空重做）。手动新增单条 CI 必须绕道 `Improve` tab 里"改进建议→点添加"路径，且没有任何**编辑**或**删除**单条 CI 的按钮。

**根因**：`frontend/src/components/AutoTestDesignV2.tsx` Coverage 区只渲染了 DataTable 展示 + 一个"生成覆盖项"按钮，未挂载行内 Edit/Delete 按钮；`autoTestAPI` 已实现 `createCoverageItem` / `updateCoverageItem` / `deleteCoverageItem` 三个方法，但只有 createCoverageItem 在 Improve tab 被消费。

**修复内容**：在 `AutoTestDesignV2.tsx` 增加：
1. State：`showCoverageForm` / `editingCoverageId` / `coverageForm` 三个新 state
2. 5 个 handlers：`openAddCoverageForm` / `openEditCoverageForm` / `closeCoverageForm` / `saveCoverageItem` / `deleteCoverageItem`（含 confirm 二次确认）
3. Coverage tab UI：顶部"+ 添加"按钮（绿色）+ 折叠式内联表单（6 个字段：requirement_id / title / description / technique / iso9126_characteristic / priority）+ 重写表格支持行内 Pencil/Trash 按钮 + 显示 CI 总数
4. 新增 4 个 lucide-react 图标：`Plus`、`Pencil`、`Trash2`、`X`

**影响**：Phase 2 之后任何 Coverage Items 修订都可以直接在前端 UI 上进行（之前必须 API 脚本），完整闭环 Interactive Review。

**证据**：`git diff frontend/src/components/AutoTestDesignV2.tsx`（commit hash 待提交后填入）。

### TOOL-FIX-003（**已修复**）— `POST /api/coverage-items/generate` 引入 `mode` 参数解决盲目 append 重复问题

**症状（修复前）**：每次点击 Coverage tab 的 "生成覆盖项" 按钮，后端会**无条件追加** LLM 生成的 14 条 CI。连续点击 N 次会产生 14×N 条重复，污染数据。

**发现路径**：Phase 2 用户验证 TOOL-FIX-002 时，前端 Coverage 列表显示 78 条而不是预期 22 条。GET /api/coverage-items 返回 49 个唯一 title × 多份副本 = 78 条 = 22 (canonical) + 14 × 4，证明按钮被多点了 4 次。

**修复内容**：

1. **后端 `backend/api/services/coverage_service.py`**：`generate_coverage_items()` 增加 `mode` 参数（默认 `dedupe`），三种模式：
   - `dedupe`（默认，幂等安全）：跳过 LLM 输出中 `(requirement_id, title)` 已存在的项 — 重复点击变成无操作
   - `replace`：删除受影响 requirement_ids 的现有 CI 后再生成 — 用于明确想要 LLM 重做的场景
   - `append`（旧行为）：纯追加，允许重复 — 仅诊断用途

2. **后端 `backend/api/routers/autotest_review.py`**：endpoint 暴露 `?mode=` query 参数，pattern 校验只接受 `dedupe|replace|append`

3. **前端 `frontend/src/services/api.ts`**：`generateCoverageItems()` 接受可选 `mode` 参数，默认 `'dedupe'`

4. **前端 `frontend/src/components/AutoTestDesignV2.tsx`**：当 CI 列表非空时，"生成覆盖项"按钮先弹 `window.prompt` 让用户选 mode；选 `replace` 时再弹 `window.confirm` 二次确认；防止无意识点击破坏数据

**临时清理证据**：本次故障发现后用 04_coverage_items_reviewed.json 的 22 个 canonical id 做白名单，批量 DELETE 其余 56 条恢复，验证 `final total: 22, duplicate titles remaining: 0`。

**影响**：Coverage tab 的 LLM 生成动作现在是**幂等的**（默认模式下），消除了 Interactive Review 过程中"误点导致数据污染"的最大隐患。

**证据**：`git diff backend/api/services/coverage_service.py backend/api/routers/autotest_review.py frontend/src/services/api.ts frontend/src/components/AutoTestDesignV2.tsx`（commit hash 待提交后填入）。

### TOOL-FIX-004（**已修复 2026-05-25**，附事故复盘）— AutoTestDesign V2 后端全部状态在内存，重载即丢

**症状**：`backend/api/services/requirement_service.py` 和 `coverage_service.py` 都用模块级 `dict`/`List` 作为存储（`_requirements: List[Requirement] = []`、`_parsed_requirements: dict = {}`、`_coverage_items: dict = {}`、`_strategies: dict = {}`）。一旦 uvicorn `--reload`（修改任何后端文件触发）重新 import 这些模块，所有数据归零。

**触发事故**：实施 TOOL-FIX-003 时修改 `coverage_service.py`，uvicorn 自动 reload 把全部 14 条 Requirements + 14 条 Parsed + 22 条 Coverage Items 一次性清空。

**恢复方式**：所有重要状态都有 JSON 快照（`01_parsed_requirements_raw.json` / `04_coverage_items_reviewed.json` / `REV-NNN_*_after.json`），用脚本依次：① `GET /api/requirements/demo?replace=true` 重灌 24 条 REQ 记录；② 对每条 Module A 的 14 个 REQ `PUT /api/requirements/{id}/parsed` 注入快照（REQ-005/006/007/011/012/013 用对应 REV after 文件覆盖）；③ 批量 `POST /api/coverage-items` 重建 22 条 CI。耗时 < 5 秒。

**未修复理由**：彻底修复需要给两个 service 加 SQLite 或文件持久化（`api/database/` 目录已存在但只供旧版用），改动较大；当前阶段以"完成 Artifact 4 证据采集"为优先级，编程式恢复脚本足够可靠。

**操作建议**：

1. 编辑后端代码 → 必然 reload → 必须立刻跑恢复脚本
2. 关键状态变更立刻 dump 快照到 `docs/test_evidence/`，作为容灾备份
3. 在 Artifact 4 §13 Limitations 列出"V2 后端状态非持久化"作为已知限制 + Future Work

**✅ 修复方案（2026-05-25 实施）**：新增 `backend/api/services/_persist.py` JSON 文件持久化层，状态目录 `backend/data/v2_state/`（可用 `V2_STATE_DIR` 环境变量覆盖）。

1. **加载**：6 个 service 模块导入时从磁盘加载（`_persist.load_list/load_dict`），替换原来的空 `[]`/`{}` 初始化。涉及 `requirement_service`（requirements + parsed）、`coverage_service`（coverage_items + strategies）、`risk_service`（risk_results）、`test_design_service`（test_cases）、`prompt_service`（prompts，默认值上叠加持久化覆盖）、`performance_service`（metrics）。
2. **保存**：每个写操作（create/update/delete/generate/analyze/adjust）后调用对应 `_save()` 落盘。`_persist._write` 用临时文件 + `os.replace` 原子写，避免半截写坏文件。
3. **为何不触发 reload 循环**：uvicorn 0.47 `--reload` 默认只监听 `*.py`，写 `.json` 不会触发重载。

**修复前数据保护**：实施前用 GET 全量快照到 `docs/test_evidence/_state_snapshot/`（requirements 14 / parsed 14 / coverage 22 / strategies 14 / risk 14 / test_cases 88 / prompts 5 / performance 30），并经后端 schema round-trip 校验（0 失败）后预灌到 `backend/data/v2_state/`，再改代码，确保改后端触发的 reload 能从预灌文件还原。

**验证**：① 编辑触发 reload 后全量计数与抽验（REQ-001 strategy=EP/BVA/ST、REQ-008 risk=2/1/2）全部一致；② 主动 `touch` 一个 service 文件强制 reload 后 test_cases 仍为 88、requirements 仍为 14，确认跨 reload 持久。

**残留说明**：Artifact 4 §13 可改为「V2 后端原为内存态，已通过 JSON 文件持久化解决；生产级方案建议迁移 SQLite」。

### TOOL-FIX-005（**已修复 2026-05-25**）— LLM 返回的 `error` 字段为字符串导致 TestCase 校验崩溃（REQ-014 生成 502）

**症状**：`POST /api/test-cases/generate-all` 跑到 REQ-014（响应时序需求）时返回 HTTP 502：`1 validation error for TestCase: error — Input should be a valid list, input_value='Timeout expected'`。导致 REQ-014 生成 0 条用例，其余 13 条不受影响。

**根因**：`TestCase.error` 字段类型是 `List[BqErrorOracle]`，但 LLM 对超时类需求倾向把 `error` 返回成描述字符串 `"Timeout expected"`。`test_design_service._generate_from_context` 原代码 `error=item.get("error") or []` 直接把字符串塞进 list 字段 → pydantic 校验失败 → 整个 generate-all 请求 502（已生成的会持久化，未生成的 REQ-014 丢失）。

**修复内容**：`test_design_service.py` 新增 `_normalize_error()`，把非 list 的 `error` 一律归一为 `[]`，list 内只保留 dict 项。REQ-014 的超时 oracle 本来就由 `expected_results`（`actual_duration ≤ 20s`，operator=lte）表达，丢弃畸形字符串不损失语义。

**验证**：修复后单独 `POST /api/test-cases/generate {"requirement_id":"REQ-014","techniques":["BVA"]}` 返回 HTTP 200，生成 6 条 BVA 时序边界用例（type1 19.9/20.0/20.1s、type2 59.9/60.0/60.1s，below/on/above 三点齐全）。最终用例总数 88 → 94，14 条需求全覆盖。

**作为 Artifact 4 证据**：这是「执行期工具改进」的典型案例——批量生成执行才暴露的 LLM 输出鲁棒性缺口，可写进 §12 Execution-driven Improvement（工具层），或作为 Interactive Review 中"人工发现工具缺陷 → 修复 → 补回遗漏用例"的过程证据。

### TOOL-FIX-006（**已修复 2026-05-25**）— 比对算子缺少"不等于（ne）"，REQ-011 被迫绕开

**症状**：Phase 1 修订 REQ-011（h1∧h2∧h3 全满足才休眠 state09，否则维持 state10/state11）时，想用 `vehicle_state ne 9` 表达"非休眠即维持"，但 `PUT /api/requirements/REQ-011/parsed` 返回 HTTP 422：`operator 'ne' invalid`。schema 的 operator `Literal` 只允许 `eq/gte/lte/gt/lt/contains`，没有不等于。当时只能用 `gt 9`（表示 {10,11}）绕开，语义不如 `ne 9` 直观。

**根因**：`backend/api/models/schemas.py` 两处 operator 定义（`ExpectedAction` line 75 + `ExpectedOutput` line 252）的 `Literal` 集合缺 `ne`；`test_design_service._normalize_expected_results` 的 `allowed_ops` 与别名表也没有 `ne`；`simulator_client._matches` 无 `ne` 分支。

**修复内容**：

1. `schemas.py`：两个 `operator` Literal 增加 `"ne"` → `Literal["eq","ne","gte","lte","gt","lt","contains"]`。
2. `test_design_service._normalize_expected_results`：`allowed_ops` 加 `ne`；别名表加 `!=`/`<>`/`≠`/`neq` → `ne`，兼容 LLM 各种写法。
3. `simulator_client._matches`：在 `eq` 分支后新增 `ne` 分支（`return actual != expected`），与 eq 对称、对任意类型生效。

**纯增量、零回归**：不改动现有 eq/gt/contains 行为；当前 94 条用例的算子分布为 eq/gt/contains，无任何用例用到 ne，因此新增 ne 不影响既有用例执行。

**验证**：① schema 直接构造 `ExpectedOutput(operator="ne")` / `ExpectedAction(operator="ne")` 不报错；② `_matches(11,"ne",9)=True`、`_matches(9,"ne",9)=False`、`_matches(11,"eq",11)=True`（eq 不受影响）；③ 后端 reload 后 14/22/94 数据完整。

**影响**：REQ-011 之类"非某状态即维持"的需求现在可用 `ne` 直接表达，oracle 更贴合需求语义；后续测试用例审查（Step 2.5.2）可把 REQ-011 的 `gt 9` 改回 `ne 9`（属数据修订，留待用例审查环节，本次只开能力不改数据）。

### TOOL-FIX-007（**已修复 2026-05-26**）— testcase prompt 缺「VCU 输出取值语义」，导致 LLM 系统性产出错误 oracle 值

**症状**：把 96 条设计用例做成数据驱动 pytest 直接对 VCU 执行（`tests/test_suite_from_design.py`）后，初次仅 **48/96 通过**。失败的 48 条不是 VCU bug，而是 LLM 设计的 oracle **取值**系统性错误：`vehicle_state eq 0`（幻觉状态）、维持态写成 `eq 10`（实际 9）、no-wake 用 `result_type eq expected`（实际 error）、卡死用 `result_type eq stuck`（实际 error）、标题"不触发"却配唤醒 oracle。

**根因**：REV-015 的 prompt 改进只加了**字段名白名单**（治 Untestability），没给字段**取值语义**。LLM 不知道 vehicle_state∈{9,10,11}、result_type∈{expected,error}、no-wake→(9,reason0,error) 等规则，只能猜。

**为何不手工改 48 条**：48 条是同类系统性错误，逐条手改是治标；根因在 prompt（工具），应改工具一次性根治（与 TOOL-FIX-003 / REV-015 选 Option B 思路一致）。

**修复内容**：`prompt_service` testcase prompt 追加「VCU 输出取值语义」块——明确 vehicle_state / pdcu_wake_reason / result_type / bus_message_flag / actual_duration / active_dtcs 的合法取值与判定口径（无效输入→9/0/error、有效唤醒→11/1-7/expected、卡死→10/DTC_001/error、时序合规用 lte）。Before/After：`prompt_testcase_v2_fieldwhitelist.json` → `prompt_testcase_v3_value_semantics.json`。

**效果**：14 需求 `regenerate=true` 重生成后通过率 **48/96 → 80/99**（一次 prompt 修复救回约 30 条），证明根因定位正确。

### TOOL-FIX-008（**已修复 2026-05-26**）— 工具执行器不能执行自己设计的用例；改由前端"执行全部"直接驱动 pytest

**症状**：前端 Results「执行全部」(`POST /api/execute`) 原走 `simulator_client → VCU HTTP /simulate`，发送的是 `in_data` 列表；但 VCU `SimulateRequest` 只认**扁平信号字段**（supply_voltage / can_msg_id / VCUO_bDIAG_VCUIdle_flg …，无 `in_data` 字段）→ 列表被整体忽略 → 所有信号 None → 全部 no-wake，passed=0。工具能**设计**用例却不能正确**执行**自己设计的用例。

**根因**：双重不匹配——(1) `in_data` 列表 vs 扁平字段；(2) 设计字段名（voltage/h1/can_bus_idle）vs VCU 信号名（supply_voltage/VCUO_*/can_stopped）。这两层翻译只存在于 pytest 数据驱动套件的**适配器**（`tests/test_suite_from_design.py::_run`）里，工具执行器没有；休眠测试还需"先唤醒"前置、卡死需序列调用。

**修复（采用"pytest 作为单一执行引擎"方案）**：新增 `backend/api/services/pytest_runner.py`，`/api/execute` 改为 **subprocess 直接跑真正的 pytest 套件**（`sys.executable -m pytest tests/test_suite_from_design.py`，含适配器），解析 JUnit XML，按嵌在参数 id 里的 **case uuid** 回映射到工具用例并 `mark_execution`。前端"执行全部"按钮**无需改动**，点击即触发真实 pytest 执行，Results 的 `<Summary>` 显示真实通过率。pytest 参数 id 调整为 `uuid|REQ|RPN|title` 以便回映射。

**验证**：`POST /api/execute` → 12.9s → 解析 96 testcase → 96/96 通过；`/api/results/summary` total=96 passed=96 pass_rate=1.0；96/96 用例 `execution_result` 填充。

**意义**：实现「设计 = 执行 = 展示」三位一体、单一事实源（pytest）——前端 Results 现在反映**真实** pytest 执行结果，可截图；消除了"工具能设计不能执行"的割裂。

---

## Phase 4 — Coverage Strategy & Method（§5 测试技术绑定）

> 对应 Interactive Review 第 3 步【Coverage Strategy & Method】，Step 2.4.2。
> 工具初版 strategy 由后端 `ensure_strategy()` 从各需求已有 Coverage Items 的 technique 字段自动推断，结果偏单一（多数只挂 1 个技术）。人工按 PROJECT_PLAN_V2 §STP-5.8 的「需求 ↔ 黑盒/白盒技术」映射表修订为多技术组合。
> **真正证据 = CSV**（`07_strategy_assignment_before.csv` vs `07_strategy_assignment.csv`，逐条 Before/After 全记录）。前端 Strategy 标签页一次只显示 1 条需求、截 14 张不现实，故仅保留 1 张 Before 视觉样例（`Phase4_Strategy_before.png`，REQ-001=EP;BVA），After 不另截图，以 CSV 为准。

| Review ID | REQ | Before（工具初版） | After（人工修订） | 修订原因 |
|---|---|---|---|---|
| REV-011 | REQ-001 | EP;BVA | EP;BVA;ST | 补状态迁移技术(ST)：w1 唤醒涉及 state09→state10→state11，需 All-Transitions 覆盖 |
| REV-011 | REQ-002 | BVA | EP;ST | 改为 EP(CAN ID 范围等价类)+ST；CAN ID 是离散范围，EP 比 BVA 更对口 |
| REV-011 | REQ-003 | BVA | EP;ST | 同上，CP 幅值等价类 + 状态迁移 |
| REV-011 | REQ-004 | BVA | EP;ST | w4 输入等价类 + 状态迁移 |
| REV-011 | REQ-005 | BVA | EP;ST | w5 输入等价类 + 状态迁移 |
| REV-011 | REQ-006 | BVA | EP;BVA;ST | 带时序唤醒：保留 BVA(duration≥10ms 边界) + 补 EP + 补 ST |
| REV-011 | REQ-007 | BVA | EP;BVA;ST | 同 REQ-006，带时序 |
| REV-011 | REQ-008 | EP | DT;ST | 休眠条件 h1 是布尔条件，改决策表(DT) + 补状态迁移(ST) |
| REV-011 | REQ-009 | EP | DT;ST | 休眠 h2：决策表 + 状态迁移 |
| REV-011 | REQ-010 | EP | DT;ST | 休眠 h3：决策表 + 状态迁移 |
| REV-011 | REQ-011 | DT | DT;ST | h1∧h2∧h3 组合保留 DT(2³ 全枚举) + 补 ST |
| REV-011 | REQ-012 | SC | ST;SC | 已知卡死缺陷：保留场景/序列(SC) + 补状态迁移(ST) 验证 state10 |
| REV-011 | REQ-013 | ST | EP | bus_message_flag 输出一致性改为输出域等价类(EP)，比 ST 更准确 |
| REV-011 | REQ-014 | BVA | BVA | actual_duration≤20s 时序边界(BVA) 保持；性能 NFR 度量见 §4.5 |

**汇总**：14 条需求全部绑定技术，技术覆盖 EP / BVA / DT / ST / SC 五种（满足 Assignment 2「多种黑盒 + 白盒」要求）。工具仅支持这 5 个技术代码，REQ-014 的 Performance Testing 概念在工具内以 BVA（时序边界）落地，真正的性能度量在 Artifact 4 §4.5 NFR 章节单独完成。

**证据**：`07_strategy_assignment_before.csv`、`07_strategy_assignment.csv`、`Phase4_Strategy_before.png`（Before 视觉样例；After 以 CSV 为准，不另截图）

---

## Phase 5 — Test Case Review（§7 测试用例 + §12 设计期改进）

> 对应 Interactive Review 第 4 步【Test Case Generation】的人工审查。审查标准**严格对照课件**：Chp4TestTechPart1Updated（EP/BVA）、Chp4TestTechPart2（白盒状态转换）、InspectionLiveSession（评审检查清单）、满分模板 Chap4 Printer Testing（数据链格式）。
> **真正证据 = JSON**（`08_test_cases_raw.json` 工具初版 vs `09_test_cases_reviewed.json` 人工修订后）。

| Review ID | 需求/数量 | LLM 初版问题 | 人工修订 | 课件依据 |
|---|---|---|---|---|
| REV-012 | REQ-014 ×6 | oracle 用 `is_compliant`——**VCU 不返回此字段，无法验证（Untestable）** | 改用真实字段 `actual_duration`：type1 `lte 20`(19.9/20.0)、`gt 20`(20.1)；type2 `lte 60`(59.9/60.0)、`gt 60`(60.1) | InspectionLiveSession P9「Untestability: How can I check this item?」+ BVA 三点 P36 |
| REV-013 | REQ-012 ×2 | 标题"**不**触发卡死"但 oracle 写 `result_type=stuck`+`active_dtcs eq DTC_001`——条件逻辑反转、且 list 字段误用 eq | 改 `result_type ne stuck` + `vehicle_state ne 10`（非卡死态） | Chp4Part1 P5「Incompletely specified conditions」（if/then/**else** 缺失类）；ne 算子来自 [[feedback-follow-assignment2-spec]] 相关的 TOOL-FIX-006 |
| REV-014 | REQ-001 +1 | BVA 缺 **invalid-too-low** 等价类（只有 9.0 on、9.1 above，漏 8.9 below）| 新增 8.9V 用例（`vehicle_state eq 9`），挂到现有 CI「硬线供电唤醒边界值测试」（该 CI 描述本就列了 8.9V，但 LLM 未生成对应用例）| Chp4Part1 P35-40 BVA 必含无效等价类 + 每边界 just-below/on/just-above 三点 |
| REV-015 | REQ-008/009/010 ×17 | oracle 用 `sleep_sub_condition_*`/`Next_State`——**VCU 不返回，Untestable** | **(a 设计期/Prompt Design)** 改进 testcase 生成 prompt：加 VCU 真实输出字段白名单、禁止臆造、active_dtcs 用 contains、状态断言用 vehicle_state；**(b)** 对 3 个需求 `regenerate=true` 重生成 → 全部改用 `vehicle_state`（含 `ne 9`） | InspectionLiveSession P9 Untestability；Assignment 2 §1.2「Prompt Design」+ tool 改进 |

**REV-015 量化效果**：重生成前全库有 **21 条用例引用 VCU 不存在字段**（is_compliant×6 / sleep_sub_condition_*×16 / Next_State×1）；改进 prompt + regenerate 后 **全库 0 条臆造字段**（脚本扫描验证）。用例总数 88→（+REQ-014 补生成）94→（+REV-014 8.9V）95→（REV-015 重生成）96。

**REV-015 残留待验（执行期改进线索，记入 §12 Execution-driven）**：重生成的 REQ-008/009/010 把"单条件满足→`vehicle_state eq 9`"作为期望，但按 REQ-011 休眠需 h1∧h2∧h3 **全部**满足；单独 h1=1 是否足以进入 state9 取决于 VCU 实际行为，**待 Step 3 pytest 执行时验证**——若 VCU 要求三条件齐全，则 in_data 需补齐另两条件，这将成为执行期（fuzz 反馈）改进的真实证据。

**Prompt Design 证据**：`prompt_testcase_before.json`（工具初版）vs `prompt_testcase_after.json`（加白名单约束后）——用于 Artifact 4 §6 Prompt Design 的 Before/After。

**证据文件**：`08_test_cases_raw.json`、`09_test_cases_reviewed.json`、`prompt_testcase_before.json`、`prompt_testcase_after.json`

---

## Phase 6 — Execution-driven Improvement（§12.2 执行期改进 / 闭环）

> 对应 Assignment 2「Mainly」黄金流水线的最后一环：**设计的用例 → 真正执行 → 发现不足 → 改进**。这是设计期人工审查（REV-001~015）**抓不到**的一类缺陷——只有把用例真正跑起来才暴露。

**做法**：把 96 条设计用例（`09_test_cases_reviewed.json`）做成**数据驱动 pytest**（`tests/test_suite_from_design.py`），每个 pytest 参数 == 一条设计用例（`TC | CI | REQ | RPN`），适配器把设计 in_data 翻译成 VCU 真实调用，断言设计 oracle。IEEE 829 生命周期（setup/测试/断言/teardown），按 RPN 风险排序。**旧的 5 个按技术硬编码套件（test_suite_a~e）已删除**——它们脱离 96 条设计、违反"scripts based on test cases"，由本数据驱动套件取代，实现"设计 96 = 执行 96"的闭环。

**通过率改进链**（每一步都定位根因，不盲目改 oracle 凑绿）：

| 阶段 | 通过率 | 根因 / 动作 |
|---|---|---|
| 初次执行 | **48/96 (50%)** | 暴露 48 条设计 oracle 缺陷（5 轮设计期审查都没抓到）|
| TOOL-FIX-007（prompt 取值语义）| **80/99 (81%)** | 系统性取值错误 → 改 prompt 重生成，一次救回 ~30 条（根因在工具）|
| 适配器修复（休眠测试先唤醒）| **92/99 (93%)** | 诊断发现 13 条是**测试脚本 harness bug**（休眠测试需先把 VCU 唤醒到 state11 再施加休眠条件），**非设计缺陷**——正确区分后修 harness，没有误改正确的设计 oracle |
| 人工执行期审查 REV-016 | **96/96 (100%)** | 改 3（REQ-010 输入矛盾/阈值、REQ-014 时序违规改走卡死路径）+ 删 4（REQ-013 输出当输入 ×2、REQ-001 卡死重复、REQ-014 type2 无触发机制）+ 加 1（REQ-001 BVA 8.9V invalid-too-low）|

**关键认知（写进 Artifact 4 §12）**：
1. **设计期审查抓不到 oracle-vs-SUT 真实行为的偏差**，只有执行能；这正是「Mainly」流水线要求"执行后改进"的原因。
2. **根因优先**：48 条系统性错误的根因是 prompt 缺取值语义（工具问题），改 1 次 prompt 顶 48 次手工补丁。
3. **诚实区分三类失败**：工具/prompt 缺陷（改 prompt）、测试脚本 harness bug（改 adapter）、真·畸形设计用例（删/改）——绝不把 harness bug 当成"设计缺陷"去改 oracle。

**通过 ≠ 仿真器全 success**：最终 96 条中 **51 条是负向测试**（预期 VCU 报错/拒绝/卡死/维持），它们通过=确认 VCU **正确地报错/拒绝**；45 条正向。已知 state10 卡死缺陷（DEF-001）由 REQ-012 的 6 条用例**复现确认**（断言 vehicle_state=10 + active_dtcs 含 DTC_001）。

**证据文件**：`tests/test_suite_from_design.py`、`10_traceability_matrix.csv`（96 行，含 Polarity 正负向列）、`prompt_testcase_v2_fieldwhitelist.json` / `prompt_testcase_v3_value_semantics.json`、pytest 执行输出（Step 3.3 待留存 html/xml/txt）。

---

## 附录：测试用例版本链（可追溯，全程保留）

| 版本 | 条数 | 含义 | 文件 | 备注 |
|---|---|---|---|---|
| v0 初次生成 | 88 | 第一次 generate-all；REQ-014 因 TOOL-FIX-005 的 502 bug 缺失 | `08_test_cases_raw_88_initial.json` | 含臆造字段 |
| v1 raw（工具初版）| 94 | 修 502 后补全 REQ-014；**人工审查前的纯工具输出** | `08_test_cases_raw.json` | 含臆造字段 21 处（Before 基线）|
| v2 设计期审查 | 96 | v2 prompt（字段白名单）+ REV-012~015 人工审查 | `09b_test_cases_v2_design_reviewed_RECONSTRUCTED.json` | **重建件**（原件被 v3 重生成覆盖）：由 v1 + `.rev015_regen.json` + REV-012/013/014 编辑精确重建；仍带 v2 期系统性取值错误（state0×9、维持=10×6），与当初执行 48/96 一致 |
| v3 raw（取值语义重生成）| 99 | v3 prompt（TOOL-FIX-007 取值语义）regenerate 全 14；REV-016 执行期审查前 | `09a_test_cases_v3regen_raw_before_REV016.json` | 执行 80/99→修适配器 92/99 |
| **v4 final（当前）** | 96 | v3 + REV-016 执行期审查（改3删4加1）| `09_test_cases_reviewed.json` | **96/96 通过**；数据驱动套件读取此文件 |

> Artifact 4 的核心 Before/After 对比 = v1（工具初版 94，含臆造字段）↔ v4（最终 96，0 臆造、96/96）。中间 v2/v3 完整保留，体现"两轮 prompt 改进 + 两轮人工审查"的迭代闭环。
