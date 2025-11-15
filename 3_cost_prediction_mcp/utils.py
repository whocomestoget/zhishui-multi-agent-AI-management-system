# ============================================================================
# 文件：utils.py
# 功能：智慧水电成本预测模型工具函数
# 技术：数据处理、特征工程、模型评估工具集
# ============================================================================

"""
智慧水电成本预测工具函数模块
- 提供数据预处理和特征工程功能
- 实现模型评估和可视化工具
- 支持数据验证和异常处理
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

from config import (
    CORE_FEATURES, PROJECT_TYPE_MAPPING, LOCATION_FACTOR_MAPPING,
    DATA_VALIDATION_RULES, MODEL_PERFORMANCE_TARGETS,
    TRAINING_DATA_CONFIG, LOGGING_CONFIG
)

# 配置日志
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG['level']),
    format=LOGGING_CONFIG['format'],
    handlers=[
        logging.FileHandler(LOGGING_CONFIG['file']),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DataProcessor:
    """
    数据处理器类
    负责数据清洗、特征工程和验证
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        
    def validate_data(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        验证数据质量和完整性
        
        Args:
            df: 输入数据框
            
        Returns:
            (is_valid, error_messages): 验证结果和错误信息
        """
        errors = []
        
        # 检查必需列是否存在
        required_columns = ['capacity_mw', 'project_type', 'location_factor', 
                          'construction_period', 'economic_indicator']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            errors.append(f"缺少必需列: {missing_columns}")
            
        # 检查数值范围
        for column, rules in DATA_VALIDATION_RULES.items():
            if column in df.columns:
                invalid_rows = df[
                    (df[column] < rules['min']) | (df[column] > rules['max'])
                ]
                if not invalid_rows.empty:
                    errors.append(f"列 {column} 存在超出范围的值: {rules}")
                    
        # 检查空值
        null_columns = df.isnull().sum()
        null_columns = null_columns[null_columns > 0]
        if not null_columns.empty:
            errors.append(f"存在空值的列: {null_columns.to_dict()}")
            
        return len(errors) == 0, errors
    
    def encode_categorical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        编码分类特征
        
        Args:
            df: 输入数据框
            
        Returns:
            编码后的数据框
        """
        df_encoded = df.copy()
        
        # 项目类型编码
        if 'project_type' in df_encoded.columns:
            df_encoded['project_type_encoded'] = df_encoded['project_type'].map(
                PROJECT_TYPE_MAPPING
            ).fillna(1)  # 默认为常规大坝
            
        # 地理位置编码
        if 'location_factor' in df_encoded.columns:
            df_encoded['location_factor_encoded'] = df_encoded['location_factor'].map(
                LOCATION_FACTOR_MAPPING
            ).fillna(1)  # 默认为河谷
            
        logger.info("分类特征编码完成")
        return df_encoded
    
    def create_smart_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        创建智慧化相关特征
        
        Args:
            df: 输入数据框
            
        Returns:
            添加智慧化特征的数据框
        """
        df_smart = df.copy()
        
        # 智慧化程度（基于项目类型和技术特征）
        if 'smart_level' not in df_smart.columns:
            df_smart['smart_level'] = 3  # 默认中等智慧化水平
            
        # 环境复杂度（基于地理位置）
        if 'environmental_complexity' not in df_smart.columns:
            complexity_map = {'河谷': 2, '山区': 3, '高山峡谷': 5, '平原': 1}
            df_smart['environmental_complexity'] = df_smart['location_factor'].map(
                complexity_map
            ).fillna(3)
            
        # 技术成熟度（基于项目类型）
        if 'technology_maturity' not in df_smart.columns:
            maturity_map = {'常规大坝': 5, '抽水蓄能': 4, '径流式': 4}
            df_smart['technology_maturity'] = df_smart['project_type'].map(
                maturity_map
            ).fillna(3)
            
        logger.info("智慧化特征创建完成")
        return df_smart
    
    def prepare_features(self, df: pd.DataFrame, fit_scaler: bool = True) -> np.ndarray:
        """
        准备模型训练特征
        
        Args:
            df: 输入数据框
            fit_scaler: 是否拟合标准化器
            
        Returns:
            标准化后的特征矩阵
        """
        # 选择核心特征（使用实际可用的特征列）
        available_features = [col for col in CORE_FEATURES if col in df.columns]
        if not available_features:
            # 如果没有找到配置的特征，使用所有数值特征
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if 'total_cost' in numeric_cols:
                numeric_cols.remove('total_cost')  # 移除目标变量
            available_features = numeric_cols
        
        feature_df = df[available_features].copy()
        logger.info(f"使用特征: {available_features}")
        
        # 处理缺失值
        feature_df = feature_df.fillna(feature_df.mean())
        
        # 标准化
        if fit_scaler:
            features_scaled = self.scaler.fit_transform(feature_df)
            logger.info("特征标准化器已拟合")
        else:
            features_scaled = self.scaler.transform(feature_df)
            
        logger.info(f"特征准备完成，形状: {features_scaled.shape}")
        return features_scaled


class ModelEvaluator:
    """
    模型评估器类
    提供模型性能评估和可视化功能
    """
    
    @staticmethod
    def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """
        计算模型评估指标
        
        Args:
            y_true: 真实值
            y_pred: 预测值
            
        Returns:
            评估指标字典
        """
        metrics = {
            'r2_score': r2_score(y_true, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
            'mae': mean_absolute_error(y_true, y_pred),
            'mape': np.mean(np.abs((y_true - y_pred) / y_true)) * 100,
            'relative_rmse': np.sqrt(mean_squared_error(y_true, y_pred)) / np.mean(y_true)
        }
        
        return metrics
    
    @staticmethod
    def evaluate_model_performance(metrics: Dict[str, float]) -> Dict[str, bool]:
        """
        评估模型是否达到性能目标
        
        Args:
            metrics: 模型评估指标
            
        Returns:
            性能达标情况
        """
        performance = {
            'r2_target_met': metrics['r2_score'] >= MODEL_PERFORMANCE_TARGETS['r2_score'],
            'rmse_target_met': metrics['relative_rmse'] <= MODEL_PERFORMANCE_TARGETS['rmse_threshold'],
            'mae_target_met': metrics['mae'] / np.mean([1000, 50000]) <= MODEL_PERFORMANCE_TARGETS['mae_threshold']
        }
        
        performance['overall_target_met'] = all(performance.values())
        
        return performance
    
    @staticmethod
    def plot_prediction_results(y_true: np.ndarray, y_pred: np.ndarray, 
                              save_path: Optional[Path] = None) -> None:
        """
        绘制预测结果对比图
        
        Args:
            y_true: 真实值
            y_pred: 预测值
            save_path: 保存路径
        """
        plt.figure(figsize=(12, 5))
        
        # 预测vs真实值散点图
        plt.subplot(1, 2, 1)
        plt.scatter(y_true, y_pred, alpha=0.6)
        plt.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--', lw=2)
        plt.xlabel('真实成本 (万元)')
        plt.ylabel('预测成本 (万元)')
        plt.title('预测值 vs 真实值')
        plt.grid(True, alpha=0.3)
        
        # 残差图
        plt.subplot(1, 2, 2)
        residuals = y_pred - y_true
        plt.scatter(y_pred, residuals, alpha=0.6)
        plt.axhline(y=0, color='r', linestyle='--')
        plt.xlabel('预测成本 (万元)')
        plt.ylabel('残差 (万元)')
        plt.title('残差分布图')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"预测结果图已保存到: {save_path}")
        
        plt.show()
    
    @staticmethod
    def plot_feature_importance(feature_importance: Dict[str, float], 
                              save_path: Optional[Path] = None) -> None:
        """
        绘制特征重要性图
        
        Args:
            feature_importance: 特征重要性字典
            save_path: 保存路径
        """
        features = list(feature_importance.keys())
        importance = list(feature_importance.values())
        
        plt.figure(figsize=(10, 6))
        bars = plt.barh(features, importance)
        plt.xlabel('特征重要性')
        plt.title('随机森林模型特征重要性')
        plt.grid(True, alpha=0.3)
        
        # 添加数值标签
        for bar, imp in zip(bars, importance):
            plt.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2, 
                    f'{imp:.3f}', va='center')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"特征重要性图已保存到: {save_path}")
        
        plt.show()


def save_model_artifacts(model, scaler, feature_importance: Dict[str, float], 
                        model_files: Dict[str, Path]) -> None:
    """
    保存模型相关文件
    
    Args:
        model: 训练好的模型
        scaler: 特征标准化器
        feature_importance: 特征重要性
        model_files: 模型文件路径配置
    """
    # 保存模型
    joblib.dump(model, model_files['cost_predictor'])
    logger.info(f"模型已保存到: {model_files['cost_predictor']}")
    
    # 保存标准化器
    joblib.dump(scaler, model_files['feature_scaler'])
    logger.info(f"标准化器已保存到: {model_files['feature_scaler']}")
    
    # 保存特征重要性
    with open(model_files['feature_importance'], 'w', encoding='utf-8') as f:
        json.dump(feature_importance, f, ensure_ascii=False, indent=2)
    logger.info(f"特征重要性已保存到: {model_files['feature_importance']}")


def load_model_artifacts(model_files: Dict[str, Path]) -> Tuple[Any, Any, Dict[str, float]]:
    """
    加载模型相关文件
    
    Args:
        model_files: 模型文件路径配置
        
    Returns:
        (model, scaler, feature_importance): 模型、标准化器、特征重要性
    """
    # 加载模型
    model = joblib.load(model_files['cost_predictor'])
    logger.info(f"模型已从 {model_files['cost_predictor']} 加载")
    
    # 加载标准化器
    scaler = joblib.load(model_files['feature_scaler'])
    logger.info(f"标准化器已从 {model_files['feature_scaler']} 加载")
    
    # 加载特征重要性
    with open(model_files['feature_importance'], 'r', encoding='utf-8') as f:
        feature_importance = json.load(f)
    logger.info(f"特征重要性已从 {model_files['feature_importance']} 加载")
    
    return model, scaler, feature_importance


def split_data(X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    分割训练和测试数据
    
    Args:
        X: 特征矩阵
        y: 目标变量
        
    Returns:
        (X_train, X_test, y_train, y_test): 训练和测试数据
    """
    return train_test_split(
        X, y, 
        test_size=TRAINING_DATA_CONFIG['test_size'],
        random_state=TRAINING_DATA_CONFIG['random_state']
    )