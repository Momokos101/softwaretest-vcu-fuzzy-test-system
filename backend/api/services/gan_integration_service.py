"""
GAN集成服务
整合GAN模型生成、数据转换和北汽接口调用
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np

from api.services.baic_adapter import BaicAdapter
from api.services.gan_model_loader import GANModelLoader
from configs.config_vcu import *

logger = logging.getLogger(__name__)

class GANIntegrationService:
    """GAN集成服务"""
    
    def __init__(self, baic_base_url: Optional[str] = None, model_path: Optional[str] = None):
        """
        初始化GAN集成服务
        
        Args:
            baic_base_url: 北汽接口基础URL，如果为None则使用默认值
            model_path: GAN模型路径，如果为None则使用配置中的路径
        """
        self.baic_adapter = BaicAdapter(base_url=baic_base_url) if baic_base_url else BaicAdapter()
        self.model_loader = GANModelLoader(model_path=model_path)
        self._model_loaded = False
    
    def load_gan_model(self, model_path: Optional[str] = None):
        """
        加载GAN模型
        
        Args:
            model_path: 模型路径，如果为None则使用配置中的路径
        """
        if model_path:
            self.model_loader.model_path = model_path
        
        success = self.model_loader.load_model()
        self._model_loaded = success
        
        if success:
            logger.info("GAN模型加载成功")
        else:
            logger.warning("GAN模型加载失败，将使用模拟模式")
        
        return success
    
    def generate_test_sequence(
        self,
        condition: Optional[Dict[str, Any]] = None,
        sequence_length: int = 8,
        temperature: float = 1.0,
        random_seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        使用GAN模型生成测试序列
        
        Args:
            condition: 生成条件（如测试阶段、目标ID、关键信号状态等）
            sequence_length: 序列长度
            temperature: 采样温度
            random_seed: 随机种子（可选）
        
        Returns:
            GAN生成的测试数据
        """
        logger.info(f"生成测试序列: length={sequence_length}, temperature={temperature}")
        
        # 如果模型未加载，尝试加载一次
        if not self._model_loaded:
            self.load_gan_model()
        
        # 使用模型加载器生成数据
        gan_data = self.model_loader.generate(
            condition=condition,
            sequence_length=sequence_length,
            temperature=temperature,
            random_seed=random_seed
        )
        
        return gan_data
    
    async def generate_and_send_test_case(
        self,
        condition: Optional[Dict[str, Any]] = None,
        sequence_length: int = 8,
        temperature: float = 1.0,
        send_to_baic: bool = True
    ) -> Dict[str, Any]:
        """
        生成测试用例并发送到北汽接口
        
        Args:
            condition: 生成条件
            sequence_length: 序列长度
            temperature: 采样温度
            send_to_baic: 是否发送到北汽接口
        
        Returns:
            包含生成数据和发送结果的信息
        """
        # 生成测试数据
        gan_data = self.generate_test_sequence(
            condition=condition,
            sequence_length=sequence_length,
            temperature=temperature
        )
        
        result = {
            "gan_data": gan_data,
            "sent_to_baic": False,
            "baic_response": None
        }
        
        # 发送到北汽接口
        if send_to_baic:
            try:
                baic_response = await self.baic_adapter.send_test_data(gan_data)
                result["sent_to_baic"] = baic_response.get("success", False)
                result["baic_response"] = baic_response
            except Exception as e:
                logger.error(f"发送数据到北汽接口失败: {str(e)}")
                result["error"] = str(e)
        
        return result
    
    async def generate_and_send_batch(
        self,
        batch_size: int = 10,
        condition: Optional[Dict[str, Any]] = None,
        sequence_length: int = 8,
        temperature: float = 1.0
    ) -> List[Dict[str, Any]]:
        """
        批量生成并发送测试用例
        
        Args:
            batch_size: 批次大小
            condition: 生成条件
            sequence_length: 序列长度
            temperature: 采样温度
        
        Returns:
            批量生成和发送的结果列表
        """
        results = []
        
        for i in range(batch_size):
            logger.info(f"生成并发送测试用例 {i+1}/{batch_size}")
            result = await self.generate_and_send_test_case(
                condition=condition,
                sequence_length=sequence_length,
                temperature=temperature,
                send_to_baic=True
            )
            results.append(result)
            
            # 添加延迟，避免请求过快
            await asyncio.sleep(0.1)
        
        return results

