# 成员 3 — 测试执行者 任务书

---

## 你在答辩中讲什么

**你讲"我们怎么测、测出了什么"**——作为真正"使用"AutoTestDesign 工具的那个人，展示整个测试流程：用工具导入需求、生成用例、对仿真器执行、分析结果。这部分最能体现工具的价值，也是 Detailed Test Design 文档（占 30 分）的直接来源。

答辩时间：约 3 分钟

---

## 你依赖谁

| 你需要的 | 来自 | 时间节点 |
|---------|-----|---------|
| `simulator_spec_for_tester.md`（5 信号说明） | 成员 1 | **第 1 周末** |
| VCU 仿真器在本地跑通 | 成员 1 | **第 1 周末** |
| 后端 FR1.0/1.1 API 可用 | 成员 2 | 第 2 周初 |
| 后端 FR2.0/3.0/6.0 全部可用 | 成员 2 | 第 2 周末 |

**等不到工具时怎么办：**
- 第 1 周：先用收到的 `simulator_spec_for_tester.md` 写 Test Plan 的 Project Scope、Test Items、Schedule 三节（这些不依赖工具）
- 第 2 周初：用工具的 FR1.0/1.1 导入需求并做解析，开始记录截图
- 第 2 周末：工具齐全后，用 EP/BVA/决策表生成测试用例，执行全部用例

---

## 你负责的工作

### 你不写新代码，但你写 pytest 脚本并执行

**编写 `tests/test_vcu_simulator.py`**

参考 `docs/DESIGN_PLAN.md` 第三节的脚本模板，完整的参数化用例：

```python
import pytest, httpx

SIMULATOR_URL = "http://localhost:8001"

@pytest.fixture(autouse=True)
def reset_simulator():
    httpx.post(f"{SIMULATOR_URL}/reset")

@pytest.mark.parametrize(
    "signal_name, value, exp_status, exp_state, exp_ready, tc_id",
    [
        # EP 用例
        ("CC2电压",   6.30, 1, 170, 1, "EP-CC2-V1"),
        ("CC2电压",   3.00, 4,  30, 0, "EP-CC2-I1"),
        ("CC2电压",   9.00, 4,  30, 0, "EP-CC2-I2"),
        ("CC2电压",  12.00, 3,  30, 0, "EP-CC2-S1"),
        ("CC电压值", 12.00, 1, 170, 1, "EP-CC-V1"),
        ("CC电压值",  2.00, 4,  30, 0, "EP-CC-I1"),
        ("CP幅值",    0.00, 1, 170, 1, "EP-CP-V1"),
        ("CP幅值",   11.00, 4,  30, 0, "EP-CP-I1"),
        ("供电电压",  0.00, 1, 170, 1, "EP-SV-V1"),
        ("供电电压", 12.50, 4,  30, 0, "EP-SV-I1"),
        ("网络唤醒报文使能状态", 0.0, 1, 170, 1, "EP-NW-V1"),
        ("网络唤醒报文使能状态", 1.0, 4,  30, 0, "EP-NW-I1"),
        # BVA 用例（CC2 7 点）
        ("CC2电压", 4.70, 4,  30, 0, "BVA-CC2-1"),
        ("CC2电压", 4.80, 1, 170, 1, "BVA-CC2-2"),
        ("CC2电压", 4.90, 1, 170, 1, "BVA-CC2-3"),
        ("CC2电压", 6.30, 1, 170, 1, "BVA-CC2-4"),
        ("CC2电压", 7.70, 1, 170, 1, "BVA-CC2-5"),
        ("CC2电压", 7.80, 4,  30, 0, "BVA-CC2-6"),
        ("CC2电压", 7.90, 4,  30, 0, "BVA-CC2-7"),
        # BVA 用例（CC电压值）
        ("CC电压值", 0.00, 1, 170, 1, "BVA-CC-1"),
        ("CC电压值", 0.10, 4,  30, 0, "BVA-CC-2"),
        ("CC电压值", 2.00, 4,  30, 0, "BVA-CC-3"),
        ("CC电压值", 3.90, 4,  30, 0, "BVA-CC-4"),
        ("CC电压值", 4.00, 1, 170, 1, "BVA-CC-5"),
        # BVA 用例（CP幅值）
        ("CP幅值",  0.00, 1, 170, 1, "BVA-CP-1"),
        ("CP幅值",  9.00, 1, 170, 1, "BVA-CP-2"),
        ("CP幅值",  9.10, 4,  30, 0, "BVA-CP-3"),
        ("CP幅值", 11.00, 4,  30, 0, "BVA-CP-4"),
        ("CP幅值", 12.90, 4,  30, 0, "BVA-CP-5"),
        ("CP幅值", 13.00, 1, 170, 1, "BVA-CP-6"),
        # BVA 用例（供电电压）
        ("供电电压",  0.00, 1, 170, 1, "BVA-SV-1"),
        ("供电电压",  9.00, 1, 170, 1, "BVA-SV-2"),
        ("供电电压",  9.10, 4,  30, 0, "BVA-SV-3"),
        ("供电电压", 12.50, 4,  30, 0, "BVA-SV-4"),
        ("供电电压", 15.90, 4,  30, 0, "BVA-SV-5"),
        ("供电电压", 16.00, 1, 170, 1, "BVA-SV-6"),
    ]
)
def test_vcu_single_signal(signal_name, value, exp_status, exp_state, exp_ready, tc_id):
    resp = httpx.post(f"{SIMULATOR_URL}/simulate",
                      json={"signal_name": signal_name, "value": value, "data_type": "float"},
                      timeout=10.0)
    assert resp.status_code == 200
    data = resp.json()
    assert data["test_status"] == exp_status, \
        f"[{tc_id}] {signal_name}={value}: status {data['test_status']} != {exp_status}"
    assert data["vehicle_state"] == exp_state, \
        f"[{tc_id}] {signal_name}={value}: state {data['vehicle_state']} != {exp_state}"
    assert data["ready_flag"] == exp_ready, \
        f"[{tc_id}] {signal_name}={value}: ready {data['ready_flag']} != {exp_ready}"

def test_sleep_command():
    resp = httpx.post(f"{SIMULATOR_URL}/simulate/sleep",
                      json={"cc2_voltage": 12.0, "cc_voltage": 12.0,
                            "cp_amplitude": 0.0, "supply_voltage": 0.0,
                            "network_wake_enable": 0.0})
    data = resp.json()
    assert data["test_status"] == 3
    assert data["vehicle_state"] == 30
    assert data["ready_flag"] == 0
```

**运行并保存结果：**
```bash
pip install pytest httpx
pytest tests/test_vcu_simulator.py -v --tb=short 2>&1 | tee docs/tasks/pytest_results.txt
```

---

## 你需要写的文档

### 文档 1：Detailed Test Design（Artifact 4，占 30 分）

**文件路径：** `docs/Detailed_Test_Design.md`

> 这是你用 AutoTestDesign 工具做测试的全过程记录，全部由你来写。

**第 1 节：Test Case Design**

你用工具生成用例后，将完整的用例设计整理成文档：

**EP 完整用例表（12 条）：**

| 用例 ID | 信号名 | 等价类 | 测试值 | 预期 test_status | 预期 vehicle_state | 预期 ready_flag | 覆盖需求 |
|--------|-------|-------|-------|----------------|------------------|----------------|---------|
| EP-CC2-V1 | CC2电压 | Valid | 6.30V | 1(PASS) | 170 | 1 | REQ-001 |
| EP-CC2-I1 | CC2电压 | Invalid-Low | 3.00V | 4(FAIL) | 30 | 0 | REQ-002 |
| ... |（完整填写 12 条）| | | | | | |

**BVA 完整用例表（24 条）：**
（参考 DESIGN_PLAN.md 第三节 3.2 的表格，全部复制并整理）

**决策表（8 条规则）：**
（参考 DESIGN_PLAN.md 第三节 3.3 的表格）

**每种技术的选型说明（各 2 句话）：**
- 为什么对 CC2电压 用 BVA：边界最关键，bug 最容易藏在 4.8V 和 7.7V 附近
- 为什么决策表测多信号组合：真实测试数据表明任一信号异常就导致整体 FAIL
- 为什么网络唤醒只用 EP：二值信号，穷举即覆盖完整

**工具截图（从 TestCaseDesign.tsx 界面截图）：**
- 生成用例前的参数设置界面
- 生成后的用例表格界面
- 执行进度界面（显示 PASS/FAIL）

**第 2 节：Test Tool Implementation**

描述测试工具的使用方式：

```markdown
## 工具 1：AutoTestDesign 工具（用例设计）
- 功能：需求导入 → 解析 → 风险分析 → 自动生成 EP/BVA/决策表用例
- 如何使用：访问 http://localhost:3000，按操作界面完成用例生成

## 工具 2：pytest + httpx（用例执行）
- 功能：直接调用 VCU 仿真器 API，参数化执行每条用例，比对结果
- 执行命令：pytest tests/test_vcu_simulator.py -v --tb=short

## Test Oracle（判定逻辑）
每条用例执行后，对比：
- 实际 test_status 是否等于预期
- 实际 vehicle_state 是否等于预期
- 实际 ready_flag 是否与 vehicle_state 一致（REQ-009 一致性验证）
三项全部匹配 → PASS，任一不匹配 → FAIL
```

**第 3 节：Test Result Analysis**

执行 pytest 后填写（等成员 2 工具完成后运行）：

```markdown
## 执行结果汇总
- 总用例数：37 条（12 EP + 24 BVA + 1 Sleep）
- 通过：X 条
- 失败：X 条
- 错误：X 条

## 覆盖率分析
- REQ-001：由 EP-CC2-V1/I1/I2 + BVA-CC2-1~7 覆盖 ✅
- REQ-002：由 EP-CC2-I1 + BVA-CC2-1 覆盖 ✅
- ...（逐条需求列出对应用例）

## 追踪矩阵
| 需求 | EP用例 | BVA用例 | DT规则 | 覆盖状态 |
|-----|-------|---------|-------|---------|
| REQ-001 | EP-CC2-V1,I1,I2 | BVA-CC2-1~7 | DT-R1~R4 | ✅ 已覆盖 |
| ... |

## 测试发现与改进（improvement with evidence）
（描述第一轮执行后发现的问题，以及你添加的新用例）
例：
- 发现：CC2=7.8V（BVA-CC2-6）在真实数据库中 PASS 和 FAIL 都有，
  为灰色边界，仿真器目前返回 FAIL。
- 改进：新增 BVA-CC2-6b（7.8V，测试 3 次取多数）验证边界稳定性。
```

### 文档 2：Test Plan —— Project Scope + Schedule + Organization Chart 三节

**交给成员 5 汇总。**

**Project Scope（约 400 字）：**
- 测试目标：使用 AutoTestDesign 工具对 VCU 仿真器进行系统性软件测试
- 测试范围：5 个输入信号的 EP/BVA/决策表测试 + 休眠触发测试
- 不在范围：VCU 固件逻辑、CAN 总线物理层
- 成功标准：37 条用例执行完毕，覆盖 10 条 VCU 需求

**Schedule / Checklist：**
```
Week 1: 收到 simulator_spec，开始写 Test Plan 框架
Week 2: 工具 FR1 可用，开始需求导入和风险分析截图
Week 3: 工具齐全，生成用例，执行 pytest，记录结果
Week 4: 完成 Detailed Test Design，准备答辩讲稿
```

**Organization Chart（画出5人分工图）：**
- 你自己写，描述 5 人各自在测试活动中的角色
- 参考 DESIGN_PLAN.md 中的 7 节 Organization Chart 说明

---

## 你需要交付给谁

| 交付物 | 交给谁 | 时间节点 |
|-------|-------|---------|
| `pytest_results.txt`（执行结果） | 成员 5 | 第 3 周末 |
| `Detailed_Test_Design.md`（完整版） | 成员 5 | 第 3 周末 |
| Test Plan 三节文字 | 成员 5 | 第 3 周初 |
| 工具操作截图（导入/执行/结果截图）| 成员 4、5 | 第 3 周末 |

---

## 答辩讲稿要点（约 3 分钟）

1. **测试流程概述**（30s）
   > "我作为测试设计者，使用 AutoTestDesign 工具对 VCU 仿真器进行了完整的测试设计与执行。整个流程是：导入需求 → 风险分析 → 用例生成 → 执行 → 结果分析。"

2. **三种技术的选择理由**（60s）
   - "我们对 5 个信号分别做了等价划分，共 12 条用例，覆盖有效类和无效类。"
   - "对 CC2 电压、CC 电压值等有精确数值边界的信号做了边界值分析，共 24 条，重点测 4.8V、7.7V、7.8V 这几个真实数据发现的边界点。"
   - "用决策表测多信号组合，验证了任一信号异常就导致整体 FAIL 的规律。"

3. **执行结果**（60s）
   > 展示 pytest 输出截图：
   > "共执行 37 条用例，通过 X 条，失败 X 条。所有 10 条 VCU 需求均有对应用例覆盖。"

4. **improvement with evidence**（30s）
   > "第一轮执行后，我们发现 CC2=7.8V 这个灰色边界在 5 个真实数据库中 PASS 和 FAIL 都有记录，工具生成的 BVA 用例成功识别了这个不确定性，这正是自动化测试工具的价值。"
