import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from models import (
    SimulateRequest, SleepRequest, SimulateResponse,
    HealthResponse, SignalInfo, ResetResponse,
)
from simulator import VCUSimulator
from constants import VALID_SIGNAL_NAMES, DB15_NOTE

app = FastAPI(
    title="VCU行为仿真器",
    description=(
        "VCU唤醒-休眠控制模块行为仿真器（端口8001）。"
        "模拟真实BAIC VCU HIL测试逻辑，支持5种输入信号的单次测试、休眠测试和批量测试。"
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_simulator = VCUSimulator()


@app.get("/health", response_model=HealthResponse, tags=["系统"])
def health_check():
    """健康检查，确认仿真器服务正常运行"""
    return HealthResponse(
        status="ok",
        service="VCU行为仿真器",
        port=8001,
        version="1.0.0",
    )


@app.post("/simulate", response_model=SimulateResponse, tags=["测试"])
def simulate(req: SimulateRequest):
    """
    单信号测试（对应真实数据库 type=1，strategy=0/1）。

    每次发送一个信号（名称+值），仿真器判断该信号是否在有效区间内，
    返回对应的VCU状态（PASS/FAIL/SLEEP）。

    **5种合法信号名称：**
    - CC2电压
    - CC电压值
    - CP幅值
    - 供电电压
    - 网络唤醒报文使能状态
    """
    result = _simulator.simulate(signal_name=req.signal_name, value=req.value)
    return SimulateResponse(**result)


@app.post("/simulate/sleep", response_model=SimulateResponse, tags=["测试"])
def simulate_sleep(req: SleepRequest):
    """
    休眠测试（对应真实数据库 type=2，strategy=-3）。

    固定5信号组合：CC2=12.0V触发休眠。
    所有字段均有默认值，可直接发送空JSON `{}`。
    预期响应：test_status=3, vehicle_state=30, vehicle_mode=2。
    """
    result = _simulator.simulate_sleep(
        cc2_voltage=req.cc2_voltage,
        cc_voltage=req.cc_voltage,
        cp_amplitude=req.cp_amplitude,
        supply_voltage=req.supply_voltage,
        network_wake_enable=req.network_wake_enable,
    )
    return SimulateResponse(**result)


@app.post("/simulate/batch", tags=["测试"])
def simulate_batch(requests: list[SimulateRequest]):
    """
    批量测试，传入信号数组，返回每条信号的判定结果数组。
    数组顺序与输入一致。
    """
    if not requests:
        raise HTTPException(status_code=400, detail="请求数组不能为空")
    if len(requests) > 500:
        raise HTTPException(status_code=400, detail="单次批量测试最多500条")

    raw = [{"signal_name": r.signal_name, "value": r.value} for r in requests]
    results = _simulator.simulate_batch(raw)
    return results


@app.get("/signals", response_model=list[SignalInfo], tags=["参考信息"])
def get_signals():
    """
    返回5个VCU输入信号的边界说明，包括物理含义、有效/无效区间。
    数据来源：5个真实BAIC VCU HIL测试数据库（共9615条记录）。
    """
    return [
        SignalInfo(
            signal_name="CC2电压",
            physical_meaning="AC充电唤醒电压，充电枪插入时由充电桩提供的主唤醒信号",
            pass_condition="[4.8V, 7.7V]（vehicle_state=170，正常唤醒）",
            fail_condition="<4.8V 或 >7.8V（vehicle_state=30）；7.8V为灰色边界统一判FAIL",
            data_type="float",
            note=f"特殊值：12.0V → 触发休眠(status=3)。{DB15_NOTE}",
        ),
        SignalInfo(
            signal_name="CC电压值",
            physical_meaning="充电枪CC接触电压，反映线缆接触电阻是否正常",
            pass_condition=">4.0V（正常接线或无充电枪）",
            fail_condition="[0.1V, 3.9V]（接触不良/错误线阻，vehicle_state=30）",
            data_type="float",
        ),
        SignalInfo(
            signal_name="CP幅值",
            physical_meaning="控制导引信号幅值，AC充电协议握手信号",
            pass_condition="0.0V（待机状态，无充电协议通信）",
            fail_condition="[9.1V, 12.9V]（协议冲突或幅值异常，vehicle_state=30）",
            data_type="float",
        ),
        SignalInfo(
            signal_name="供电电压",
            physical_meaning="外部交流供电电压，正常充电时应无额外供电",
            pass_condition="0.0V（无外部供电，正常状态）",
            fail_condition="[9.1V, 15.9V]（意外供电/过压，vehicle_state=30）",
            data_type="float",
        ),
        SignalInfo(
            signal_name="网络唤醒报文使能状态",
            physical_meaning="网络远程唤醒使能标志，控制是否允许通过CAN网络远程唤醒VCU",
            pass_condition="0（未使能，不干扰CC2充电唤醒）",
            fail_condition="1（已使能，与CC2唤醒协议冲突，vehicle_state=30）",
            data_type="int",
        ),
    ]


@app.post("/reset", response_model=ResetResponse, tags=["系统"])
def reset():
    """
    重置仿真器状态机。
    当前仿真器为无状态设计（每次请求独立判定），
    此端点保留用于未来有状态扩展，现在始终返回成功。
    """
    return ResetResponse(success=True, message="仿真器状态已重置（当前为无状态模式）")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
