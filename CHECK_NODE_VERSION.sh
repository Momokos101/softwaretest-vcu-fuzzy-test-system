#!/bin/bash
# 检查Node.js版本并安装依赖

echo "=========================================="
echo "Node.js版本检查"
echo "=========================================="
echo ""

if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    NPM_VERSION=$(npm --version)
    
    echo "✓ Node.js已安装"
    echo "  版本: $NODE_VERSION"
    echo "  npm版本: $NPM_VERSION"
    echo ""
    
    # 检查版本是否满足要求（v16+即可）
    NODE_MAJOR=$(echo $NODE_VERSION | sed 's/v\([0-9]*\).*/\1/')
    if [ "$NODE_MAJOR" -ge 16 ]; then
        echo "✓ 版本满足要求（需要v16+，当前v$NODE_MAJOR）"
        echo ""
        
        # 进入前端目录
        cd "$(dirname "$0")/frontend" || exit 1
        
        # 安装依赖
        if [ ! -d "node_modules" ]; then
            echo "→ 开始安装前端依赖..."
            npm install
            if [ $? -eq 0 ]; then
                echo "✓ 依赖安装完成"
            else
                echo "✗ 依赖安装失败"
                exit 1
            fi
        else
            echo "✓ 依赖已安装"
        fi
        
        echo ""
        echo "=========================================="
        echo "准备启动前端服务器..."
        echo "=========================================="
        echo ""
        echo "前端将在 http://localhost:3000 启动"
        echo "按 Ctrl+C 停止服务器"
        echo ""
        
        npm run dev
    else
        echo "✗ 版本过低（需要v16+，当前v$NODE_MAJOR）"
        echo "请升级Node.js版本"
    fi
else
    echo "✗ Node.js未安装"
    echo ""
    echo "请先安装Node.js："
    echo "1. 双击下载的 node-v24.12.0.pkg 文件"
    echo "2. 按照安装向导完成安装"
    echo "3. 安装完成后重新运行此脚本"
    exit 1
fi
