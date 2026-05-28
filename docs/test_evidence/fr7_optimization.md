# FR 7.0 测试套件优化（Test Suite Optimization）证据

> **FR 7.0 原文**：系统包含一个优化功能，用于**基于风险或覆盖效率**对生成的测试套件进行**优先级排序（prioritize）**或**最小化（minimize）**。
> 本工具在 AutoTestDesign 的 **Optimize (FR7.0)** 标签页实现两项能力，均对工具自身的 96 条测试套件操作；后端 `GET /api/optimize/prioritize`、`GET /api/optimize/minimize`（`backend/api/services/optimize_service.py`）。
> 数据快照：`fr7_optimization/prioritize.json`、`fr7_optimization/minimize.json`（由实时端点导出）。

---

## 1. 风险优先级排序（Prioritize by Risk / RPN）

**准则**：按需求 RPN **升序**排列全部 96 条用例（**RPN=1 风险最高，最先执行**）。RPN 来自 FR 2.0 风险分析（`risk_results.json`），与 pytest 套件 `test_suite_from_design.py::_params` 的执行顺序一致。

| RPN | 优先级 | 用例数 | 代表需求 |
|---|---|---|---|
| **1** | High | 6 | REQ-012（state10 卡死缺陷，最高风险，最先跑）|
| **2** | High | 34 | REQ-001/008/009/010/011（核心唤醒+休眠条件）|
| **4** | High | 7 | REQ-003（CP 唤醒）|
| **6** | Medium | 35 | REQ-002/004/005/007/014 |
| **8** | Medium | 4 | REQ-013（输出一致性）|
| **9** | Medium | 10 | REQ-006（口盖唤醒）|

输出每条用例的 `rank / requirement_id / title / technique / polarity / rpn / extent / priority / status`，前端表格按 rank 展示。**风险高的用例排在最前**，符合 Chap5 MTP「Risk-Based Focus」。

## 2. 覆盖最小化（Minimize by Coverage Efficiency）

**算法**：贪心 set-cover。**覆盖单元 = 需求 × 技术 × 正负向（= Coverage Item × polarity）**。每轮选"新覆盖单元最多"的用例；平手时优先保留**高风险（RPN 小）、低耗时**用例。

| 指标 | 值 |
|---|---|
| 最小化前 | **96** 条 |
| 最小化后 | **65** 条 |
| 削减 | **31 条（-32.3%）** |
| 覆盖单元保持 | **65/65 = 100%** |
| 需求保持 | **14/14** |
| 需求×技术保持 | **39/39** |
| 覆盖是否下降 | ❌ 否（`full_coverage_retained = true`）|

**最小化后技术分布**（保留 65 条）：EP 20 / BVA 18 / ST 18 / DT 7 / SC 2 —— 五种技术全保留。
**移除 31 条**（覆盖冗余）：BVA 15 / EP 7 / DT 6 / SC 3 —— 主要是同一 (需求×技术×正负向) 下的多余边界点（如同一供电唤醒 CI 的 8.9/9.0/9.1 三点保留 1 条代表）。

> **覆盖不降证明**：最小化子集仍命中全部 65 个覆盖单元 → 每个 Coverage Item（按 需求×技术 映射，22/22）在正/负向上至少各留 1 条；每条需求、每种技术-需求组合都仍有用例。这正是 FR 7.0「在不降覆盖的前提下提升覆盖效率」。

---

## 2b. 最小化有效性验证（把 65 条回归到 VCU 上实跑对比）

> 问题：最小化删了 32% 用例，**效果还在吗？** 把最小化后的 65 条用同一适配器跑 VCU，与全量 96 条对比通过率、缺陷检出、分支覆盖。
> 复现：`SUITE_CASE_IDS=minimized_kept_ids.json coverage run --branch -m pytest tests/test_suite_from_design.py`（`test_suite_from_design.py` 支持 `SUITE_CASE_IDS` 子集过滤，默认跑全 96）。

| 指标 | 全量 96 条 | 最小化 65 条 | 结论 |
|---|---|---|---|
| 通过率 | 96/96 (100%) | **65/65 (100%)** | ✅ 全通过，被删的确为冗余 |
| 执行耗时 | 12.56s | **5.62s** | ✅ **-55%**（效率显著提升）|
| DEF-001 卡死检出 | ✅ | ✅（保留 2 条 REQ-012 卡死用例）| ✅ 核心缺陷仍复现 |
| simulator.py 语句覆盖（文件级）| 76.6%（180/226）| 75.4%（178/226）| -2 行 |
| simulator.py 分支覆盖（文件级）| 76/108 | 74/108 | -2 弧 |
| 纯 Module A 语句覆盖 | 95.8%（160/167）| ~94.6%（158/167）| -2 行 |
| 纯 Module A 分支覆盖 | 89.0%（73/82）| ~86.6%（71/82）| -2 弧 |

**丢失的恰好是 2 条"边界细分"分支**（`coverage_full96.json` vs `coverage_min65.json` 精确 diff）：
- **L199**（`_handle_sleep` 内 `self._rapid_sleep_timestamps = []`）= **快速循环计数复位**分支（间隔 ≥1s 时重置），只被被删的 REQ-012 **间隔边界**用例（interval=1.0s/1.1s 不触发）覆盖；
- **L239**（`_detect_wake_reason` 内 `return 0, "...持续时间不足"`）= **供电电压达标但时序不足**分支，只被被删的 REQ-001 BVA 时序负向用例覆盖。

**结论（最小化是否有效）**：
- ✅ **有效**：用例数 -32%、耗时 -55%，而**需求覆盖 14/14、Coverage Item 22/22、正负向、DEF-001 缺陷检出全部保留**，通过率仍 100%。
- ⚠ **代价透明**：最小化准则 `需求×技术×正负向`（= Coverage Item × polarity）**比分支级粗**，会把同一覆盖单元内的"边界细分变体"合并，因此损失 2 条分支弧（计数复位 / 时序不足）。即「覆盖效率↑，但分支覆盖 -2.4pp」——这是 set-cover 类最小化的固有取舍。
- **建议用法**：最小化套件适合**回归冒烟 / CI 快速门禁**（省 55% 时间、保住缺陷检出与 CI 覆盖）；**完整验收**仍跑全 96 条以覆盖全部边界分支。

> 证据：`fr7_optimization/coverage_full96.json`、`coverage_min65.json`、`minimized_kept_ids.json`（65 条 id）。

## 3. 实现位置
- 后端：`backend/api/services/optimize_service.py`（`prioritize_suite()` / `minimize_suite()`）+ 路由 `backend/api/routers/autotest_review.py`（`/api/optimize/prioritize`、`/api/optimize/minimize`）。
- 前端：`frontend/src/components/AutoTestDesignV2.tsx` 的 **Optimize (FR7.0)** 标签页（「按风险(RPN)排序」+「覆盖最小化」两个按钮，分别渲染优先级表与最小化统计/保留-移除明细）；`frontend/src/services/api.ts` 的 `optimizePrioritize` / `optimizeMinimize`。
- 证据快照：`fr7_optimization/prioritize.json`、`fr7_optimization/minimize.json`。

> 说明：原 Improve 页面的「基于执行结果的第二轮 LLM 用例增广」属**执行期改进**（已记于 §12 / `improvement_evidence.md`，后端 `/api/improve` 端点保留，入口已移至 Results 页底部）；本页面改为 FR 7.0 优化（优先级排序 + 最小化）。两者目的不同：增广（加用例）vs 优化（排序/最小化）。注：该 LLM 增广**不是 fuzz**（无随机/变异输入、强功能 oracle），Assignment 2 也无 fuzz 相关 FR。
