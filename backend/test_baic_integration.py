#!/usr/bin/env python3
"""
测试北汽接口对接功能
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.services.baic_adapter import BaicAdapter
from api.services.gan_integration_service import GANIntegrationService

async def test_baic_adapter():
    """测试北汽适配器"""
    print("=" * 60)
    print("测试1: 北汽适配器 - 数据转换")
    print("=" * 60)
    
    adapter = BaicAdapter(base_url="http://127.0.0.1:4523/m1/7470950-7205604-default")
    
    # 模拟GAN生成的数据
    gan_data = {
        "cc2_voltage": 7.5,
        "vehicle_status": 100,
        "ready_flag": 1,
        "voltage_sequence": [7.5, 6.8, 5.2, 4.8],
        "output_fields": {
            "动力防盗允许READY标志位": 1
        }
    }
    
    print(f"\nGAN生成的数据:")
    print(f"  {gan_data}")
    
    # 转换为北汽格式
    baic_format = adapter.convert_gan_data_to_baic_format(gan_data)
    print(f"\n转换后的北汽格式:")
    import json
    print(json.dumps(baic_format, indent=2, ensure_ascii=False))
    
    # 测试发送（实际发送需要北汽接口运行）
    print(f"\n尝试发送到北汽接口...")
    response = await adapter.send_test_data(gan_data)
    print(f"发送结果: {response.get('success', False)}")
    if not response.get('success'):
        print(f"错误信息: {response.get('error', '未知错误')}")
    
    print("\n" + "=" * 60)

async def test_gan_integration():
    """测试GAN集成服务"""
    print("=" * 60)
    print("测试2: GAN集成服务 - 生成并发送测试用例")
    print("=" * 60)
    
    gan_service = GANIntegrationService(
        baic_base_url="http://127.0.0.1:4523/m1/7470950-7205604-default"
    )
    
    # 生成单个测试用例
    print(f"\n生成单个测试用例...")
    result = await gan_service.generate_and_send_test_case(
        condition={"target_phase": "wake", "vehicle_status": 100},
        sequence_length=8,
        temperature=1.0,
        send_to_baic=True
    )
    
    print(f"生成结果:")
    print(f"  - 已生成: {result.get('gan_data') is not None}")
    print(f"  - 已发送: {result.get('sent_to_baic', False)}")
    if result.get('baic_response'):
        print(f"  - 发送成功: {result['baic_response'].get('success', False)}")
    
    print("\n" + "=" * 60)

async def test_batch_generation():
    """测试批量生成"""
    print("=" * 60)
    print("测试3: 批量生成测试用例")
    print("=" * 60)
    
    gan_service = GANIntegrationService(
        baic_base_url="http://127.0.0.1:4523/m1/7470950-7205604-default"
    )
    
    print(f"\n批量生成3个测试用例...")
    results = await gan_service.generate_and_send_batch(
        batch_size=3,
        condition={"target_phase": "wake"},
        sequence_length=8,
        temperature=1.0
    )
    
    success_count = sum(1 for r in results if r.get("sent_to_baic", False))
    print(f"\n批量生成结果:")
    print(f"  - 总数: {len(results)}")
    print(f"  - 成功: {success_count}")
    print(f"  - 失败: {len(results) - success_count}")
    
    print("\n" + "=" * 60)

async def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("北汽接口对接功能测试")
    print("=" * 60)
    print("\n注意: 此测试需要北汽接口服务运行在")
    print("      http://127.0.0.1:4523/m1/7470950-7205604-default/gan/data/input")
    print("\n如果接口未运行，测试会显示连接错误，这是正常的。")
    print("=" * 60 + "\n")
    
    try:
        # 测试1: 适配器
        await test_baic_adapter()
        
        # 测试2: 集成服务
        await test_gan_integration()
        
        # 测试3: 批量生成
        await test_batch_generation()
        
        print("\n" + "=" * 60)
        print("所有测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())

