# Node.js安装指南 - MacBook M4 (ARM64)

## 你的系统信息
- ✅ MacBook M4
- ✅ ARM64架构（Apple Silicon）
- ✅ 需要下载ARM64版本的Node.js

## 安装步骤

### 方式1：从官网下载（推荐）

1. **访问Node.js官网**
   - 打开：https://nodejs.org/
   - 网站会自动检测你的系统，显示ARM64版本

2. **下载**
   - 点击绿色的"LTS"按钮
   - 会自动下载 `node-v20.x.x-arm64.pkg` 文件
   - 或者手动选择 "macOS Installer (.pkg)" - ARM64版本

3. **安装**
   - 双击下载的 `.pkg` 文件
   - 按照安装向导完成（全部默认选项即可）

4. **验证**
   ```bash
   node --version
   npm --version
   ```

### 方式2：使用国内镜像（如果官网下载慢）

访问：https://npmmirror.com/mirrors/node/
- 选择最新的LTS版本
- 下载 `node-v20.x.x-darwin-arm64.pkg`

## 安装完成后

运行自动安装脚本：
```bash
cd /Users/siri-iii/Desktop/软工项目
./auto_setup.sh
```

脚本会自动：
1. 检查Node.js安装
2. 安装前端依赖
3. 启动开发服务器
