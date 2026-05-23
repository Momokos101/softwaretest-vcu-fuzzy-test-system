# VCU 仿真器说明文档（V2）

> 面向：Member 3（测试执行者）  
> 用途：了解 VCU V2 被测对象规格，以便设计测试计划、测试用例和追踪矩阵。

---

## 1. 被测对象概述

VCU 仿真器是一个 Software-in-the-Loop 被测目标应用，模拟整车控制器在唤醒、初始化、正常运行、休眠和故障保护中的行为。它通过 FastAPI 暴露 REST 接口，供 AutoTestDesign Tool 执行测试用例。

仿真器地址：`http://localhost:8001`

核心状态：

| 状态 | 输出 | 含义 |
|------|------|------|
| `state09` | `vehicle_state=9` | 休眠 |
| `state10` | `vehicle_state=10` | 初始化，或快速循环后卡死 |
| `state11` | `vehicle_state=11` | 正常运行 |
| `fault_protection` | `state_name=fault_protection` | 过压保护 |
| `undervoltage_shutdown` | `state_name=undervoltage_shutdown` | 欠压关断 |

---

## 2. 模块划分

| 模块 | 名称 | 测试重点 |
|------|------|----------|
| Module A | 电源状态管理 | 7 路唤醒、3 条休眠条件、state10 卡死 |
| Module B | 信号有效性保护 | 过压、欠压、去抖 |
| Module C | CAN 总线通信管理 | CAN ID 过滤、bus_off |
| Module D | 诊断与故障管理 | DTC_001/002/003 记录、查询、清除 |
| Module E | 功耗监控 | 运行功耗告警、休眠功耗合规 |

---

## 3. 输入条件

### 3.1 唤醒条件 w1~w7

| 编号 | 输入字段 | 触发条件 | 期望 |
|------|----------|----------|------|
| w1 | `supply_voltage` + `duration_ms` | `supply_voltage > 9.0` 且 `duration_ms >= 10` | `state11`, `pdcu_wake_reason=1` |
| w2 | `can_msg_id` | `0x400 <= can_msg_id <= 0x47F` | `state11`, `pdcu_wake_reason=2` |
| w3 | `cp_voltage` | `cp_voltage > 9.0` | `state11`, `pdcu_wake_reason=3` |
| w4 | `cc_voltage` | `cc_voltage < 4.4` | `state11`, `pdcu_wake_reason=4` |
| w5 | `cc2_voltage` | `cc2_voltage < cc2_ubr_threshold` | `state11`, `pdcu_wake_reason=5` |
| w6 | `hood_voltage` + `duration_ms` | `hood_voltage > 4.0` 且 `duration_ms >= 10` | `state11`, `pdcu_wake_reason=6` |
| w7 | `door_voltage` + `duration_ms` | `door_voltage < 1.0` 且 `duration_ms >= 10` | `state11`, `pdcu_wake_reason=7` |

### 3.2 休眠条件 h1~h3

休眠必须三个条件同时满足：

| 编号 | 输入字段 | 条件 | 说明 |
|------|----------|------|------|
| h1 | `VCUO_bDIAG_VCUIdle_flg` | `=1` | VCU 空闲 |
| h2 | `VCUO_bDIAG_AuthComplete_flg` | `=1` | 认证完成 |
| h3 | `can_stopped` | `true` | CAN 0x400~0x47F 停发 |

正式休眠测试必须通过 `/simulate` 输入 h1/h2/h3。`/simulate/sleep` 是兼容/演示快捷接口，不用于正式覆盖统计。

---

## 4. 输出字段

| 字段 | 含义 |
|------|------|
| `vehicle_state` | 9/10/11 主状态编码 |
| `state_name` | `state09/state10/state11/fault_protection/undervoltage_shutdown` |
| `vehicle_mode` | 5=运行，2=休眠/故障 |
| `power_current` | 当前功耗电流 |
| `bus_message_flag` | state11 正常通信为 1；state09、欠压、bus_off 为 0 |
| `pdcu_wake_reason` | 1~7 对应 w1~w7，0 表示无唤醒 |
| `actual_duration` | 模拟执行时长 |
| `result_type` | `expected` 或 `error` |
| `power_alarm_flag` | 功耗告警 |
| `bus_off_flag` | CAN bus_off 标志 |
| `active_dtcs` | 当前 active DTC 列表 |
| `signal_guard_result` | Module B 校验结果 |
| `test_status` | 兼容字段：1=PASS，3=SLEEP，4=FAIL |

---

## 5. V2 需求列表（24 条）

| ID | 模块 | 标题 | 期望行为 |
|----|------|------|----------|
| REQ-001 | A | 硬线供电唤醒 | `supply_voltage > 9V` 且 `duration_ms >= 10` 时唤醒 |
| REQ-002 | A/C | CAN 网络唤醒 | `can_msg_id` 在 `[0x400,0x47F]` 内时唤醒 |
| REQ-003 | A | CP 信号唤醒 | `cp_voltage > 9V` 时唤醒 |
| REQ-004 | A | CC 信号唤醒 | `cc_voltage < 4.4V` 时唤醒 |
| REQ-005 | A | CC2 信号唤醒 | `cc2_voltage < ubr_threshold` 时唤醒 |
| REQ-006 | A | 口盖信号唤醒 | `hood_voltage > 4V` 且 `duration_ms >= 10` 时唤醒 |
| REQ-007 | A | 门板信号唤醒 | `door_voltage < 1V` 且 `duration_ms >= 10` 时唤醒 |
| REQ-008 | A | 休眠条件 h1 | h1 是休眠必要条件 |
| REQ-009 | A | 休眠条件 h2 | h2 是休眠必要条件 |
| REQ-010 | A/C | 休眠条件 h3 | h3 是休眠必要条件 |
| REQ-011 | A | 三条件同时休眠 | h1 AND h2 AND h3 同时满足才进入 state09 |
| REQ-012 | A/D | state10 卡死检测 | 快速唤醒-休眠循环触发卡死并记录 DTC_001 |
| REQ-013 | A | 输出一致性 | state11 时 `bus_message_flag=1`；state09 时为 0 |
| REQ-014 | A | 响应时序 | type1 `actual_duration <= 20s`；type2 `<= 60s` |
| REQ-015 | B | 过压保护 | `supply_voltage > 16V` 进入 `fault_protection` |
| REQ-016 | B | 欠压保护 | `supply_voltage < 6V` 进入 `undervoltage_shutdown` |
| REQ-017 | B | 信号去抖 | w1/w6/w7 `duration_ms < 5` 视为噪声 |
| REQ-018 | C | CAN ID 过滤 | 只处理 `[0x400,0x47F]`，越界不唤醒 |
| REQ-019 | C | CAN bus_off | `error_counter > 255` 后 `bus_off_flag=1` |
| REQ-020 | D | DTC 生成 | 卡死、过压、欠压分别写入 DTC_001/002/003 |
| REQ-021 | D | DTC 查询 | `GET /dtc` 返回代码、状态、次数、时间戳 |
| REQ-022 | D | DTC 清除 | `POST /reset?clear_dtc=true` 将 DTC 置为 cleared |
| REQ-023 | E | 功耗告警 | state11 下高电流持续超阈值后告警 |
| REQ-024 | E | 休眠功耗合规 | state09 下 `power_current <= 0.01A` |

---

## 6. 推荐测试设计

| 测试套件 | 技术 | 覆盖重点 |
|----------|------|----------|
| Suite A | EP | 7 路唤醒的有效/无效类 |
| Suite B | BVA | 9V、10ms、4V、1V、6V、16V、5ms 等边界 |
| Suite C | Decision Table | h1/h2/h3 组合 |
| Suite D | State Transition | state09/state10/state11/保护状态 |
| Suite E | Scenario + Sequence | 快速循环触发 state10 卡死 |
| Suite F | EP + BVA | Module B 过压/欠压/去抖 |
| Suite G | EP + BVA + Decision Table | CAN ID 边界和 bus_off |
| Suite H | State + CRUD | DTC 生命周期 |
| Suite I | BVA | 功耗阈值 |
| Suite J | Performance Testing | `actual_duration` 时序合规 |

这组设计对应课程中的等价类、边界值、决策表、状态转移、场景测试、风险驱动测试和非功能测试。

---

## 7. 快速验证示例

```bash
# 唤醒
curl -X POST http://localhost:8001/simulate \
  -H "Content-Type: application/json" \
  -d '{"supply_voltage":9.3,"duration_ms":15}'

# 正式休眠
curl -X POST http://localhost:8001/simulate \
  -H "Content-Type: application/json" \
  -d '{"VCUO_bDIAG_VCUIdle_flg":1,"VCUO_bDIAG_AuthComplete_flg":1,"can_stopped":true}'

# 过压保护
curl -X POST http://localhost:8001/simulate \
  -H "Content-Type: application/json" \
  -d '{"supply_voltage":16.5,"duration_ms":15}'

# 查询 DTC
curl http://localhost:8001/dtc
```
