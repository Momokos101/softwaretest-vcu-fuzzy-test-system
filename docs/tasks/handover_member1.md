# Member 1 交接文档 — VCU 仿真器开发者（V2）

**交接日期**：2026-05
**交接人**：Member 1（VCU 仿真器开发者）
**接收方**：Member 2（工具开发者）、Member 3（测试执行者）、Member 5（文档统筹）

---

## 一、我做了什么

我完成了一个符合 `PROJECT_PLAN_V2.md` 的 VCU 行为仿真器。它是 AutoTestDesign Tool 的被测目标应用，用于演示从需求、风险分析、测试设计、测试执行到结果追踪的完整软件测试流程。

当前仿真器不再以旧版 `vehicle_state=170/30` 作为主语义，而是采用 V2 状态机：

| 状态 | 含义 |
|------|------|
| `state09` / `vehicle_state=9` | 休眠 |
| `state10` / `vehicle_state=10` | 初始化，或快速循环后卡死 |
| `state11` / `vehicle_state=11` | 正常运行 |
| `fault_protection` | 过压保护 |
| `undervoltage_shutdown` | 欠压关断 |

旧字段 `test_status`、`ready_flag`、`battery_voltage` 等仍保留，是为了兼容后端已有调用；新开发和测试应优先使用 V2 字段。

---

## 二、交付物清单

### 代码

| 文件 | 说明 |
|------|------|
| `vcu_simulator/main.py` | FastAPI 服务入口，端口 8001，注册 V2 API |
| `vcu_simulator/simulator.py` | Module A 状态机核心逻辑 |
| `vcu_simulator/models.py` | V2 请求/响应模型，保留兼容字段 |
| `vcu_simulator/constants.py` | V2 阈值配置和兼容常量 |
| `vcu_simulator/modules/signal_guard.py` | Module B：过压、欠压、去抖 |
| `vcu_simulator/modules/can_manager.py` | Module C：CAN ID 过滤、bus_off |
| `vcu_simulator/modules/dtc_manager.py` | Module D：DTC 记录、查询、清除 |
| `vcu_simulator/modules/power_monitor.py` | Module E：功耗告警、休眠功耗合规 |
| `tests/test_vcu_simulator_v2.py` | V2 仿真器测试 |

### 文档

| 文件 | 面向 | 内容 |
|------|------|------|
| `docs/tasks/simulator_api_for_tool.md` | Member 2 | V2 API、字段、curl 示例、对接检查清单 |
| `docs/tasks/simulator_spec_for_tester.md` | Member 3 | V2 被测对象说明、24 条需求、测试关注点 |
| `docs/Risk_Analysis_Report.md` | Member 4/5 | V2 风险分析报告，按 ISO 9126 和 RPN 组织 |
| `docs/local_plans/vcu_simulator_v2_modification_plan.md` | 本地记录 | 仿真器 V2 修改计划 |

---

## 三、启动方式

```bash
cd vcu_simulator
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

服务地址：`http://localhost:8001`
Swagger 文档：`http://localhost:8001/docs`

---

## 四、API 速查

| 端点 | 方法 | 用途 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/signals` | GET | 获取 V2 输入信号说明 |
| `/simulate` | POST | 正式 V2 仿真入口，覆盖唤醒/休眠/保护/CAN/功耗 |
| `/simulate/sleep` | POST | 兼容/演示用休眠快捷接口 |
| `/simulate/batch` | POST | 批量执行 `/simulate` |
| `/reset` | POST | 重置状态机，`clear_dtc=true` 时清除 DTC |
| `/state` | GET | 查询当前 VCU 状态 |
| `/config` | GET/PUT | 查询或修改阈值配置 |
| `/dtc` | GET | 查询 DTC 记录 |
| `/performance` | GET | 查询 `actual_duration` 统计 |

**重要约定**：

- 正式测试休眠条件时，使用 `/simulate` 的 h1/h2/h3 字段。
- `/simulate/sleep` 只是兼容旧版和演示用的快捷接口，不作为 h1/h2/h3 需求覆盖的正式证据。

---

## 五、正式休眠接口说明

V2 休眠条件为：

| 条件 | 字段 | 含义 |
|------|------|------|
| h1 | `VCUO_bDIAG_VCUIdle_flg=1` | VCU 空闲 |
| h2 | `VCUO_bDIAG_AuthComplete_flg=1` | 认证流程完成 |
| h3 | `can_stopped=true` | CAN 0x400~0x47F 停发 |

正式休眠测试请求：

```bash
curl -X POST http://localhost:8001/simulate \
  -H "Content-Type: application/json" \
  -d '{"VCUO_bDIAG_VCUIdle_flg":1,"VCUO_bDIAG_AuthComplete_flg":1,"can_stopped":true}'
```

期望：`vehicle_state=9, state_name=state09, test_status=3`。

---

## 六、验证结果

本地已通过：

```bash
vcu_simulator/.venv/bin/python -m unittest tests/test_vcu_simulator_v2.py
```

结果：

```text
Ran 15 tests
OK
```

覆盖点包括：

- 7 路唤醒 w1~w7
- 休眠 h1/h2/h3 必要且充分条件
- 过压、欠压、去抖
- CAN ID 边界和 bus_off
- DTC 记录、查询、清除
- 功耗告警和休眠功耗合规
- 快速唤醒-休眠循环导致 state10 卡死
- `/config` 阈值更新后影响仿真结果

---

## 七、交接注意事项

1. Member 2 对接时，以 `docs/tasks/simulator_api_for_tool.md` 为准。
2. Member 3 设计测试时，以 `docs/tasks/simulator_spec_for_tester.md` 和 `PROJECT_PLAN_V2.md` 的 24 条需求为准。
3. 不要再把旧版 `vehicle_state=170/30` 作为新测试的主 oracle。
4. `/simulate/sleep` 是快捷接口，不用于正式需求覆盖统计。
5. GAN 接口缺少 `model_weights/vcu` 是独立问题，不属于 VCU 仿真器 V2 的完成范围。
