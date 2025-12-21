#!/usr/bin/env python3
"""
设置GAN模型路径
帮助用户配置模型文件位置
"""
import os
import sys
import shutil
from pathlib import Path

def setup_model():
    """设置模型路径"""
    print("=" * 60)
    print("GAN模型设置向导")
    print("=" * 60)
    print()
    
    # 目标目录
    target_dir = "model_weights/vcu"
    os.makedirs(target_dir, exist_ok=True)
    
    print(f"目标模型目录: {os.path.abspath(target_dir)}")
    print()
    
    # 询问用户模型文件位置
    print("请选择模型文件的位置:")
    print("1. 模型文件已经在其他位置，告诉我路径")
    print("2. 模型文件在当前项目目录中")
    print("3. 模型文件在其他目录，需要复制")
    print("4. 跳过（稍后手动配置）")
    
    choice = input("\n请选择 (1-4): ").strip()
    
    if choice == "1":
        model_path = input("请输入模型文件的完整路径: ").strip()
        if os.path.exists(model_path):
            print(f"\n✓ 找到模型文件: {model_path}")
            
            # 创建符号链接或复制
            target_file = os.path.join(target_dir, os.path.basename(model_path))
            try:
                if os.path.exists(target_file):
                    os.remove(target_file)
                os.symlink(model_path, target_file)
                print(f"✓ 已创建符号链接: {target_file}")
            except:
                # 如果符号链接失败，尝试复制
                shutil.copy2(model_path, target_file)
                print(f"✓ 已复制模型文件到: {target_file}")
            
            print(f"\n模型路径已配置: {target_file}")
        else:
            print(f"✗ 文件不存在: {model_path}")
    
    elif choice == "2":
        print("\n正在搜索当前目录中的模型文件...")
        model_files = []
        for root, dirs, files in os.walk("."):
            skip_dirs = ['__pycache__', '.git', 'node_modules', 'venv', '.venv', 'api', 'data']
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for file in files:
                if file.endswith(('.pth', '.pt', '.pkl', '.h5', '.ckpt')):
                    file_path = os.path.join(root, file)
                    model_files.append(file_path)
        
        if model_files:
            print(f"\n找到 {len(model_files)} 个可能的模型文件:")
            for i, f in enumerate(model_files, 1):
                print(f"  {i}. {f}")
            
            idx = input(f"\n请选择文件编号 (1-{len(model_files)}): ").strip()
            try:
                selected = model_files[int(idx) - 1]
                target_file = os.path.join(target_dir, os.path.basename(selected))
                shutil.copy2(selected, target_file)
                print(f"✓ 已复制模型文件到: {target_file}")
            except:
                print("✗ 选择无效")
        else:
            print("✗ 未找到模型文件")
    
    elif choice == "3":
        source_dir = input("请输入模型文件所在目录: ").strip()
        if os.path.exists(source_dir):
            model_files = [f for f in os.listdir(source_dir) 
                          if f.endswith(('.pth', '.pt', '.pkl', '.h5', '.ckpt'))]
            if model_files:
                print(f"\n找到 {len(model_files)} 个模型文件:")
                for i, f in enumerate(model_files, 1):
                    print(f"  {i}. {f}")
                
                idx = input(f"\n请选择文件编号 (1-{len(model_files)}): ").strip()
                try:
                    selected = model_files[int(idx) - 1]
                    source_file = os.path.join(source_dir, selected)
                    target_file = os.path.join(target_dir, selected)
                    shutil.copy2(source_file, target_file)
                    print(f"✓ 已复制模型文件到: {target_file}")
                except:
                    print("✗ 选择无效")
            else:
                print("✗ 目录中没有找到模型文件")
        else:
            print(f"✗ 目录不存在: {source_dir}")
    
    elif choice == "4":
        print("\n跳过设置。请手动将模型文件放到以下目录:")
        print(f"  {os.path.abspath(target_dir)}")
        return
    
    # 检查设置结果
    print("\n" + "=" * 60)
    print("检查模型文件...")
    print("=" * 60)
    
    if os.path.exists(target_dir):
        files = [f for f in os.listdir(target_dir) 
                if f.endswith(('.pth', '.pt', '.pkl', '.h5', '.ckpt'))]
        if files:
            print(f"✓ 找到 {len(files)} 个模型文件:")
            for f in files:
                size = os.path.getsize(os.path.join(target_dir, f)) / (1024 * 1024)
                print(f"  - {f} ({size:.2f} MB)")
            print("\n✓ 模型设置完成！")
        else:
            print("✗ 模型目录中没有找到模型文件")
            print(f"\n请将模型文件放到: {os.path.abspath(target_dir)}")
    else:
        print(f"✗ 模型目录不存在: {target_dir}")

if __name__ == "__main__":
    setup_model()



