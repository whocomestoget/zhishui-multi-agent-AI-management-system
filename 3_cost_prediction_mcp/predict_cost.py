#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水利工程成本预测工具
四川智水信息技术有限公司
使用训练好的Lasso回归模型进行成本预测
"""

import joblib
import numpy as np
import json
import os
import logging
from datetime import datetime

# 配置日志
logger = logging.getLogger(__name__)

class HydropowerCostPredictor:
    """水利工程成本预测器"""
    
    def __init__(self, model_dir=None):
        """初始化预测器"""
        if model_dir is None:
            # 获取当前文件所在目录的绝对路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.model_dir = os.path.join(current_dir, 'models')
        else:
            self.model_dir = model_dir
            
        self.model = None
        self.scaler = None
        self.project_type_mapping = None
        self.location_mapping = None
        self.feature_columns = None
        
        self._load_model()
    
    def _load_model(self):
        """加载训练好的模型和相关配置"""
        try:
            # 检查模型目录是否存在
            if not os.path.exists(self.model_dir):
                raise FileNotFoundError(f"模型目录不存在: {self.model_dir}")
            
            # 加载模型和标准化器
            model_path = os.path.join(self.model_dir, 'final_solution_model.joblib')
            scaler_path = os.path.join(self.model_dir, 'final_solution_scaler.joblib')
            history_path = os.path.join(self.model_dir, 'final_solution_training_history.json')
            
            # 检查文件是否存在
            for file_path, file_name in [(model_path, '模型文件'), (scaler_path, '标准化器文件'), (history_path, '训练历史文件')]:
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"{file_name}不存在: {file_path}")
            
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            
            # 加载配置信息
            with open(history_path, 'r', encoding='utf-8') as f:
                history = json.load(f)
                
            self.project_type_mapping = history['project_type_mapping']
            # 使用已知的特征列表
            self.feature_columns = ['capacity_mw', 'capacity_per_period', 'economic_indicator', 'project_type_encoded']
            
            logger.info("模型加载成功！")
            logger.info(f"模型目录: {self.model_dir}")
            logger.info(f"模型类型: {history['model_type']}")
            logger.info(f"训练时间: {history['timestamp']}")
            logger.info(f"测试集R²分数: {history['best_model_metrics']['test_r2']:.4f}")
            logger.info(f"过拟合差距: {history['best_model_metrics']['overfitting_percentage']:.2f}%")
            
        except Exception as e:
            raise Exception(f"模型加载失败: {str(e)}")
    
    def predict_single(self, capacity_mw, project_type, construction_period, economic_indicator):
        """预测单个项目的成本
        
        参数:
            capacity_mw: 装机容量 (MW)
            project_type: 项目类型 ('常规大坝', '抽水蓄能', '径流式')
            construction_period: 建设周期 (年)
            economic_indicator: 经济指标 (0-1之间的小数)
        
        返回:
            预测成本 (亿元)
        """
        try:
            # 验证输入参数
            if project_type not in self.project_type_mapping:
                raise ValueError(f"无效的项目类型: {project_type}. 支持的类型: {list(self.project_type_mapping.keys())}")
            
            # 编码分类特征
            project_type_encoded = self.project_type_mapping[project_type]
            
            # 计算capacity_per_period特征
            capacity_per_period = capacity_mw / construction_period if construction_period > 0 else 0
            
            # 构建特征向量 (4个特征，按训练时的顺序: capacity_mw, capacity_per_period, economic_indicator, project_type_encoded)
            features = np.array([[
                capacity_mw,
                capacity_per_period, 
                economic_indicator,
                project_type_encoded
            ]])
            
            # 调试信息已移除，保持代码整洁
            
            # 标准化特征
            features_scaled = self.scaler.transform(features)
            
            # 预测
            prediction = self.model.predict(features_scaled)[0]
            
            # 确保预测结果为正值（成本不能为负）
            if prediction < 0:
                logger.warning(f"预测结果为负值 {prediction:.2f}，调整为最小合理值")
                # 基于装机容量的最小成本估算（每MW约500万元）
                prediction = max(0.05, capacity_mw * 0.005)  # 最小0.05亿元
            
            return prediction
            
        except Exception as e:
            raise Exception(f"预测失败: {str(e)}")
    
    def predict_batch(self, projects_data):
        """批量预测多个项目的成本
        
        参数:
            projects_data: 项目数据列表，每个元素是包含项目信息的字典
        
        返回:
            预测结果列表
        """
        results = []
        
        for i, project in enumerate(projects_data):
            try:
                prediction = self.predict_single(
                    project['capacity_mw'],
                    project['project_type'],
                    project['construction_period'],
                    project['economic_indicator']
                )
                
                results.append({
                    'project_index': i + 1,
                    'project_info': project,
                    'predicted_cost': prediction,
                    'status': 'success'
                })
                
            except Exception as e:
                results.append({
                    'project_index': i + 1,
                    'project_info': project,
                    'predicted_cost': None,
                    'status': 'error',
                    'error_message': str(e)
                })
        
        return results
    
    def get_feature_importance(self):
        """获取特征重要性"""
        history_path = os.path.join(self.model_dir, 'final_solution_training_history.json')
        
        with open(history_path, 'r', encoding='utf-8') as f:
            history_data = json.load(f)
        
        return history_data['feature_importance']
    
    def print_prediction_report(self, capacity_mw, project_type,
                               construction_period, economic_indicator):
        """打印详细的预测报告"""
        print("\n" + "=" * 50)
        print("水利工程成本预测报告")
        print("四川智水信息技术有限公司")
        print("=" * 50)
        
        print(f"预测时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n项目基本信息:")
        print(f"  装机容量: {capacity_mw:,} MW")
        print(f"  项目类型: {project_type}")
        print(f"  建设周期: {construction_period} 年")
        print(f"  经济指标: {economic_indicator}")
        
        try:
            predicted_cost = self.predict_single(
                capacity_mw, project_type,
                construction_period, economic_indicator
            )
            
            print("\n预测结果:")
            print(f"  预测总成本: {predicted_cost:.2f} 亿元")
            print(f"  单位成本: {predicted_cost * 10000 / capacity_mw:.2f} 万元/MW")
            
            # 显示特征重要性
            print("\n模型特征重要性:")
            importance_data = self.get_feature_importance()
            feature_name_map = {
                'capacity_mw': '装机容量',
                'capacity_per_period': '年均装机容量',
                'project_type_encoded': '项目类型',
                'economic_indicator': '经济指标'
            }
            for feature, importance in importance_data.items():
                feature_name = feature_name_map.get(feature, feature)
                print(f"  {feature_name}: {importance*100:.1f}%")
            
            print("\n" + "=" * 50)
            
        except Exception as e:
            print(f"\n预测失败: {str(e)}")
            print("=" * 50)

def main():
    """主函数 - 仅用于模块导入测试"""
    try:
        # 初始化预测器以验证模型加载
        predictor = HydropowerCostPredictor()
        logger.info("✅ 成本预测器初始化成功，模型已就绪")
        
    except Exception as e:
        logger.error(f"❌ 模型加载失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()