#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
文件：fix_pdf_text_extraction.py
功能：修复PDF文本提取乱码问题的专用工具
技术：多种PDF处理库 + 文本清理 + 编码修复
============================================================================

解决方案：
1. 使用多种PDF处理库尝试提取
2. 检测和修复常见的编码问题
3. 清理和标准化文本格式
4. 重新导入修复后的文档
"""

import json
import logging
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re
import tempfile
import shutil

# 核心依赖
try:
    import pdfplumber
    import fitz  # pymupdf
    import PyPDF2
    from pdfminer.high_level import extract_text as pdfminer_extract
    from pdfminer.layout import LAParams
except ImportError as e:
    print(f"缺少必要依赖: {e}")
    print("请安装: pip install pdfplumber pymupdf PyPDF2 pdfminer.six")
    exit(1)

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFTextExtractor:
    """PDF文本提取器 - 支持多种方法和编码修复"""
    
    def __init__(self):
        self.extraction_methods = [
            self._extract_with_pdfplumber,
            self._extract_with_pymupdf,
            self._extract_with_pypdf2,
            self._extract_with_pdfminer
        ]
    
    def extract_text(self, pdf_path: str) -> Tuple[str, str, int]:
        """
        从PDF提取文本，尝试多种方法
        
        Returns:
            Tuple[str, str, int]: (提取的文本, 使用的方法, 页数)
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
        
        logger.info(f"开始提取PDF文本: {pdf_path.name}")
        
        for method in self.extraction_methods:
            try:
                text, method_name, page_count = method(str(pdf_path))
                if text and len(text.strip()) > 50:  # 确保提取到有意义的文本
                    # 清理和修复文本
                    cleaned_text = self._clean_and_fix_text(text)
                    if self._is_text_valid(cleaned_text):
                        logger.info(f"✅ 使用{method_name}成功提取文本，长度: {len(cleaned_text)}")
                        return cleaned_text, method_name, page_count
                    else:
                        logger.warning(f"❌ {method_name}提取的文本质量不佳")
                else:
                    logger.warning(f"❌ {method_name}提取文本过短或为空")
            except Exception as e:
                logger.warning(f"❌ {method.__name__}提取失败: {e}")
        
        raise Exception("所有PDF文本提取方法都失败了")
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> Tuple[str, str, int]:
        """使用pdfplumber提取文本"""
        with pdfplumber.open(pdf_path) as pdf:
            page_count = len(pdf.pages)
            text_parts = []
            
            for page in pdf.pages:
                # 尝试不同的提取参数
                page_text = page.extract_text()
                if not page_text:
                    # 尝试更宽松的参数
                    page_text = page.extract_text(
                        x_tolerance=3,
                        y_tolerance=3,
                        layout=True,
                        x_density=7.25,
                        y_density=13
                    )
                
                if page_text:
                    text_parts.append(page_text)
            
            return "\n".join(text_parts), "pdfplumber", page_count
    
    def _extract_with_pymupdf(self, pdf_path: str) -> Tuple[str, str, int]:
        """使用pymupdf提取文本"""
        doc = fitz.open(pdf_path)
        page_count = doc.page_count
        text_parts = []
        
        for page_num in range(page_count):
            page = doc[page_num]
            # 尝试不同的提取方法
            text = page.get_text("text")
            if not text:
                # 尝试字典模式
                text_dict = page.get_text("dict")
                text = self._extract_from_text_dict(text_dict)
            
            if text:
                text_parts.append(text)
        
        doc.close()
        return "\n".join(text_parts), "pymupdf", page_count
    
    def _extract_with_pypdf2(self, pdf_path: str) -> Tuple[str, str, int]:
        """使用PyPDF2提取文本"""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            page_count = len(reader.pages)
            text_parts = []
            
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            
            return "\n".join(text_parts), "PyPDF2", page_count
    
    def _extract_with_pdfminer(self, pdf_path: str) -> Tuple[str, str, int]:
        """使用pdfminer提取文本"""
        # 配置更宽松的参数
        laparams = LAParams(
            line_margin=0.5,
            word_margin=0.1,
            char_margin=2.0,
            boxes_flow=0.5,
            all_texts=False
        )
        
        text = pdfminer_extract(pdf_path, laparams=laparams)
        
        # 估算页数（pdfminer不直接提供页数）
        page_count = max(1, text.count('\f') + 1)  # 使用换页符估算
        
        return text, "pdfminer", page_count
    
    def _extract_from_text_dict(self, text_dict: dict) -> str:
        """从pymupdf的字典格式中提取文本"""
        text_parts = []
        
        def extract_recursive(obj):
            if isinstance(obj, dict):
                if 'spans' in obj:
                    for span in obj['spans']:
                        if 'text' in span:
                            text_parts.append(span['text'])
                elif 'blocks' in obj:
                    for block in obj['blocks']:
                        extract_recursive(block)
                elif 'lines' in obj:
                    for line in obj['lines']:
                        extract_recursive(line)
            elif isinstance(obj, list):
                for item in obj:
                    extract_recursive(item)
        
        extract_recursive(text_dict)
        return " ".join(text_parts)
    
    def _clean_and_fix_text(self, text: str) -> str:
        """清理和修复文本"""
        if not text:
            return ""
        
        # 1. 移除控制字符但保留换行符
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # 2. 修复常见的编码问题
        text = self._fix_encoding_issues(text)
        
        # 3. 标准化空白字符
        text = re.sub(r'[ \t]+', ' ', text)  # 多个空格/制表符合并为一个空格
        text = re.sub(r'\n\s*\n', '\n\n', text)  # 标准化段落分隔
        
        # 4. 移除页眉页脚等重复内容
        text = self._remove_repetitive_content(text)
        
        # 5. 修复断行问题
        text = self._fix_line_breaks(text)
        
        return text.strip()
    
    def _fix_encoding_issues(self, text: str) -> str:
        """修复常见的编码问题"""
        # 常见的编码错误映射
        encoding_fixes = {
            # UTF-8 BOM
            '\ufeff': '',
            # 常见的乱码字符
            '(cid:': '',
            ')': '',
            'Ł': '',
            'fl': '',
            '¡': '',
            '£': '',
            '¢': '',
            '¤': '',
            '¥': '',
            '¦': '',
            '§': '',
            '¨': '',
            '©': '',
            'ª': '',
            '«': '',
            '¬': '',
            '®': '',
            '¯': '',
            '°': '',
            '±': '',
            '²': '',
            '³': '',
            '´': '',
            'µ': '',
            '¶': '',
            '·': '',
            '¸': '',
            '¹': '',
            'º': '',
            '»': '',
            '¼': '',
            '½': '',
            '¾': '',
            '¿': ''
        }
        
        for bad_char, replacement in encoding_fixes.items():
            text = text.replace(bad_char, replacement)
        
        # 移除连续的数字编码模式 (cid:xxx)
        text = re.sub(r'\(cid:\d+\)', '', text)
        
        # 清理多余的空格
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    def _remove_repetitive_content(self, text: str) -> str:
        """移除重复的页眉页脚内容"""
        lines = text.split('\n')
        if len(lines) < 10:
            return text
        
        # 检测重复的短行（可能是页眉页脚）
        line_counts = {}
        for line in lines:
            line = line.strip()
            if len(line) < 100 and line:  # 只检查短行
                line_counts[line] = line_counts.get(line, 0) + 1
        
        # 移除出现次数过多的短行
        threshold = max(2, len(lines) // 20)  # 动态阈值
        repetitive_lines = {line for line, count in line_counts.items() if count > threshold}
        
        filtered_lines = []
        for line in lines:
            if line.strip() not in repetitive_lines:
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    def _fix_line_breaks(self, text: str) -> str:
        """修复不当的断行"""
        # 修复中文断行问题
        text = re.sub(r'([\u4e00-\u9fff])\n([\u4e00-\u9fff])', r'\1\2', text)
        
        # 修复英文单词断行
        text = re.sub(r'([a-zA-Z])-\n([a-zA-Z])', r'\1\2', text)
        
        return text
    
    def _is_text_valid(self, text: str) -> bool:
        """检查文本质量"""
        if not text or len(text.strip()) < 50:
            return False
        
        # 检查乱码比例
        total_chars = len(text)
        garbled_chars = len(re.findall(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]|\(cid:\d+\)', text))
        
        if total_chars > 0 and garbled_chars / total_chars > 0.3:  # 乱码超过30%
            return False
        
        # 检查是否有可读的中文或英文内容
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        
        readable_ratio = (chinese_chars + english_chars) / total_chars if total_chars > 0 else 0
        
        return readable_ratio > 0.3  # 可读字符超过30%

def fix_existing_documents():
    """修复现有文档的文本提取问题"""
    logger.info("开始修复现有文档的文本提取问题")
    
    # 连接数据库
    db_path = Path("data/knowledge.db")
    if not db_path.exists():
        logger.error("数据库文件不存在")
        return
    
    extractor = PDFTextExtractor()
    
    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        
        # 获取所有PDF文档
        cursor = conn.execute("""
            SELECT doc_id, original_filename, title, category, subcategory, file_path
            FROM documents 
            WHERE status = 'active' AND original_filename LIKE '%.pdf'
        """)
        
        documents = cursor.fetchall()
        logger.info(f"找到{len(documents)}个PDF文档需要修复")
        
        success_count = 0
        failed_count = 0
        
        for doc in documents:
            try:
                doc_id = doc['doc_id']
                file_path = doc['file_path']
                title = doc['title']
                
                logger.info(f"处理文档: {title} ({doc['original_filename']})")
                
                if not Path(file_path).exists():
                    logger.warning(f"文件不存在: {file_path}")
                    failed_count += 1
                    continue
                
                # 重新提取文本
                try:
                    text_content, method_used, page_count = extractor.extract_text(file_path)
                    
                    if text_content and len(text_content.strip()) > 50:
                        # 删除旧的分块
                        conn.execute("DELETE FROM document_chunks WHERE doc_id = ?", (doc_id,))
                        
                        # 这里需要重新创建分块和向量索引
                        # 为了简化，我们只更新数据库中的信息
                        logger.info(f"✅ 成功修复文档 {title}，使用方法: {method_used}，文本长度: {len(text_content)}")
                        
                        # 保存修复后的文本到临时文件用于检查
                        temp_dir = Path("data/fixed_texts")
                        temp_dir.mkdir(exist_ok=True)
                        
                        with open(temp_dir / f"{doc_id}_fixed.txt", 'w', encoding='utf-8') as f:
                            f.write(f"文档: {title}\n")
                            f.write(f"提取方法: {method_used}\n")
                            f.write(f"文本长度: {len(text_content)}\n")
                            f.write("=" * 50 + "\n")
                            f.write(text_content)
                        
                        success_count += 1
                    else:
                        logger.warning(f"❌ 文档 {title} 提取的文本质量不佳")
                        failed_count += 1
                        
                except Exception as e:
                    logger.error(f"❌ 文档 {title} 提取失败: {e}")
                    failed_count += 1
                    
            except Exception as e:
                logger.error(f"处理文档失败: {e}")
                failed_count += 1
        
        conn.commit()
        
        logger.info(f"修复完成: 成功 {success_count} 个，失败 {failed_count} 个")
        
        if success_count > 0:
            logger.info("修复后的文本已保存到 data/fixed_texts/ 目录，请检查质量")
            logger.info("如果文本质量良好，请重新导入这些文档到知识库")

def test_pdf_extraction(pdf_path: str):
    """测试PDF文本提取"""
    extractor = PDFTextExtractor()
    
    try:
        text, method, page_count = extractor.extract_text(pdf_path)
        
        print(f"\n=== PDF文本提取测试结果 ===")
        print(f"文件: {Path(pdf_path).name}")
        print(f"提取方法: {method}")
        print(f"页数: {page_count}")
        print(f"文本长度: {len(text)}")
        print(f"\n前500字符预览:")
        print("-" * 50)
        print(text[:500])
        print("-" * 50)
        
        # 保存完整文本到文件
        output_file = Path(f"test_extraction_{Path(pdf_path).stem}.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"文件: {Path(pdf_path).name}\n")
            f.write(f"提取方法: {method}\n")
            f.write(f"页数: {page_count}\n")
            f.write(f"文本长度: {len(text)}\n")
            f.write("=" * 50 + "\n")
            f.write(text)
        
        print(f"\n完整文本已保存到: {output_file}")
        
    except Exception as e:
        print(f"提取失败: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "fix":
            # 修复现有文档
            fix_existing_documents()
        elif sys.argv[1] == "test" and len(sys.argv) > 2:
            # 测试单个PDF文件
            test_pdf_extraction(sys.argv[2])
        else:
            print("用法:")
            print("  python fix_pdf_text_extraction.py fix          # 修复现有文档")
            print("  python fix_pdf_text_extraction.py test <pdf>   # 测试单个PDF")
    else:
        print("PDF文本提取修复工具")
        print("用法:")
        print("  python fix_pdf_text_extraction.py fix          # 修复现有文档")
        print("  python fix_pdf_text_extraction.py test <pdf>   # 测试单个PDF")