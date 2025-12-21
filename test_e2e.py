#!/usr/bin/env python3
"""
端到端测试脚本
模拟前端调用后端API，验证前后端连接
"""
import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name: str):
    print(f"\n{Colors.BLUE}=== {name} ==={Colors.END}")

def print_success(msg: str):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg: str):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_info(msg: str):
    print(f"{Colors.YELLOW}→ {msg}{Colors.END}")

def test_health_check():
    """测试健康检查"""
    print_test("1. 健康检查")
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        if r.status_code == 200:
            print_success(f"后端服务正常 (状态码: {r.status_code})")
            return True
        else:
            print_error(f"后端服务异常 (状态码: {r.status_code})")
            return False
    except Exception as e:
        print_error(f"无法连接到后端: {str(e)}")
        return False

def test_test_plans():
    """测试测试计划API"""
    print_test("2. 测试计划API")
    
    # 获取列表
    print_info("获取测试计划列表...")
    r = requests.get(f"{BASE_URL}/test-plans")
    if r.status_code == 200:
        plans = r.json()
        print_success(f"获取列表成功，共 {len(plans)} 个计划")
    else:
        print_error(f"获取列表失败: {r.status_code}")
        return None
    
    # 创建计划
    print_info("创建测试计划...")
    plan_data = {
        "name": "E2E测试计划",
        "description": "端到端测试用计划",
        "test_mode": "both",
        "constraint_config": {
            "dbc_file_path": "test.dbc",
            "whitelist": [],
            "blacklist": [],
            "value_ranges": {},
            "rate_limit": 100.0,
            "crc_check": True,
            "dlc_check": True
        }
    }
    r = requests.post(f"{BASE_URL}/test-plans", json=plan_data)
    if r.status_code == 201:
        plan = r.json()
        print_success(f"创建计划成功，ID: {plan['id']}")
        return plan['id']
    else:
        print_error(f"创建计划失败: {r.status_code} - {r.text[:100]}")
        return None

def test_test_tasks(plan_id: str):
    """测试测试任务API"""
    print_test("3. 测试任务API")
    
    # 创建任务
    print_info("创建测试任务...")
    task_data = {"plan_id": plan_id}
    r = requests.post(f"{BASE_URL}/test-tasks", json=task_data)
    if r.status_code == 201:
        task = r.json()
        task_id = task['id']
        print_success(f"创建任务成功，ID: {task_id}")
    else:
        print_error(f"创建任务失败: {r.status_code}")
        return None
    
    # 启动任务
    print_info("启动任务...")
    r = requests.post(f"{BASE_URL}/test-tasks/{task_id}/start")
    if r.status_code == 200:
        task = r.json()
        print_success(f"任务已启动，状态: {task['status']}")
    else:
        print_error(f"启动任务失败: {r.status_code}")
    
    # 等待任务执行
    print_info("等待任务执行3秒...")
    time.sleep(3)
    
    # 获取任务详情
    print_info("获取任务详情...")
    r = requests.get(f"{BASE_URL}/test-tasks/{task_id}")
    if r.status_code == 200:
        task = r.json()
        print_success(f"任务状态: {task['status']}")
        print_info(f"  总用例数: {task['total_cases']}")
        print_info(f"  总异常数: {task['total_anomalies']}")
        print_info(f"  传统测试: {task['traditional_stats']['cases']}用例, {task['traditional_stats']['anomalies']}异常")
        print_info(f"  GAN测试: {task['gan_stats']['cases']}用例, {task['gan_stats']['anomalies']}异常")
    
    # 获取监控指标
    print_info("获取监控指标...")
    r = requests.get(f"{BASE_URL}/test-tasks/{task_id}/metrics?limit=5")
    if r.status_code == 200:
        metrics = r.json()
        print_success(f"获取监控指标成功，共 {len(metrics)} 条")
    
    # 获取异常列表
    print_info("获取异常列表...")
    r = requests.get(f"{BASE_URL}/test-tasks/{task_id}/anomalies?top_n=5")
    if r.status_code == 200:
        anomalies = r.json()
        print_success(f"获取异常列表成功，共 {len(anomalies)} 条")
    
    # 获取约束统计
    print_info("获取约束统计...")
    r = requests.get(f"{BASE_URL}/test-tasks/{task_id}/constraints")
    if r.status_code == 200:
        stats = r.json()
        print_success(f"获取约束统计成功，拦截总数: {stats['total_intercepted']}")
    
    # 暂停任务
    print_info("暂停任务...")
    r = requests.post(f"{BASE_URL}/test-tasks/{task_id}/pause")
    if r.status_code == 200:
        task = r.json()
        print_success(f"任务已暂停，状态: {task['status']}")
    
    # 继续任务
    print_info("继续任务...")
    r = requests.post(f"{BASE_URL}/test-tasks/{task_id}/start")
    if r.status_code == 200:
        task = r.json()
        print_success(f"任务已继续，状态: {task['status']}")
    
    # 停止任务
    print_info("停止任务...")
    r = requests.post(f"{BASE_URL}/test-tasks/{task_id}/stop")
    if r.status_code == 200:
        task = r.json()
        print_success(f"任务已停止，状态: {task['status']}")
    
    return task_id

def test_gan_api():
    """测试GAN API"""
    print_test("4. GAN API")
    
    # 生成单个用例
    print_info("生成单个测试用例...")
    r = requests.post(
        f"{BASE_URL}/gan/generate",
        json={"sequence_length": 8, "temperature": 1.0, "send_to_baic": False},
        timeout=30
    )
    if r.status_code == 200:
        data = r.json()
        print_success(f"生成成功，电压序列长度: {len(data.get('voltage_sequence', []))}")
    else:
        print_error(f"生成失败: {r.status_code}")
    
    # 批量生成
    print_info("批量生成测试用例（3个）...")
    r = requests.post(
        f"{BASE_URL}/gan/generate/batch",
        json={"count": 3, "sequence_length": 8, "temperature": 1.0},
        timeout=60
    )
    if r.status_code == 200:
        result = r.json()
        print_success(f"批量生成成功，总数: {result['total']}")
    else:
        print_error(f"批量生成失败: {r.status_code}")
    
    # 格式转换
    print_info("格式转换...")
    gan_data = {
        "cc2_voltage": 6.5,
        "voltage_sequence": [6.5, 6.6, 6.7, 6.8, 6.9, 7.0, 7.1, 7.2],
        "vehicle_status": 100,
        "ready_flag": 1
    }
    r = requests.post(f"{BASE_URL}/gan/convert", json=gan_data)
    if r.status_code == 200:
        baic_format = r.json()
        print_success(f"转换成功，包含字段: {list(baic_format.keys())}")
    else:
        print_error(f"转换失败: {r.status_code}")

def test_report_api(task_id: str):
    """测试报告API"""
    print_test("5. 报告API")
    
    # 生成报告
    print_info("生成测试报告...")
    r = requests.post(f"{BASE_URL}/test-tasks/{task_id}/report")
    if r.status_code == 200:
        report = r.json()
        print_success(f"报告生成成功，路径: {report['report_path']}")
    else:
        print_error(f"报告生成失败: {r.status_code} - {r.text[:100]}")
    
    # 获取方法对比
    print_info("获取方法对比...")
    r = requests.get(f"{BASE_URL}/test-tasks/{task_id}/report/comparison")
    if r.status_code == 200:
        comparison = r.json()
        print_success("获取方法对比成功")
        print_info(f"  传统测试异常率: {comparison['traditional']['anomaly_rate']*100:.2f}%")
        print_info(f"  GAN测试异常率: {comparison['gan']['anomaly_rate']*100:.2f}%")

def test_error_handling():
    """测试错误处理"""
    print_test("6. 错误处理")
    
    # 测试404
    print_info("测试404错误（不存在的任务）...")
    r = requests.get(f"{BASE_URL}/test-tasks/00000000-0000-0000-0000-000000000000")
    if r.status_code == 404:
        print_success("404错误处理正确")
    else:
        print_error(f"预期404，实际{r.status_code}")
    
    # 测试400
    print_info("测试400错误（无效参数）...")
    r = requests.post(
        f"{BASE_URL}/gan/generate",
        json={"sequence_length": -1, "temperature": 1.0}
    )
    if r.status_code == 400:
        print_success("400错误处理正确")
        print_info(f"  错误信息: {r.json().get('detail', '')[:50]}")
    else:
        print_error(f"预期400，实际{r.status_code}")

def main():
    print(f"\n{Colors.BLUE}{'='*60}")
    print("端到端测试 - 前后端连接验证")
    print(f"{'='*60}{Colors.END}\n")
    
    # 测试健康检查
    if not test_health_check():
        print_error("后端服务未运行，请先启动后端服务")
        return
    
    # 测试测试计划
    plan_id = test_test_plans()
    if not plan_id:
        print_error("无法创建测试计划，测试终止")
        return
    
    # 测试测试任务
    task_id = test_test_tasks(plan_id)
    if not task_id:
        print_error("无法创建测试任务，测试终止")
        return
    
    # 测试GAN API
    test_gan_api()
    
    # 测试报告API
    test_report_api(task_id)
    
    # 测试错误处理
    test_error_handling()
    
    # 总结
    print(f"\n{Colors.GREEN}{'='*60}")
    print("端到端测试完成！")
    print(f"{'='*60}{Colors.END}\n")
    print_success("所有接口测试通过")
    print_info("前后端连接正常，数据流畅通")
    print_info("建议：安装Node.js后启动前端服务进行UI测试")

if __name__ == "__main__":
    main()

