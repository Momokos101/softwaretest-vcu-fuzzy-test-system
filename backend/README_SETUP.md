# 后端API设置和运行指南

## 环境要求

- Python 3.8+
- pip

## 安装步骤

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量（可选）

创建 `.env` 文件：

```bash
# API服务器配置
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# 北汽接口配置
BAIC_API_BASE_URL=http://127.0.0.1:4523/m1/7470950-7205604-default
```

### 3. 启动服务器

**方式1: 使用启动脚本**
```bash
python run_server.py
```

**方式2: 直接使用uvicorn**
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

**方式3: 使用Python模块**
```bash
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 访问API文档

启动后，访问以下地址查看API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- API根路径: http://localhost:8000/

## 测试

### 测试北汽接口对接

```bash
python test_baic_integration.py
```

### 运行使用示例

```bash
python example_usage.py
```

## API端点概览

### 测试计划管理
- `POST /api/test-plans` - 创建测试计划
- `GET /api/test-plans` - 获取测试计划列表
- `GET /api/test-plans/{plan_id}` - 获取测试计划详情
- `DELETE /api/test-plans/{plan_id}` - 删除测试计划

### 测试任务管理
- `POST /api/test-tasks` - 创建测试任务
- `POST /api/test-tasks/{task_id}/start` - 启动测试任务
- `POST /api/test-tasks/{task_id}/pause` - 暂停测试任务
- `POST /api/test-tasks/{task_id}/stop` - 停止测试任务
- `GET /api/test-tasks/{task_id}` - 获取测试任务详情
- `GET /api/test-tasks/{task_id}/anomalies` - 获取异常列表

### GAN测试
- `POST /api/gan/generate` - 生成单个测试用例
- `POST /api/gan/generate/batch` - 批量生成测试用例
- `POST /api/gan/convert` - 转换数据格式

### 测试报告
- `POST /api/test-tasks/{task_id}/report` - 生成测试报告
- `GET /api/test-tasks/{task_id}/report/download` - 下载报告
- `GET /api/test-tasks/{task_id}/report/comparison` - 获取方法对比

### 约束管理
- `GET /api/test-tasks/{task_id}/constraints` - 获取约束统计

### 监控
- `GET /api/test-tasks/{task_id}/metrics` - 获取监控指标
- `WS /ws/test-tasks/{task_id}` - WebSocket实时监控

## 项目结构

```
backend/
├── api/
│   ├── __init__.py
│   ├── main.py                 # FastAPI主应用
│   ├── models/
│   │   └── schemas.py          # 数据模型定义
│   ├── routers/                # API路由
│   │   ├── test_plans.py
│   │   ├── test_tasks.py
│   │   ├── gan.py              # GAN测试路由
│   │   ├── reports.py
│   │   ├── constraints.py
│   │   └── monitoring.py
│   ├── services/               # 业务逻辑服务
│   │   ├── test_plan_service.py
│   │   ├── test_task_service.py
│   │   ├── gan_integration_service.py  # GAN集成服务
│   │   ├── baic_adapter.py     # 北汽接口适配器
│   │   ├── report_service.py
│   │   ├── constraint_service.py
│   │   └── monitoring_service.py
│   ├── database/
│   │   └── db.py               # 数据库操作
│   └── websocket_manager.py    # WebSocket管理
├── configs/                    # 配置文件
├── data/                       # 数据目录
├── requirements.txt            # Python依赖
├── run_server.py               # 启动脚本
├── test_baic_integration.py    # 测试脚本
├── example_usage.py            # 使用示例
└── README_SETUP.md             # 本文档
```

## 常见问题

### 1. 导入错误

如果遇到模块导入错误，确保：
- 在项目根目录（backend/）运行命令
- Python路径正确设置

### 2. 端口被占用

如果8000端口被占用，可以：
- 修改环境变量 `API_PORT`
- 或直接指定端口：`uvicorn api.main:app --port 8080`

### 3. 北汽接口连接失败

如果北汽接口未运行或URL不正确：
- 检查 `BAIC_API_BASE_URL` 配置
- 确认北汽接口服务是否运行
- 查看日志了解详细错误信息

## 下一步

1. **集成实际GAN模型**: 在 `api/services/gan_integration_service.py` 中替换模拟实现
2. **完善约束器**: 实现统一约束器的完整逻辑
3. **添加认证**: 根据需求添加JWT认证等安全机制
4. **优化性能**: 根据实际使用情况优化数据库查询和API响应速度



