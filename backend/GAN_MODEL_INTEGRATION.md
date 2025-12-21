# GAN模型集成指南

## 概述

本文档说明如何将训练好的GAN模型集成到系统中。

## 当前状态

✅ **已完成**:
- GAN模型加载器 (`api/services/gan_model_loader.py`)
- 模型加载接口
- 条件向量准备
- 数据后处理
- 模拟模式（当模型未加载时）

## 模型文件位置

根据配置，模型文件应位于：
- 配置路径: `model_weights/vcu/` (来自 `configs/config_vcu_base.py`)

## 集成步骤

### 步骤1: 准备模型文件

将训练好的GAN模型文件放到模型目录中：

```bash
backend/
└── model_weights/
    └── vcu/
        ├── generator.pth          # PyTorch模型文件
        └── checkpoint.pth         # 或检查点文件
```

### 步骤2: 根据模型结构修改加载代码

在 `api/services/gan_model_loader.py` 的 `load_model` 方法中，根据你的模型结构修改加载逻辑：

#### 情况1: 完整模型（包含结构）

```python
# 如果模型保存时包含了完整的结构
self.generator = torch.load(model_file, map_location=self.device)
self.generator.eval()
```

#### 情况2: 仅权重（需要先定义模型结构）

```python
# 需要先导入或定义模型结构
from your_model_module import Generator  # 导入你的生成器类

# 创建模型实例
self.generator = Generator(
    z_dim=Z_DIM,
    c_dim=C_DIM,
    # ... 其他参数
).to(self.device)

# 加载权重
checkpoint = torch.load(model_file, map_location=self.device)
self.generator.load_state_dict(checkpoint['generator_state_dict'])
self.generator.eval()
```

#### 情况3: 自定义模型格式

如果模型不是PyTorch格式，需要：
1. 实现相应的加载逻辑
2. 实现模型推理接口
3. 确保输出格式与 `_postprocess_generated` 方法兼容

### 步骤3: 调整模型输入输出

#### 输入格式

模型接收两个输入：
1. **噪声向量 z**: 形状为 `(1, Z_DIM)`，其中 `Z_DIM=128`（来自配置）
2. **条件向量 c**: 形状为 `(1, C_DIM)`，其中 `C_DIM=9`（来自配置）

条件向量包含：
- `[0]`: 异常标志
- `[1]`: 整车状态（归一化到[0,1]）
- `[2]`: READY标志位
- `[3]`: 异常类型编码
- `[4:9]`: 电压特征（5维）

#### 输出格式

模型应输出电压序列数据，可以是：
- 形状为 `(1, sequence_length)` 的张量
- 或形状为 `(1, sequence_length, 1)` 的张量

输出数据会被 `_postprocess_generated` 方法处理：
1. 归一化到[0,1]
2. 映射到电压范围 [CC2_MIN_VOLTAGE, CC2_MAX_VOLTAGE]
3. 裁剪到有效范围

### 步骤4: 测试模型加载

```python
from api.services.gan_model_loader import GANModelLoader

loader = GANModelLoader(model_path="model_weights/vcu/generator.pth")
success = loader.load_model()

if success:
    print("✓ 模型加载成功")
    # 测试生成
    result = loader.generate(
        condition={"target_phase": "wake", "vehicle_status": 100},
        sequence_length=8,
        temperature=1.0
    )
    print(f"生成的电压序列: {result['voltage_sequence']}")
else:
    print("✗ 模型加载失败，使用模拟模式")
```

### 步骤5: 在服务中使用

模型加载器已经集成到 `GANIntegrationService` 中：

```python
from api.services.gan_integration_service import GANIntegrationService

# 初始化服务（会自动尝试加载模型）
service = GANIntegrationService(
    baic_base_url="http://127.0.0.1:4523/m1/7470950-7205604-default",
    model_path="model_weights/vcu/generator.pth"  # 可选，指定模型路径
)

# 手动加载模型（如果需要）
service.load_gan_model("model_weights/vcu/generator.pth")

# 生成测试用例
result = await service.generate_and_send_test_case(
    condition={"target_phase": "wake"},
    sequence_length=8,
    temperature=1.0,
    send_to_baic=True
)
```

## 配置说明

### 模型参数配置

在 `configs/config_vcu_model.py` 中：

```python
Z_DIM = 128          # 噪声向量维度
EMBEDDING_DIM = 128  # 嵌入维度
G_DIM = 64          # 生成器维度
D_DIM = 32          # 判别器维度
```

### 数据范围配置

在 `configs/config_vcu_base.py` 中：

```python
CC2_MIN_VOLTAGE = 4.8   # 最小电压
CC2_MAX_VOLTAGE = 7.8   # 最大电压
SLEEP_VOLTAGE = 12.0    # 休眠电压
MAX_SEQUENCE_LENGTH = 100  # 最大序列长度
```

### 条件维度配置

在 `configs/config_vcu_base.py` 中：

```python
C_DIM = 9  # 条件维度
```

## 模拟模式

如果模型文件不存在或加载失败，系统会自动使用模拟模式：

- 使用随机数生成电压序列
- 基于配置的电压范围
- 根据条件调整数据
- 标记 `model_used: False` 以便区分

## 调试建议

### 1. 检查模型文件

```python
import os
model_path = "model_weights/vcu"
if os.path.exists(model_path):
    print(f"模型目录存在: {model_path}")
    files = os.listdir(model_path)
    print(f"文件列表: {files}")
else:
    print(f"模型目录不存在: {model_path}")
```

### 2. 检查模型结构

```python
import torch
checkpoint = torch.load("model_weights/vcu/generator.pth", map_location='cpu')
print("检查点键:", checkpoint.keys())
if 'generator_state_dict' in checkpoint:
    state_dict = checkpoint['generator_state_dict']
    print("状态字典键:", list(state_dict.keys())[:5])  # 显示前5个
```

### 3. 测试生成

```python
from api.services.gan_model_loader import GANModelLoader

loader = GANModelLoader()
loader.load_model()

# 测试不同条件
conditions = [
    {"target_phase": "wake"},
    {"target_phase": "sleep"},
    {"target_phase": "ready", "vehicle_status": 100}
]

for cond in conditions:
    result = loader.generate(condition=cond, sequence_length=8)
    print(f"条件: {cond}")
    print(f"电压序列: {result['voltage_sequence']}")
    print(f"使用模型: {result.get('model_used', False)}")
    print()
```

## 常见问题

### Q1: 模型加载失败怎么办？

**A**: 系统会自动回退到模拟模式，不会影响功能。检查：
1. 模型文件路径是否正确
2. 模型文件格式是否匹配
3. PyTorch版本是否兼容

### Q2: 如何知道是否使用了真实模型？

**A**: 检查生成结果中的 `model_used` 字段：
- `True`: 使用了真实模型
- `False`: 使用了模拟模式

### Q3: 模型输出格式不匹配怎么办？

**A**: 修改 `_postprocess_generated` 方法，根据你的模型输出格式进行调整。

### Q4: 如何支持不同的模型架构？

**A**: 在 `load_model` 方法中添加对不同模型格式的检测和加载逻辑。

## 下一步

1. **准备模型文件**: 将训练好的模型放到指定目录
2. **修改加载代码**: 根据实际模型结构调整加载逻辑
3. **测试验证**: 使用测试脚本验证模型生成效果
4. **性能优化**: 根据实际使用情况优化生成速度

## 相关文件

- `api/services/gan_model_loader.py` - 模型加载器
- `api/services/gan_integration_service.py` - 集成服务
- `configs/config_vcu_model.py` - 模型配置
- `configs/config_vcu_base.py` - 基础配置



