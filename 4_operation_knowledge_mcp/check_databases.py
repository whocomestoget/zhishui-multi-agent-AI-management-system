#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库检查工具
检查所有可能的数据库文件内容
"""

import sqlite3
import os
from pathlib import Path

def check_database(db_path):
    """检查数据库内容"""
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return
    
    print(f"\n📊 检查数据库: {db_path}")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("📝 数据库中没有表")
            return
        
        print(f"📋 表列表: {[table[0] for table in tables]}")
        
        # 检查每个表的记录数
        for table in tables:
            table_name = table[0]
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  📊 {table_name}: {count} 条记录")
                
                # 如果有记录，显示前几条
                if count > 0 and count <= 5:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                    rows = cursor.fetchall()
                    print(f"    前3条记录:")
                    for i, row in enumerate(rows, 1):
                        print(f"      {i}. {row}")
                        
            except Exception as e:
                print(f"  ❌ 查询表 {table_name} 失败: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 连接数据库失败: {e}")

def main():
    """主函数"""
    print("🔍 智水运维知识库 - 数据库检查工具")
    print("=" * 60)
    
    # 检查所有可能的数据库文件
    databases = [
        "data/knowledge.db",
        "knowledge_base/metadata.db"
    ]
    
    for db_path in databases:
        check_database(db_path)
    
    print("\n✅ 检查完成")

if __name__ == "__main__":
    main()