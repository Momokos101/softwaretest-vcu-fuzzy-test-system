# VCU仿真器 API 接口说明文档（V2）

> 面向：Member 2（工具开发者）
> 用途：AutoTestDesign Tool 后端中 `simulator_client.py` 对接 VCU V2 仿真器
> 仿真器地址：`http://localhost:8001`

---

## 概览

| 端点 | 方法 | 用途 |
|------|------|------|
| `/health` | GET | 健康检查，确认仿真器已启动 |
| `/signals` | GET | 获取 V2 输入信号说明 |
| `/simulate` | POST | 统一仿真入口，支持唤醒/休眠/保护/功耗监控 |
| `/simulate/sleep` | POST | 休眠快捷测试，自动发送 h1/h2/h3 |
| `/simulate/batch` | POST | 批量执行 `/simulate` 请求 |
| `/reset` | POST | 重置状态机；可清除 DTC |
| `/state` | GET | 查询当前 VCU 状态 |
| `/config` | GET/PUT | 查询或修改 V2 阈值配置 |
| `/dtc` | GET | 查询 DTC 记录 |
| `/performance` | GET | 查询 actual_duration 统计 |

---

## 状态与结果编码

| 字段 | V2 含义 |
|------|---------|
| `vehicle_state=9` | state09，休眠 |
| `vehicle_state=10` | state10，初始化/卡死 |
| `vehicle_state=11` | state11，正常运行 |
| `test_status=1` | PASS，预期唤醒成功 |
| `test_status=3` | SLEEP，预期休眠成功 |
| `test_status=4` | FAIL，错误输入、保护状态、bus_off 或卡死 |
| `result_type=expected` | 行为符合当前输入预期 |
| `result_type=error` | 输入无效、条件不足或故障触发 |

保护状态请优先查看 `state_name`：`fault_protection` 或 `undervoltage_shutdown`。

---

## 1. GET /health

响应示例：

```json
{
  "status": "ok",
  "service": "VCU行为仿真器",
  "port": 8001,
  "version": "1.0.0"
}
```

---

## 2. POST /simulate

### 唤醒输入字段

| 唤醒编号 | 字段 | 触发条件 | 备注 |
|---------|------|----------|------|
| w1 | `supply_voltage` + `duration_ms` | `supply_voltage > 9.0` 且 `duration_ms >= 10` | 过压/欠压/去抖适用 |
| w2 | `can_msg_id` | `0x400 <= can_msg_id <= 0x47F` | bus_off 时不唤醒 |
| w3 | `cp_voltage` | `cp_voltage > 9.0` | 无时序要求 |
| w4 | `cc_voltage` | `cc_voltage < 4.4` | 无时序要求 |
| w5 | `cc2_voltage` | `cc2_voltage < cc2_ubr_threshold` | 默认阈值 4.4 |
| w6 | `hood_voltage` + `duration_ms` | `hood_voltage > 4.0` 且 `duration_ms >= 10` | 去抖适用 |
| w7 | `door_voltage` + `duration_ms` | `door_voltage < 1.0` 且 `duration_ms >= 10` | 去抖适用 |

### 休眠输入字段

休眠必须同时满足：

```json
{
  "VCUO_bDIAG_VCUIdle_flg": 1,
  "VCUO_bDIAG_AuthComplete_flg": 1,
  "can_stopped": true
}
```

### 兼容输入

仍支持旧字段 `signal_name` + `value`，但会被转换成 V2 字段。新代码优先使用上面的 V2 字段。

### 响应体

```json
{
  "vehicle_state": 11,
  "vehicle_mode": 5,
  "power_current": 0.05,
  "bus_message_flag": 1,
  "pdcu_wake_reason": 1,
  "actual_duration": 14.7,
  "result_type": "expected",
  "power_alarm_flag": 0,
  "bus_off_flag": 0,
  "active_dtcs": [],
  "signal_guard_result": {"valid": true, "fault_type": null, "reason": "信号有效"},
  "detail": "供电电压=9.3V > 9V，持续15ms >= 10ms，Module B校验通过，唤醒成功",
  "state_name": "state11",
  "test_status": 1,
  "ready_flag": 1,
  "bms_wake_cmd": 1,
  "mcu_wake_cmd": 1,
  "battery_voltage": 12.92
}
```

### curl 示例

```bash
curl -X POST http://localhost:8001/simulate \
  -H "Content-Type: application/json" \
  -d '{"supply_voltage": 9.3, "duration_ms": 15}'
```

期望：`test_status=1, vehicle_state=11, pdcu_wake_reason=1`。

```bash
curl -X POST http://localhost:8001/simulate \
  -H "Content-Type: application/json" \
  -d '{"supply_voltage": 9.3, "duration_ms": 4}'
```

期望：`test_status=4, vehicle_state=9, signal_guard_result.fault_type=debounce_rejected`。

---

## 3. POST /simulate/sleep

快捷休眠接口。请求体字段均可省略，接口会发送 h1/h2/h3。

```bash
curl -X POST http://localhost:8001/simulate/sleep \
  -H "Content-Type: application/json" \
  -d '{}'
```

期望：`test_status=3, vehicle_state=9, state_name=state09, ready_flag=0`。

---

## 4. POST /simulate/batch

传入 `SimulateRequest` 数组，最多 500 条：

```json
[
  {"supply_voltage": 9.3, "duration_ms": 15},
  {"can_msg_id": 1024},
  {"cp_voltage": 8.0}
]
```

响应为结果数组，顺序与输入一致。兼容字段 `signal_name` 和 `input_value` 会随结果返回。

---

## 5. POST /reset

```bash
curl -X POST 'http://localhost:8001/reset?clear_dtc=true'
```

`clear_dtc=true` 时，所有 DTC 状态置为 `cleared`。

---

## 6. GET/PUT /config

`GET /config` 返回所有 V2 阈值。`PUT /config` 支持局部更新，更新后立即影响仿真逻辑。

示例：

```bash
curl -X PUT http://localhost:8001/config \
  -H "Content-Type: application/json" \
  -d '{"config":{"guard":{"overvoltage_threshold":15.0},"can":{"bus_off_threshold":3},"power":{"run_alarm_threshold_a":0.1}}}'
```

主要配置段：

| 配置段 | 说明 |
|--------|------|
| `wake` | w1-w7 唤醒阈值 |
| `guard` | 过压、欠压、去抖阈值 |
| `can` | CAN ID 范围和 bus_off 阈值 |
| `power` | 运行/休眠/卡死功耗阈值 |
| `timing` | type1/type2 时长和快速循环卡死阈值 |

---

## 7. GET /dtc

返回所有 DTC，包含：

```json
[
  {
    "code": "DTC_001",
    "count": 1,
    "first_seen": "2026-05-22T01:00:00",
    "last_seen": "2026-05-22T01:00:01",
    "status": "active",
    "reason": "连续快速唤醒-休眠导致 state10 卡死"
  }
]
```

---

## 快速对接检查清单

- [ ] `GET /health` 返回 `status=ok`
- [ ] `POST /simulate` supply=9.3V + duration=15ms → `test_status=1, vehicle_state=11`
- [ ] `POST /simulate` supply=9.3V + duration=4ms → `test_status=4`
- [ ] `POST /simulate/sleep` → `test_status=3, vehicle_state=9`
- [ ] `POST /simulate/batch` 数组返回顺序与输入一致
- [ ] `PUT /config` 后阈值变化能影响后续结果
