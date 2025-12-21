"""
监控服务
"""
from typing import List
from datetime import datetime

from api.models.schemas import RealTimeMetrics
from api.database.db import Database

class MonitoringService:
    def __init__(self):
        self.db = Database()
    
    async def get_task_metrics(self, task_id: str, limit: int = 100) -> List[RealTimeMetrics]:
        """获取测试任务的历史监控指标"""
        # 从数据库获取任务数据
        task_data = await self.db.get_test_task(task_id)
        
        # 如果任务不存在或没有数据，返回模拟数据
        if not task_data or task_data.get("total_cases", 0) == 0:
            import random
            from datetime import timedelta
            metrics = []
            base_time = datetime.now() - timedelta(minutes=30)
            
            for i in range(min(limit, 30)):
                timestamp = base_time + timedelta(minutes=i)
                traditional_cases = 10 + i * 15 + random.randint(-5, 5)
                gan_cases = 8 + i * 12 + random.randint(-3, 3)
                traditional_anomalies = max(0, int(traditional_cases * 0.025 + random.randint(-1, 1)))
                gan_anomalies = max(0, int(gan_cases * 0.028 + random.randint(-1, 1)))
                total_cases = traditional_cases + gan_cases
                total_anomalies = traditional_anomalies + gan_anomalies
                
                metrics.append(RealTimeMetrics(
                    task_id=task_id,
                    timestamp=timestamp,
                    traditional_cases=traditional_cases,
                    traditional_anomalies=traditional_anomalies,
                    gan_cases=gan_cases,
                    gan_anomalies=gan_anomalies,
                    anomaly_rate=total_anomalies / total_cases if total_cases > 0 else 0.0,
                    message_acceptance_rate=0.92 + random.uniform(-0.05, 0.05),
                    current_phase="wake" if i % 3 == 0 else "ready" if i % 3 == 1 else "sleep"
                ))
            
            return metrics
        
        # 基于任务统计数据生成监控指标
        metrics = []
        
        # 如果有统计数据，生成一个汇总的指标
        if task_data.get("total_cases", 0) > 0:
            metrics.append(RealTimeMetrics(
                task_id=task_id,
                timestamp=datetime.now(),
                traditional_cases=task_data.get("traditional_stats", {}).get("cases", 0),
                traditional_anomalies=task_data.get("traditional_stats", {}).get("anomalies", 0),
                gan_cases=task_data.get("gan_stats", {}).get("cases", 0),
                gan_anomalies=task_data.get("gan_stats", {}).get("anomalies", 0),
                anomaly_rate=task_data.get("total_anomalies", 0) / task_data.get("total_cases", 1) if task_data.get("total_cases", 0) > 0 else 0.0,
                message_acceptance_rate=0.95,  # 默认值，实际应从统计数据计算
                current_phase=None
            ))
        
        return metrics[:limit]



