"""
测试任务服务
"""
from typing import List, Optional
from datetime import datetime
import uuid
import asyncio

from api.models.schemas import (
    TestTaskResponse, TaskStatus, AnomalyResponse, AnomalyType
)
from api.database.db import Database
from api.services.test_plan_service import TestPlanService
from api.services.constraint_service import ConstraintService
from api.websocket_manager import WebSocketManager

class TestTaskService:
    def __init__(self):
        self.db = Database()
        self.plan_service = TestPlanService()
        self.constraint_service = ConstraintService()
        self.ws_manager = WebSocketManager()
        self.running_tasks = {}  # 存储正在运行的任务
    
    async def create_task(self, plan_id: str) -> TestTaskResponse:
        """创建测试任务"""
        # 验证测试计划是否存在
        plan = await self.plan_service.get_test_plan(plan_id)
        if not plan:
            raise ValueError(f"测试计划 {plan_id} 不存在")
        
        task_id = str(uuid.uuid4())
        now = datetime.now()
        
        task_data = {
            "id": task_id,
            "plan_id": plan_id,
            "status": TaskStatus.PENDING.value,
            "traditional_stats": {
                "cases": 0,
                "anomalies": 0,
                "anomaly_rate": 0.0
            },
            "gan_stats": {
                "cases": 0,
                "anomalies": 0,
                "anomaly_rate": 0.0
            },
            "total_cases": 0,
            "total_anomalies": 0,
            "started_at": None,
            "paused_at": None,
            "completed_at": None,
            "created_at": now.isoformat()
        }
        
        await self.db.save_test_task(task_data)
        return TestTaskResponse(**task_data)
    
    async def start_task(self, task_id: str) -> Optional[TestTaskResponse]:
        """启动测试任务"""
        task_data = await self.db.get_test_task(task_id)
        if not task_data:
            return None
        
        task_data["status"] = TaskStatus.RUNNING.value
        task_data["started_at"] = datetime.now().isoformat()
        task_data["paused_at"] = None
        
        await self.db.update_test_task(task_id, task_data)
        return TestTaskResponse(**task_data)
    
    async def pause_task(self, task_id: str) -> Optional[TestTaskResponse]:
        """暂停测试任务"""
        task_data = await self.db.get_test_task(task_id)
        if not task_data:
            return None
        
        if task_data["status"] != TaskStatus.RUNNING.value:
            raise ValueError("只能暂停运行中的任务")
        
        task_data["status"] = TaskStatus.PAUSED.value
        task_data["paused_at"] = datetime.now().isoformat()
        
        await self.db.update_test_task(task_id, task_data)
        return TestTaskResponse(**task_data)
    
    async def stop_task(self, task_id: str) -> Optional[TestTaskResponse]:
        """停止测试任务"""
        task_data = await self.db.get_test_task(task_id)
        if not task_data:
            return None
        
        task_data["status"] = TaskStatus.STOPPED.value
        task_data["completed_at"] = datetime.now().isoformat()
        
        # 停止后台任务
        if task_id in self.running_tasks:
            self.running_tasks[task_id].cancel()
            del self.running_tasks[task_id]
        
        await self.db.update_test_task(task_id, task_data)
        return TestTaskResponse(**task_data)
    
    async def get_task(self, task_id: str) -> Optional[TestTaskResponse]:
        """获取测试任务"""
        task_data = await self.db.get_test_task(task_id)
        if task_data:
            return TestTaskResponse(**task_data)
        return None
    
    async def get_tasks(self, skip: int = 0, limit: int = 100) -> List[TestTaskResponse]:
        """获取测试任务列表"""
        tasks_data = await self.db.get_test_tasks(skip=skip, limit=limit)
        
        # 如果数据库为空，返回模拟数据
        if not tasks_data:
            now = datetime.now()
            mock_tasks = [
                {
                    "id": "task-001",
                    "plan_id": "plan-001",
                    "status": TaskStatus.RUNNING.value,
                    "traditional_stats": {"cases": 450, "anomalies": 12, "anomaly_rate": 2.67},
                    "gan_stats": {"cases": 320, "anomalies": 8, "anomaly_rate": 2.5},
                    "total_cases": 770,
                    "total_anomalies": 20,
                    "started_at": now.isoformat(),
                    "paused_at": None,
                    "completed_at": None,
                    "created_at": now.isoformat()
                },
                {
                    "id": "task-002",
                    "plan_id": "plan-002",
                    "status": TaskStatus.COMPLETED.value,
                    "traditional_stats": {"cases": 1000, "anomalies": 25, "anomaly_rate": 2.5},
                    "gan_stats": {"cases": 0, "anomalies": 0, "anomaly_rate": 0.0},
                    "total_cases": 1000,
                    "total_anomalies": 25,
                    "started_at": (now).isoformat(),
                    "paused_at": None,
                    "completed_at": (now).isoformat(),
                    "created_at": (now).isoformat()
                },
                {
                    "id": "task-003",
                    "plan_id": "plan-003",
                    "status": TaskStatus.PAUSED.value,
                    "traditional_stats": {"cases": 0, "anomalies": 0, "anomaly_rate": 0.0},
                    "gan_stats": {"cases": 180, "anomalies": 5, "anomaly_rate": 2.78},
                    "total_cases": 180,
                    "total_anomalies": 5,
                    "started_at": (now).isoformat(),
                    "paused_at": (now).isoformat(),
                    "completed_at": None,
                    "created_at": (now).isoformat()
                }
            ]
            return [TestTaskResponse(**task) for task in mock_tasks]
        
        return [TestTaskResponse(**task) for task in tasks_data]
    
    async def get_task_anomalies(
        self, 
        task_id: str, 
        top_n: int = 10,
        source: Optional[str] = None,
        min_severity: int = 1
    ) -> List[AnomalyResponse]:
        """获取任务的异常列表"""
        anomalies_data = await self.db.get_task_anomalies(
            task_id, top_n=top_n, source=source, min_severity=min_severity
        )
        
        # 如果数据库为空，返回模拟数据
        if not anomalies_data:
            now = datetime.now()
            mock_anomalies = [
                {
                    "id": f"anomaly-{i+1}",
                    "task_id": task_id,
                    "anomaly_type": AnomalyType.STATE_MACHINE_ERROR.value if i % 3 == 0 else AnomalyType.TIMEOUT.value if i % 3 == 1 else AnomalyType.VALUE_OUT_OF_RANGE.value,
                    "severity": 3 if i < 3 else 2 if i < 6 else 1,
                    "test_case": {"voltage": 12.5 + i * 0.1, "status": 100 + i},
                    "context": {"phase": "wake", "location": f"signal_{i+1}", "expected": "ready", "actual": "error"},
                    "detected_at": (now).isoformat(),
                    "source": "traditional" if i % 2 == 0 else "gan",
                    "reproducible": True if i < 5 else False,
                    "min_reproduce_script": f"{{'voltage': {12.5 + i * 0.1}, 'trigger': 'signal_{i+1}'}}" if i < 5 else None
                }
                for i in range(min(top_n, 10))
            ]
            return [AnomalyResponse(**anomaly) for anomaly in mock_anomalies]
        
        return [AnomalyResponse(**anomaly) for anomaly in anomalies_data]
    
    async def execute_test_task(self, task_id: str):
        """
        执行测试任务（后台任务）
        这里应该调用实际的测试执行逻辑
        """
        try:
            task_data = await self.db.get_test_task(task_id)
            if not task_data:
                return
            
            plan = await self.plan_service.get_test_plan(task_data["plan_id"])
            if not plan:
                return
            
            # 模拟测试执行过程
            # 实际实现中，这里应该：
            # 1. 根据plan配置启动传统测试或GAN测试
            # 2. 生成测试用例
            # 3. 通过约束器验证
            # 4. 注入到HIL平台
            # 5. 监测响应并判定异常
            # 6. 实时更新状态并通过WebSocket推送
            
            iteration = 0
            while task_data["status"] == TaskStatus.RUNNING.value:
                # 检查是否被暂停
                task_data = await self.db.get_test_task(task_id)
                if task_data["status"] != TaskStatus.RUNNING.value:
                    break
                
                # 模拟生成测试用例和检测异常
                iteration += 1
                
                # 更新统计信息（示例）
                if plan.traditional_config and plan.traditional_config.enabled:
                    task_data["traditional_stats"]["cases"] += 10
                    if iteration % 5 == 0:
                        task_data["traditional_stats"]["anomalies"] += 1
                
                if plan.gan_config and plan.gan_config.enabled:
                    task_data["gan_stats"]["cases"] += 10
                    if iteration % 3 == 0:
                        task_data["gan_stats"]["anomalies"] += 1
                
                task_data["total_cases"] = (
                    task_data["traditional_stats"]["cases"] + 
                    task_data["gan_stats"]["cases"]
                )
                task_data["total_anomalies"] = (
                    task_data["traditional_stats"]["anomalies"] + 
                    task_data["gan_stats"]["anomalies"]
                )
                
                # 计算异常率
                if task_data["traditional_stats"]["cases"] > 0:
                    task_data["traditional_stats"]["anomaly_rate"] = (
                        task_data["traditional_stats"]["anomalies"] / 
                        task_data["traditional_stats"]["cases"]
                    )
                
                if task_data["gan_stats"]["cases"] > 0:
                    task_data["gan_stats"]["anomaly_rate"] = (
                        task_data["gan_stats"]["anomalies"] / 
                        task_data["gan_stats"]["cases"]
                    )
                
                await self.db.update_test_task(task_id, task_data)
                
                # 通过WebSocket推送实时更新
                await self.ws_manager.broadcast_to_task(task_id, {
                    "type": "metrics_update",
                    "task_id": task_id,
                    "timestamp": datetime.now().isoformat(),
                    "metrics": {
                        "traditional_cases": task_data["traditional_stats"]["cases"],
                        "traditional_anomalies": task_data["traditional_stats"]["anomalies"],
                        "gan_cases": task_data["gan_stats"]["cases"],
                        "gan_anomalies": task_data["gan_stats"]["anomalies"],
                        "total_cases": task_data["total_cases"],
                        "total_anomalies": task_data["total_anomalies"]
                    }
                })
                
                # 模拟执行间隔
                await asyncio.sleep(2)
                
                # 限制迭代次数（示例）
                if iteration >= 100:
                    task_data["status"] = TaskStatus.COMPLETED.value
                    task_data["completed_at"] = datetime.now().isoformat()
                    await self.db.update_test_task(task_id, task_data)
                    break
            
        except asyncio.CancelledError:
            # 任务被取消
            task_data = await self.db.get_test_task(task_id)
            if task_data:
                task_data["status"] = TaskStatus.STOPPED.value
                await self.db.update_test_task(task_id, task_data)
        except Exception as e:
            # 任务执行失败
            task_data = await self.db.get_test_task(task_id)
            if task_data:
                task_data["status"] = TaskStatus.FAILED.value
                await self.db.update_test_task(task_id, task_data)



