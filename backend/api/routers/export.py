"""
导出路由
"""
from fastapi import APIRouter
from fastapi.responses import Response

from api.models.schemas import ExportFormat, ExportRequest, ExportScope
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


@router.get("/export/{format}")
async def export_by_format(format: ExportFormat):
    """Plan V2 route: GET /api/export/{json|csv|excel}."""
    content, media_type, filename = export_service.export_data(
        ExportRequest(format=format, scope=ExportScope())
    )
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
