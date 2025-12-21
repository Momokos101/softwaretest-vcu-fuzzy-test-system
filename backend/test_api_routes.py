#!/usr/bin/env python3
"""
测试API路由是否正常工作
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试所有模块导入"""
    print("=" * 60)
    print("测试1: 模块导入")
    print("=" * 60)
    
    try:
        from api.main import app
        print("✓ api.main 导入成功")
        
        from api.routers import test_plans, test_tasks, gan, reports, constraints, monitoring
        print("✓ 所有路由模块导入成功")
        
        from api.services import baic_adapter, gan_integration_service
        print("✓ 所有服务模块导入成功")
        
        from api.database.db import Database
        print("✓ 数据库模块导入成功")
        
        print("\n✓ 所有模块导入测试通过！\n")
        return True
    except Exception as e:
        print(f"✗ 导入失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_data_conversion():
    """测试数据转换"""
    print("=" * 60)
    print("测试2: 数据格式转换")
    print("=" * 60)
    
    try:
        from api.services.baic_adapter import BaicAdapter
        
        adapter = BaicAdapter()
        
        # 测试数据
        gan_data = {
            "cc2_voltage": 7.5,
            "vehicle_status": 100,
            "ready_flag": 1,
            "output_fields": {
                "动力防盗允许READY标志位": 1
            }
        }
        
        result = adapter.convert_gan_data_to_baic_format(gan_data)
        
        # 验证结果
        assert "inputData" in result
        assert len(result["inputData"]) > 0
        
        # 检查转换是否正确
        cc2_found = False
        for item in result["inputData"]:
            if item["name"] == "CC2电压值" and item["value"] == 75:
                cc2_found = True
                break
        
        assert cc2_found, "CC2电压值转换错误"
        
        print("✓ 数据转换测试通过")
        print(f"  输入: {gan_data}")
        print(f"  输出: {result}")
        print("\n✓ 数据格式转换测试通过！\n")
        return True
    except Exception as e:
        print(f"✗ 数据转换测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_database():
    """测试数据库"""
    print("=" * 60)
    print("测试3: 数据库操作")
    print("=" * 60)
    
    try:
        from api.database.db import Database
        
        db = Database()
        print("✓ 数据库初始化成功")
        
        # 测试数据库表是否创建
        import sqlite3
        conn = sqlite3.connect("data/test_system.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ["test_plans", "test_tasks", "anomalies", "constraint_stats"]
        for table in required_tables:
            assert table in tables, f"缺少表: {table}"
        
        print(f"✓ 数据库表创建成功: {', '.join(tables)}")
        conn.close()
        
        print("\n✓ 数据库测试通过！\n")
        return True
    except Exception as e:
        print(f"✗ 数据库测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("API路由和核心功能测试")
    print("=" * 60 + "\n")
    
    results = []
    results.append(("模块导入", test_imports()))
    results.append(("数据转换", test_data_conversion()))
    results.append(("数据库", test_database()))
    
    print("=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("✓ 所有测试通过！API可以正常使用。")
        print("\n下一步: 集成实际GAN模型")
    else:
        print("✗ 部分测试失败，请检查错误信息")
    print("=" * 60 + "\n")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)



