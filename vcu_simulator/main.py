import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from models import (
    SimulateRequest, SleepRequest, SimulateResponse,
    HealthResponse, SignalInfo, ResetResponse, StateResponse,
    ConfigResponse, ConfigUpdateRequest, PerformanceResponse,
)
from simulator import VCUSimulator
from constants import VALID_SIGNAL_NAMES, DB15_NOTE

app = FastAPI(
    title="VCU行为仿真器",
    description=(
        "VCU唤醒-休眠控制模块行为仿真器（端口8001）。"
        "按PROJECT_PLAN_V2实现5模块VCU状态机，支持唤醒、休眠、CAN、DTC和功耗监控。"
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
    V2统一仿真入口。

    支持7路唤醒、3路休眠条件、Module B输入保护、Module C CAN管理、
    Module D DTC记录和Module E功耗监控。旧版signal_name/value字段保留兼容。
    """
    result = _simulator.simulate(**req.model_dump())
    return SimulateResponse(**result)


@app.post("/simulate/sleep", response_model=SimulateResponse, tags=["测试"])
def simulate_sleep(req: SleepRequest):
    """
    休眠测试（对应真实数据库 type=2，strategy=-3）。

    快捷发送 V2 休眠条件 h1/h2/h3。
    所有字段均有默认值，可直接发送空JSON `{}`。
    预期响应：test_status=3, vehicle_state=9, state_name=state09, vehicle_mode=2。
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

    raw = [r.model_dump() for r in requests]
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
            signal_name="供电电压",
            physical_meaning="w1硬线供电唤醒信号",
            pass_condition=">9.0V 且 duration_ms >= 10，vehicle_state=11",
            fail_condition="<=9.0V不唤醒；>16.0V过压保护；<6.0V欠压关断",
            data_type="float",
        ),
        SignalInfo(
            signal_name="CAN网络报文",
            physical_meaning="w2 CAN网络唤醒报文ID",
            pass_condition="can_msg_id ∈ [0x400, 0x47F]，vehicle_state=11",
            fail_condition="超出范围静默丢弃；bus_off时不唤醒",
            data_type="int",
        ),
        SignalInfo(
            signal_name="CP信号",
            physical_meaning="w3 CP信号",
            pass_condition="cp_voltage > 9.0V，vehicle_state=11",
            fail_condition="<=9.0V不唤醒",
            data_type="float",
        ),
        SignalInfo(
            signal_name="CC信号",
            physical_meaning="w4 CC信号",
            pass_condition="cc_voltage < 4.4V，vehicle_state=11",
            fail_condition=">=4.4V不唤醒",
            data_type="float",
        ),
        SignalInfo(
            signal_name="CC2信号",
            physical_meaning="w5 CC2 UBR电压下降沿",
            pass_condition="cc2_voltage < ubr_threshold，vehicle_state=11",
            fail_condition=">=ubr_threshold不唤醒",
            data_type="float",
        ),
        SignalInfo(
            signal_name="口盖信号",
            physical_meaning="w6口盖唤醒信号",
            pass_condition="hood_voltage > 4.0V 且 duration_ms >= 10，vehicle_state=11",
            fail_condition="值或时序不足不唤醒；duration_ms < 5视为噪声",
            data_type="float",
        ),
        SignalInfo(
            signal_name="门板信号",
            physical_meaning="w7门板唤醒信号",
            pass_condition="door_voltage < 1.0V 且 duration_ms >= 10，vehicle_state=11",
            fail_condition="值或时序不足不唤醒；duration_ms < 5视为噪声",
            data_type="float",
        ),
    ]


@app.post("/reset", response_model=ResetResponse, tags=["系统"])
def reset(clear_dtc: bool = False):
    """
    重置仿真器状态机到state09。clear_dtc=true时将所有DTC置为cleared。
    """
    _simulator.reset(clear_dtc=clear_dtc)
    message = "仿真器状态已重置到state09"
    if clear_dtc:
        message += "，DTC已清除"
    return ResetResponse(success=True, message=message)


@app.get("/state", response_model=StateResponse, tags=["系统"])
def get_state():
    """查询当前VCU状态。"""
    return StateResponse(**_simulator.get_state())


@app.get("/config", response_model=ConfigResponse, tags=["系统"])
def get_config():
    """查询所有V2阈值配置。"""
    return ConfigResponse(config=_simulator.get_config())


@app.put("/config", response_model=ConfigResponse, tags=["系统"])
def update_config(req: ConfigUpdateRequest):
    """局部更新V2阈值配置。"""
    return ConfigResponse(config=_simulator.update_config(req.config))


@app.get("/dtc", tags=["诊断"])
def get_dtc():
    """查询所有DTC，包含active和cleared记录。"""
    return _simulator.dtc_manager.get_all()


@app.get("/performance", response_model=PerformanceResponse, tags=["系统"])
def get_performance():
    """查询actual_duration统计。"""
    return PerformanceResponse(**_simulator.get_performance())


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
