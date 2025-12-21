"""
测试任务管理路由
"""
from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from typing import List
from datetime import datetime

from api.models.schemas import (
    TestTaskResponse, TaskStatus, TaskStartRequest, AnomalyResponse
)
from api.services.test_task_service import TestTaskService
from api.websocket_manager import WebSocketManager

router = APIRouter()
service = TestTaskService()
ws_manager = WebSocketManager()

@router.post("/test-tasks", response_model=TestTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_test_task(request: TaskStartRequest):
    """
    创建并启动测试任务
    """
    try:
        task = await service.create_task(request.plan_id)
        return task
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建测试任务失败: {str(e)}"
        )

@router.post("/test-tasks/{task_id}/start", response_model=TestTaskResponse)
async def start_test_task(task_id: str, background_tasks: BackgroundTasks):
    """
    启动测试任务
    """
    try:
        task = await service.start_task(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"测试任务 {task_id} 不存在"
            )
        
        # 在后台启动测试执行
        background_tasks.add_task(service.execute_test_task, task_id)
        
        return task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"启动测试任务失败: {str(e)}"
        )

@router.post("/test-tasks/{task_id}/pause", response_model=TestTaskResponse)
async def pause_test_task(task_id: str):
    """
    暂停测试任务
    """
    try:
        task = await service.pause_task(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"测试任务 {task_id} 不存在"
            )
        
        # 通知WebSocket客户端
        await ws_manager.broadcast_to_task(
            task_id,
            {"type": "task_paused", "task_id": task_id, "timestamp": datetime.now().isoformat()}
        )
        
        return task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"暂停测试任务失败: {str(e)}"
        )

@router.post("/test-tasks/{task_id}/stop", response_model=TestTaskResponse)
async def stop_test_task(task_id: str):
    """
    停止测试任务（紧急停止）
    """
    try:
        task = await service.stop_task(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"测试任务 {task_id} 不存在"
            )
        
        # 通知WebSocket客户端
        await ws_manager.broadcast_to_task(
            task_id,
            {"type": "task_stopped", "task_id": task_id, "timestamp": datetime.now().isoformat()}
        )
        
        return task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"停止测试任务失败: {str(e)}"
        )

@router.get("/test-tasks/{task_id}", response_model=TestTaskResponse)
async def get_test_task(task_id: str):
    """
    获取测试任务详情
    """
    try:
        task = await service.get_task(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"测试任务 {task_id} 不存在"
            )
        return task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取测试任务失败: {str(e)}"
        )

@router.get("/test-tasks", response_model=List[TestTaskResponse])
async def get_test_tasks(skip: int = 0, limit: int = 100):
    """
    获取测试任务列表
    """
    try:
        tasks = await service.get_tasks(skip=skip, limit=limit)
        return tasks
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取测试任务列表失败: {str(e)}"
        )

@router.get("/test-tasks/{task_id}/anomalies", response_model=List[AnomalyResponse])
async def get_task_anomalies(
    task_id: str,
    top_n: int = 10,
    source: str = None,  # "traditional" or "gan"
    min_severity: int = 1
):
    """
    获取测试任务的异常列表（Top N）
    """
    try:
        anomalies = await service.get_task_anomalies(
            task_id, top_n=top_n, source=source, min_severity=min_severity
        )
        return anomalies
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取异常列表失败: {str(e)}"
        )



