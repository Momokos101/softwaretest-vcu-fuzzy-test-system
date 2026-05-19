# VCU仿真器 API 接口说明文档

> 面向：Member 2（工具开发者）  
> 用途：AutoTestDesign Tool 后端中 `simulator_client.py` 对接仿真器所需的完整接口规范  
> 仿真器地址：`http://localhost:8001`

---

## 概览

| 端点 | 方法 | 用途 |
|------|------|------|
| `/health` | GET | 健康检查，确认仿真器已启动 |
| `/signals` | GET | 获取5个信号的边界说明 |
| `/simulate` | POST | 单信号测试（主要接口） |
| `/simulate/sleep` | POST | 休眠测试（固定5信号组合） |
| `/simulate/batch` | POST | 批量测试（数组输入） |
| `/reset` | POST | 重置状态机 |

---

## 1. GET /health — 健康检查

**用途**：工具后端启动时调用，确认仿真器服务正常。

**请求**：无请求体

**响应示例**：
```json
{
  "status": "ok",
  "service": "VCU行为仿真器",
  "port": 8001,
  "version": "1.0.0"
}
```

**curl 示例**：
```bash
curl http://localhost:8001/health
```

---

## 2. GET /signals — 获取信号边界说明

**用途**：工具前端"信号参考"页面或测试用例生成时调用，获取5个信号的有效/无效区间。

**响应字段**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `signal_name` | string | 信号名称 |
| `physical_meaning` | string | 物理含义 |
| `pass_condition` | string | PASS条件描述 |
| `fail_condition` | string | FAIL条件描述 |
| `data_type` | string | `float` 或 `int` |
| `note` | string（可选） | 附加说明（如db_15批次差异） |

**curl 示例**：
```bash
curl http://localhost:8001/signals
```

---

## 3. POST /simulate — 单信号测试（主接口）

**用途**：AutoTestDesign Tool 执行每一条测试用例时调用。每次发送一个信号，获取VCU判定结果。

### 请求体

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `signal_name` | string | 是 | 5种信号之一（见下方枚举） |
| `value` | float | 是 | 该信号的测试值 |
| `data_type` | string | 否 | `"float"`（默认）或 `"int"` |

**合法 signal_name 枚举（必须完全一致，含中文）**：
- `CC2电压`
- `CC电压值`
- `CP幅值`
- `供电电压`
- `网络唤醒报文使能状态`

### 响应体

| 字段 | 类型 | 含义 | 可能值 |
|------|------|------|--------|
| `test_status` | int | 测试结果 | `1`=PASS, `3`=SLEEP, `4`=FAIL |
| `vehicle_state` | int | 整车State状态 | `170`=唤醒, `30`=休眠/失败 |
| `vehicle_mode` | int | 整车模式 | `5`=唤醒模式, `2`=休眠模式 |
| `ready_flag` | int | READY标志位 | `1`=允许, `0`=禁止 |
| `bms_wake_cmd` | int | BMS低压唤醒指令 | 恒定 `1` |
| `mcu_wake_cmd` | int | MCU低压唤醒指令 | 恒定 `1` |
| `battery_voltage` | float | 蓄电池电压 | 恒定 `12.92` |
| `actual_duration` | float | 模拟测试时长（秒） | ~100.3~100.6 |
| `detail` | string | 判定详情说明 | 可读文本 |

### 判定结果速查表

| signal_name | 输入值范围 | test_status | vehicle_state |
|-------------|-----------|-------------|---------------|
| CC2电压 | [4.8, 7.7]V | 1 (PASS) | 170 |
| CC2电压 | 12.0V | 3 (SLEEP) | 30 |
| CC2电压 | 7.8V 或其他越界 | 4 (FAIL) | 30 |
| CC电压值 | [0.1, 3.9]V | 4 (FAIL) | 30 |
| CC电压值 | 其他 | 1 (PASS) | 170 |
| CP幅值 | [9.1, 12.9]V | 4 (FAIL) | 30 |
| CP幅值 | 其他（含0V） | 1 (PASS) | 170 |
| 供电电压 | [9.1, 15.9]V | 4 (FAIL) | 30 |
| 供电电压 | 其他（含0V） | 1 (PASS) | 170 |
| 网络唤醒报文使能状态 | 1 | 4 (FAIL) | 30 |
| 网络唤醒报文使能状态 | 0 | 1 (PASS) | 170 |

### curl 示例

**正常唤醒（期望 PASS）**：
```bash
curl -X POST http://localhost:8001/simulate \
  -H "Content-Type: application/json" \
  -d '{"signal_name": "CC2电压", "value": 6.3, "data_type": "float"}'
```
期望响应：`test_status=1, vehicle_state=170, ready_flag=1`

**越界失败（期望 FAIL）**：
```bash
curl -X POST http://localhost:8001/simulate \
  -H "Content-Type: application/json" \
  -d '{"signal_name": "CC2电压", "value": 9.0, "data_type": "float"}'
```
期望响应：`test_status=4, vehicle_state=30, ready_flag=0`

---

## 4. POST /simulate/sleep — 休眠测试

**用途**：测试VCU在固定5信号组合下进入休眠状态的行为。

### 请求体（所有字段均有默认值，可直接发送 `{}`）

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `cc2_voltage` | float | 12.0 | CC2电压，休眠触发固定值 |
| `cc_voltage` | float | 12.0 | CC电压值 |
| `cp_amplitude` | float | 0.0 | CP幅值 |
| `supply_voltage` | float | 0.0 | 供电电压 |
| `network_wake_enable` | float | 0.0 | 网络唤醒使能 |

### curl 示例

```bash
curl -X POST http://localhost:8001/simulate/sleep \
  -H "Content-Type: application/json" \
  -d '{"cc2_voltage":12.0,"cc_voltage":12.0,"cp_amplitude":0.0,"supply_voltage":0.0,"network_wake_enable":0.0}'
```
期望响应：`test_status=3, vehicle_state=30, vehicle_mode=2, ready_flag=0`

---

## 5. POST /simulate/batch — 批量测试

**用途**：一次发送多个测试用例，减少HTTP往返次数。

### 请求体

传入 `SimulateRequest` 数组，最多500条：
```json
[
  {"signal_name": "CC2电压", "value": 4.8},
  {"signal_name": "CC2电压", "value": 4.9},
  {"signal_name": "CC电压值", "value": 2.0},
  {"signal_name": "网络唤醒报文使能状态", "value": 1}
]
```

### 响应

返回结果数组，每条额外包含 `signal_name` 和 `input_value` 字段，顺序与输入一致。

### curl 示例

```bash
curl -X POST http://localhost:8001/simulate/batch \
  -H "Content-Type: application/json" \
  -d '[{"signal_name":"CC2电压","value":4.8},{"signal_name":"CC2电压","value":9.0}]'
```

---

## 6. POST /reset — 重置状态机

**用途**：仿真器当前为无状态设计，此接口保留用于未来有状态扩展。

```bash
curl -X POST http://localhost:8001/reset
```
响应：`{"success": true, "message": "仿真器状态已重置（当前为无状态模式）"}`

---

## 错误响应

| HTTP状态码 | 场景 | 示例 |
|-----------|------|------|
| 422 | 字段校验失败（signal_name非法、缺少必填字段） | `{"detail": [{"msg": "..."}]}` |
| 400 | 业务逻辑错误（批量数组为空、超过500条） | `{"detail": "请求数组不能为空"}` |

---

## 快速对接检查清单

- [ ] `GET /health` 返回 `status=ok`
- [ ] `POST /simulate` CC2=6.3V → `test_status=1, vehicle_state=170`
- [ ] `POST /simulate` CC2=9.0V → `test_status=4, vehicle_state=30`
- [ ] `POST /simulate/sleep` → `test_status=3, vehicle_state=30`
- [ ] `POST /simulate/batch` 数组返回顺序与输入一致
