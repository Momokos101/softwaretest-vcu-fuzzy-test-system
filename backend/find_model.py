#!/usr/bin/env python3
"""
查找训练好的GAN模型文件
"""
import os
import sys
from pathlib import Path

def find_model_files(root_dir="."):
    """查找所有可能的模型文件"""
    model_extensions = ['.pth', '.pt', '.pkl', '.h5', '.ckpt', '.pb', '.onnx']
    model_files = []
    
    print("=" * 60)
    print("搜索GAN模型文件...")
    print("=" * 60)
    
    for root, dirs, files in os.walk(root_dir):
        # 跳过一些目录
        skip_dirs = ['__pycache__', '.git', 'node_modules', 'venv', '.venv']
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if any(file.endswith(ext) for ext in model_extensions):
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                model_files.append((file_path, file_size))
                print(f"找到: {file_path} ({file_size:.2f} MB)")
    
    return model_files

def check_model_directory():
    """检查模型目录"""
    model_paths = [
        "model_weights/vcu",
        "model_weights",
        "checkpoints",
        "models",
        "saved_models",
        "../model_weights/vcu",
        "../model_weights"
    ]
    
    print("\n" + "=" * 60)
    print("检查常见模型目录...")
    print("=" * 60)
    
    for path in model_paths:
        full_path = os.path.abspath(path)
        if os.path.exists(full_path):
            print(f"✓ 目录存在: {full_path}")
            files = os.listdir(full_path)
            if files:
                print(f"  文件列表:")
                for f in files[:10]:  # 只显示前10个
                    print(f"    - {f}")
                if len(files) > 10:
                    print(f"    ... 还有 {len(files) - 10} 个文件")
        else:
            print(f"✗ 目录不存在: {full_path}")

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("GAN模型文件查找工具")
    print("=" * 60 + "\n")
    
    # 查找模型文件
    model_files = find_model_files()
    
    # 检查模型目录
    check_model_directory()
    
    print("\n" + "=" * 60)
    if model_files:
        print(f"找到 {len(model_files)} 个可能的模型文件")
        print("\n建议:")
        print("1. 将模型文件复制到: backend/model_weights/vcu/")
        print("2. 或者修改配置中的 MODEL_PATH")
        print("3. 或者在初始化时指定模型路径")
    else:
        print("未找到模型文件")
        print("\n请:")
        print("1. 确认模型文件的位置")
        print("2. 将模型文件放到: backend/model_weights/vcu/")
        print("3. 或者告诉我模型文件的位置，我可以帮你配置")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()



