from pydantic import BaseModel, Field, field_validator
from typing import Any, Optional
from constants import VALID_SIGNAL_NAMES


class SimulateRequest(BaseModel):
    signal_name: Optional[str] = Field(default=None, description="兼容字段或V2信号名称")
    value: Optional[float] = Field(default=None, description="兼容字段或V2信号值")
    data_type: str = Field(default="float", description="数据类型：float 或 int")
    duration_ms: Optional[int] = Field(default=None, description="有时序要求信号的持续时间")

    supply_voltage: Optional[float] = Field(default=None, description="w1 供电电压")
    can_msg_id: Optional[int] = Field(default=None, description="w2 CAN报文ID")
    cp_voltage: Optional[float] = Field(default=None, description="w3 CP信号电压")
    cc_voltage: Optional[float] = Field(default=None, description="w4 CC信号电压")
    cc2_voltage: Optional[float] = Field(default=None, description="w5 CC2信号电压")
    hood_voltage: Optional[float] = Field(default=None, description="w6 口盖信号电压")
    door_voltage: Optional[float] = Field(default=None, description="w7 门板信号电压")

    VCUO_bDIAG_VCUIdle_flg: Optional[int] = Field(default=None, description="h1 VCUIdle_flg")
    VCUO_bDIAG_AuthComplete_flg: Optional[int] = Field(default=None, description="h2 AuthComplete_flg")
    can_stopped: Optional[bool] = Field(default=None, description="h3 CAN 0x400~0x47F停发")

    can_error_count: int = Field(default=0, description="本次注入的CAN错误数量")
    power_current: Optional[float] = Field(default=None, description="当前功耗电流A")

    @field_validator("signal_name")
    @classmethod
    def validate_signal_name(cls, v):
        v2_names = {"供电电压", "CP信号", "CC信号", "CC2信号", "口盖信号", "门板信号", "CAN网络报文"}
        if v is not None and v not in VALID_SIGNAL_NAMES and v not in v2_names:
            raise ValueError(
                f"未知信号名称: '{v}'。"
                f"合法信号为: {VALID_SIGNAL_NAMES + sorted(v2_names)}"
            )
        return v

    @field_validator("data_type")
    @classmethod
    def validate_data_type(cls, v):
        if v not in ("float", "int"):
            raise ValueError("data_type 必须为 'float' 或 'int'")
        return v


class SleepRequest(BaseModel):
    """V2休眠快捷测试请求；接口会发送h1/h2/h3。"""
    cc2_voltage: float = Field(default=12.0, description="CC2电压，休眠触发固定值12.0V")
    cc_voltage: float = Field(default=12.0, description="CC电压值，休眠固定值")
    cp_amplitude: float = Field(default=0.0, description="CP幅值，休眠固定值")
    supply_voltage: float = Field(default=0.0, description="供电电压，休眠固定值")
    network_wake_enable: float = Field(default=0.0, description="网络唤醒使能，休眠固定值")


class SimulateResponse(BaseModel):
    """V2仿真器响应体，保留部分旧字段用于后端兼容。"""
    vehicle_state: int = Field(..., description="9=休眠, 10=初始化, 11=运行")
    vehicle_mode: int = Field(..., description="整车模式（5=唤醒模式, 2=休眠模式）")
    power_current: float = Field(..., description="当前功耗电流A")
    bus_message_flag: int = Field(..., description="CAN通信标志")
    pdcu_wake_reason: int = Field(..., description="唤醒原因编号")
    actual_duration: float = Field(..., description="模拟测试时长（秒）")
    result_type: str = Field(..., description="expected 或 error")
    power_alarm_flag: int = Field(..., description="功耗告警")
    bus_off_flag: int = Field(..., description="CAN bus_off 标志")
    active_dtcs: list[str] = Field(default_factory=list, description="当前active DTC代码")
    signal_guard_result: dict[str, Any] = Field(default_factory=dict, description="Module B校验结果")
    detail: str = Field(..., description="判定详情说明")
    state_name: str = Field(default="state09", description="状态名称")

    test_status: int = Field(default=1, description="兼容字段：1=PASS, 3=SLEEP, 4=FAIL")
    ready_flag: int = Field(default=0, description="兼容字段")
    bms_wake_cmd: int = Field(default=1, description="兼容字段")
    mcu_wake_cmd: int = Field(default=1, description="兼容字段")
    battery_voltage: float = Field(default=12.92, description="兼容字段")


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


class StateResponse(BaseModel):
    vehicle_state: int
    state_name: str
    vehicle_mode: int
    bus_message_flag: int
    power_alarm_flag: int
    bus_off_flag: int
    active_dtcs: list[str]


class ConfigResponse(BaseModel):
    config: dict[str, Any]


class ConfigUpdateRequest(BaseModel):
    config: dict[str, Any]


class PerformanceResponse(BaseModel):
    total_requests: int
    type1_requests: int
    type2_requests: int
    max_actual_duration: float
    average_actual_duration: float
    durations: list[float]
