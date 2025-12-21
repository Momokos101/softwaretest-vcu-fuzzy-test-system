#!/bin/bash
# 自动安装和启动前端脚本

echo "=========================================="
echo "前端环境自动安装脚本"
echo "=========================================="
echo ""

# 检查Node.js
echo "检查Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    NPM_VERSION=$(npm --version)
    echo "✓ Node.js已安装: $NODE_VERSION"
    echo "✓ npm已安装: $NPM_VERSION"
    echo ""
    
    # 进入前端目录
    cd "$(dirname "$0")/frontend" || exit 1
    
    # 检查依赖
    if [ -d "node_modules" ]; then
        echo "✓ 依赖已安装"
    else
        echo "→ 开始安装依赖（这可能需要几分钟）..."
        npm install
        if [ $? -eq 0 ]; then
            echo "✓ 依赖安装完成"
        else
            echo "✗ 依赖安装失败"
            exit 1
        fi
    fi
    
    echo ""
    echo "=========================================="
    echo "启动前端开发服务器..."
    echo "前端地址: http://localhost:3000"
    echo "按 Ctrl+C 停止服务器"
    echo "=========================================="
    echo ""
    
    npm run dev
else
    echo "✗ Node.js未安装"
    echo ""
    echo "请先安装Node.js："
    echo "1. 访问 https://nodejs.org/"
    echo "2. 下载LTS版本并安装"
    echo "3. 安装完成后重新运行此脚本"
    echo ""
    echo "或者运行: ./setup_frontend.sh"
    exit 1
fi
