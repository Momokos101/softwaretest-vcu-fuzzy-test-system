#!/usr/bin/env python3
"""
使用示例：如何集成GAN生成和北汽接口调用
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.services.gan_integration_service import GANIntegrationService

async def example_single_test_case():
    """示例1: 生成单个测试用例并发送"""
    print("示例1: 生成单个测试用例并发送到北汽接口")
    print("-" * 60)
    
    # 初始化GAN集成服务
    gan_service = GANIntegrationService(
        baic_base_url="http://127.0.0.1:4523/m1/7470950-7205604-default"
    )
    
    # 定义生成条件
    condition = {
        "target_phase": "wake",  # 唤醒阶段
        "vehicle_status": 100,    # 整车状态
    }
    
    # 生成并发送
    result = await gan_service.generate_and_send_test_case(
        condition=condition,
        sequence_length=8,      # 序列长度
        temperature=1.0,         # 采样温度
        send_to_baic=True        # 发送到北汽接口
    )
    
    # 检查结果
    if result.get("sent_to_baic"):
        print("✓ 测试用例已成功发送到北汽接口")
        print(f"  生成的数据: {result['gan_data']}")
    else:
        print("✗ 发送失败")
        print(f"  错误: {result.get('error', '未知错误')}")
    
    print()

async def example_batch_test_cases():
    """示例2: 批量生成测试用例"""
    print("示例2: 批量生成测试用例")
    print("-" * 60)
    
    gan_service = GANIntegrationService(
        baic_base_url="http://127.0.0.1:4523/m1/7470950-7205604-default"
    )
    
    # 批量生成10个测试用例
    results = await gan_service.generate_and_send_batch(
        batch_size=10,
        condition={"target_phase": "wake"},
        sequence_length=8,
        temperature=1.0
    )
    
    # 统计结果
    success_count = sum(1 for r in results if r.get("sent_to_baic", False))
    print(f"✓ 批量生成完成: {success_count}/{len(results)} 成功")
    print()

async def example_in_test_task():
    """示例3: 在测试任务执行中集成"""
    print("示例3: 在测试任务执行流程中集成")
    print("-" * 60)
    
    gan_service = GANIntegrationService()
    
    # 模拟测试任务执行循环
    print("模拟测试任务执行...")
    for i in range(5):
        print(f"\n第 {i+1} 轮测试:")
        
        # 根据测试阶段选择不同的条件
        if i < 2:
            phase = "wake"  # 唤醒阶段
        elif i < 4:
            phase = "ready"  # Ready阶段
        else:
            phase = "sleep"  # 休眠阶段
        
        condition = {
            "target_phase": phase,
            "vehicle_status": 100 + i * 10
        }
        
        # 生成并发送测试用例
        result = await gan_service.generate_and_send_test_case(
            condition=condition,
            sequence_length=8,
            temperature=1.0,
            send_to_baic=True
        )
        
        if result.get("sent_to_baic"):
            print(f"  ✓ {phase}阶段测试用例已发送")
        else:
            print(f"  ✗ {phase}阶段测试用例发送失败")
        
        # 模拟执行间隔
        await asyncio.sleep(0.5)
    
    print("\n✓ 测试任务执行完成")
    print()

async def main():
    """运行所有示例"""
    print("=" * 60)
    print("GAN生成与北汽接口对接使用示例")
    print("=" * 60)
    print()
    
    try:
        await example_single_test_case()
        await example_batch_test_cases()
        await example_in_test_task()
        
        print("=" * 60)
        print("所有示例运行完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n运行示例时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())



