# ============================================================================
# 文件：utils.py
# 功能：前端工具函数库 - 提供格式化、导入导出等通用功能
# 技术：Python + Pandas + JSON
# ============================================================================

"""
工具函数模块：
- 提供数据格式化功能（货币、百分比等）
- 提供数据导入导出功能（Excel、JSON等）
- 提供数据验证功能
"""

import pandas as pd
import json
from typing import Dict, List, Any, Optional
from io import BytesIO
import base64

def format_currency(amount: float, currency: str = "¥") -> str:
    """
    格式化货币显示
    
    Args:
        amount: 金额
        currency: 货币符号，默认为人民币
    
    Returns:
        格式化后的货币字符串
    """
    if amount is None:
        return f"{currency}0.00"
    
    # 处理大数值的显示
    if abs(amount) >= 100000000:  # 1亿以上
        return f"{currency}{amount/100000000:.2f}亿"
    elif abs(amount) >= 10000:  # 1万以上
        return f"{currency}{amount/10000:.2f}万"
    else:
        return f"{currency}{amount:,.2f}"

def format_percentage(value: float, decimal_places: int = 2) -> str:
    """
    格式化百分比显示
    
    Args:
        value: 数值（0-1之间或0-100之间）
        decimal_places: 小数位数
    
    Returns:
        格式化后的百分比字符串
    """
    if value is None:
        return "0.00%"
    
    # 如果值在0-1之间，认为是小数形式
    if 0 <= value <= 1:
        percentage = value * 100
    else:
        percentage = value
    
    return f"{percentage:.{decimal_places}f}%"

def export_to_excel(data: pd.DataFrame, filename: str = "export.xlsx") -> BytesIO:
    """
    导出数据到Excel文件
    
    Args:
        data: 要导出的DataFrame
        filename: 文件名
    
    Returns:
        Excel文件的字节流
    """
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        data.to_excel(writer, index=False, sheet_name='数据')
    output.seek(0)
    return output

def export_to_json(data: Dict[str, Any], filename: str = "export.json") -> str:
    """
    导出数据到JSON格式
    
    Args:
        data: 要导出的数据字典
        filename: 文件名
    
    Returns:
        JSON字符串
    """
    return json.dumps(data, ensure_ascii=False, indent=2)

def import_from_excel(file_bytes: bytes, sheet_name: str = None) -> pd.DataFrame:
    """
    从Excel文件导入数据
    
    Args:
        file_bytes: Excel文件字节数据
        sheet_name: 工作表名称，默认为第一个工作表
    
    Returns:
        导入的DataFrame
    """
    try:
        df = pd.read_excel(BytesIO(file_bytes), sheet_name=sheet_name)
        return df
    except Exception as e:
        raise ValueError(f"Excel文件导入失败：{str(e)}")

def validate_project_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    验证项目数据的完整性和有效性
    
    Args:
        data: 项目数据字典
    
    Returns:
        验证结果字典，包含is_valid和errors字段
    """
    errors = []
    
    # 必填字段检查
    required_fields = ["project_name", "start_date", "budget"]
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"缺少必填字段：{field}")
    
    # 数据类型检查
    if "budget" in data:
        try:
            float(data["budget"])
        except (ValueError, TypeError):
            errors.append("预算必须是数字")
    
    # 日期格式检查
    if "start_date" in data:
        try:
            pd.to_datetime(data["start_date"])
        except:
            errors.append("开始日期格式不正确")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }

def create_download_link(data: bytes, filename: str, mime_type: str = "application/octet-stream") -> str:
    """
    创建文件下载链接
    
    Args:
        data: 文件字节数据
        filename: 文件名
        mime_type: MIME类型
    
    Returns:
        下载链接的HTML字符串
    """
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:{mime_type};base64,{b64}" download="{filename}">下载 {filename}</a>'
    return href

def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    安全获取字典值
    
    Args:
        data: 数据字典
        key: 键名
        default: 默认值
    
    Returns:
        字典值或默认值
    """
    return data.get(key, default) if data else default

def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    截断文本
    
    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 后缀
    
    Returns:
        截断后的文本
    """
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix