# NFR 性能度量（Step 4.5 — Artifact 4 §13 NFR / Project Requirement Specification §4）

> **度量对象 = AutoTestDesign 工具自身**（不是被测的 VCU 仿真器）。数据来源：工具 `/api/performance`（`backend/data/v2_state/performance.json`，72 条），LLM = **qwen3.7-max（百炼 DashScope 云端）**。
> 数字由脚本对 performance.json 按 operation 聚合，非手填。

## 1. NFR 规格 vs 实测

| NFR | 规格（Project Requirement Specification §4.1）| 实测 | 结论 |
|---|---|---|---|
| **NFR 4.1.1** Analysis Time | 100 条需求的解析 + 风险分析 ≤ **5 s** | `risk.analyze` 单批（14 条需求）**75.4 s** → 折合 ~5.4 s/需求、~540 s/100 条 | ❌ **严重超标（~100×）** |
| **NFR 4.1.2** Test Case Generation | 单条需求生成完整用例集 ≤ **2 s** | `testcase.generate`（n=32）：min **35.0 s** / mean **75.4 s** / max **124.6 s** | ❌ **严重超标（mean ~37×）** |
| NFR 4.2.2 Traceability | 用例须可追溯到 REQ-ID 与技术 | `10_traceability_matrix.csv`（96 行，REQ↔CI↔技术↔结果）| ✅ 满足 |
| NFR 4.2.1 Interface | 干净直观的 UI | AutoTestDesign V2 7 标签页（Concept→…→Optimize）| ✅ 满足 |
| NFR 4.4.1/4.4.2 Stack/Modularity | 现代开源栈 + 松耦合 | FastAPI + React + Vite；service 分层（requirement/coverage/risk/test_design/optimize…）| ✅ 满足 |

> 其它 LLM 操作实测：`improve.generate`（第二轮增广）n=3，9.7~67.3 s，mean 43.4 s；另有 `llm.reasoning_stream` 36 次（reasoning token 流，未单独计时）。

## 2. 根因分析

- **唯一根因 = 云端推理型 LLM 往返延迟**：qwen3.7-max 开启 reasoning，每次 JSON 生成调用需 35~125 s（含思考链）。NFR 4.1.1/4.1.2 的 2 s/5 s 目标默认的是**快速/本地**生成，与"云端 reasoning LLM 单次往返数十秒"在数量级上不匹配。
- 与功能正确性无关：工具功能（解析/覆盖/风险/用例/oracle/优化）均正确，仅**响应时延**不达标。

## 3. 改进建议（按 Assignment §5「不可隐瞒、需给改进」）

1. **关闭 reasoning**：`LLM_ENABLE_THINKING=false`（已部分缓解）——去掉思考链可显著降时延。
2. **本地/小模型**：用本地量化小模型或更快的非 reasoning 模型做结构化生成，牺牲少量质量换 <2 s。
3. **结果缓存**：相同需求/prompt 命中缓存，重复生成 0 延迟。
4. **并发批量**：14 条需求并发生成（当前串行），墙钟时间从 Σ 降到 max。
5. **流式 + 预生成**：UI 流式返回；非交互式场景离线预生成用例库。

## 4. 与"被测系统时序"的区分（避免混淆）

本节 NFR 是 **AutoTestDesign 工具**的响应时延。被测 **VCU 仿真器**自身的时序（REQ-014：type1 唤醒 ≈14.7 s ≤20 s ✓、卡死 41 s）是 **SUT 的建模行为/被测对象**，属 §10 结果分析与 DEF-001，**不是**工具 NFR，二者不可混为一谈。

## 5. 证据文件
- `backend/data/v2_state/performance.json`（72 条 LLM 调用计时，model=qwen3.7-max）
- 前端 Results 页底部「LLM 调用性能日志」可截图
- 规格出处：`Project Requirement Specification.docx` §4.1（NFR 4.1.1 / 4.1.2 原文）
