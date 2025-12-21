"""
GAN测试相关路由
"""
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, Optional
from pydantic import BaseModel

from api.services.gan_integration_service import GANIntegrationService

router = APIRouter()
gan_service = GANIntegrationService()

class GenerateTestCaseRequest(BaseModel):
    """生成测试用例请求"""
    condition: Optional[Dict[str, Any]] = None
    sequence_length: int = 8
    temperature: float = 1.0
    send_to_baic: bool = True

class GenerateBatchRequest(BaseModel):
    """批量生成请求"""
    count: int = 10  # 使用count而不是batch_size，与API测试一致
    condition: Optional[Dict[str, Any]] = None
    sequence_length: int = 8
    temperature: float = 1.0

@router.post("/gan/generate")
async def generate_test_case(request: GenerateTestCaseRequest):
    """
    生成单个测试用例并发送到北汽接口
    """
    try:
        # 参数验证
        if request.sequence_length <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="sequence_length必须大于0"
            )
        if request.sequence_length > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="sequence_length不能超过100"
            )
        if not (0.1 <= request.temperature <= 10.0):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="temperature必须在0.1到10.0之间"
            )
        
        result = await gan_service.generate_and_send_test_case(
            condition=request.condition,
            sequence_length=request.sequence_length,
            temperature=request.temperature,
            send_to_baic=request.send_to_baic
        )
        # 返回格式：包含gan_data和发送状态
        return {
            **result.get("gan_data", {}),
            "sent_to_baic": result.get("sent_to_baic", False),
            "baic_response": result.get("baic_response")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成测试用例失败: {str(e)}"
        )

@router.post("/gan/generate/batch")
@router.post("/gan/generate-batch")  # 同时支持两种路由格式
async def generate_test_cases_batch(request: GenerateBatchRequest):
    """
    批量生成测试用例并发送到北汽接口
    注意：批量生成可能需要较长时间，建议使用较小的count值
    """
    try:
        # 参数验证
        if request.count <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="count必须大于0"
            )
        if request.count > 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="count不能超过20，建议使用10以下"
            )
        if request.sequence_length <= 0 or request.sequence_length > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="sequence_length必须在1到100之间"
            )
        
        # 限制批量大小，避免超时
        max_batch_size = 10
        actual_count = min(request.count, max_batch_size)
        if request.count > max_batch_size:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"批量大小 {request.count} 超过限制 {max_batch_size}，已调整为 {actual_count}")
        
        results = await gan_service.generate_and_send_batch(
            batch_size=actual_count,  # 使用count
            condition=request.condition,
            sequence_length=request.sequence_length,
            temperature=request.temperature
        )
        # 提取gan_data字段，简化返回格式
        simplified_results = []
        for r in results:
            gan_data = r.get("gan_data", {})
            simplified_results.append({
                **gan_data,
                "sent_to_baic": r.get("sent_to_baic", False)
            })
        
        return {
            "total": len(simplified_results),
            "success_count": sum(1 for r in simplified_results if r.get("sent_to_baic", False)),
            "results": simplified_results
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量生成测试用例失败: {str(e)}"
        )

@router.post("/gan/convert")
async def convert_gan_data_to_baic_format(gan_data: Dict[str, Any]):
    """
    将GAN生成的数据转换为北汽接口格式（不发送）
    """
    try:
        baic_format = gan_service.baic_adapter.convert_gan_data_to_baic_format(gan_data)
        return baic_format
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据转换失败: {str(e)}"
        )

