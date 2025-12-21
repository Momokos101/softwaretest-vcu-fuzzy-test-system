"""
测试计划服务
"""
from typing import List, Optional
from datetime import datetime
import uuid
import json
import os

from api.models.schemas import TestPlanCreate, TestPlanResponse
from api.database.db import Database

class TestPlanService:
    def __init__(self):
        self.db = Database()
        self.plans_dir = "data/test_plans"
        os.makedirs(self.plans_dir, exist_ok=True)
    
    async def create_test_plan(self, plan: TestPlanCreate) -> TestPlanResponse:
        """创建测试计划"""
        plan_id = str(uuid.uuid4())
        now = datetime.now()
        
        plan_data = {
            "id": plan_id,
            "name": plan.name,
            "description": plan.description,
            "test_mode": plan.test_mode.value,
            "traditional_config": plan.traditional_config.dict() if plan.traditional_config else None,
            "gan_config": plan.gan_config.dict() if plan.gan_config else None,
            "constraint_config": plan.constraint_config.dict(),
            "baseline_log_path": plan.baseline_log_path,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "status": "draft"
        }
        
        # 保存到数据库
        await self.db.save_test_plan(plan_data)
        
        # 保存到文件（备份）
        plan_file = os.path.join(self.plans_dir, f"{plan_id}.json")
        with open(plan_file, "w", encoding="utf-8") as f:
            json.dump(plan_data, f, ensure_ascii=False, indent=2)
        
        return TestPlanResponse(**plan_data)
    
    async def get_test_plan(self, plan_id: str) -> Optional[TestPlanResponse]:
        """获取测试计划"""
        plan_data = await self.db.get_test_plan(plan_id)
        if plan_data:
            return TestPlanResponse(**plan_data)
        return None
    
    async def get_test_plans(self, skip: int = 0, limit: int = 100) -> List[TestPlanResponse]:
        """获取测试计划列表"""
        plans_data = await self.db.get_test_plans(skip=skip, limit=limit)
        
        # 如果数据库为空，返回模拟数据
        if not plans_data:
            from api.models.schemas import TestMode, TraditionalTestConfig, GANTestConfig, ConstraintConfig
            mock_plans = [
                {
                    "id": "plan-001",
                    "name": "VCU唤醒-休眠基础测试",
                    "description": "针对VCU控制器的唤醒和休眠流程进行基础测试",
                    "test_mode": TestMode.BOTH.value,
                    "traditional_config": TraditionalTestConfig(enabled=True, intensity=5).dict(),
                    "gan_config": GANTestConfig(enabled=True, model_version="v1.0", sampling_temperature=1.0).dict(),
                    "constraint_config": ConstraintConfig(
                        rate_limit=100.0,
                        crc_check=True,
                        dlc_check=True
                    ).dict(),
                    "baseline_log_path": None,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "status": "active"
                },
                {
                    "id": "plan-002",
                    "name": "传统模糊测试专项",
                    "description": "使用传统变异规则进行边界值测试",
                    "test_mode": TestMode.TRADITIONAL.value,
                    "traditional_config": TraditionalTestConfig(enabled=True, intensity=8, max_cases=1000).dict(),
                    "gan_config": None,
                    "constraint_config": ConstraintConfig(
                        rate_limit=150.0,
                        crc_check=True,
                        dlc_check=True
                    ).dict(),
                    "baseline_log_path": None,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "status": "draft"
                },
                {
                    "id": "plan-003",
                    "name": "GAN智能测试专项",
                    "description": "使用GAN模型生成智能测试用例",
                    "test_mode": TestMode.GAN.value,
                    "traditional_config": None,
                    "gan_config": GANTestConfig(enabled=True, model_version="v1.2", sampling_temperature=1.2, max_cases=500).dict(),
                    "constraint_config": ConstraintConfig(
                        rate_limit=80.0,
                        crc_check=True,
                        dlc_check=True
                    ).dict(),
                    "baseline_log_path": None,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "status": "active"
                }
            ]
            return [TestPlanResponse(**plan) for plan in mock_plans]
        
        return [TestPlanResponse(**plan) for plan in plans_data]
    
    async def update_test_plan(self, plan_id: str, plan: TestPlanCreate) -> Optional[TestPlanResponse]:
        """更新测试计划"""
        # 先检查计划是否存在
        existing_plan = await self.get_test_plan(plan_id)
        if not existing_plan:
            return None
        
        now = datetime.now()
        
        plan_data = {
            "id": plan_id,
            "name": plan.name,
            "description": plan.description,
            "test_mode": plan.test_mode.value,
            "traditional_config": plan.traditional_config.dict() if plan.traditional_config else None,
            "gan_config": plan.gan_config.dict() if plan.gan_config else None,
            "constraint_config": plan.constraint_config.dict(),
            "baseline_log_path": plan.baseline_log_path,
            "created_at": existing_plan.created_at.isoformat() if isinstance(existing_plan.created_at, datetime) else existing_plan.created_at,
            "updated_at": now.isoformat(),
            "status": existing_plan.status
        }
        
        # 更新数据库
        await self.db.update_test_plan(plan_id, plan_data)
        
        # 更新文件（备份）
        plan_file = os.path.join(self.plans_dir, f"{plan_id}.json")
        with open(plan_file, "w", encoding="utf-8") as f:
            json.dump(plan_data, f, ensure_ascii=False, indent=2)
        
        return TestPlanResponse(**plan_data)
    
    async def delete_test_plan(self, plan_id: str) -> bool:
        """删除测试计划"""
        return await self.db.delete_test_plan(plan_id)



