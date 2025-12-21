"""
北汽接口适配器
将GAN生成的数据转换为北汽接口格式并发送
"""
import httpx
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class BaicAdapter:
    """北汽接口适配器"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:4523/m1/7470950-7205604-default"):
        """
        初始化适配器
        
        Args:
            base_url: 北汽接口基础URL
        """
        self.base_url = base_url.rstrip('/')
        self.endpoint = f"{self.base_url}/gan/data/input"
        self.timeout = 30.0
    
    def convert_gan_data_to_baic_format(
        self, 
        gan_data: Dict[str, Any]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        将GAN生成的数据转换为北汽接口格式
        
        Args:
            gan_data: GAN生成的数据，格式示例：
                {
                    "cc2_voltage": 7.5,  # CC2电压值（浮点数）
                    "vehicle_status": 100,  # 整车状态（整数）
                    "ready_flag": 1,  # READY标志位（0或1）
                    "voltage_sequence": [7.5, 6.8, 5.2, ...],  # 电压序列（可选）
                    # 其他信号...
                }
        
        Returns:
            符合北汽接口格式的数据：
            {
                "inputData": [
                    {"name": "CC2电压值", "value": 75},  # 注意：value需要是整数
                    {"name": "整车状态", "value": 100},
                    {"name": "READY标志位", "value": 1},
                    ...
                ]
            }
        """
        input_data = []
        
        # 信号名称映射（GAN数据字段名 -> 北汽接口信号名）
        signal_mapping = {
            "cc2_voltage": "CC2电压值",
            "vehicle_status": "整车状态",
            "ready_flag": "READY标志位",
            "动力防盗允许READY标志位": "动力防盗允许READY标志位",
            "CC2电压值": "CC2电压值",
            "整车状态": "整车状态",
        }
        
        # 处理主要信号
        for gan_key, baic_name in signal_mapping.items():
            if gan_key in gan_data:
                value = gan_data[gan_key]
                # 转换为整数：如果是浮点数（如电压），乘以10转换为整数（保留1位小数精度）
                if isinstance(value, float):
                    # 电压值：7.5V -> 75 (保留1位小数)
                    int_value = int(value * 10)
                elif isinstance(value, (int, str)):
                    int_value = int(value)
                else:
                    continue
                
                input_data.append({
                    "name": baic_name,
                    "value": int_value
                })
        
        # 处理output_fields（如果存在）
        if "output_fields" in gan_data:
            for field_name, field_value in gan_data["output_fields"].items():
                # 避免重复添加已处理的字段
                if field_name not in signal_mapping:
                    if isinstance(field_value, float):
                        int_value = int(field_value * 10)
                    elif isinstance(field_value, (int, str)):
                        int_value = int(field_value)
                    else:
                        continue
                    
                    input_data.append({
                        "name": field_name,
                        "value": int_value
                    })
        
        # 处理电压序列（如果存在，发送第一个值作为主要电压）
        if "voltage_sequence" in gan_data and len(gan_data["voltage_sequence"]) > 0:
            first_voltage = gan_data["voltage_sequence"][0]
            # 检查是否已经添加了CC2电压值
            has_cc2 = any(item["name"] == "CC2电压值" for item in input_data)
            if not has_cc2:
                input_data.append({
                    "name": "CC2电压值",
                    "value": int(first_voltage * 10)
                })
        
        return {"inputData": input_data}
    
    async def send_test_data(
        self, 
        gan_data: Dict[str, Any],
        retry_times: int = 3
    ) -> Dict[str, Any]:
        """
        发送测试数据到北汽接口
        
        Args:
            gan_data: GAN生成的数据
            retry_times: 重试次数
        
        Returns:
            响应数据
        """
        # 转换为北汽格式
        baic_format_data = self.convert_gan_data_to_baic_format(gan_data)
        
        logger.info(f"发送数据到北汽接口: {self.endpoint}")
        logger.debug(f"请求数据: {baic_format_data}")
        
        # 发送HTTP请求
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            last_error = None
            for attempt in range(retry_times):
                try:
                    response = await client.post(
                        self.endpoint,
                        json=baic_format_data,
                        headers={"Content-Type": "application/json"}
                    )
                    response.raise_for_status()
                    
                    result = response.json()
                    logger.info(f"北汽接口响应成功: {result}")
                    return {
                        "success": True,
                        "data": result,
                        "sent_data": baic_format_data,
                        "timestamp": datetime.now().isoformat()
                    }
                except httpx.HTTPStatusError as e:
                    last_error = e
                    logger.warning(f"北汽接口请求失败 (尝试 {attempt + 1}/{retry_times}): {e.response.status_code} - {e.response.text}")
                    if attempt < retry_times - 1:
                        await asyncio.sleep(1)  # 等待1秒后重试
                except httpx.RequestError as e:
                    last_error = e
                    logger.error(f"北汽接口请求错误 (尝试 {attempt + 1}/{retry_times}): {str(e)}")
                    if attempt < retry_times - 1:
                        await asyncio.sleep(1)
                except Exception as e:
                    last_error = e
                    logger.error(f"发送数据到北汽接口时发生未知错误: {str(e)}")
                    break
            
            # 所有重试都失败
            return {
                "success": False,
                "error": str(last_error) if last_error else "未知错误",
                "sent_data": baic_format_data,
                "timestamp": datetime.now().isoformat()
            }
    
    def convert_voltage_sequence_to_baic_format(
        self,
        voltage_sequence: List[float],
        additional_signals: Optional[Dict[str, Any]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        将电压序列转换为北汽接口格式
        
        Args:
            voltage_sequence: 电压序列，例如 [7.5, 6.8, 5.2, ...]
            additional_signals: 额外的信号数据
        
        Returns:
            符合北汽接口格式的数据
        """
        gan_data = {
            "cc2_voltage": voltage_sequence[0] if voltage_sequence else 0.0,
            "voltage_sequence": voltage_sequence
        }
        
        if additional_signals:
            gan_data.update(additional_signals)
        
        return self.convert_gan_data_to_baic_format(gan_data)

