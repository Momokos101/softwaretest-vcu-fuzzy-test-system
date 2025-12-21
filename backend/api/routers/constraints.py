"""
约束管理路由
"""
from fastapi import APIRouter, HTTPException, status

from api.models.schemas import ConstraintStats
from api.services.constraint_service import ConstraintService

router = APIRouter()
service = ConstraintService()

@router.get("/test-tasks/{task_id}/constraints", response_model=ConstraintStats)
async def get_constraint_stats(task_id: str):
    """
    获取测试任务的约束统计信息
    包括拦截总数、拦截原因分布、已启用规则等
    """
    try:
        stats = await service.get_constraint_stats(task_id)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取约束统计失败: {str(e)}"
        )



