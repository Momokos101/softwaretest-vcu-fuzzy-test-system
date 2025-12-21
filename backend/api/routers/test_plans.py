"""
测试计划管理路由
"""
from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime
import uuid

from api.models.schemas import (
    TestPlanCreate, TestPlanResponse, TestMode
)
from api.services.test_plan_service import TestPlanService

router = APIRouter()
service = TestPlanService()

@router.post("/test-plans", response_model=TestPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_test_plan(plan: TestPlanCreate):
    """
    创建测试计划
    
    支持配置传统测试和GAN测试两种模式
    """
    try:
        # 根据test_mode自动设置配置
        if plan.test_mode == TestMode.TRADITIONAL:
            if not plan.traditional_config:
                from api.models.schemas import TraditionalTestConfig
                plan.traditional_config = TraditionalTestConfig(enabled=True)
            if plan.gan_config:
                plan.gan_config.enabled = False
        elif plan.test_mode == TestMode.GAN:
            if not plan.gan_config:
                from api.models.schemas import GANTestConfig
                plan.gan_config = GANTestConfig(enabled=True)
            if plan.traditional_config:
                plan.traditional_config.enabled = False
        elif plan.test_mode == TestMode.BOTH:
            if not plan.traditional_config:
                from api.models.schemas import TraditionalTestConfig
                plan.traditional_config = TraditionalTestConfig(enabled=True)
            if not plan.gan_config:
                from api.models.schemas import GANTestConfig
                plan.gan_config = GANTestConfig(enabled=True)
        
        created_plan = await service.create_test_plan(plan)
        return created_plan
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建测试计划失败: {str(e)}"
        )

@router.get("/test-plans", response_model=List[TestPlanResponse])
async def get_test_plans(skip: int = 0, limit: int = 100):
    """
    获取测试计划列表
    """
    try:
        plans = await service.get_test_plans(skip=skip, limit=limit)
        return plans
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取测试计划列表失败: {str(e)}"
        )

@router.get("/test-plans/{plan_id}", response_model=TestPlanResponse)
async def get_test_plan(plan_id: str):
    """
    获取单个测试计划详情
    """
    try:
        plan = await service.get_test_plan(plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"测试计划 {plan_id} 不存在"
            )
        return plan
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取测试计划失败: {str(e)}"
        )

@router.put("/test-plans/{plan_id}", response_model=TestPlanResponse)
async def update_test_plan(plan_id: str, plan: TestPlanCreate):
    """
    更新测试计划
    """
    try:
        # 根据test_mode自动设置配置
        if plan.test_mode == TestMode.TRADITIONAL:
            if not plan.traditional_config:
                from api.models.schemas import TraditionalTestConfig
                plan.traditional_config = TraditionalTestConfig(enabled=True)
            if plan.gan_config:
                plan.gan_config.enabled = False
        elif plan.test_mode == TestMode.GAN:
            if not plan.gan_config:
                from api.models.schemas import GANTestConfig
                plan.gan_config = GANTestConfig(enabled=True)
            if plan.traditional_config:
                plan.traditional_config.enabled = False
        elif plan.test_mode == TestMode.BOTH:
            if not plan.traditional_config:
                from api.models.schemas import TraditionalTestConfig
                plan.traditional_config = TraditionalTestConfig(enabled=True)
            if not plan.gan_config:
                from api.models.schemas import GANTestConfig
                plan.gan_config = GANTestConfig(enabled=True)
        
        updated_plan = await service.update_test_plan(plan_id, plan)
        if not updated_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"测试计划 {plan_id} 不存在"
            )
        return updated_plan
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新测试计划失败: {str(e)}"
        )

@router.delete("/test-plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test_plan(plan_id: str):
    """
    删除测试计划
    """
    try:
        success = await service.delete_test_plan(plan_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"测试计划 {plan_id} 不存在"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除测试计划失败: {str(e)}"
        )



