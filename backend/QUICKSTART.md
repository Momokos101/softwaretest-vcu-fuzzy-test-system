# 快速启动指南

## 5分钟快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 启动服务器

```bash
python run_server.py
```

服务器将在 http://localhost:8000 启动

### 3. 访问API文档

打开浏览器访问：http://localhost:8000/docs

### 4. 测试北汽接口对接

在另一个终端运行：

```bash
python test_baic_integration.py
```

## 快速测试API

### 创建测试计划

```bash
curl -X POST "http://localhost:8000/api/test-plans" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试计划1",
    "description": "这是一个测试计划",
    "test_mode": "both",
    "constraint_config": {
      "rate_limit": 100.0,
      "crc_check": true,
      "dlc_check": true
    }
  }'
```

### 生成GAN测试用例并发送到北汽接口

```bash
curl -X POST "http://localhost:8000/api/gan/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "condition": {"target_phase": "wake"},
    "sequence_length": 8,
    "temperature": 1.0,
    "send_to_baic": true
  }'
```

### 转换GAN数据格式（不发送）

```bash
curl -X POST "http://localhost:8000/api/gan/convert" \
  -H "Content-Type: application/json" \
  -d '{
    "cc2_voltage": 7.5,
    "vehicle_status": 100,
    "ready_flag": 1
  }'
```

## 数据转换示例

**输入（GAN格式）**:
```json
{
  "cc2_voltage": 7.5,
  "vehicle_status": 100,
  "ready_flag": 1
}
```

**输出（北汽格式）**:
```json
{
  "inputData": [
    {"name": "CC2电压值", "value": 75},
    {"name": "整车状态", "value": 100},
    {"name": "READY标志位", "value": 1}
  ]
}
```

## 下一步

1. 查看完整文档: [README_SETUP.md](README_SETUP.md)
2. 了解对接详情: [BAIC_INTEGRATION.md](BAIC_INTEGRATION.md)
3. 运行示例代码: `python example_usage.py`



