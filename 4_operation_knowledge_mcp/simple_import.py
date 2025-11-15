#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的文档导入工具
直接使用MCP接口导入文档，避免复杂的内部调用
"""

import base64
import json
from pathlib import Path

def read_pdf_as_base64(file_path: str) -> str:
    """读取PDF文件并转换为base64编码"""
    with open(file_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

def create_import_data():
    """创建导入数据"""
    documents_dir = Path("knowledge_base/documents")
    
    # 文档映射
    docs = [
        {
            "file": "变电站运维方案.pdf",
            "title": "变电站运维标准操作方案",
            "category": "电力系统运维",
            "subcategory": "变电站"
        },
        {
            "file": "水电管理及维修服务方案.pdf", 
            "title": "水电站管理及维修服务标准方案",
            "category": "电力系统运维",
            "subcategory": "水电站"
        }
    ]
    
    import_commands = []
    
    for doc in docs:
        file_path = documents_dir / doc["file"]
        if file_path.exists():
            try:
                file_content = read_pdf_as_base64(str(file_path))
                
                # 创建MCP调用命令
                mcp_call = {
                    "server_name": "mcp.config.usrlocalmcp.zhishui-knowledge",
                    "tool_name": "import_document",
                    "args": {
                        "file_content": file_content,
                        "filename": doc["file"],
                        "title": doc["title"],
                        "category": doc["category"],
                        "subcategory": doc["subcategory"]
                    }
                }
                
                import_commands.append({
                    "document": doc["title"],
                    "mcp_call": mcp_call
                })
                
                print(f"准备导入: {doc['title']}")
                
            except Exception as e:
                print(f"处理文件失败 {doc['file']}: {e}")
        else:
            print(f"文件不存在: {file_path}")
    
    return import_commands

def main():
    print("="*60)
    print("四川智水运维知识库 - 简化导入工具")
    print("="*60)
    
    commands = create_import_data()
    
    print(f"\n生成了 {len(commands)} 个导入命令")
    print("\n请在Trae AI中逐个执行以下MCP调用:\n")
    
    for i, cmd in enumerate(commands, 1):
        print(f"=== 文档 {i}: {cmd['document']} ===")
        print("MCP调用参数:")
        print(json.dumps(cmd['mcp_call'], ensure_ascii=False, indent=2))
        print()
    
    print("\n导入完成后，可以使用以下命令测试:")
    print("MCP调用: search_knowledge")
    print("参数: {\"query\": \"变电站\", \"top_k\": 3}")

if __name__ == "__main__":
    main()