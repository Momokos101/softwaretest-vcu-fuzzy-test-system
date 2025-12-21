"""
测试报告路由
"""
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from typing import Optional

from api.models.schemas import TestReportRequest, TestReportResponse
from api.services.report_service import ReportService

router = APIRouter()
service = ReportService()

@router.post("/test-tasks/{task_id}/report", response_model=TestReportResponse)
async def generate_report(task_id: str, request: Optional[TestReportRequest] = None):
    """
    生成测试报告
    """
    if not request:
        request = TestReportRequest(task_id=task_id)
    
    try:
        report = await service.generate_report(request)
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成测试报告失败: {str(e)}"
        )

@router.get("/test-tasks/{task_id}/report/download")
async def download_report(task_id: str, format: str = "pdf"):
    """
    下载测试报告文件
    """
    try:
        file_path = await service.get_report_file_path(task_id, format)
        if not file_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"报告文件不存在，请先生成报告"
            )
        
        media_type_map = {
            "pdf": "application/pdf",
            "markdown": "text/markdown",
            "json": "application/json"
        }
        
        return FileResponse(
            file_path,
            media_type=media_type_map.get(format, "application/octet-stream"),
            filename=f"test_report_{task_id}.{format}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"下载报告失败: {str(e)}"
        )

@router.get("/test-tasks/{task_id}/report/comparison")
async def get_method_comparison(task_id: str):
    """
    获取测试方法对比数据
    """
    try:
        comparison = await service.get_method_comparison(task_id)
        return comparison
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取方法对比失败: {str(e)}"
        )



