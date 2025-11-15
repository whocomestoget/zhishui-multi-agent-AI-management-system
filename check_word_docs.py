#!/usr/bin/env python3
"""
检查Word文档生成情况的脚本
"""

import os
import glob
from datetime import datetime

def check_word_documents():
    """检查Word文档生成情况"""
    print("🔍 检查Word文档生成情况...")
    
    # 检查桌面上的智水信息AI分析报告文件夹
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    reports_dir = os.path.join(desktop_path, "智水信息AI分析报告")
    
    print(f"📁 检查目录: {reports_dir}")
    
    if os.path.exists(reports_dir):
        print("✅ 报告目录存在")
        
        # 查找所有Word文档
        word_files = glob.glob(os.path.join(reports_dir, "*.docx"))
        
        if word_files:
            print(f"📄 找到 {len(word_files)} 个Word文档:")
            for i, file_path in enumerate(word_files, 1):
                file_name = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                print(f"  {i}. {file_name}")
                print(f"     大小: {file_size} bytes")
                print(f"     修改时间: {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print()
        else:
            print("❌ 未找到Word文档")
    else:
        print("❌ 报告目录不存在")
        print(f"💡 尝试创建目录: {reports_dir}")
        try:
            os.makedirs(reports_dir, exist_ok=True)
            print("✅ 目录创建成功")
        except Exception as e:
            print(f"❌ 目录创建失败: {str(e)}")
    
    # 也检查项目reports目录
    project_reports_dir = os.path.join(os.path.dirname(__file__), "7_agno_coordinator", "reports")
    print(f"\n📁 检查项目reports目录: {project_reports_dir}")
    
    if os.path.exists(project_reports_dir):
        word_files = glob.glob(os.path.join(project_reports_dir, "*.docx"))
        if word_files:
            print(f"📄 项目reports目录中找到 {len(word_files)} 个Word文档:")
            for file_path in word_files:
                print(f"  - {os.path.basename(file_path)}")
        else:
            print("❌ 项目reports目录中未找到Word文档")
    else:
        print("❌ 项目reports目录不存在")

if __name__ == "__main__":
    check_word_documents()