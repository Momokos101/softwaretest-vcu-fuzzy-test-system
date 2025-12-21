# Node.js安装指南

## 当前状态
- ❌ 系统未安装Node.js
- ❌ 系统未安装Homebrew
- ❌ 系统未安装nvm

## 推荐安装方式

### 方式1：从官网下载安装包（最简单）

1. **访问Node.js官网**
   - 打开浏览器访问：https://nodejs.org/
   - 点击下载LTS版本（推荐）

2. **安装**
   - 下载完成后双击 `.pkg` 文件
   - 按照安装向导完成安装

3. **验证安装**
   ```bash
   node --version
   npm --version
   ```

### 方式2：使用nvm安装（推荐开发者）

1. **安装nvm**
   ```bash
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
   ```

2. **重新加载shell配置**
   ```bash
   source ~/.zshrc
   # 或者
   source ~/.bash_profile
   ```

3. **安装Node.js LTS版本**
   ```bash
   nvm install --lts
   nvm use --lts
   ```

4. **验证安装**
   ```bash
   node --version
   npm --version
   ```

## 安装完成后的步骤

1. **进入前端目录**
   ```bash
   cd /Users/siri-iii/Desktop/软工项目/frontend
   ```

2. **安装依赖**
   ```bash
   npm install
   ```
   这可能需要几分钟时间

3. **启动开发服务器**
   ```bash
   npm run dev
   ```

4. **访问前端**
   - 浏览器打开：http://localhost:5173
   - 或根据终端显示的地址访问

## 如果遇到问题

### 问题1：npm install 很慢
```bash
# 使用国内镜像
npm config set registry https://registry.npmmirror.com
npm install
```

### 问题2：端口被占用
```bash
# 修改vite.config.ts中的端口
# 或使用其他端口启动
npm run dev -- --port 3001
```

### 问题3：依赖安装失败
```bash
# 清除缓存重试
rm -rf node_modules package-lock.json
npm install
```
