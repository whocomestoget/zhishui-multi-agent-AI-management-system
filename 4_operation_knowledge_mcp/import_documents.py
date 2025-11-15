#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档导入工具 - 四川智水运维知识库
功能：批量导入documents目录中的PDF文件到知识库
"""

import os
import sys
import base64
import json
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

try:
    from knowledge_mcp import import_document
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保knowledge_mcp.py文件存在")
    sys.exit(1)

def read_pdf_as_base64(file_path: str) -> str:
    """读取PDF文件并转换为base64编码"""
    try:
        with open(file_path, 'rb') as f:
            pdf_content = f.read()
        return base64.b64encode(pdf_content).decode('utf-8')
    except Exception as e:
        print(f"读取文件失败 {file_path}: {e}")
        return None

def import_pdf_file(file_path: str, category: str, subcategory: str = ""):
    """导入单个PDF文件"""
    print(f"\n正在导入: {file_path}")
    
    # 读取文件内容
    file_content = read_pdf_as_base64(file_path)
    if not file_content:
        return False
    
    # 获取文件名和标题
    filename = os.path.basename(file_path)
    title = filename.replace('.pdf', '')
    
    try:
        # 调用导入函数
        result = import_document(
            file_content=file_content,
            filename=filename,
            title=title,
            category=category,
            subcategory=subcategory
        )
        
        # 解析结果
        result_data = json.loads(result)
        if 'error' in result_data:
            print(f"导入失败: {result_data['error']}")
            return False
        else:
            print(f"导入成功: {result_data.get('title', title)}")
            print(f"文档ID: {result_data.get('doc_id', 'N/A')}")
            print(f"分块数量: {result_data.get('chunk_count', 'N/A')}")
            return True
            
    except Exception as e:
        print(f"导入过程出错: {e}")
        return False

def main():
    """主函数：批量导入PDF文件"""
    print("="*60)
    print("四川智水运维知识库 - 文档导入工具")
    print("="*60)
    
    # 文档目录
    documents_dir = Path("knowledge_base/documents")
    
    if not documents_dir.exists():
        print(f"文档目录不存在: {documents_dir}")
        return
    
    # 预定义的文档分类映射
    document_categories = {
        "变电站运维方案.pdf": {
            "category": "电力系统运维",
            "subcategory": "变电站"
        },
        "水电管理及维修服务方案.pdf": {
            "category": "电力系统运维", 
            "subcategory": "水电站"
        }
    }
    
    # 查找PDF文件
    pdf_files = list(documents_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("未找到PDF文件")
        return
    
    print(f"找到 {len(pdf_files)} 个PDF文件:")
    for pdf_file in pdf_files:
        print(f"  - {pdf_file.name}")
    
    print("\n开始导入...")
    
    success_count = 0
    total_count = len(pdf_files)
    
    for pdf_file in pdf_files:
        filename = pdf_file.name
        
        # 获取分类信息
        if filename in document_categories:
            category_info = document_categories[filename]
            category = category_info["category"]
            subcategory = category_info["subcategory"]
        else:
            # 默认分类
            category = "运维标准规范"
            subcategory = "技术标准"
            print(f"警告: {filename} 使用默认分类")
        
        # 导入文件
        if import_pdf_file(str(pdf_file), category, subcategory):
            success_count += 1
    
    print("\n" + "="*60)
    print(f"导入完成: {success_count}/{total_count} 个文件成功导入")
    print("="*60)
    
    if success_count > 0:
        print("\n现在可以使用以下命令测试知识库:")
        print("python -c \"from knowledge_mcp import search_knowledge; print(search_knowledge('变电站'))\"")

if __name__ == "__main__":
    main()