"""
智能GAN模型加载器
根据权重文件的实际形状动态构建模型结构
"""
import os
import h5py
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import logging
from typing import Optional, Dict, Any
import numpy as np

logger = logging.getLogger(__name__)

def build_model_from_weights(weights_file: str):
    """
    根据权重文件的实际形状构建模型
    
    Args:
        weights_file: 权重文件路径
    
    Returns:
        构建好的模型
    """
    with h5py.File(weights_file, 'r') as f:
        # 提取权重信息
        dense_kernel = f['layers/dense/vars/0']  # 条件编码层
        dense1_kernel = f['layers/dense_1/vars/0']  # 生成器第一层
        
        c_dim = int(dense_kernel.shape[0])  # 条件维度
        ef_dim = int(dense_kernel.shape[1])  # 嵌入维度
        z_dim = int(dense1_kernel.shape[0] - ef_dim)  # 噪声维度
        first_dense_output = int(dense1_kernel.shape[1])  # 第一层全连接输出
        
        logger.info(f"从权重文件推断: C_DIM={c_dim}, Z_DIM={z_dim}, EF_DIM={ef_dim}")
        logger.info(f"第一层全连接输出: {first_dense_output}")
        
        # 构建模型
        # 输入
        c_input = keras.Input(shape=(c_dim,), name='condition')
        z_input = keras.Input(shape=(z_dim,), name='noise')
        
        # 条件编码（根据encode_condition逻辑）
        c_encoded = c_input
        n = 2 ** (len(bin(c_dim)) - 3)  # 计算初始维度
        while n >= ef_dim * 2:
            c_encoded = layers.Dense(n)(c_encoded)
            c_encoded = layers.LeakyReLU(alpha=0.2)(c_encoded)
            n = n // 2
        
        # 最终条件嵌入
        c_encoded = layers.Dense(ef_dim)(c_encoded)
        c_encoded = layers.LeakyReLU(alpha=0.2)(c_encoded)
        
        # 拼接条件和噪声
        combined = layers.Concatenate()([c_encoded, z_input])
        
        # 第一层全连接（匹配权重文件形状）
        h0 = layers.Dense(first_dense_output)(combined)
        h0 = layers.BatchNormalization()(h0)
        h0 = layers.LeakyReLU(alpha=0.2)(h0)
        
        # 后续层（根据权重文件推断）
        # 这里需要根据实际的conv1d_transpose等层的形状来构建
        # 暂时简化处理
        
        # 创建模型
        model = keras.Model(inputs=[c_input, z_input], outputs=h0, name='generator')
        
        # 加载权重（只加载能匹配的层）
        try:
            model.load_weights(weights_file, by_name=True, skip_mismatch=True)
            logger.info("✓ 成功加载部分权重（跳过不匹配的层）")
        except Exception as e:
            logger.warning(f"加载权重时出现问题: {e}")
        
        return model



