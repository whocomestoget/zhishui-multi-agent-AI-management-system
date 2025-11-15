# ============================================================================
# 文件：generate_data_template.py
# 功能：生成智慧水电成本预测模型训练数据模板和说明文档
# 技术：数据模板生成、业务字段定义、数据验证规则
# ============================================================================

"""
智慧水电成本预测数据模板生成器
- 生成标准的训练数据模板
- 提供详细的字段说明和数据要求
- 包含数据验证规则和示例数据
- 支持Excel和CSV格式输出
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DataTemplateGenerator:
    """
    数据模板生成器
    为智慧水电成本预测模型生成标准数据模板
    """
    
    def __init__(self):
        self.template_fields = self._define_template_fields()
        self.validation_rules = self._define_validation_rules()
        self.example_data = self._generate_example_data(1000)  # 生成1000个示例数据
    
    def _define_template_fields(self) -> Dict[str, Dict[str, Any]]:
        """
        定义数据模板字段（简化版：5个输入参数 + 1个目标变量）
        
        Returns:
            字段定义字典
        """
        fields = {
            # 简化的输入参数
            'capacity_mw': {
                'description': '装机容量(MW)',
                'type': 'numeric',
                'required': True,
                'min_value': 1,
                'max_value': 30000,
                'example': 500,
                'business_meaning': '水电站的总装机容量，单位为兆瓦(MW)'
            },
            'project_type': {
                'description': '项目类型',
                'type': 'categorical',
                'required': True,
                'options': ['大型水电站', '中型水电站', '小型水电站'],
                'example': '大型水电站',
                'business_meaning': '水电项目的类型分类'
            },
            'location_factor': {
                'description': '地理位置因子',
                'type': 'categorical',
                'required': True,
                'options': ['山区', '丘陵', '河谷'],
                'example': '山区',
                'business_meaning': '项目所在地理位置的复杂程度'
            },
            'construction_period': {
                'description': '建设周期(月)',
                'type': 'numeric',
                'required': True,
                'min_value': 12,
                'max_value': 120,
                'example': 48,
                'business_meaning': '项目从开工到完工的建设周期，单位为月'
            },
            'economic_indicator': {
                'description': '经济指标',
                'type': 'numeric',
                'required': True,
                'min_value': 0,
                'max_value': 1,
                'example': 0.75,
                'business_meaning': '项目的综合经济指标评分(0-1，百分比形式)'
            },
            
            # 目标变量
            'total_cost': {
                'description': '项目总投资(亿元)',
                'type': 'numeric',
                'required': True,
                'min_value': 0.1,
                'max_value': 10000,
                'example': 15,
                'business_meaning': '项目的总投资金额，单位为亿元人民币（目标变量）',
                'is_target': True
            }
        }
        
        return fields
    
    def _define_validation_rules(self) -> Dict[str, List[str]]:
        """
        定义数据验证规则
        
        Returns:
            验证规则字典
        """
        rules = {
            'data_quality': [
                '所有必填字段不能为空',
                '数值字段必须在合理范围内',
                '分类字段必须在预定义选项中',
                '项目名称不能重复'
            ],
            'business_logic': [
                '装机容量与年发电量应保持合理比例',
                '单位千瓦投资应在行业合理范围内(5000-20000元/kW)',
                '建设周期应与项目规模匹配',
                '智慧化等级与自动化程度应保持一致性'
            ],
            'data_consistency': [
                '同一地区的项目应具有相似的地质和环境特征',
                '相同类型项目的技术参数应在合理范围内',
                '成本数据应基于同一价格水平(建议统一到某一年份)'
            ]
        }
        
        return rules
    
    def _generate_example_data(self, num_examples: int = 10) -> List[Dict[str, Any]]:
        """
        生成示例数据（简化版）
        
        Args:
            num_examples: 生成示例数据的数量
        
        Returns:
            示例数据列表
        """
        import random
        
        examples = []
        for i in range(num_examples):  # 生成指定数量的示例
            # 先生成输入参数
            capacity = round(random.uniform(50, 30000), 1)
            project_type = random.choice(['大型水电站', '中型水电站', '小型水电站'])
            location_factor = random.choice(['山区', '丘陵', '河谷'])
            construction_period = random.randint(24, 96)
            economic_indicator = round(random.uniform(0, 1), 3)  # 0-1范围，保留3位小数
            
            # 基于输入参数生成合理的总投资（单位：亿元）
            base_cost = capacity * random.uniform(0.2, 0.5)  # 基础成本（亿元/MW）
            
            # 根据项目类型调整成本
            if project_type == '大型水电站':
                base_cost *= random.uniform(1.2, 1.5)
            elif project_type == '小型水电站':
                base_cost *= random.uniform(0.8, 1.0)
            
            # 根据地理位置调整成本
            if location_factor == '山区':
                base_cost *= random.uniform(1.1, 1.3)
            elif location_factor == '河谷':
                base_cost *= random.uniform(0.9, 1.1)
            
            # 根据建设周期调整成本
            if construction_period > 60:
                base_cost *= random.uniform(1.1, 1.2)
            
            # 根据经济指标调整成本
            if economic_indicator > 80:
                base_cost *= random.uniform(0.9, 1.0)
            elif economic_indicator < 50:
                base_cost *= random.uniform(1.1, 1.2)
            
            example = {
                'capacity_mw': capacity,
                'project_type': project_type,
                'location_factor': location_factor,
                'construction_period': construction_period,
                'economic_indicator': economic_indicator,
                'total_cost': round(base_cost, 2)  # 保留2位小数（亿元）
            }
            
            examples.append(example)
        
        return examples
    
    def generate_excel_template(self, output_path: str) -> None:
        """
        生成Excel格式的数据模板
        
        Args:
            output_path: 输出文件路径
        """
        output_path = Path(output_path)
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # 1. 数据模板工作表 - 字段名放在行上面（转置结构）
            template_data = {
                '字段名': [],
                '中文描述': [],
                '数据类型': [],
                '示例值': [],
                '数据输入': []  # 空行供用户填写
            }
            
            # 填充字段信息
            for field_name, field_info in self.template_fields.items():
                template_data['字段名'].append(field_name)
                template_data['中文描述'].append(field_info['description'])
                template_data['数据类型'].append(field_info['type'])
                template_data['示例值'].append(field_info['example'])
                template_data['数据输入'].append('')  # 空值供用户填写
            
            # 创建DataFrame并转置，使字段名作为行标题
            template_df = pd.DataFrame(template_data)
            template_df = template_df.set_index('字段名').T  # 转置，字段名作为列标题
            template_df.to_excel(writer, sheet_name='数据模板', index=True)
            
            # 2. 字段说明工作表
            field_info = []
            for field_name, field_info_dict in self.template_fields.items():
                field_info.append({
                    '字段名': field_name,
                    '中文描述': field_info_dict['description'],
                    '数据类型': field_info_dict['type'],
                    '是否必填': '是' if field_info_dict['required'] else '否',
                    '示例值': field_info_dict['example'],
                    '业务含义': field_info_dict['business_meaning'],
                    '选项/范围': field_info_dict.get('options', 
                                                str(field_info_dict.get('min_value', '')) + 
                                                ('-' + str(field_info_dict.get('max_value', '')) if field_info_dict.get('max_value') else ''))
                })
            
            field_df = pd.DataFrame(field_info)
            field_df.to_excel(writer, sheet_name='字段说明', index=False)
            
            # 3. 示例数据工作表
            example_df = pd.DataFrame(self.example_data)
            example_df.to_excel(writer, sheet_name='示例数据', index=False)
            
            # 4. 验证规则工作表
            validation_info = []
            for category, rules in self.validation_rules.items():
                for rule in rules:
                    validation_info.append({
                        '规则类别': category,
                        '验证规则': rule
                    })
            
            validation_df = pd.DataFrame(validation_info)
            validation_df.to_excel(writer, sheet_name='验证规则', index=False)
        
        logger.info(f"Excel数据模板已生成: {output_path}")
    
    def generate_csv_template(self, output_path: str) -> None:
        """
        生成CSV格式的数据模板
        
        Args:
            output_path: 输出文件路径
        """
        output_path = Path(output_path)
        
        # 创建空模板
        template_df = pd.DataFrame([{field: '' for field in self.template_fields.keys()}])
        template_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        # 生成示例数据文件（添加时间戳避免文件占用）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        example_path = output_path.parent / f"{output_path.stem}_examples_{timestamp}.csv"
        example_df = pd.DataFrame(self.example_data)
        example_df.to_csv(example_path, index=False, encoding='utf-8-sig')
        
        logger.info(f"CSV数据模板已生成: {output_path}")
        logger.info(f"CSV示例数据已生成: {example_path}")
    
    def generate_documentation(self, output_path: str) -> None:
        """
        生成详细的数据说明文档
        
        Args:
            output_path: 输出文件路径
        """
        output_path = Path(output_path)
        
        doc_content = {
            'document_info': {
                'title': '智慧水电成本预测模型训练数据说明文档',
                'version': '1.0',
                'creation_date': datetime.now().isoformat(),
                'purpose': '为智慧水电成本预测模型提供标准化的训练数据格式和要求说明'
            },
            'data_overview': {
                'total_fields': len(self.template_fields),
                'required_fields': sum(1 for f in self.template_fields.values() if f['required']),
                'optional_fields': sum(1 for f in self.template_fields.values() if not f['required']),
                'target_variable': 'total_cost',
                'recommended_sample_size': '建议至少100个项目样本，理想情况下300+个样本'
            },
            'field_definitions': self.template_fields,
            'validation_rules': self.validation_rules,
            'data_collection_guidelines': {
                'data_sources': [
                    '历史水电项目的设计文件和竣工资料',
                    '项目可行性研究报告',
                    '工程造价咨询报告',
                    '政府部门的项目审批文件',
                    '设备供应商的报价单据'
                ],
                'data_quality_requirements': [
                    '确保成本数据的时间一致性(建议统一到2023年价格水平)',
                    '核实项目信息的准确性和完整性',
                    '排除异常项目(如政策性项目、试验性项目)',
                    '确保地理分布的代表性'
                ],
                'preprocessing_steps': [
                    '统一成本数据的计价基础',
                    '处理缺失值和异常值',
                    '标准化分类变量的命名',
                    '验证数据的逻辑一致性'
                ]
            },
            'usage_instructions': {
                'file_format': 'Excel (.xlsx) 或 CSV (.csv)',
                'encoding': 'UTF-8',
                'data_entry_tips': [
                    '按照字段说明准确填写每个字段',
                    '必填字段不能为空',
                    '分类字段必须从预定义选项中选择',
                    '数值字段注意单位和精度要求',
                    '保持数据的一致性和准确性'
                ],
                'validation_checklist': [
                    '检查所有必填字段是否完整',
                    '验证数值字段是否在合理范围内',
                    '确认分类字段是否符合预定义选项',
                    '检查业务逻辑的一致性',
                    '核实成本数据的合理性'
                ]
            },
            'example_projects': self.example_data
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(doc_content, f, ensure_ascii=False, indent=2)
        
        logger.info(f"数据说明文档已生成: {output_path}")
    
    def generate_all_templates(self, output_dir: str) -> Dict[str, str]:
        """
        生成所有模板文件
        
        Args:
            output_dir: 输出目录
            
        Returns:
            生成的文件路径字典
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d")
        
        file_paths = {
            'excel_template': output_dir / f'智慧水电成本预测数据模板_{timestamp}.xlsx',
            'csv_template': output_dir / f'智慧水电成本预测数据模板_{timestamp}.csv',
            'documentation': output_dir / f'数据说明文档_{timestamp}.json',
            'readme': output_dir / 'README_数据准备指南.md'
        }
        
        # 生成各种格式的模板
        self.generate_excel_template(file_paths['excel_template'])
        self.generate_csv_template(file_paths['csv_template'])
        self.generate_documentation(file_paths['documentation'])
        self._generate_readme(file_paths['readme'])
        
        logger.info(f"所有模板文件已生成到目录: {output_dir}")
        
        return {k: str(v) for k, v in file_paths.items()}
    
    def _generate_readme(self, output_path: Path) -> None:
        """
        生成README文件
        
        Args:
            output_path: 输出路径
        """
        readme_content = """
# 智慧水电成本预测模型 - 数据准备指南

## 概述

本指南帮助您准备用于训练智慧水电成本预测模型的数据。模型基于随机森林算法，能够预测水电项目的总投资成本。

## 文件说明

- `智慧水电成本预测数据模板_YYYYMMDD.xlsx`: Excel格式的数据模板，包含多个工作表
- `智慧水电成本预测数据模板_YYYYMMDD.csv`: CSV格式的数据模板
- `数据说明文档_YYYYMMDD.json`: 详细的字段定义和验证规则
- `README_数据准备指南.md`: 本文件

## 数据要求

### 基本要求
- **样本数量**: 建议至少100个项目，理想情况下300+个项目
- **数据质量**: 确保数据准确、完整、一致
- **时间范围**: 建议使用近5-10年的项目数据
- **地理分布**: 覆盖不同地区和类型的项目

### 必填字段 (21个)
1. 项目名称 (project_name)
2. 项目类型 (project_type)
3. 所在省份 (location_province)
4. 装机容量 (capacity_mw)
5. 年发电量 (annual_generation_gwh)
6. 坝高 (dam_height_m)
7. 库容 (reservoir_capacity_million_m3)
8. 水轮机类型 (turbine_type)
9. 水轮机台数 (turbine_count)
10. 水头 (head_m)
11. 智慧化等级 (smart_level)
12. 自动化程度 (automation_degree)
13. 数字孪生 (digital_twin)
14. AI应用程度 (ai_application)
15. 地质条件 (geological_condition)
16. 环境敏感性 (environmental_sensitivity)
17. 地震烈度 (seismic_intensity)
18. 建设周期 (construction_period_years)
19. 经济发展水平 (economic_development_level)
20. 政策支持力度 (policy_support_level)
21. **项目总投资** (total_cost) - 目标变量

## 数据收集建议

### 数据来源
1. **项目设计文件**: 获取技术参数和设计方案
2. **可行性研究报告**: 获取经济分析和投资估算
3. **工程造价报告**: 获取详细的成本分解
4. **竣工验收资料**: 获取实际建设成本
5. **政府审批文件**: 获取项目基本信息

### 数据质量控制
1. **成本数据统一**: 建议统一到2023年价格水平
2. **单位统一**: 严格按照模板要求的单位填写
3. **逻辑检查**: 确保相关字段之间的逻辑一致性
4. **异常值处理**: 识别和处理明显的异常数据

## 使用步骤

1. **下载模板**: 使用Excel模板进行数据录入
2. **参考示例**: 查看"示例数据"工作表了解填写格式
3. **字段说明**: 参考"字段说明"工作表了解每个字段的含义
4. **数据验证**: 按照"验证规则"工作表检查数据质量
5. **保存数据**: 保存为CSV或Excel格式用于模型训练

## 注意事项

⚠️ **重要提醒**:
- 确保成本数据的准确性，这直接影响模型预测效果
- 智慧化相关字段是模型的重要特征，请准确填写
- 地理和环境信息影响成本结构，不可忽略
- 建设周期和政策环境对成本有重要影响

## 技术支持

如有数据准备相关问题，请联系技术团队获取支持。

---

**四川智水信息技术有限公司**  
**AI智慧管理解决方案开发团队**
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        logger.info(f"README文件已生成: {output_path}")


def main_template_generation(output_dir: str = "data_templates") -> Dict[str, str]:
    """
    主要模板生成流程
    
    Args:
        output_dir: 输出目录
        
    Returns:
        生成的文件路径字典
    """
    logger.info("开始生成数据模板")
    
    try:
        # 创建模板生成器
        generator = DataTemplateGenerator()
        
        # 生成所有模板
        file_paths = generator.generate_all_templates(output_dir)
        
        logger.info("=" * 60)
        logger.info("数据模板生成完成:")
        for file_type, file_path in file_paths.items():
            logger.info(f"{file_type}: {file_path}")
        logger.info("=" * 60)
        
        return file_paths
        
    except Exception as e:
        logger.error(f"模板生成过程中发生错误: {str(e)}")
        raise


if __name__ == "__main__":
    # 示例使用
    import argparse
    
    parser = argparse.ArgumentParser(description='生成智慧水电成本预测数据模板')
    parser.add_argument('--output_dir', type=str, default='data_templates', 
                       help='模板输出目录')
    
    args = parser.parse_args()
    
    # 生成模板
    file_paths = main_template_generation(args.output_dir)
    
    print("\n数据模板生成完成！")
    print("\n生成的文件:")
    for file_type, file_path in file_paths.items():
        print(f"- {file_type}: {file_path}")
    
    print("\n请按照模板要求准备训练数据，然后使用train_model.py进行模型训练。")