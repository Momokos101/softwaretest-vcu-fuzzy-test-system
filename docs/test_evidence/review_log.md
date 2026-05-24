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

## Phase 3 — Test Cases 审查（待 Step 11 之后填）

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

### TOOL-FIX-004（**已记录，未修复**，附事故复盘）— AutoTestDesign V2 后端全部状态在内存，重载即丢

**症状**：`backend/api/services/requirement_service.py` 和 `coverage_service.py` 都用模块级 `dict`/`List` 作为存储（`_requirements: List[Requirement] = []`、`_parsed_requirements: dict = {}`、`_coverage_items: dict = {}`、`_strategies: dict = {}`）。一旦 uvicorn `--reload`（修改任何后端文件触发）重新 import 这些模块，所有数据归零。

**触发事故**：实施 TOOL-FIX-003 时修改 `coverage_service.py`，uvicorn 自动 reload 把全部 14 条 Requirements + 14 条 Parsed + 22 条 Coverage Items 一次性清空。

**恢复方式**：所有重要状态都有 JSON 快照（`01_parsed_requirements_raw.json` / `04_coverage_items_reviewed.json` / `REV-NNN_*_after.json`），用脚本依次：① `GET /api/requirements/demo?replace=true` 重灌 24 条 REQ 记录；② 对每条 Module A 的 14 个 REQ `PUT /api/requirements/{id}/parsed` 注入快照（REQ-005/006/007/011/012/013 用对应 REV after 文件覆盖）；③ 批量 `POST /api/coverage-items` 重建 22 条 CI。耗时 < 5 秒。

**未修复理由**：彻底修复需要给两个 service 加 SQLite 或文件持久化（`api/database/` 目录已存在但只供旧版用），改动较大；当前阶段以"完成 Artifact 4 证据采集"为优先级，编程式恢复脚本足够可靠。

**操作建议**：

1. 编辑后端代码 → 必然 reload → 必须立刻跑恢复脚本
2. 关键状态变更立刻 dump 快照到 `docs/test_evidence/`，作为容灾备份
3. 在 Artifact 4 §13 Limitations 列出"V2 后端状态非持久化"作为已知限制 + Future Work
