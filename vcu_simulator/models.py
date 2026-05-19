from pydantic import BaseModel, Field, field_validator
from typing import Optional
from constants import VALID_SIGNAL_NAMES


class SimulateRequest(BaseModel):
    signal_name: str = Field(..., description="信号名称，5种之一")
    value: float = Field(..., description="信号测试值")
    data_type: str = Field(default="float", description="数据类型：float 或 int")

    @field_validator("signal_name")
    @classmethod
    def validate_signal_name(cls, v):
        if v not in VALID_SIGNAL_NAMES:
            raise ValueError(
                f"未知信号名称: '{v}'。"
                f"合法信号为: {VALID_SIGNAL_NAMES}"
            )
        return v

    @field_validator("data_type")
    @classmethod
    def validate_data_type(cls, v):
        if v not in ("float", "int"):
            raise ValueError("data_type 必须为 'float' 或 'int'")
        return v


class SleepRequest(BaseModel):
    """休眠测试固定5信号组合（strategy=-3，type=2）"""
    cc2_voltage: float = Field(default=12.0, description="CC2电压，休眠触发固定值12.0V")
    cc_voltage: float = Field(default=12.0, description="CC电压值，休眠固定值")
    cp_amplitude: float = Field(default=0.0, description="CP幅值，休眠固定值")
    supply_voltage: float = Field(default=0.0, description="供电电压，休眠固定值")
    network_wake_enable: float = Field(default=0.0, description="网络唤醒使能，休眠固定值")


class SimulateResponse(BaseModel):
    """仿真器响应体，对应真实数据库 actual_output 关键字段"""
    test_status: int = Field(..., description="1=PASS, 3=SLEEP, 4=FAIL")
    vehicle_state: int = Field(..., description="整车State状态（170=唤醒, 30=休眠/失败）")
    vehicle_mode: int = Field(..., description="整车模式（5=唤醒模式, 2=休眠模式）")
    ready_flag: int = Field(..., description="动力防盗允许READY标志位（1=允许, 0=禁止）")
    bms_wake_cmd: int = Field(..., description="BMS低压唤醒指令（恒定=1）")
    mcu_wake_cmd: int = Field(..., description="MCU低压唤醒指令（恒定=1）")
    battery_voltage: float = Field(..., description="蓄电池电压（恒定=12.92V）")
    actual_duration: float = Field(..., description="模拟测试时长（秒）")
    detail: str = Field(..., description="判定详情说明")


class HealthResponse(BaseModel):
    status: str
    service: str
    port: int
    version: str


class SignalInfo(BaseModel):
    signal_name: str
    physical_meaning: str
    pass_condition: str
    fail_condition: str
    data_type: str
    note: Optional[str] = None


class ResetResponse(BaseModel):
    success: bool
    message: str
