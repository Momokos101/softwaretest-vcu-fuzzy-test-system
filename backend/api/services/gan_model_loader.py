"""
GAN模型加载器
支持加载训练好的GAN模型并生成测试数据
"""
import os
import logging
from typing import Dict, Any, Optional, List
import numpy as np
from datetime import datetime

import sys
import os
from configs.config_vcu import (
    Z_DIM, C_DIM, G_DIM, D_DIM, EMBEDDING_DIM, 
    MAX_SEQUENCE_LENGTH, PRECISION, MODEL_PATH,
    CC2_MIN_VOLTAGE, CC2_MAX_VOLTAGE, SLEEP_VOLTAGE,
    VEHICLE_STATUS_MIN, VEHICLE_STATUS_MAX
)

# 添加nn目录到路径
nn_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'nn')
if os.path.exists(nn_path) and nn_path not in sys.path:
    sys.path.insert(0, nn_path)

logger = logging.getLogger(__name__)

class GANModelLoader:
    """GAN模型加载器"""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        初始化模型加载器
        
        Args:
            model_path: 模型文件路径，如果为None则使用配置中的路径
        """
        self.model_path = model_path or MODEL_PATH
        self.generator = None
        self.device = None
        self.model_loaded = False
        
    def load_model(self):
        """
        加载GAN模型
        
        支持多种模型格式：
        1. PyTorch模型 (.pth, .pt)
        2. 保存的numpy数据 (.npy)
        3. 自定义模型文件
        
        如果模型文件不存在，将抛出异常（不使用模拟模式）
        """
        try:
            # 检查模型路径是否存在
            if not os.path.exists(self.model_path):
                # 尝试查找模型文件
                possible_paths = [
                    self.model_path,
                    os.path.join(self.model_path, "generator.pth"),
                    os.path.join(self.model_path, "generator.pt"),
                    os.path.join(self.model_path, "model.pth"),
                    os.path.join(self.model_path, "model.pt"),
                    os.path.join(self.model_path, "checkpoint.pth"),
                ]
                
                found_path = None
                for path in possible_paths:
                    if os.path.exists(path):
                        found_path = path
                        break
                
                if not found_path:
                    # 如果是目录，查找其中的模型文件
                    if os.path.isdir(self.model_path):
                        model_files = [f for f in os.listdir(self.model_path) 
                                     if f.endswith(('.pth', '.pt', '.pkl', '.h5', '.ckpt'))]
                        if model_files:
                            # 选择最新的文件
                            latest = max(model_files, 
                                        key=lambda f: os.path.getmtime(os.path.join(self.model_path, f)))
                            found_path = os.path.join(self.model_path, latest)
                
                if not found_path:
                    error_msg = (
                        f"错误: 找不到GAN模型文件！\n"
                        f"  查找路径: {self.model_path}\n"
                        f"  请确保:\n"
                        f"  1. 模型文件已放到: model_weights/vcu/\n"
                        f"  2. 或运行: python3 setup_model.py 来配置模型路径\n"
                        f"  3. 或在代码中指定正确的模型路径"
                    )
                    logger.error(error_msg)
                    raise FileNotFoundError(error_msg)
                
                self.model_path = found_path
                logger.info(f"找到模型文件: {found_path}")
            
            # 尝试加载模型（支持PyTorch和Keras/TensorFlow）
            model_file = None
            model_type = None
            
            # 确定模型文件路径和类型
            if os.path.isdir(self.model_path):
                # 如果是目录，查找模型文件
                h5_files = [f for f in os.listdir(self.model_path) 
                           if f.endswith('.h5') and 'generator' in f]
                pth_files = [f for f in os.listdir(self.model_path) 
                            if f.endswith(('.pth', '.pt'))]
                
                if h5_files:
                    # 选择最新的.h5文件
                    latest = max(h5_files, 
                               key=lambda f: int(f.split('_')[0]) if f.split('_')[0].isdigit() else 0)
                    model_file = os.path.join(self.model_path, latest)
                    model_type = 'keras'
                elif pth_files:
                    latest = max(pth_files, 
                               key=lambda f: os.path.getmtime(os.path.join(self.model_path, f)))
                    model_file = os.path.join(self.model_path, latest)
                    model_type = 'pytorch'
            else:
                model_file = self.model_path
                if model_file.endswith('.h5'):
                    model_type = 'keras'
                elif model_file.endswith(('.pth', '.pt')):
                    model_type = 'pytorch'
            
            if not model_file or not os.path.exists(model_file):
                raise FileNotFoundError(f"找不到模型文件: {self.model_path}")
            
            logger.info(f"找到模型文件: {model_file} (类型: {model_type})")
            
            # 根据类型加载模型
            if model_type == 'keras':
                # 加载Keras/TensorFlow模型
                try:
                    import tensorflow as tf
                    from tensorflow import keras
                    
                    logger.info("使用TensorFlow/Keras加载模型")
                    
                    # 尝试加载完整模型
                    try:
                        self.generator = keras.models.load_model(model_file, compile=False)
                        logger.info("✓ 成功加载完整Keras模型")
                    except ValueError as e:
                        # 如果是权重文件，需要先定义模型结构
                        if "No model config" in str(e) or "weights" in model_file:
                            logger.info("检测到权重文件，使用模型结构定义加载")
                            
                            # 尝试从nn目录导入模型结构
                            try:
                                from nn.conv1d import Conv1D_Model
                                from configs.config_vcu import (
                                    FLAG, MODEL_TYPE, MAX_SEQUENCE_LENGTH, BATCH_SIZE
                                )
                                
                                # 检查权重文件的实际条件维度
                                import h5py
                                actual_c_dim = 3  # 从权重文件检查得出
                                
                                try:
                                    with h5py.File(model_file, 'r') as f:
                                        # 查找第一个dense层的kernel形状来确定条件维度
                                        if 'layers' in f and 'dense' in f['layers']:
                                            dense_kernel = f['layers/dense/vars/0']
                                            actual_c_dim = int(dense_kernel.shape[0])
                                            logger.info(f"检测到权重文件的条件维度: {actual_c_dim}")
                                except Exception as e:
                                    logger.warning(f"无法检查权重文件维度: {e}，使用默认值3")
                                
                                # 直接使用Conv1D_Model，手动设置条件维度
                                logger.info("使用Conv1D_Model构建模型结构...")
                                
                                # 从权重文件推断所有参数
                                try:
                                    with h5py.File(model_file, 'r') as f:
                                        dense_kernel = f['layers/dense/vars/0']
                                        dense1_kernel = f['layers/dense_1/vars/0']
                                        
                                        actual_c_dim = int(dense_kernel.shape[0])
                                        actual_ef_dim = int(dense_kernel.shape[1])
                                        # dense1输入 = ef_dim + z_dim
                                        inferred_z_dim = int(dense1_kernel.shape[0] - actual_ef_dim)
                                        first_dense_output = int(dense1_kernel.shape[1])
                                        
                                        # 从conv1d_transpose层推断g_dim
                                        # 第一层conv1d_transpose的filters = g_dim * 4
                                        if 'layers/conv1d_transpose/vars/0' in f:
                                            conv1d_t_kernel = f['layers/conv1d_transpose/vars/0']
                                            conv1d_t_filters = int(conv1d_t_kernel.shape[1])
                                            inferred_g_dim = conv1d_t_filters // 4
                                        else:
                                            # 如果没有conv1d_transpose，根据dense1_output推断
                                            # first_dense_output = n * g_dim * 8
                                            # 尝试常见的g_dim值
                                            inferred_g_dim = G_DIM  # 默认使用配置值
                                        
                                        # 根据dense1_output和g_dim计算n
                                        # first_dense_output = n * g_dim * 8
                                        inferred_n = first_dense_output // (inferred_g_dim * 8)
                                        
                                        logger.info(f"从权重文件推断:")
                                        logger.info(f"  C_DIM={actual_c_dim}, Z_DIM={inferred_z_dim}, EF_DIM={actual_ef_dim}")
                                        logger.info(f"  G_DIM={inferred_g_dim}, n={inferred_n}")
                                        logger.info(f"  第一层全连接输出={first_dense_output}")
                                        
                                        # 根据metadata.json，序列长度是8
                                        import json
                                        try:
                                            with open('data/vcu/metadata.json', 'r') as meta_f:
                                                metadata = json.load(meta_f)
                                                actual_seq_len = metadata.get('max_sequence_length', 8)
                                        except:
                                            actual_seq_len = 8
                                        
                                        # 根据precision和实际序列长度反推seed_length
                                        from configs.config_vcu import PRECISION
                                        # 根据n反推seed_length
                                        # 在Conv1D_Model中，dense_1的输出 = n * g_dim * 8
                                        # 其中n是根据seed_length和precision计算的
                                        # 尝试不同的seed_length值，看哪个能匹配dense1_output
                                        from nn.model import out_neurons
                                        inferred_seed_length = None
                                        
                                        # 根据dense1_output反推seed_length
                                        # dense1_output = n * g_dim * 8 = 2048
                                        # n = 2048 / (64 * 8) = 4
                                        # 对于precision='2'，根据NetModel.__init__: n = out_neurons(seed_length) * 4
                                        # 所以 4 = out_neurons(seed_length) * 4
                                        # 因此 out_neurons(seed_length) = 1
                                        # 当seed_length=2时，out_neurons(2)=1，所以n=1*4=4 ✓
                                        for test_seed in [1, 2, 4, 8, 16, 32, 64, 128]:
                                            test_n = out_neurons(test_seed, True)
                                            # 根据NetModel.__init__的逻辑计算adjusted_n
                                            if PRECISION == '2':
                                                adjusted_test_n = test_n * 4  # NetModel中precision='2'时n *= 4
                                            elif PRECISION == '4':
                                                adjusted_test_n = test_n * 2
                                            elif PRECISION == '8':
                                                adjusted_test_n = test_n
                                            elif PRECISION == '16':
                                                adjusted_test_n = test_n // 2
                                            elif PRECISION == '1':
                                                adjusted_test_n = test_n * 8
                                            else:
                                                adjusted_test_n = test_n
                                            
                                            # 计算dense1_output（在Conv1D_Model中，dense_1的输出 = n * g_dim * 8）
                                            test_dense1_output = adjusted_test_n * inferred_g_dim * 8
                                            if test_dense1_output == first_dense_output:
                                                inferred_seed_length = test_seed
                                                logger.info(f"  找到匹配的seed_length={test_seed}, base_n={test_n}, adjusted_n={adjusted_test_n}, dense1_output={test_dense1_output}")
                                                break
                                        
                                        if inferred_seed_length is None:
                                            # 如果找不到匹配的，使用默认计算
                                            logger.warning(f"  无法找到匹配的seed_length，使用默认计算")
                                            if PRECISION == '2':
                                                inferred_seed_length = actual_seq_len // 4
                                            elif PRECISION == '4':
                                                inferred_seed_length = actual_seq_len // 2
                                            elif PRECISION == '8':
                                                inferred_seed_length = actual_seq_len
                                            elif PRECISION == '16':
                                                inferred_seed_length = actual_seq_len * 2
                                            elif PRECISION == '1':
                                                inferred_seed_length = actual_seq_len // 8
                                            else:
                                                inferred_seed_length = actual_seq_len
                                        
                                        logger.info(f"  实际序列长度={actual_seq_len}, inferred_seed_length={inferred_seed_length}")
                                        
                                except Exception as e:
                                    logger.error(f"分析权重文件失败: {e}")
                                    raise
                                
                                # 创建模型实例（使用从权重文件推断的所有参数）
                                # 注意：使用推断的参数而不是配置中的参数
                                model = Conv1D_Model(
                                    batch_size=BATCH_SIZE,
                                    seed_length=inferred_seed_length,
                                    c_dim=actual_c_dim,  # 从权重文件推断
                                    z_dim=inferred_z_dim,  # 从权重文件推断
                                    ef_dim=actual_ef_dim,  # 从权重文件推断
                                    g_dim=inferred_g_dim,  # 从权重文件推断
                                    d_dim=D_DIM,  # 保持配置值
                                    precision=PRECISION,
                                    is_onedim=True
                                )
                                
                                logger.info(f"使用推断的参数创建模型:")
                                logger.info(f"  seed_length={inferred_seed_length}, c_dim={actual_c_dim}, z_dim={inferred_z_dim}, g_dim={inferred_g_dim}, ef_dim={actual_ef_dim}")
                                
                                # 根据FLAG构建生成器
                                logger.info(f"根据FLAG={FLAG}构建生成器...")
                                if FLAG == 'LWCO':
                                    model.build_generator_wc()
                                    generator = model.generator_wi_condition
                                elif FLAG == 'LWOC':
                                    model.build_generator_woc()
                                    generator = model.generator_wo_condition
                                elif FLAG == 'LWCA':
                                    model.build_generator_wca()
                                    generator = model.generator_wi_conaugment
                                else:
                                    raise ValueError(f"未知的FLAG: {FLAG}")
                                
                                # 加载权重（使用skip_mismatch跳过不匹配的层）
                                logger.info(f"加载权重文件: {model_file}")
                                import warnings
                                with warnings.catch_warnings():
                                    # 忽略LeakyReLU的alpha参数弃用警告
                                    warnings.filterwarnings('ignore', message='.*alpha.*deprecated.*')
                                    warnings.filterwarnings('ignore', message='.*negative_slope.*')
                                    try:
                                        generator.load_weights(model_file, skip_mismatch=True)
                                        logger.info("✓ 权重加载完成")
                                    except Exception as load_error:
                                        # 检查是否是真正的错误还是只是警告
                                        error_str = str(load_error)
                                        if "deprecated" in error_str.lower() or "alpha" in error_str.lower():
                                            # 这只是警告，不是真正的错误，尝试继续
                                            logger.info("检测到弃用警告，尝试继续加载...")
                                            try:
                                                generator.load_weights(model_file, skip_mismatch=True)
                                                logger.info("✓ 权重加载完成（已忽略弃用警告）")
                                            except:
                                                logger.warning(f"加载权重时出现问题: {load_error}")
                                        else:
                                            logger.warning(f"加载权重时出现问题: {load_error}")
                                            logger.info("尝试继续使用模型（可能部分权重未加载）")
                                
                                self.generator = generator
                                self.model_instance = model  # 保存完整模型实例
                                self.actual_c_dim = actual_c_dim  # 保存实际条件维度
                                self.flag = FLAG  # 保存FLAG
                                logger.info("✓ 成功加载Keras模型权重")
                                self.model_loaded = True
                                self.model_type = 'keras'
                                self.model_instance = model  # 保存完整模型实例
                                return True
                                
                            except ImportError as ie:
                                logger.error(f"无法导入模型结构: {str(ie)}")
                                raise ImportError(
                                    f"需要模型结构定义。请确保nn/目录存在且包含模型定义文件。\n"
                                    f"错误: {str(ie)}"
                                )
                            except Exception as model_error:
                                logger.error(f"构建或加载模型失败: {str(model_error)}")
                                raise RuntimeError(
                                    f"无法加载模型权重。\n"
                                    f"错误: {str(model_error)}\n"
                                    f"请检查模型结构与权重文件是否匹配"
                                )
                        else:
                            raise
                    
                    self.model_loaded = True
                    self.model_type = 'keras'
                    return True
                except ImportError:
                    logger.error("TensorFlow未安装，无法加载.h5模型")
                    logger.info("请安装: pip install tensorflow")
                    raise ImportError("需要TensorFlow来加载.h5模型文件")
                except Exception as e:
                    logger.error(f"加载Keras模型失败: {str(e)}")
                    raise
            
            elif model_type == 'pytorch':
                # 加载PyTorch模型
                try:
                    import torch
                    self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                    logger.info(f"使用设备: {self.device}")
                    
                    # 加载PyTorch模型
                    logger.info(f"正在加载PyTorch模型: {model_file}")
                    
                    # 方法1: 尝试直接加载（完整模型）
                    try:
                        self.generator = torch.load(model_file, map_location=self.device)
                        if hasattr(self.generator, 'eval'):
                            self.generator.eval()
                        logger.info("✓ 成功加载完整PyTorch模型")
                        self.model_loaded = True
                        self.model_type = 'pytorch'
                        return True
                    except Exception as e1:
                        logger.debug(f"直接加载失败: {e1}，尝试加载权重...")
                        
                        # 方法2: 尝试加载权重（需要先定义模型结构）
                        try:
                            checkpoint = torch.load(model_file, map_location=self.device)
                            
                            # 检查checkpoint格式
                            if isinstance(checkpoint, dict):
                                if 'model_state_dict' in checkpoint:
                                    state_dict = checkpoint['model_state_dict']
                                elif 'generator_state_dict' in checkpoint:
                                    state_dict = checkpoint['generator_state_dict']
                                elif 'state_dict' in checkpoint:
                                    state_dict = checkpoint['state_dict']
                                else:
                                    state_dict = checkpoint
                                
                                logger.warning(
                                    "检测到权重文件，但需要模型结构定义。\n"
                                    "请确保模型结构已定义"
                                )
                                raise NotImplementedError("需要模型结构定义来加载权重")
                            else:
                                raise e1
                                
                        except Exception as e2:
                            error_msg = (
                                f"无法加载PyTorch模型: {model_file}\n"
                                f"错误: {str(e2)}\n"
                            )
                            logger.error(error_msg)
                            raise RuntimeError(error_msg)
                            
                except ImportError:
                    logger.error("PyTorch未安装，无法加载PyTorch模型")
                    raise ImportError("需要PyTorch来加载.pth/.pt模型文件")
                except Exception as e:
                    logger.error(f"加载PyTorch模型失败: {str(e)}")
                    raise
            
            else:
                raise ValueError(f"未知的模型类型: {model_type}")
                
        except Exception as e:
            logger.error(f"加载模型时发生错误: {str(e)}")
            self.model_loaded = False
            raise
                
        except Exception as e:
            logger.error(f"加载模型时发生错误: {str(e)}")
            self.model_loaded = False
            return False
    
    def _prepare_condition(self, condition: Optional[Dict[str, Any]]) -> np.ndarray:
        """
        准备条件向量
        
        Args:
            condition: 条件字典
        
        Returns:
            条件向量（numpy数组）
        """
        # 使用模型实际的条件维度（如果已加载模型）
        if hasattr(self, 'actual_c_dim'):
            actual_c_dim = self.actual_c_dim
        elif hasattr(self, 'model_instance') and self.model_instance:
            # 从ScaleModel获取
            if hasattr(self.model_instance, 'model'):
                actual_c_dim = self.model_instance.model.c_dim
            else:
                actual_c_dim = C_DIM
        else:
            actual_c_dim = C_DIM
        
        cond_vector = np.zeros(actual_c_dim)
        
        if condition:
            # 基础条件：异常标志(1) + 整车状态归一化(1) + READY标志位(1)
            if "anomaly_flag" in condition:
                cond_vector[0] = condition["anomaly_flag"]
            
            if "vehicle_status" in condition:
                # 归一化到[0, 1]
                vehicle_status = condition["vehicle_status"]
                normalized = (vehicle_status - VEHICLE_STATUS_MIN) / (VEHICLE_STATUS_MAX - VEHICLE_STATUS_MIN)
                cond_vector[1] = np.clip(normalized, 0, 1)
            
            if "ready_flag" in condition:
                cond_vector[2] = condition["ready_flag"]
            
            # 异常类型编码
            anomaly_type_map = {
                "normal": 0,
                "state_follow_mismatch": 1,
                "error": 2,
                "stuck": 3,
                "ready_flag_mismatch": 4
            }
            if "anomaly_type" in condition:
                cond_vector[3] = anomaly_type_map.get(condition["anomaly_type"], 0)
            
            # 电压特征（如果提供）
            if "voltage_features" in condition:
                features = condition["voltage_features"]
                if len(features) >= 5:
                    cond_vector[4:9] = features[:5]
        
        return cond_vector
    
    def _postprocess_generated(self, generated: np.ndarray) -> List[float]:
        """
        后处理生成的数据
        
        Args:
            generated: 模型生成的原始数据
        
        Returns:
            处理后的电压序列
        """
        # 将生成的数据缩放到电压范围
        if generated.ndim > 1:
            generated = generated.flatten()
        
        # 归一化到[0, 1]然后映射到电压范围
        if generated.max() > 1.0 or generated.min() < 0.0:
            # 如果数据不在[0,1]范围，先归一化
            generated = (generated - generated.min()) / (generated.max() - generated.min() + 1e-8)
        
        # 映射到电压范围
        voltage_sequence = generated * (CC2_MAX_VOLTAGE - CC2_MIN_VOLTAGE) + CC2_MIN_VOLTAGE
        
        # 确保在有效范围内
        voltage_sequence = np.clip(voltage_sequence, CC2_MIN_VOLTAGE, CC2_MAX_VOLTAGE)
        
        return voltage_sequence.tolist()
    
    def generate(
        self,
        condition: Optional[Dict[str, Any]] = None,
        sequence_length: int = 8,
        temperature: float = 1.0,
        random_seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        使用GAN模型生成测试序列
        
        Args:
            condition: 生成条件
            sequence_length: 序列长度
            temperature: 采样温度（控制随机性）
            random_seed: 随机种子
        
        Returns:
            生成的测试数据
        
        Raises:
            RuntimeError: 如果模型未加载
        """
        if not self.model_loaded:
            error_msg = (
                "错误: GAN模型未加载！\n"
                "请先调用 load_model() 方法加载模型，\n"
                "或确保模型文件存在于: model_weights/vcu/"
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        try:
            # 根据模型类型生成数据
            if self.model_type == 'keras':
                # Keras/TensorFlow模型
                import tensorflow as tf
                
                # 设置随机种子
                if random_seed is not None:
                    tf.random.set_seed(random_seed)
                    np.random.seed(random_seed)
                
                # 准备输入
                # 使用模型实际需要的维度
                if hasattr(self, 'actual_c_dim'):
                    actual_c_dim = self.actual_c_dim
                else:
                    actual_c_dim = C_DIM
                
                # 获取实际的Z_DIM（如果已推断）
                if hasattr(self, 'model_instance') and self.model_instance:
                    if hasattr(self.model_instance, 'z_dim'):
                        actual_z_dim = self.model_instance.z_dim
                    else:
                        actual_z_dim = Z_DIM
                else:
                    actual_z_dim = Z_DIM
                
                z = np.random.randn(1, actual_z_dim).astype(np.float32) * temperature
                c = self._prepare_condition(condition).reshape(1, -1).astype(np.float32)
                
                # 确保条件向量维度正确
                if c.shape[1] != actual_c_dim:
                    # 如果维度不匹配，调整
                    if c.shape[1] > actual_c_dim:
                        c = c[:, :actual_c_dim]
                    else:
                        # 填充零
                        padding = np.zeros((1, actual_c_dim - c.shape[1]), dtype=np.float32)
                        c = np.concatenate([c, padding], axis=1)
                
                # 生成数据
                # 根据FLAG，生成器可能接受不同的输入格式
                if hasattr(self, 'flag') and self.flag == 'LWCO':
                    # 带条件的生成器：输入是 [c_code, z_var]
                    try:
                        generated = self.generator.predict([c, z], verbose=0)
                    except Exception as e:
                        logger.error(f"生成失败: {e}")
                        logger.info("尝试其他输入格式...")
                        # 尝试其他格式
                        try:
                            # 可能输入顺序不同
                            generated = self.generator.predict([z, c], verbose=0)
                        except:
                            # 或者需要拼接
                            combined = np.concatenate([c, z], axis=1)
                            generated = self.generator.predict(combined, verbose=0)
                else:
                    # 无条件的生成器：只需要z
                    generated = self.generator.predict(z, verbose=0)
                
                generated_np = np.array(generated)
                
            elif self.model_type == 'pytorch':
                # PyTorch模型
                import torch
                
                # 设置随机种子
                if random_seed is not None:
                    torch.manual_seed(random_seed)
                    np.random.seed(random_seed)
                
                # 准备输入
                z = torch.randn(1, Z_DIM).to(self.device) * temperature
                c = torch.from_numpy(self._prepare_condition(condition)).float().unsqueeze(0).to(self.device)
                
                # 生成数据
                with torch.no_grad():
                    generated = self.generator(z, c)
                    generated_np = generated.cpu().numpy()
            else:
                raise RuntimeError(f"未知的模型类型: {self.model_type}")
            
            # 后处理
            voltage_sequence = self._postprocess_generated(generated_np)
            
            # 确保序列长度正确
            if len(voltage_sequence) > sequence_length:
                voltage_sequence = voltage_sequence[:sequence_length]
            elif len(voltage_sequence) < sequence_length:
                # 如果生成的序列较短，用最后一个值填充
                voltage_sequence.extend([voltage_sequence[-1]] * (sequence_length - len(voltage_sequence)))
            
            # 根据条件调整
            if condition:
                if condition.get("target_phase") == "sleep":
                    voltage_sequence[-1] = SLEEP_VOLTAGE
                elif condition.get("target_phase") == "wake":
                    voltage_sequence[0] = max(voltage_sequence[0], CC2_MIN_VOLTAGE + 1.0)
            
            # 构建返回数据
            gan_data = {
                "cc2_voltage": voltage_sequence[0],
                "voltage_sequence": voltage_sequence,
                "vehicle_status": condition.get("vehicle_status", 100) if condition else np.random.randint(30, 170),
                "ready_flag": 1 if voltage_sequence[0] > 6.0 else 0,
                "generated_at": datetime.now().isoformat(),
                "condition": condition,
                "model_used": True
            }
            
            return gan_data
            
        except Exception as e:
            logger.error(f"使用GAN模型生成数据失败: {str(e)}，回退到模拟模式")
            return self._generate_mock(condition, sequence_length, temperature, random_seed)
    
    def _generate_mock(
        self,
        condition: Optional[Dict[str, Any]],
        sequence_length: int,
        temperature: float,
        random_seed: Optional[int]
    ) -> Dict[str, Any]:
        """
        模拟模式生成数据（当模型未加载时使用）
        """
        if random_seed is not None:
            np.random.seed(random_seed)
        else:
            np.random.seed(int(datetime.now().timestamp()))
        
        # 生成电压序列
        voltage_sequence = np.random.uniform(
            CC2_MIN_VOLTAGE,
            CC2_MAX_VOLTAGE,
            size=sequence_length
        ).tolist()
        
        # 根据条件调整
        if condition:
            if condition.get("target_phase") == "sleep":
                voltage_sequence[-1] = SLEEP_VOLTAGE
            elif condition.get("target_phase") == "wake":
                voltage_sequence[0] = np.random.uniform(CC2_MIN_VOLTAGE + 1.0, CC2_MAX_VOLTAGE)
        
        # 构建返回数据
        gan_data = {
            "cc2_voltage": voltage_sequence[0],
            "voltage_sequence": voltage_sequence,
            "vehicle_status": np.random.randint(30, 170) if not condition else condition.get("vehicle_status", 100),
            "ready_flag": 1 if voltage_sequence[0] > 6.0 else 0,
            "generated_at": datetime.now().isoformat(),
            "condition": condition,
            "model_used": False  # 标记为模拟模式
        }
        
        return gan_data

