"""
导出路由
"""
from fastapi import APIRouter
from fastapi.responses import Response

from api.models.schemas import ExportRequest
from api.services import export_service

router = APIRouter()


@router.post("/export")
async def export_data(request: ExportRequest):
    """导出数据"""
    content, media_type, filename = export_service.export_data(request)

    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
