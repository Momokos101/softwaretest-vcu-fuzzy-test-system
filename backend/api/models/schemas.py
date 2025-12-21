"""
Pydantic数据模型定义
用于API请求和响应的数据验证
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum

# ========== 测试计划相关模型 ==========

class TestMode(str, Enum):
    """测试模式枚举"""
    TRADITIONAL = "traditional"  # 传统模糊测试
    GAN = "gan"  # GAN智能测试
    BOTH = "both"  # 两种模式都启用

class TraditionalTestConfig(BaseModel):
    """传统测试配置"""
    enabled: bool = True
    mutation_rules: List[str] = Field(default_factory=lambda: [
        "single_param", "multi_param", "timing_perturb", "repeat"
    ])
    intensity: int = Field(default=5, ge=1, le=10, description="变异强度 1-10")
    max_cases: Optional[int] = Field(default=None, description="最大用例数")

class GANTestConfig(BaseModel):
    """GAN测试配置"""
    enabled: bool = True
    model_version: str = Field(default="v1.0", description="模型版本")
    sampling_temperature: float = Field(default=1.0, ge=0.1, le=2.0, description="采样温度")
    max_cases: Optional[int] = Field(default=None, description="最大用例数")

class ConstraintConfig(BaseModel):
    """约束配置"""
    dbc_file_path: Optional[str] = Field(default=None, description="DBC文件路径")
    whitelist: List[str] = Field(default_factory=list, description="信号白名单")
    blacklist: List[str] = Field(default_factory=list, description="禁发列表")
    value_ranges: Dict[str, Dict[str, float]] = Field(
        default_factory=dict, 
        description="数值范围约束，格式: {signal_name: {min: x, max: y}}"
    )
    rate_limit: float = Field(default=100.0, description="报文发送速率上限 (pkt/s)")
    crc_check: bool = Field(default=True, description="是否启用CRC校验")
    dlc_check: bool = Field(default=True, description="是否启用DLC长度检查")

class TestPlanCreate(BaseModel):
    """创建测试计划请求"""
    name: str = Field(..., description="测试计划名称")
    description: Optional[str] = Field(default=None, description="描述")
    test_mode: TestMode = Field(default=TestMode.BOTH, description="测试模式")
    traditional_config: Optional[TraditionalTestConfig] = Field(default=None)
    gan_config: Optional[GANTestConfig] = Field(default=None)
    constraint_config: ConstraintConfig = Field(..., description="约束配置")
    baseline_log_path: Optional[str] = Field(default=None, description="基准日志路径(BLF/ASC)")

class TestPlanResponse(BaseModel):
    """测试计划响应"""
    id: str
    name: str
    description: Optional[str]
    test_mode: TestMode
    traditional_config: Optional[TraditionalTestConfig]
    gan_config: Optional[GANTestConfig]
    constraint_config: ConstraintConfig
    baseline_log_path: Optional[str]
    created_at: datetime
    updated_at: datetime
    status: str  # draft, active, completed

# ========== 测试任务相关模型 ==========

class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"  # 待执行
    RUNNING = "running"  # 运行中
    PAUSED = "paused"  # 已暂停
    STOPPED = "stopped"  # 已停止
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败

class TestTaskResponse(BaseModel):
    """测试任务响应"""
    id: str
    plan_id: str
    status: TaskStatus
    traditional_stats: Dict[str, Any] = Field(default_factory=dict)  # 传统测试统计
    gan_stats: Dict[str, Any] = Field(default_factory=dict)  # GAN测试统计
    total_cases: int = 0
    total_anomalies: int = 0
    started_at: Optional[datetime] = None
    paused_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class TaskStartRequest(BaseModel):
    """启动任务请求"""
    plan_id: str

# ========== 异常相关模型 ==========

class AnomalyType(str, Enum):
    """异常类型枚举"""
    NORMAL = "normal"
    STATE_FOLLOW_MISMATCH = "state_follow_mismatch"
    ERROR = "error"
    STUCK = "stuck"
    READY_FLAG_MISMATCH = "ready_flag_mismatch"

class AnomalyResponse(BaseModel):
    """异常响应"""
    id: str
    task_id: str
    anomaly_type: AnomalyType
    severity: int = Field(ge=1, le=5, description="严重等级 1-5")
    test_case: Dict[str, Any] = Field(..., description="触发异常的测试用例")
    context: Dict[str, Any] = Field(default_factory=dict, description="异常上下文")
    detected_at: datetime
    source: Literal["traditional", "gan"] = Field(..., description="异常来源")
    reproducible: bool = Field(default=False, description="是否可复现")
    min_reproduce_script: Optional[Dict[str, Any]] = Field(default=None, description="最小复现脚本")

# ========== 监控相关模型 ==========

class RealTimeMetrics(BaseModel):
    """实时监控指标"""
    task_id: str
    timestamp: datetime
    traditional_cases: int = 0
    traditional_anomalies: int = 0
    gan_cases: int = 0
    gan_anomalies: int = 0
    anomaly_rate: float = 0.0  # 异常触发率
    message_acceptance_rate: float = 0.0  # 报文受理率
    current_phase: Optional[str] = Field(default=None, description="当前测试阶段")

# ========== 约束统计相关模型 ==========

class ConstraintStats(BaseModel):
    """约束统计"""
    total_intercepted: int = 0  # 总拦截数
    interception_reasons: Dict[str, int] = Field(
        default_factory=dict,
        description="按拦截原因分类统计"
    )
    enabled_rules: List[str] = Field(default_factory=list, description="已启用的约束规则")

# ========== 报告相关模型 ==========

class TestReportRequest(BaseModel):
    """生成测试报告请求"""
    task_id: str
    format: Literal["pdf", "markdown", "json"] = Field(default="pdf")
    include_comparison: bool = Field(default=True, description="是否包含方法对比")

class MethodComparison(BaseModel):
    """测试方法对比"""
    traditional: Dict[str, Any]  # 传统方法指标
    gan: Dict[str, Any]  # GAN方法指标
    summary: str  # 对比摘要

class TestReportResponse(BaseModel):
    """测试报告响应"""
    task_id: str
    report_path: str
    format: str
    generated_at: datetime
    comparison: Optional[MethodComparison] = None



