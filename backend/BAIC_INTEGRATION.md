# 北汽接口对接说明

## 概述

本文档说明如何将GAN模型生成的数据与北汽接口（`POST /gan/data/input`）对接。

## 接口格式

### 北汽接口要求

- **URL**: `POST /gan/data/input`
- **请求体格式**:
```json
{
  "inputData": [
    {
      "name": "信号名称（string）",
      "value": 整数值（integer）
    }
  ]
}
```

### GAN生成的数据格式

GAN模型生成的数据通常包含：
- `cc2_voltage`: CC2电压值（浮点数，如 7.5）
- `vehicle_status`: 整车状态（整数，如 100）
- `ready_flag`: READY标志位（0或1）
- `voltage_sequence`: 电压序列（浮点数数组）
- `output_fields`: 其他输出字段（字典）

## 数据转换方案

### 1. 信号映射

| GAN数据字段 | 北汽接口信号名 | 转换规则 |
|------------|--------------|---------|
| `cc2_voltage` | "CC2电压值" | 浮点数 × 10 → 整数（保留1位小数精度） |
| `vehicle_status` | "整车状态" | 直接使用整数 |
| `ready_flag` | "READY标志位" | 直接使用整数（0或1） |
| `output_fields["动力防盗允许READY标志位"]` | "动力防盗允许READY标志位" | 直接使用整数 |

### 2. 转换示例

**GAN生成的数据**:
```python
{
    "cc2_voltage": 7.5,
    "vehicle_status": 100,
    "ready_flag": 1,
    "voltage_sequence": [7.5, 6.8, 5.2],
    "output_fields": {
        "动力防盗允许READY标志位": 1
    }
}
```

**转换后的北汽格式**:
```json
{
  "inputData": [
    {"name": "CC2电压值", "value": 75},
    {"name": "整车状态", "value": 100},
    {"name": "READY标志位", "value": 1},
    {"name": "动力防盗允许READY标志位", "value": 1}
  ]
}
```

## 使用方法

### 1. 直接使用适配器

```python
from api.services.baic_adapter import BaicAdapter

# 初始化适配器
adapter = BaicAdapter(base_url="http://127.0.0.1:4523/m1/7470950-7205604-default")

# GAN生成的数据
gan_data = {
    "cc2_voltage": 7.5,
    "vehicle_status": 100,
    "ready_flag": 1
}

# 转换为北汽格式
baic_format = adapter.convert_gan_data_to_baic_format(gan_data)
# 结果: {"inputData": [{"name": "CC2电压值", "value": 75}, ...]}

# 发送到北汽接口
response = await adapter.send_test_data(gan_data)
```

### 2. 使用GAN集成服务（推荐）

```python
from api.services.gan_integration_service import GANIntegrationService

# 初始化服务
gan_service = GANIntegrationService(
    baic_base_url="http://127.0.0.1:4523/m1/7470950-7205604-default"
)

# 生成并发送单个测试用例
result = await gan_service.generate_and_send_test_case(
    condition={"target_phase": "wake"},
    sequence_length=8,
    temperature=1.0,
    send_to_baic=True
)

# 批量生成并发送
results = await gan_service.generate_and_send_batch(
    batch_size=10,
    condition={"target_phase": "wake"},
    sequence_length=8,
    temperature=1.0
)
```

### 3. 通过API调用

```bash
# 生成单个测试用例并发送
curl -X POST "http://localhost:8000/api/gan/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "condition": {"target_phase": "wake"},
    "sequence_length": 8,
    "temperature": 1.0,
    "send_to_baic": true
  }'

# 批量生成
curl -X POST "http://localhost:8000/api/gan/generate/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "batch_size": 10,
    "sequence_length": 8,
    "temperature": 1.0
  }'

# 仅转换格式（不发送）
curl -X POST "http://localhost:8000/api/gan/convert" \
  -H "Content-Type: application/json" \
  -d '{
    "cc2_voltage": 7.5,
    "vehicle_status": 100,
    "ready_flag": 1
  }'
```

## 集成到测试任务执行流程

在测试任务执行时，可以这样集成：

```python
# 在 test_task_service.py 的 execute_test_task 方法中
from api.services.gan_integration_service import GANIntegrationService

gan_service = GANIntegrationService()

# 生成测试用例
test_case = await gan_service.generate_and_send_test_case(
    condition={
        "target_phase": "wake",  # 或 "sleep", "ready"
        "vehicle_status": 100
    },
    sequence_length=8,
    temperature=1.0,
    send_to_baic=True
)

# 检查发送结果
if test_case.get("sent_to_baic"):
    logger.info("测试用例已成功发送到北汽接口")
    # 继续后续处理...
else:
    logger.error("发送到北汽接口失败")
```

## 配置说明

### 环境变量

可以在环境变量中配置北汽接口URL：

```bash
export BAIC_API_BASE_URL="http://127.0.0.1:4523/m1/7470950-7205604-default"
```

### 代码配置

在 `api/services/gan_integration_service.py` 中：

```python
gan_service = GANIntegrationService(
    baic_base_url=os.getenv("BAIC_API_BASE_URL", "http://127.0.0.1:4523/m1/7470950-7205604-default")
)
```

## 错误处理

适配器会自动处理以下情况：
1. **网络错误**: 自动重试3次，每次间隔1秒
2. **HTTP错误**: 记录错误状态码和响应内容
3. **数据格式错误**: 记录转换失败的原因

所有错误都会记录到日志中，并返回详细的错误信息。

## 注意事项

1. **数据类型转换**: 
   - 浮点数（如电压值）需要乘以10转换为整数（保留1位小数精度）
   - 例如：7.5V → 75

2. **信号名称映射**: 
   - 确保GAN数据中的字段名与北汽接口要求的信号名正确映射
   - 可以在 `baic_adapter.py` 中的 `signal_mapping` 字典中添加新的映射

3. **请求频率**: 
   - 批量发送时建议添加延迟（如0.1秒），避免请求过快
   - 可以根据北汽接口的速率限制调整

4. **实际GAN模型集成**: 
   - 当前 `gan_integration_service.py` 中的 `generate_test_sequence` 方法是模拟实现
   - 需要替换为实际的GAN模型调用代码

## 下一步

1. **集成实际GAN模型**: 在 `gan_integration_service.py` 中加载和调用训练好的GAN模型
2. **完善信号映射**: 根据实际需求添加更多信号映射关系
3. **添加数据验证**: 在发送前验证数据是否符合约束条件
4. **实现重试策略**: 根据实际需求调整重试次数和间隔
