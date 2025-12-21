#!/usr/bin/env python3
"""
从GitHub仓库下载训练好的GAN模型文件
"""
import os
import sys
import requests
from pathlib import Path

GITHUB_REPO = "Momokos101/wgan"
BRANCH = "main"
MODEL_DIR = "model_weights/vcu"

def download_file(url, filepath):
    """下载文件"""
    print(f"正在下载: {os.path.basename(filepath)}...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\r  进度: {percent:.1f}% ({downloaded}/{total_size} bytes)", end='', flush=True)
        
        print(f"\n✓ 下载完成: {filepath}")
        return True
    except Exception as e:
        print(f"\n✗ 下载失败: {str(e)}")
        if os.path.exists(filepath):
            os.remove(filepath)
        return False

def get_latest_generator_model():
    """获取最新的生成器模型文件"""
    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/git/trees/{BRANCH}?recursive=1"
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        
        # 查找所有generator模型文件
        generator_files = [
            f for f in data.get('tree', [])
            if f['path'].startswith('model_weights/vcu/') and 
               'generator' in f['path'] and 
               f['path'].endswith('.h5')
        ]
        
        if not generator_files:
            print("未找到生成器模型文件")
            return None
        
        # 选择最新的（按时间戳，最大的）
        # 文件名格式: model_weights/vcu/1118235316_conv1d_LWCO_generator.weights.h5
        def get_timestamp(file_path):
            try:
                # 提取文件名中的时间戳（第一个数字部分）
                filename = os.path.basename(file_path)
                timestamp_str = filename.split('_')[0]
                return int(timestamp_str)
            except:
                return 0
        
        latest = max(generator_files, key=get_timestamp)
        
        return latest['path']
    except Exception as e:
        print(f"获取文件列表失败: {str(e)}")
        return None

def main():
    """主函数"""
    print("=" * 60)
    print("从GitHub下载GAN模型文件")
    print("=" * 60)
    print(f"仓库: {GITHUB_REPO}")
    print(f"分支: {BRANCH}")
    print()
    
    # 获取最新的生成器模型
    model_path = get_latest_generator_model()
    
    if not model_path:
        print("✗ 无法找到模型文件")
        return
    
    print(f"找到最新模型: {model_path}")
    print()
    
    # 构建下载URL
    download_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{BRANCH}/{model_path}"
    local_path = model_path
    
    # 下载生成器
    if download_file(download_url, local_path):
        print(f"\n✓ 模型文件已下载到: {os.path.abspath(local_path)}")
        
        # 也下载对应的判别器（可选）
        discriminator_path = model_path.replace('generator', 'discriminator')
        discriminator_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{BRANCH}/{discriminator_path}"
        
        # 自动下载判别器（可选，但通常不需要用于生成）
        # 如果需要判别器，取消下面的注释
        # download_file(discriminator_url, discriminator_path)
        
        print("\n" + "=" * 60)
        print("下载完成！")
        print("=" * 60)
        print(f"\n模型文件位置: {os.path.abspath(local_path)}")
        print("\n现在可以运行:")
        print("  python3 -c \"from api.services.gan_model_loader import GANModelLoader; loader = GANModelLoader(); loader.load_model()\"")
    else:
        print("\n✗ 下载失败")

if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        print("错误: 需要安装requests库")
        print("运行: pip3 install requests")
        sys.exit(1)
    
    main()

