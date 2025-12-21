# Node.js安装指南（最简单方式）

## 当前问题
- 系统未安装Node.js
- 网络连接可能有问题，无法自动下载

## 推荐安装方式（最简单）

### 方式1：从官网下载安装包（推荐）

1. **打开浏览器**
   - 访问：https://nodejs.org/
   - 或直接搜索"Node.js下载"

2. **下载LTS版本**
   - 点击绿色的"LTS"按钮下载
   - 会下载一个 `.pkg` 文件（macOS安装包）

3. **安装**
   - 双击下载的 `.pkg` 文件
   - 按照安装向导完成安装
   - 全部选择默认选项即可

4. **验证安装**
   打开终端，运行：
   ```bash
   node --version
   npm --version
   ```
   如果显示版本号（如 v20.x.x），说明安装成功

5. **安装前端依赖并启动**
   ```bash
   cd /Users/siri-iii/Desktop/软工项目/frontend
   npm install
   npm run dev
   ```

## 如果下载很慢

可以使用国内镜像：
- 淘宝镜像：https://npmmirror.com/mirrors/node/
- 选择LTS版本下载

## 安装完成后

运行以下命令启动前端：
```bash
cd /Users/siri-iii/Desktop/软工项目
./setup_frontend.sh
```

或者手动：
```bash
cd frontend
npm install
npm run dev
```

前端将在 http://localhost:3000 启动
