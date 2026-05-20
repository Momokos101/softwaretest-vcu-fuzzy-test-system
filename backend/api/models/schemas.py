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

# ========== AutoTestDesign 需求管理模型 ==========

class RequirementSource(str, Enum):
    """需求来源"""
    CSV = "csv"
    TEXT = "text"
    FORM = "form"

class Requirement(BaseModel):
    """需求基础模型"""
    id: str
    source: RequirementSource
    raw_text: str = Field(..., description="原始需求文本")
    created_at: datetime
    updated_at: datetime
    parsed: bool = Field(default=False, description="是否已解析")

class RequirementCreate(BaseModel):
    """创建需求请求"""
    source: RequirementSource
    raw_text: str

class RequirementUpdate(BaseModel):
    """更新需求请求"""
    raw_text: str

class ParsedRequirement(BaseModel):
    """解析后的需求"""
    requirement_id: str
    input_fields: List[str] = Field(default_factory=list, description="输入字段列表")
    data_ranges: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="数据范围，可为 {type: range, min, max} 或 {type: threshold, operator, threshold}"
    )
    conditions: List[str] = Field(default_factory=list, description="条件列表")
    actions: List[str] = Field(default_factory=list, description="动作列表")
    parse_confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="解析置信度")
    updated_at: datetime

# ========== AutoTestDesign 风险分析模型 ==========

class RiskDimension(BaseModel):
    """风险维度评分"""
    criticality: float = Field(default=5.0, ge=0.0, le=10.0, description="关键性，0-10")
    boundary_sensitivity: float = Field(default=5.0, ge=0.0, le=10.0, description="边界敏感性，0-10")
    complexity: float = Field(default=5.0, ge=0.0, le=10.0, description="复杂度，0-10")
    state_impact: float = Field(default=5.0, ge=0.0, le=10.0, description="状态影响，0-10")
    testability: float = Field(default=5.0, ge=0.0, le=10.0, description="可测试性，0-10")

class RiskAnalysisResult(BaseModel):
    """风险分析结果"""
    requirement_id: str
    dimensions: RiskDimension
    total_score: float = Field(..., ge=0.0, le=10.0, description="加权风险总分，0-10")
    priority: Literal["High", "Medium", "Low"] = Field(..., description="测试优先级")
    created_at: datetime

class RiskAdjustmentRequest(BaseModel):
    """风险调整请求"""
    requirement_id: str
    dimensions: RiskDimension

# ========== AutoTestDesign 测试用例模型 ==========

class TestTechnique(str, Enum):
    """测试技术"""
    EQUIVALENCE_PARTITIONING = "ep"
    BOUNDARY_VALUE_ANALYSIS = "bva"
    DECISION_TABLE = "dt"

class TestCaseStatus(str, Enum):
    """测试用例状态"""
    PENDING = "pending"
    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"

class TestCase(BaseModel):
    """测试用例"""
    id: str
    requirement_id: str
    technique: TestTechnique
    signal_name: str = Field(..., description="信号名称")
    test_value: float = Field(..., description="测试值")
    expected_result: Literal["PASS", "FAIL", "SLEEP"] = Field(..., description="预期结果")
    expected_status: int = Field(..., description="预期仿真器test_status：1=PASS, 3=SLEEP, 4=FAIL")
    expected_vehicle_state: int = Field(..., description="预期vehicle_state：170=唤醒, 30=休眠/失败")
    status: TestCaseStatus = Field(default=TestCaseStatus.PENDING)
    execution_result: Optional[Dict[str, Any]] = None
    created_at: datetime

class TestCaseCreate(BaseModel):
    """创建测试用例请求"""
    requirement_id: str
    technique: TestTechnique
    signal_name: str
    test_value: float
    expected_result: Literal["PASS", "FAIL", "SLEEP"]
    expected_status: int
    expected_vehicle_state: int

class TestCaseUpdate(BaseModel):
    """更新测试用例请求"""
    signal_name: Optional[str] = None
    test_value: Optional[float] = None
    expected_result: Optional[Literal["PASS", "FAIL", "SLEEP"]] = None
    expected_status: Optional[int] = None
    expected_vehicle_state: Optional[int] = None

class TestGenerationRequest(BaseModel):
    """测试生成请求"""
    requirement_id: str
    techniques: List[TestTechnique] = Field(..., description="选择的测试技术")
    bva_delta: Optional[float] = Field(default=0.1, description="BVA边界偏移量")

# ========== AutoTestDesign 执行结果模型 ==========

class ExecutionResult(BaseModel):
    """执行结果"""
    test_case_id: str
    test_status: int = Field(..., description="1=PASS, 3=SLEEP, 4=FAIL")
    vehicle_state: int
    vehicle_mode: int
    ready_flag: int
    actual_duration: float
    detail: str
    executed_at: datetime
    match_expected: bool = Field(..., description="是否符合预期")

class BatchExecutionRequest(BaseModel):
    """批量执行请求"""
    test_case_ids: List[str]

# ========== AutoTestDesign 导出模型 ==========

class ExportFormat(str, Enum):
    """导出格式"""
    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"

class ExportScope(BaseModel):
    """导出范围"""
    include_requirements: bool = True
    include_risk_analysis: bool = True
    include_test_cases: bool = True
    include_execution_results: bool = True
    include_ep_cases: bool = True
    include_bva_cases: bool = True
    include_dt_cases: bool = True
    include_traceability_matrix: bool = True

class ExportRequest(BaseModel):
    """导出请求"""
    format: ExportFormat
    scope: ExportScope
    requirement_ids: Optional[List[str]] = Field(default=None, description="指定需求ID，None表示全部")

