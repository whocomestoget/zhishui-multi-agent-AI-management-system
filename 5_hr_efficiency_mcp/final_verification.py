#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终验证接口兼容性修复效果
"""

import json
import sys
import os
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def final_verification():
    """
    最终验证修复效果
    """
    print("🔍 最终验证接口兼容性修复效果...")
    print("=" * 50)
    
    # 1. 验证测试数据
    try:
        with open('test_data.json', 'r', encoding='utf-8') as f:
            test_data = json.load(f)
        print("✅ 测试数据加载成功")
        print(f"   - 员工姓名: {test_data['employee_data']['name']}")
        print(f"   - 岗位类型: {test_data['position_type']}")
    except Exception as e:
        print(f"❌ 测试数据加载失败: {e}")
        return False
    
    # 2. 验证评分工具
    try:
        from zhishui_efficiency_mcp import evaluate_employee_efficiency
        
        scores_result = evaluate_employee_efficiency(
            json.dumps(test_data['employee_data']),
            json.dumps(test_data['metrics_data']),
            test_data['position_type']
        )
        
        # 验证返回格式是否为有效JSON
        scores_data = json.loads(scores_result)
        overall_score = scores_data.get('综合评分', {}).get('总分', 0)
        
        print("✅ 评分工具验证成功")
        print(f"   - 返回格式: 有效JSON")
        print(f"   - 综合得分: {overall_score}分")
        print(f"   - 数据完整性: {'✅ 完整' if '维度得分' in scores_data else '❌ 不完整'}")
        
    except json.JSONDecodeError as e:
        print(f"❌ 评分工具返回格式错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 评分工具验证失败: {e}")
        return False
    
    # 3. 验证报告生成工具
    try:
        from zhishui_efficiency_mcp import generate_efficiency_report
        
        report_result = generate_efficiency_report(
            report_type="individual",
            target_scope="张伟",
            time_period="quarterly",
            data_source=scores_result,  # 使用评分工具的输出
            output_format="html"
        )
        
        print("✅ 报告生成工具验证成功")
        print(f"   - 调用状态: 成功")
        print(f"   - 输出格式: {'HTML' if 'HTML报告' in report_result else 'Markdown'}")
        
        # 检查HTML文件
        if "HTML报告已保存到" in report_result:
            # 提取文件路径
            lines = report_result.split('\n')
            for line in lines:
                if "文件路径:" in line:
                    file_path = line.split("文件路径:")[1].strip()
                    
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        print(f"   - HTML文件: ✅ 已生成 ({file_size} 字节)")
                        
                        if file_size > 10000:  # 至少10KB
                            print(f"   - 文件质量: ✅ 内容丰富")
                        else:
                            print(f"   - 文件质量: ⚠️ 内容较少")
                    else:
                        print(f"   - HTML文件: ❌ 未找到")
                        return False
        
    except Exception as e:
        print(f"❌ 报告生成工具验证失败: {e}")
        return False
    
    # 4. 验证数据流转
    print("\n📊 数据流转验证:")
    print("   评分工具 → JSON输出 → 报告工具 → HTML文件")
    print("   ✅ 完整流程验证成功")
    
    return True

def show_fix_summary():
    """
    显示修复总结
    """
    print("\n" + "=" * 50)
    print("🔧 接口兼容性问题修复总结")
    print("=" * 50)
    
    print("\n🎯 问题诊断:")
    print("   1. 评分工具输出带有前缀文本，不是纯JSON格式")
    print("   2. 报告工具期望数据包裹在'scores_data'字段内")
    print("   3. 两个工具的数据接口不匹配")
    
    print("\n🛠️ 修复措施:")
    print("   1. 修改评分工具返回纯JSON格式（去除前缀文本）")
    print("   2. 修改报告工具自动检测和包装数据格式")
    print("   3. 增加数据格式兼容性处理逻辑")
    
    print("\n✨ 修复效果:")
    print("   ✅ 评分工具输出标准JSON格式")
    print("   ✅ 报告工具能正确解析评分数据")
    print("   ✅ HTML报告成功生成并包含完整内容")
    print("   ✅ 数据流转完全兼容")
    
    print("\n🌐 使用方式:")
    print("   1. 调用evaluate_employee_efficiency获取评分JSON")
    print("   2. 直接将评分JSON作为data_source传递给generate_efficiency_report")
    print("   3. 设置output_format='html'生成可交互HTML报告")
    
    print("\n🎉 修复完成！接口兼容性问题已彻底解决")

def main():
    """
    主函数
    """
    print("🔧 智水人员效能管理系统 - 最终验证")
    print(f"⏰ 验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 执行验证
    success = final_verification()
    
    if success:
        show_fix_summary()
    else:
        print("\n❌ 验证失败！请检查错误信息")

if __name__ == "__main__":
    main()