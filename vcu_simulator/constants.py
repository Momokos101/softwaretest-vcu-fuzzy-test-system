# 5个VCU输入信号的边界常量
# 所有数值均来自对5个真实BAIC VCU HIL测试数据库的完整分析
# (db_10 / db_11 / db_15 / db / db_2，共9615条记录)

SIGNAL_RULES = {
    "CC2电压": {
        # CC2电压：AC充电唤醒电压，主唤醒信号
        # db_2确认：4.8V在旧版BAIC数据口径中表示成功唤醒
        # 4DB一致：7.7V为稳定上界；db_15异常批次扩展至8.1V
        "valid_min": 4.8,
        "valid_max": 7.7,
        # 7.8V为灰色边界：db_10有PASS，其余DB均FAIL，仿真器统一判FAIL
        "boundary": 7.8,
        # CC2=12.0V触发休眠（type=2，strategy=-3）
        "sleep_trigger": 12.0,
        # 所有越界统一state=30；state=12/46是数据库中偶发异常态，与电压无直接关联
    },
    "CC电压值": {
        # CC电压值：充电枪CC接触电压，线缆健康检测
        # [0.1, 3.9]V → 接触不良/错误线阻 → FAIL
        # 其他值（>4.0V）→ 正常接线或无枪 → PASS
        "fail_min": 0.1,
        "fail_max": 3.9,
    },
    "CP幅值": {
        # CP幅值：控制导引信号幅值，AC充电协议信号
        # [9.1, 12.9]V → 协议冲突或幅值异常 → FAIL
        # 0.0V → 待机状态 → PASS
        "fail_min": 9.1,
        "fail_max": 12.9,
    },
    "供电电压": {
        # 供电电压：外部交流供电电压
        # [9.1, 15.9]V → 意外供电/过压 → FAIL
        # 0.0V → 无外部供电 → PASS
        "fail_min": 9.1,
        "fail_max": 15.9,
    },
    "网络唤醒报文使能状态": {
        # 网络远程唤醒使能，二值信号
        # 1 → 与CC2唤醒冲突 → FAIL（176/177条记录确认）
        # 0 → 未使能，不干扰CC2唤醒 → PASS
        "fail_value": 1.0,
    },
}

# 固定输出字段（来自真实数据库，对所有场景恒定）
BATTERY_VOLTAGE = 12.92   # 蓄电池电压（恒定）
BMS_WAKE_CMD = 1          # BMS低压唤醒指令（恒定）
MCU_WAKE_CMD = 1          # MCU低压唤醒指令（恒定）

# 模拟测试时长（基于真实HIL数据均值，单位：秒）
DURATION_PASS = 100.4
DURATION_FAIL = 100.6
DURATION_SLEEP = 100.3

# 所有合法信号名称
VALID_SIGNAL_NAMES = list(SIGNAL_RULES.keys())

# 休眠测试固定输入值（strategy=-3，type=2）
SLEEP_FIXED_VALUES = {
    "cc2_voltage": 12.0,
    "cc_voltage": 12.0,
    "cp_amplitude": 0.0,
    "supply_voltage": 0.0,
    "network_wake_enable": 0.0,
}

# db_15批次差异说明（用于/signals端点）
DB15_NOTE = (
    "db_15批次（939条记录）CC2有效上界扩展至8.1V，"
    "含7.8V/7.9V/8.0V/8.1V的PASS记录。"
    "仿真器采用主流4DB配置：valid=[4.8, 7.7]V。"
)

# V2 state-machine constants from PROJECT_PLAN_V2.md
STATE_SLEEP = 9
STATE_INIT = 10
STATE_RUN = 11
STATE_FAULT_PROTECTION = "fault_protection"
STATE_UNDERVOLTAGE_SHUTDOWN = "undervoltage_shutdown"

V2_WAKE_THRESHOLDS = {
    "supply_voltage": 9.0,
    "supply_duration_ms": 10,
    "cp_voltage": 9.0,
    "cc_voltage": 4.4,
    "cc2_ubr_threshold": 4.4,
    "hood_voltage": 4.0,
    "hood_duration_ms": 10,
    "door_voltage": 1.0,
    "door_duration_ms": 10,
}

V2_CAN_CONFIG = {
    "valid_id_min": 0x400,
    "valid_id_max": 0x47F,
    "bus_off_threshold": 255,
}

V2_GUARD_CONFIG = {
    "overvoltage_threshold": 16.0,
    "undervoltage_threshold": 6.0,
    "debounce_min_ms": 5,
}

V2_POWER_CONFIG = {
    "run_expected_current_a": 0.05,
    "run_alarm_threshold_a": 0.2,
    "run_alarm_duration_ms": 500,
    "sleep_expected_current_a": 0.01,
    "sleep_alarm_threshold_a": 0.05,
    "stuck_current_a": 0.25,
}

V2_TIMING_CONFIG = {
    "type1_max_duration": 20.0,
    "type2_max_duration": 60.0,
    "type1_nominal_duration": 14.7,
    "type2_nominal_duration": 42.0,
    "stuck_est_time": 20.0,
    "rapid_cycle_interval_s": 1.0,
    "rapid_cycle_threshold": 3,
}

V2_CONFIG = {
    "wake": V2_WAKE_THRESHOLDS,
    "can": V2_CAN_CONFIG,
    "guard": V2_GUARD_CONFIG,
    "power": V2_POWER_CONFIG,
    "timing": V2_TIMING_CONFIG,
}
