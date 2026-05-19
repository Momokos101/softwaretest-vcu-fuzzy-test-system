# VCU仿真器说明文档

> 面向：Member 3（测试执行者）  
> 用途：了解测试对象的完整规格，以便设计测试计划和编写测试用例

---

## 1. 仿真器是什么

VCU仿真器是一个模拟汽车整车控制器（VCU）唤醒-休眠行为的软件程序。

**为什么用仿真器而不是真实硬件**：汽车行业在接入真实台架（HIL）前，标准流程是先对SIL（Software In the Loop）仿真模型进行测试。仿真器的所有边界值均来自5个真实BAIC VCU HIL测试数据库（db_10 / db_11 / db_15 / db / db_2，共**9615条**测试记录），具备充分的真实数据依据。

**仿真器地址**：`http://localhost:8001`（独立FastAPI服务，需先启动）

**启动方式**：
```bash
cd vcu_simulator
pip install -r requirements.txt
python main.py
```

---

## 2. 5个输入信号详细说明

### 2.1 信号总览表

| 信号名 | 物理含义 | 数据类型 | PASS区间 | FAIL区间 | 特殊值 |
|--------|---------|---------|---------|---------|--------|
| **CC2电压** | AC充电唤醒电压，充电桩提供的主唤醒信号 | float (V) | [4.8, 7.7]V | <4.8V 或 >7.8V | 12.0V→休眠, 7.8V→灰色边界 |
| **CC电压值** | 充电枪CC接触电压，检测线缆接触电阻 | float (V) | >4.0V（或0） | [0.1, 3.9]V | — |
| **CP幅值** | AC充电协议控制导引信号幅值 | float (V) | 0.0V（待机） | [9.1, 12.9]V | — |
| **供电电压** | 外部交流供电电压 | float (V) | 0.0V（无供电） | [9.1, 15.9]V | — |
| **网络唤醒报文使能状态** | 网络远程唤醒使能标志 | int (0/1) | 0（未使能） | 1（使能冲突） | — |

### 2.2 各信号物理背景

**CC2电压（最重要的信号）**  
当充电枪插入时，充电桩会通过CC2线提供一个约6~7V的直流电压，VCU检测到这个电压后判断"有充电枪插入→唤醒"。如果这个电压不在正常范围内，说明充电枪或充电桩有问题。12V是特殊指令，代表"请进入休眠"。

**CC电压值**  
充电枪内部有一根CC（Charge Connection）线，通过线缆电阻来告诉VCU充电枪是否正确连接。电阻偏低（对应电压0.1~3.9V）说明接触不良或用错了充电线。

**CP幅值**  
CP（Control Pilot）是AC充电协议的握手信号，正常待机时应该是0V。如果检测到9~13V的CP信号，说明协议通信出现了冲突或异常。

**供电电压**  
正常充电时VCU不应检测到外部AC供电。如果检测到9~16V的供电，说明有意外的电源接入，可能是过压故障。

**网络唤醒报文使能状态**  
VCU可以通过CAN网络被远程唤醒，但这个功能启用时（值=1）会和充电唤醒信号产生冲突，所以充电测试时应保持禁用（值=0）。

---

## 3. 所有输出字段含义

### 3.1 test_status（测试结果码）

| 值 | 含义 | 对应真实数据库 strategy |
|----|------|----------------------|
| `1` | **PASS** — 信号在有效区间，VCU正常唤醒 | strategy=0 |
| `3` | **SLEEP** — 接收到休眠指令，VCU正常进入休眠 | strategy=-3 |
| `4` | **FAIL** — 信号异常，VCU检测到故障 | strategy=1 |

### 3.2 vehicle_state（整车State状态）

| 值 | 含义 |
|----|------|
| `170` | 唤醒状态（VCU正常工作，可进行充电） |
| `30` | 休眠/故障状态（含正常休眠和故障两种情况，由test_status区分） |

> **注意**：真实数据库中还有state=12和state=46，但这些是与输入电压无关的偶发异常态（如硬件瞬态），无法通过特定信号值可靠触发，**仿真器不模拟这两个值**。

### 3.3 vehicle_mode（整车模式）

| 值 | 含义 |
|----|------|
| `5` | 唤醒模式（对应 test_status=1） |
| `2` | 休眠模式（对应 test_status=3 或 4） |

### 3.4 ready_flag（动力防盗允许READY标志位）

| 值 | 含义 | 与vehicle_state的关系 |
|----|------|----------------------|
| `1` | 允许就绪 | vehicle_state=170 时恒为1 |
| `0` | 禁止就绪 | vehicle_state=30 时恒为0 |

> **REQ-009约束**：ready_flag 与 vehicle_state 必须始终保持一致。

### 3.5 恒定输出字段

以下字段在所有测试场景中值固定不变（来自真实数据库统计）：

| 字段 | 恒定值 | 说明 |
|------|--------|------|
| `bms_wake_cmd` | 1 | BMS低压唤醒指令 |
| `mcu_wake_cmd` | 1 | MCU低压唤醒指令 |
| `battery_voltage` | 12.92V | 蓄电池电压 |
| `actual_duration` | ~100.3~100.6s | 模拟测试时长（基于真实HIL均值） |

---

## 4. 三个重要真实数据发现

这三点是从5个真实数据库分析中得到的关键修正，**在设计测试用例时必须准确理解**：

### 发现1：CC2=4.8V 能成功唤醒VCU（BVA下界）

- **数据来源**：db_2.db 中 CC2=4.8V 的6条记录
- **数据库记录**：test_status=4（因为这批被标注为 strategy=1 的异常注入测试，框架期望FAIL，VCU实际输出了PASS，所以框架判"异常"）
- **VCU实际行为**：CC2=4.8V → vehicle_state=**170**（VCU硬件成功唤醒）
- **仿真器结论**：CC2=4.8V → 返回 `test_status=1, vehicle_state=170`（PASS）
- **测试设计意义**：4.8V 是真实BVA下界，测试用例中 4.8V应为PASS，4.7V应为FAIL

### 发现2：休眠测试需要5个信号全部固定

- **数据来源**：3308条 strategy=-3 记录，type=2
- **规律**：休眠测试不是单信号测试，而是固定5信号组合同时发送：
  - CC2=12.0V（休眠触发值）
  - CC=12.0V，CP=0.0V，Supply=0.0V，NetWake=0.0
- **仿真器结论**：使用专用 `POST /simulate/sleep` 接口，响应 `test_status=3`
- **测试设计意义**：休眠测试必须用 `/simulate/sleep`，不能用 `/simulate` 单信号接口发CC2=12.0V来模拟

### 发现3：db_15 CC2有效上界扩展至8.1V（批次配置差异）

- **数据来源**：db_15.db，939条strategy=0的PASS记录
- **规律**：db_15中7.8V/7.9V/8.0V/8.1V均有PASS记录，与其他4个DB（最大7.7V）不同
- **原因**：db_15代表不同VCU固件版本或硬件批次，有效区间扩展到[4.9, 8.1]V
- **仿真器结论**：采用主流配置（4DB一致）：valid=[4.8, 7.7]V，7.8V统一判FAIL
- **测试设计意义**：7.8V是灰色边界测试用例，仿真器判FAIL，但真实世界中存在PASS的可能性

---

## 5. 10条VCU需求（完整版）

| ID | Title | Description | Category | 优先级 |
|----|-------|-------------|----------|--------|
| REQ-001 | CC2 Wake Voltage Valid Range | System shall accept CC2 voltage in [4.8V, 7.7V] as valid wake-up signal and output vehicle_state=170, vehicle_mode=5, ready_flag=1. Value 7.8V is a boundary case observed to FAIL in majority of real tests. | Input Validation | High |
| REQ-002 | CC2 Voltage Below Valid Range | System shall output test_status=4, vehicle_state=30, vehicle_mode=2, ready_flag=0 when CC2 voltage is below 4.8V. All 35 real test records with CC2 < 4.8V confirm vehicle_state=30. | Input Validation | High |
| REQ-003 | CC2 Voltage Above Valid Range | System shall output test_status=4, vehicle_state=30, vehicle_mode=2, ready_flag=0 when CC2 voltage exceeds 7.8V and is not the sleep trigger 12.0V. Real data: 37/38 records confirm state=30. | Input Validation | High |
| REQ-004 | Sleep Trigger Voltage | System shall output test_status=3, vehicle_state=30, vehicle_mode=2, ready_flag=0 when CC2 voltage equals exactly 12.0V with sleep command (type=2). | State Transition | High |
| REQ-005 | CC Voltage Cable Check | System shall output test_status=4, vehicle_state=30 when CC电压值 is in range [0.1V, 3.9V], indicating invalid cable contact resistance. | Safety | Medium |
| REQ-006 | CP Amplitude Interference Check | System shall output test_status=4, vehicle_state=30 when CP幅值 is in range [9.1V, 12.9V], indicating CP signal conflict or protocol anomaly. | Safety | Medium |
| REQ-007 | Supply Voltage Overvoltage Check | System shall output test_status=4, vehicle_state=30 when 供电电压 is in range [9.1V, 15.9V], indicating unexpected external supply or overvoltage. | Safety | Medium |
| REQ-008 | Network Wake Conflict Check | System shall output test_status=4, vehicle_state=30 when 网络唤醒报文使能状态=1 conflicts with CC2 wake protocol. Normal state is 0 (disabled). | Safety | Medium |
| REQ-009 | READY Flag Consistency | When vehicle_state=170 system shall set ready_flag=1. When vehicle_state=30 system shall set ready_flag=0. These two fields must always be consistent. | State Control | High |
| REQ-010 | Test Duration Compliance | Each single-signal test shall complete within 120 seconds. Based on real HIL data, actual_duration averages approximately 100 seconds. | Timing | Low |

---

## 6. 测试接口快速参考

```bash
# 启动仿真器（必须先完成）
cd vcu_simulator && python main.py

# 正常唤醒测试
curl -X POST http://localhost:8001/simulate \
  -H "Content-Type: application/json" \
  -d '{"signal_name": "CC2电压", "value": 6.3}'
# 期望: test_status=1, vehicle_state=170, ready_flag=1

# 越界FAIL测试
curl -X POST http://localhost:8001/simulate \
  -H "Content-Type: application/json" \
  -d '{"signal_name": "CC2电压", "value": 9.0}'
# 期望: test_status=4, vehicle_state=30, ready_flag=0

# 休眠测试
curl -X POST http://localhost:8001/simulate/sleep \
  -H "Content-Type: application/json" \
  -d '{}'
# 期望: test_status=3, vehicle_state=30, vehicle_mode=2
```
