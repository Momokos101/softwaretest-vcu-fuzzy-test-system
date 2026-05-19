# Member 1 交接文档 — VCU仿真器开发者

**交接日期**：2026-05  
**交接人**：Member 1（VCU仿真器开发者）  
**接收方**：Member 2（工具开发者）、Member 3（测试执行者）、Member 5（文档统筹）

---

## 一、我做了什么（一句话）

我建了一个"假的VCU芯片"程序，让整个测试工具有真实的测试对象可以打。

---

## 二、交付物清单

### 代码（全部在 `vcu_simulator/` 目录）

| 文件 | 说明 |
|------|------|
| `vcu_simulator/main.py` | FastAPI服务入口，端口8001，注册全部6个API端点 |
| `vcu_simulator/simulator.py` | 核心判定逻辑：VCUSimulator类，5信号PASS/FAIL/SLEEP判定 |
| `vcu_simulator/models.py` | 请求/响应数据模型，含字段合法性校验 |
| `vcu_simulator/constants.py` | 5个信号的边界常量（来自5个真实数据库，共9615条记录） |
| `vcu_simulator/requirements.txt` | 依赖：fastapi, uvicorn, pydantic |

### 文档

| 文件 | 面向 | 内容 |
|------|------|------|
| `docs/tasks/simulator_api_for_tool.md` | **Member 2** | 全部API端点的URL、字段说明、curl示例、对接检查清单 |
| `docs/tasks/simulator_spec_for_tester.md` | **Member 3** | 5信号物理含义、所有输出值含义、10条需求、3个真实数据发现 |
| `docs/Risk_Analysis_Report.md` | **Member 5** | 7章风险分析报告（Artifact 2），含需求列表、评分表、风险矩阵、测试优先级、Test Items附录 |

---

## 三、启动方式

```bash
# 进入仿真器目录
cd vcu_simulator

# 首次运行：建虚拟环境并安装依赖
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 启动（之后每次直接这一条）
python main.py
# 服务运行在 http://localhost:8001
# Swagger文档在 http://localhost:8001/docs
```

---

## 四、API速查（Member 2 重点看）

仿真器地址：`http://localhost:8001`

| 端点 | 方法 | 用途 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/signals` | GET | 5个信号的边界说明 |
| `/simulate` | POST | **主接口**：单信号测试 |
| `/simulate/sleep` | POST | 休眠测试（固定5信号组合） |
| `/simulate/batch` | POST | 批量测试（数组） |
| `/reset` | POST | 重置状态机 |

**最常用的请求格式**：
```bash
# 单信号测试
curl -X POST http://localhost:8001/simulate \
  -H "Content-Type: application/json" \
  -d '{"signal_name": "CC2电压", "value": 6.3}'

# 返回
{
  "test_status": 1,       # 1=PASS, 3=SLEEP, 4=FAIL
  "vehicle_state": 170,   # 170=唤醒, 30=休眠/故障
  "vehicle_mode": 5,      # 5=唤醒模式, 2=休眠模式
  "ready_flag": 1,        # 1=允许, 0=禁止
  ...
}
```

**5个合法的 signal_name**（字段名必须完全一致，含中文）：
- `CC2电压`
- `CC电压值`
- `CP幅值`
- `供电电压`
- `网络唤醒报文使能状态`

---

## 五、判定逻辑速查（Member 3 重点看）

| signal_name | 输入值 | test_status | vehicle_state |
|-------------|--------|-------------|---------------|
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

> **重要**：CC2=7.8V 是灰色边界，仿真器统一返回 FAIL（主流4个DB行为）

---

## 六、验证结果（已通过）

以下场景均经过本地curl验证，结果全部正确：

- ✓ 正常唤醒（CC2=6.3V → status=1, state=170）
- ✓ 越界FAIL（CC2=9.0V → status=4, state=30）
- ✓ 休眠测试（/simulate/sleep → status=3, state=30）
- ✓ BVA下界（CC2=4.8V → PASS）
- ✓ BVA下界-1（CC2=4.7V → FAIL）
- ✓ BVA上界（CC2=7.7V → PASS）
- ✓ 灰色边界（CC2=7.8V → FAIL）
- ✓ 全部4个其他信号的PASS/FAIL场景
- ✓ 批量测试接口（/simulate/batch）
- ✓ 非法信号名校验（HTTP 422）
- ✓ /signals 端点返回5个信号说明
- ✓ /reset 端点

---

## 七、注意事项

1. **仿真器必须先启动**，Member 2 的工具后端才能调用 `/simulate`。建议 Member 2 在 `simulator_client.py` 中先用 `GET /health` 确认连通性再发测试请求。

2. **vcu_simulator/.venv/** 已加入 .gitignore（或应加入），不需要提交虚拟环境。

3. **db_15 批次差异**：真实数据中 db_15 的 CC2 有效上界是 8.1V（与其他4个DB不同）。仿真器采用主流配置 [4.8, 7.7]V。如果 Member 3 设计了 CC2=7.9V 的 PASS 用例，仿真器会返回 FAIL，这是正常的——那是测试 db_15 批次差异的用例，应在报告中特别标注。

4. **state=12 / state=46 不在仿真器中**：这两个状态存在于真实数据库，但它们是与输入电压无关的偶发硬件异常态，无法通过特定信号值可靠触发，仿真器不模拟。

---

## 八、文档对接关系图

```
Member 1（我）
    │
    ├──→ Member 2：simulator_api_for_tool.md
    │         （接口格式、字段名、curl示例、对接检查清单）
    │
    ├──→ Member 3：simulator_spec_for_tester.md
    │         （信号物理含义、输出值含义、10条需求、3个数据发现）
    │
    └──→ Member 5：Risk_Analysis_Report.md
              （Artifact 2，7章，含 Test Items 附录）
```
