"""
约束服务
"""
from api.models.schemas import ConstraintStats
from api.database.db import Database

class ConstraintService:
    def __init__(self):
        self.db = Database()
    
    async def get_constraint_stats(self, task_id: str) -> ConstraintStats:
        """获取测试任务的约束统计"""
        stats_data = await self.db.get_constraint_stats(task_id)
        
        if not stats_data:
            # 返回模拟数据
            return ConstraintStats(
                total_intercepted=156,
                interception_reasons={
                    "超出范围": 45,
                    "速率超限": 32,
                    "在禁发列表": 28,
                    "CRC校验失败": 25,
                    "DLC长度错误": 18,
                    "白名单检查": 8
                },
                enabled_rules=[
                    "whitelist_check",
                    "blacklist_check",
                    "value_range_check",
                    "rate_limit_check",
                    "crc_check",
                    "dlc_check"
                ]
            )
        
        return ConstraintStats(**stats_data)



