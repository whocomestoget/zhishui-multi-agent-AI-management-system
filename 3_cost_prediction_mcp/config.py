# ============================================================================
# 文件：config.py
# 功能：智慧水电成本预测模型配置文件
# 技术：基于Random Forest算法的成本预测配置
# ============================================================================

"""
智慧水电成本预测模型配置
- 定义模型超参数和特征工程配置
- 基于论文《Explainable Machine Learning to Predict the Construction Cost of Power Plant》
- 针对智慧水电项目特点进行优化
"""

import os
from pathlib import Path

# 项目路径配置
PROJECT_ROOT = Path(__file__).parent
MODELS_DIR = PROJECT_ROOT / "models"
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

# 确保目录存在
MODELS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# 随机森林模型超参数（基于论文优化）
RANDOM_FOREST_PARAMS = {
    'n_estimators': 100,        # 论文最优值
    'max_features': 8,          # 论文最优值
    'max_depth': 15,            # 根据特征数调整
    'min_samples_split': 5,     # 防止过拟合
    'min_samples_leaf': 2,      # 叶节点最小样本数
    'random_state': 42,         # 可重复性
    'n_jobs': -1               # 使用所有CPU核心
}

# 核心特征集（简化版本）
CORE_FEATURES = [
    'capacity_mw',           # 装机容量（MW）- 最重要特征
    'project_type_encoded',  # 项目类型编码
    'location_factor_encoded', # 地理位置编码
    'construction_period',   # 建设周期（年）
    'economic_indicator'     # 经济指标（开工年GDP增长率）
]

# 分类特征映射
PROJECT_TYPE_MAPPING = {
    '常规大坝': 1,
    '抽水蓄能': 2,
    '径流式': 3
}

LOCATION_FACTOR_MAPPING = {
    '河谷': 1,
    '山区': 2,
    '高山峡谷': 3,
    '丘陵': 1,  # 与河谷等价
    '平原': 1   # 与河谷等价
}

# 模型评估指标目标
MODEL_PERFORMANCE_TARGETS = {
    'r2_score': 0.75,          # R²目标值（论文达到0.956）
    'rmse_threshold': 0.15,    # 相对误差阈值
    'mae_threshold': 0.12      # 平均绝对误差阈值
}

# 数据验证规则
DATA_VALIDATION_RULES = {
    'capacity_mw': {'min': 1, 'max': 30000},
    'construction_period': {'min': 1, 'max': 10},
    'economic_indicator': {'min': 0, 'max': 1},
    'total_cost': {'min': 0.1, 'max': 10000}  # 亿元
}

# 成本预测相关配置
COST_PREDICTION_CONFIG = {
    'base_cost_per_mw': 0.45,       # 基础成本（亿元/MW）
    'smart_premium_factor': 1.2,    # 智慧化溢价系数
    'confidence_interval': 0.85,    # 置信区间
    'currency': 'RMB',              # 货币单位
    'cost_unit': '亿元'             # 成本单位
}

# 风险评估权重
RISK_ASSESSMENT_WEIGHTS = {
    'project_complexity': 0.25,
    'technology_risk': 0.20,
    'environmental_factor': 0.15,
    'team_experience': 0.15,
    'client_type': 0.10,
    'market_conditions': 0.15
}

# 日志配置
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': LOGS_DIR / 'model_training.log'
}

# 模型文件路径
MODEL_FILES = {
    'cost_predictor': MODELS_DIR / 'cost_predictor.pkl',
    'feature_scaler': MODELS_DIR / 'feature_scaler.pkl',
    'risk_weights': MODELS_DIR / 'risk_weights.json',
    'feature_importance': MODELS_DIR / 'feature_importance.json'
}

# 训练数据配置
TRAINING_DATA_CONFIG = {
    'test_size': 0.2,           # 测试集比例
    'validation_size': 0.1,     # 验证集比例
    'random_state': 42,         # 随机种子
    'stratify_column': 'project_type_encoded'  # 分层抽样列
}