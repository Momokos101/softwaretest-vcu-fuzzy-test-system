"""
监控相关路由
"""
from fastapi import APIRouter, HTTPException, status
from typing import List

from api.models.schemas import RealTimeMetrics
from api.services.monitoring_service import MonitoringService

router = APIRouter()
service = MonitoringService()

@router.get("/test-tasks/{task_id}/metrics", response_model=List[RealTimeMetrics])
async def get_task_metrics(task_id: str, limit: int = 100):
    """
    获取测试任务的历史监控指标
    """
    try:
        metrics = await service.get_task_metrics(task_id, limit=limit)
        return metrics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取监控指标失败: {str(e)}"
        )



