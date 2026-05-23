"""
Pydantic数据模型定义
用于API请求和响应的数据验证
"""
from pydantic import BaseModel, Field, computed_field
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

# ========== AutoTestDesign V2 需求管理模型 ==========

class RequirementSource(str, Enum):
    """需求来源"""
    CSV = "csv"
    TEXT = "text"
    FORM = "form"
    DEMO = "demo"


class Requirement(BaseModel):
    """AutoTestDesign V2 原始需求。"""
    id: str
    source: RequirementSource
    raw_text: str = Field(..., description="原始需求文本")
    title: Optional[str] = Field(default=None, description="需求标题")
    module: Optional[str] = Field(default=None, description="VCU模块，如 A/B/C/D/E")
    category: Optional[str] = Field(default=None, description="需求分类")
    priority: Optional[str] = Field(default=None, description="文档或人工标注优先级")
    created_at: datetime
    updated_at: datetime
    parsed: bool = Field(default=False, description="是否已解析")


class RequirementCreate(BaseModel):
    """创建需求请求"""
    source: RequirementSource = RequirementSource.FORM
    raw_text: str
    id: Optional[str] = None
    title: Optional[str] = None
    module: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None


class RequirementUpdate(BaseModel):
    """更新需求请求"""
    raw_text: Optional[str] = None
    title: Optional[str] = None
    module: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None


class RequirementsParseRequest(BaseModel):
    """批量解析原始需求文本并创建需求。"""
    raw_text: str
    source: RequirementSource = RequirementSource.TEXT
    persist: bool = True


class InputField(BaseModel):
    name: str
    data_type: str = "float"
    valid_range: Optional[Dict[str, Any]] = None
    unit: Optional[str] = None
    has_timing: bool = False


class RequirementCondition(BaseModel):
    type: Literal["timing", "logical", "combined", "threshold", "state", "scenario"] = "logical"
    description: str
    threshold: Optional[Any] = None


class ExpectedAction(BaseModel):
    output_field: str
    expected_value: Any
    operator: Literal["eq", "gte", "lte", "gt", "lt", "contains"] = "eq"


class ParsedRequirement(BaseModel):
    """LLM 解析后的结构化需求。"""
    requirement_id: str
    title: Optional[str] = None
    module: Optional[str] = None
    description: str = ""
    input_fields: List[InputField] = Field(default_factory=list)
    conditions: List[RequirementCondition] = Field(default_factory=list)
    expected_actions: List[ExpectedAction] = Field(default_factory=list)
    parse_confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    llm_model: Optional[str] = None
    elapsed_ms: Optional[float] = None
    updated_at: datetime

    @computed_field
    @property
    def data_ranges(self) -> Dict[str, Dict[str, Any]]:
        """兼容旧前端：从 input_fields 派生 data_ranges。"""
        ranges: Dict[str, Dict[str, Any]] = {}
        for field in self.input_fields:
            if field.valid_range is not None:
                ranges[field.name] = field.valid_range
        return ranges

    @computed_field
    @property
    def actions(self) -> List[str]:
        """兼容旧前端：返回动作描述。"""
        return [
            f"{item.output_field} {item.operator} {item.expected_value}"
            for item in self.expected_actions
        ]


# ========== AutoTestDesign V2 风险分析模型 ==========

class RiskDimension(BaseModel):
    """风险维度评分。数值越小风险越高，与 Tech×Business RPN 一致。"""
    tech_risk: int = Field(default=3, ge=1, le=5)
    business_risk: int = Field(default=3, ge=1, le=5)
    safety_impact: Optional[int] = Field(default=None, ge=1, le=5)
    detectability: Optional[int] = Field(default=None, ge=1, le=5)


class RiskAnalysisResult(BaseModel):
    """ISO 9126 + Chapter 4 RPN 风险分析结果。"""
    requirement_id: str
    iso9126_characteristic: Literal[
        "Functionality", "Reliability", "Efficiency", "Maintainability", "Usability", "Portability"
    ] = "Functionality"
    tech_risk: int = Field(..., ge=1, le=5)
    business_risk: int = Field(..., ge=1, le=5)
    rpn: int = Field(..., ge=1, le=25)
    extent: Literal["Extensive", "Broad", "Cursory", "Low priority"]
    reasoning: str
    llm_model: Optional[str] = None
    elapsed_ms: Optional[float] = None
    created_at: datetime

    @computed_field
    @property
    def dimensions(self) -> RiskDimension:
        return RiskDimension(tech_risk=self.tech_risk, business_risk=self.business_risk)

    @computed_field
    @property
    def total_score(self) -> float:
        """兼容旧前端，按 0-10 风险强度返回。"""
        return round((26 - self.rpn) / 25 * 10, 2)

    @computed_field
    @property
    def priority(self) -> str:
        if self.rpn <= 5:
            return "High"
        if self.rpn <= 10:
            return "Medium"
        return "Low"


class RiskAdjustmentRequest(BaseModel):
    """人工覆盖风险评分。"""
    requirement_id: Optional[str] = None
    iso9126_characteristic: Optional[str] = None
    tech_risk: Optional[int] = Field(default=None, ge=1, le=5)
    business_risk: Optional[int] = Field(default=None, ge=1, le=5)
    dimensions: Optional[RiskDimension] = None
    reasoning: Optional[str] = None


# ========== AutoTestDesign V2 覆盖项 / 策略 / Prompt ==========

class CoverageItem(BaseModel):
    id: str
    requirement_id: str
    title: str
    description: str
    technique: str
    iso9126_characteristic: Optional[str] = None
    priority: str = "Medium"
    created_at: datetime
    updated_at: datetime


class CoverageItemCreate(BaseModel):
    requirement_id: str
    title: str
    description: str
    technique: str
    iso9126_characteristic: Optional[str] = None
    priority: str = "Medium"


class CoverageItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    technique: Optional[str] = None
    iso9126_characteristic: Optional[str] = None
    priority: Optional[str] = None


class TestStrategy(BaseModel):
    requirement_id: str
    techniques: List[str] = Field(default_factory=lambda: ["EP", "BVA"])
    rationale: str = ""
    updated_at: datetime


class StrategyUpdate(BaseModel):
    techniques: List[str]
    rationale: Optional[str] = None


class PromptTemplate(BaseModel):
    type: str
    system_prompt: str
    user_prompt: str
    updated_at: datetime


class PromptUpdate(BaseModel):
    system_prompt: Optional[str] = None
    user_prompt: Optional[str] = None


# ========== AutoTestDesign V2 测试用例模型 ==========

class TestTechnique(str, Enum):
    """测试技术"""
    EQUIVALENCE_PARTITIONING = "EP"
    BOUNDARY_VALUE_ANALYSIS = "BVA"
    DECISION_TABLE = "DT"
    STATE_TRANSITION = "ST"
    SCENARIO = "SC"


class TestCaseStatus(str, Enum):
    """测试用例状态"""
    PENDING = "pending"
    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"


class TestInput(BaseModel):
    name: str
    data_type: str = "float"
    value: Any
    duration: Optional[float] = None
    unit: Optional[str] = None


class ExpectedOutput(BaseModel):
    name: str
    operator: Literal["eq", "gte", "lte", "gt", "lt", "contains"] = "eq"
    value: Any
    out_type: int = 1
    out_range: int = 2


class BqErrorOracle(BaseModel):
    error_type: int
    out_data: List[Dict[str, Any]] = Field(default_factory=list)


class TestCase(BaseModel):
    """AutoTestDesign V2 测试用例。"""
    id: str
    requirement_id: str
    coverage_item_id: Optional[str] = None
    title: str
    technique: TestTechnique
    type: int = Field(default=1, description="bq_new type: 1=唤醒/单步, 2=休眠/场景")
    in_data: List[TestInput] = Field(default_factory=list)
    expected_results: List[ExpectedOutput] = Field(default_factory=list)
    error: List[BqErrorOracle] = Field(default_factory=list)
    est_time: float = 20.0
    oracle_reasoning: str = ""
    status: TestCaseStatus = TestCaseStatus.PENDING
    execution_result: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def signal_name(self) -> str:
        return self.in_data[0].name if self.in_data else ""

    @computed_field
    @property
    def test_value(self) -> float:
        if not self.in_data:
            return 0.0
        try:
            return float(self.in_data[0].value)
        except (TypeError, ValueError):
            return 0.0

    @computed_field
    @property
    def expected_result(self) -> str:
        result_type = next((item.value for item in self.expected_results if item.name == "result_type"), None)
        if result_type == "expected":
            return "PASS"
        if result_type == "sleep":
            return "SLEEP"
        state_value = next(
            (
                item.value
                for item in self.expected_results
                if item.name in {"vehicle_state", "整车State状态", "vcu_state", "state"}
            ),
            None,
        )
        if state_value in {11, "11", "state11"}:
            return "PASS"
        if state_value in {9, "9", "state09"}:
            return "SLEEP"
        return "FAIL"

    @computed_field
    @property
    def expected_status(self) -> int:
        return 1 if self.expected_result == "PASS" else 3 if self.expected_result == "SLEEP" else 4

    @computed_field
    @property
    def expected_vehicle_state(self) -> int:
        value = next((item.value for item in self.expected_results if item.name in {"vehicle_state", "整车State状态"}), None)
        try:
            return int(value)
        except (TypeError, ValueError):
            return 11 if self.expected_result == "PASS" else 9


class TestCaseCreate(BaseModel):
    requirement_id: str
    coverage_item_id: Optional[str] = None
    title: str
    technique: TestTechnique
    type: int = 1
    in_data: List[TestInput]
    expected_results: List[ExpectedOutput]
    error: List[BqErrorOracle] = Field(default_factory=list)
    est_time: float = 20.0
    oracle_reasoning: str = ""


class TestCaseUpdate(BaseModel):
    title: Optional[str] = None
    technique: Optional[TestTechnique] = None
    type: Optional[int] = None
    in_data: Optional[List[TestInput]] = None
    expected_results: Optional[List[ExpectedOutput]] = None
    error: Optional[List[BqErrorOracle]] = None
    est_time: Optional[float] = None
    oracle_reasoning: Optional[str] = None
    # 旧前端兼容字段
    signal_name: Optional[str] = None
    test_value: Optional[float] = None
    expected_result: Optional[Literal["PASS", "FAIL", "SLEEP"]] = None
    expected_status: Optional[int] = None
    expected_vehicle_state: Optional[int] = None


class TestGenerationRequest(BaseModel):
    requirement_id: str
    techniques: List[str] = Field(..., description="EP/BVA/DT/ST/SC")
    coverage_item_ids: Optional[List[str]] = None
    bva_delta: Optional[float] = Field(default=0.1)
    regenerate: bool = False


class BulkTestGenerationRequest(BaseModel):
    requirement_ids: Optional[List[str]] = None
    techniques: Optional[List[str]] = None
    bva_delta: Optional[float] = Field(default=0.1)
    regenerate: bool = False


# ========== AutoTestDesign V2 执行结果模型 ==========

class ExecutionResult(BaseModel):
    test_case_id: str
    request_payload: Dict[str, Any]
    actual_output: Dict[str, Any]
    expected_output: List[ExpectedOutput]
    match_expected: bool
    mismatches: List[str] = Field(default_factory=list)
    executed_at: datetime
    elapsed_ms: float


class BatchExecutionRequest(BaseModel):
    test_case_ids: Optional[List[str]] = None
    reset_before_run: bool = True


class ResultsSummary(BaseModel):
    total: int
    passed: int
    failed: int
    errors: int
    pass_rate: float
    coverage_rate: float
    dtc_counts: Dict[str, int] = Field(default_factory=dict)
    failure_reasons: Dict[str, int] = Field(default_factory=dict)
    performance: Dict[str, Any] = Field(default_factory=dict)


class ImproveRequest(BaseModel):
    requirement_ids: Optional[List[str]] = None
    failed_only: bool = True
    max_suggestions: int = 10


class ImproveSuggestion(BaseModel):
    id: str
    requirement_id: str
    title: str
    reason: str
    coverage_item: CoverageItem
    test_case: Optional[TestCase] = None
    created_at: datetime


class PerformanceMetric(BaseModel):
    operation: str
    elapsed_ms: float
    model: Optional[str] = None
    created_at: datetime
    detail: Dict[str, Any] = Field(default_factory=dict)


# ========== AutoTestDesign V2 导出模型 ==========

class ExportFormat(str, Enum):
    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"


class ExportScope(BaseModel):
    include_requirements: bool = True
    include_parsed_requirements: bool = True
    include_risk_analysis: bool = True
    include_coverage_items: bool = True
    include_strategies: bool = True
    include_test_cases: bool = True
    include_execution_results: bool = True
    include_traceability_matrix: bool = True
    include_bq_new_cases: bool = True
    include_ep_cases: bool = True
    include_bva_cases: bool = True
    include_dt_cases: bool = True
    include_st_cases: bool = True
    include_scenario_cases: bool = True


class ExportRequest(BaseModel):
    format: ExportFormat
    scope: ExportScope = Field(default_factory=ExportScope)
    requirement_ids: Optional[List[str]] = Field(default=None)
