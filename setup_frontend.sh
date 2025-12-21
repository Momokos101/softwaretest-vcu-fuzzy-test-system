#!/bin/bash
# 前端环境安装和启动脚本

set -e

echo "=========================================="
echo "前端环境安装和启动脚本"
echo "=========================================="
echo ""

# 检查Node.js
echo "1. 检查Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    NPM_VERSION=$(npm --version)
    echo "✓ Node.js已安装: $NODE_VERSION"
    echo "✓ npm已安装: $NPM_VERSION"
else
    echo "✗ Node.js未安装"
    echo ""
    echo "请先安装Node.js："
    echo "  方式1: 访问 https://nodejs.org/ 下载安装"
    echo "  方式2: 运行: curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash"
    echo ""
    exit 1
fi

echo ""
echo "2. 进入前端目录..."
cd "$(dirname "$0")/frontend" || exit 1

echo ""
echo "3. 检查依赖..."
if [ -d "node_modules" ]; then
    echo "✓ 依赖已安装"
else
    echo "→ 开始安装依赖（这可能需要几分钟）..."
    npm install
    echo "✓ 依赖安装完成"
fi

echo ""
echo "4. 启动开发服务器..."
echo "→ 前端将在 http://localhost:3000 启动"
echo "→ 按 Ctrl+C 停止服务器"
echo ""
npm run dev
