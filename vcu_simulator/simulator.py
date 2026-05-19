from constants import (
    SIGNAL_RULES,
    BATTERY_VOLTAGE, BMS_WAKE_CMD, MCU_WAKE_CMD,
    DURATION_PASS, DURATION_FAIL, DURATION_SLEEP,
)


class VCUSimulator:
    """
    VCU唤醒-休眠行为仿真器。
    基于5个真实BAIC VCU HIL测试数据库（共9615条记录）提炼的判定逻辑。
    每次调用 simulate() 传入单个信号名称和值，返回VCU状态响应。
    """

    def simulate(self, signal_name: str, value: float) -> dict:
        """单信号判定（对应真实数据库 type=1，strategy=0/1）"""

        if signal_name == "CC2电压":
            return self._judge_cc2(value)

        elif signal_name == "CC电压值":
            rules = SIGNAL_RULES["CC电压值"]
            if rules["fail_min"] <= value <= rules["fail_max"]:
                return self._fail(
                    detail=f"CC电压值={value}V ∈ [{rules['fail_min']},{rules['fail_max']}]V"
                           f" → 接触不良/错误线阻 → FAIL"
                )
            return self._pass(detail=f"CC电压值={value}V 正常（无线缆故障）→ PASS")

        elif signal_name == "CP幅值":
            rules = SIGNAL_RULES["CP幅值"]
            if rules["fail_min"] <= value <= rules["fail_max"]:
                return self._fail(
                    detail=f"CP幅值={value}V ∈ [{rules['fail_min']},{rules['fail_max']}]V"
                           f" → 协议冲突/幅值异常 → FAIL"
                )
            return self._pass(detail=f"CP幅值={value}V 正常（待机状态）→ PASS")

        elif signal_name == "供电电压":
            rules = SIGNAL_RULES["供电电压"]
            if rules["fail_min"] <= value <= rules["fail_max"]:
                return self._fail(
                    detail=f"供电电压={value}V ∈ [{rules['fail_min']},{rules['fail_max']}]V"
                           f" → 意外供电/过压 → FAIL"
                )
            return self._pass(detail=f"供电电压={value}V 正常（无外部供电）→ PASS")

        elif signal_name == "网络唤醒报文使能状态":
            rules = SIGNAL_RULES["网络唤醒报文使能状态"]
            if value == rules["fail_value"]:
                return self._fail(
                    detail=f"网络唤醒使能={int(value)}（已使能）→ 与CC2唤醒协议冲突 → FAIL"
                )
            return self._pass(detail=f"网络唤醒使能={int(value)}（未使能）→ 不干扰CC2唤醒 → PASS")

        # 走不到这里，signal_name 已在 models.py 校验
        raise ValueError(f"未知信号: {signal_name}")

    def simulate_sleep(self, cc2_voltage: float, cc_voltage: float,
                       cp_amplitude: float, supply_voltage: float,
                       network_wake_enable: float) -> dict:
        """
        休眠测试（对应真实数据库 type=2，strategy=-3）。
        固定5信号组合：CC2=12.0V + 其他稳定值 → 触发VCU进入休眠模式。
        """
        detail = (
            f"休眠测试：CC2={cc2_voltage}V(=12.0V触发休眠) "
            f"CC={cc_voltage}V CP={cp_amplitude}V "
            f"Supply={supply_voltage}V NetWake={int(network_wake_enable)}"
            f" → 正常休眠"
        )
        return self._sleep(detail=detail)

    def simulate_batch(self, requests: list) -> list:
        """批量测试，依次调用 simulate()，返回结果数组"""
        results = []
        for req in requests:
            result = self.simulate(
                signal_name=req["signal_name"],
                value=req["value"],
            )
            result["signal_name"] = req["signal_name"]
            result["input_value"] = req["value"]
            results.append(result)
        return results

    # ------------------------------------------------------------------ #
    # 内部辅助方法                                                         #
    # ------------------------------------------------------------------ #

    def _judge_cc2(self, value: float) -> dict:
        """CC2电压专用判定，含灰色边界和休眠触发"""
        rules = SIGNAL_RULES["CC2电压"]

        # 休眠触发（精度±0.05V，与真实数据库一致）
        if abs(value - rules["sleep_trigger"]) < 0.05:
            return self._sleep(
                detail=f"CC2电压={value}V ≈ 12.0V → 触发休眠（strategy=-3）"
            )

        # 正常唤醒区间
        if rules["valid_min"] <= value <= rules["valid_max"]:
            return self._pass(
                detail=f"CC2电压={value}V ∈ [{rules['valid_min']},{rules['valid_max']}]V"
                       f" → 正常唤醒 vehicle_state=170"
            )

        # 灰色边界 7.8V（db_10有PASS/FAIL，其余DB均FAIL，统一判FAIL）
        if abs(value - rules["boundary"]) < 0.05:
            return self._fail(
                detail=f"CC2电压={value}V 在灰色边界{rules['boundary']}V"
                       f" → 主流4DB判FAIL（db_15批次除外）"
            )

        # 所有其他越界情况统一 state=30
        # state=12/46 是数据库中偶发的非电压相关异常态，不在仿真器中模拟
        return self._fail(
            detail=f"CC2电压={value}V 越界（有效区间[4.8,7.7]V）→ FAIL (vehicle_state=30)"
        )

    def _pass(self, detail: str = "") -> dict:
        return {
            "test_status": 1,
            "vehicle_state": 170,
            "vehicle_mode": 5,
            "ready_flag": 1,
            "bms_wake_cmd": BMS_WAKE_CMD,
            "mcu_wake_cmd": MCU_WAKE_CMD,
            "battery_voltage": BATTERY_VOLTAGE,
            "actual_duration": DURATION_PASS,
            "detail": detail,
        }

    def _fail(self, state: int = 30, detail: str = "") -> dict:
        return {
            "test_status": 4,
            "vehicle_state": state,
            "vehicle_mode": 2,
            "ready_flag": 0,
            "bms_wake_cmd": BMS_WAKE_CMD,
            "mcu_wake_cmd": MCU_WAKE_CMD,
            "battery_voltage": BATTERY_VOLTAGE,
            "actual_duration": DURATION_FAIL,
            "detail": detail,
        }

    def _sleep(self, detail: str = "") -> dict:
        return {
            "test_status": 3,
            "vehicle_state": 30,
            "vehicle_mode": 2,
            "ready_flag": 0,
            "bms_wake_cmd": BMS_WAKE_CMD,
            "mcu_wake_cmd": MCU_WAKE_CMD,
            "battery_voltage": BATTERY_VOLTAGE,
            "actual_duration": DURATION_SLEEP,
            "detail": detail,
        }
