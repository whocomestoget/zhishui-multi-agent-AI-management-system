# ============================================================================
# 文件：1_frontend_dashboard/models.py
# 功能：数据模型和业务逻辑
# 技术：Pydantic数据模型
# ============================================================================

"""
四川智水AI智慧管理平台 - 数据模型

功能模块：
1. 项目数据模型
2. 财务数据模型
3. 运维数据模型
4. 用户数据模型
5. 系统配置模型
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime, date
from enum import Enum
from dataclasses import dataclass, field
from pydantic import BaseModel, Field, validator
import pandas as pd
import json

# ============================================================================
# 枚举类型定义
# ============================================================================

class ProjectStatus(str, Enum):
    """项目状态枚举"""
    PLANNING = "规划中"
    IN_PROGRESS = "进行中"
    TESTING = "测试中"
    COMPLETED = "已完成"
    SUSPENDED = "暂停"
    CANCELLED = "已取消"

class ProjectType(str, Enum):
    """项目类型枚举"""
    SMART_POWER = "智慧电厂"
    SMART_STATION = "智能电站"
    SMART_WATER = "智慧水利"
    DAM_MONITORING = "大坝监测"
    OTHER = "其他"

class IndustryType(str, Enum):
    """行业类型枚举"""
    POWER = "电力"
    WATER = "水利"
    ENERGY = "能源"
    INFRASTRUCTURE = "基础设施"

class ClientType(str, Enum):
    """客户类型枚举"""
    STATE_OWNED = "国企"
    CENTRAL_ENTERPRISE = "央企"
    PRIVATE = "民企"
    GOVERNMENT = "政府"

class AgentType(str, Enum):
    """智能体类型枚举"""
    FINANCIAL = "财务分析"
    OPERATION = "运维知识"
    COST = "成本核算"
    DECISION = "决策分析"
    EFFICIENCY = "效能管理"
    COORDINATOR = "协调中心"

class DataSource(str, Enum):
    """数据源类型枚举"""
    EXCEL = "Excel文件"
    DATABASE = "数据库"
    API = "API接口"
    MANUAL = "手动输入"

# ============================================================================
# 基础数据模型
# ============================================================================

class BaseDataModel(BaseModel):
    """基础数据模型类"""
    
    class Config:
        # 允许使用枚举值
        use_enum_values = True
        # 验证赋值
        validate_assignment = True
        # 允许额外字段
        extra = "allow"

class TimestampMixin(BaseModel):
    """时间戳混入类"""
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    def update_timestamp(self):
        """更新时间戳"""
        self.updated_at = datetime.now()
        
    class Config:
        # 允许使用枚举值
        use_enum_values = True
        # 验证赋值
        validate_assignment = True
        # 允许额外字段
        extra = "allow"

# ============================================================================
# 项目相关模型
# ============================================================================

class ProjectInfo(TimestampMixin):
    """项目信息模型"""
    
    # 基本信息
    project_id: str = Field(..., description="项目ID")
    project_name: str = Field(..., description="项目名称")
    project_type: ProjectType = Field(..., description="项目类型")
    project_status: ProjectStatus = Field(..., description="项目状态")
    
    # 客户信息
    client_name: str = Field(..., description="客户名称")
    client_type: ClientType = Field(..., description="客户类型")
    industry_type: IndustryType = Field(..., description="行业类型")
    
    # 时间信息
    start_date: date = Field(..., description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    planned_duration: int = Field(..., description="计划工期（天）")
    
    # 财务信息
    contract_amount: float = Field(..., description="合同金额（万元）")
    paid_amount: float = Field(0.0, description="已付金额（万元）")
    cost_budget: float = Field(..., description="成本预算（万元）")
    actual_cost: float = Field(0.0, description="实际成本（万元）")
    
    # 团队信息
    project_manager: str = Field(..., description="项目经理")
    team_size: int = Field(..., description="团队规模")
    
    # 描述信息
    description: Optional[str] = Field(None, description="项目描述")
    remarks: Optional[str] = Field(None, description="备注")
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        """验证结束日期"""
        if v and 'start_date' in values and v < values['start_date']:
            raise ValueError('结束日期不能早于开始日期')
        return v
    
    @validator('paid_amount')
    def validate_paid_amount(cls, v, values):
        """验证已付金额"""
        if v < 0:
            raise ValueError('已付金额不能为负数')
        if 'contract_amount' in values and v > values['contract_amount']:
            raise ValueError('已付金额不能超过合同金额')
        return v
    
    @property
    def remaining_amount(self) -> float:
        """剩余金额"""
        return self.contract_amount - self.paid_amount
    
    @property
    def payment_progress(self) -> float:
        """付款进度（百分比）"""
        if self.contract_amount == 0:
            return 0.0
        return (self.paid_amount / self.contract_amount) * 100
    
    @property
    def cost_progress(self) -> float:
        """成本进度（百分比）"""
        if self.cost_budget == 0:
            return 0.0
        return (self.actual_cost / self.cost_budget) * 100
    
    @property
    def profit_margin(self) -> float:
        """利润率（百分比）"""
        if self.contract_amount == 0:
            return 0.0
        profit = self.contract_amount - self.actual_cost
        return (profit / self.contract_amount) * 100

class ProjectMilestone(BaseDataModel):
    """项目里程碑模型"""
    
    milestone_id: str = Field(..., description="里程碑ID")
    project_id: str = Field(..., description="项目ID")
    milestone_name: str = Field(..., description="里程碑名称")
    planned_date: date = Field(..., description="计划日期")
    actual_date: Optional[date] = Field(None, description="实际日期")
    status: str = Field(..., description="状态")
    description: Optional[str] = Field(None, description="描述")

# ============================================================================
# 财务相关模型
# ============================================================================

class FinancialData(TimestampMixin):
    """财务数据模型"""
    
    # 基本信息
    record_id: str = Field(..., description="记录ID")
    project_id: Optional[str] = Field(None, description="项目ID")
    period: str = Field(..., description="期间（YYYY-MM）")
    
    # 收入数据
    revenue: float = Field(0.0, description="营业收入（万元）")
    other_income: float = Field(0.0, description="其他收入（万元）")
    total_income: float = Field(0.0, description="总收入（万元）")
    
    # 成本数据
    direct_cost: float = Field(0.0, description="直接成本（万元）")
    indirect_cost: float = Field(0.0, description="间接成本（万元）")
    total_cost: float = Field(0.0, description="总成本（万元）")
    
    # 费用数据
    sales_expense: float = Field(0.0, description="销售费用（万元）")
    admin_expense: float = Field(0.0, description="管理费用（万元）")
    rd_expense: float = Field(0.0, description="研发费用（万元）")
    finance_expense: float = Field(0.0, description="财务费用（万元）")
    
    # 利润数据
    gross_profit: float = Field(0.0, description="毛利润（万元）")
    operating_profit: float = Field(0.0, description="营业利润（万元）")
    net_profit: float = Field(0.0, description="净利润（万元）")
    
    # 比率数据
    gross_margin: float = Field(0.0, description="毛利率（%）")
    operating_margin: float = Field(0.0, description="营业利润率（%）")
    net_margin: float = Field(0.0, description="净利润率（%）")
    
    # 数据源
    data_source: DataSource = Field(DataSource.MANUAL, description="数据源")
    
    def calculate_derived_fields(self):
        """计算衍生字段"""
        # 计算总收入
        self.total_income = self.revenue + self.other_income
        
        # 计算毛利润
        self.gross_profit = self.revenue - self.total_cost
        
        # 计算营业利润
        total_expenses = self.sales_expense + self.admin_expense + self.rd_expense + self.finance_expense
        self.operating_profit = self.gross_profit - total_expenses
        
        # 计算净利润（简化，不考虑税费）
        self.net_profit = self.operating_profit
        
        # 计算比率
        if self.revenue > 0:
            self.gross_margin = (self.gross_profit / self.revenue) * 100
            self.operating_margin = (self.operating_profit / self.revenue) * 100
            self.net_margin = (self.net_profit / self.revenue) * 100
        
        self.update_timestamp()

class CashFlowData(BaseDataModel):
    """现金流数据模型"""
    
    record_id: str = Field(..., description="记录ID")
    project_id: Optional[str] = Field(None, description="项目ID")
    period: str = Field(..., description="期间（YYYY-MM）")
    
    # 经营活动现金流
    operating_cash_inflow: float = Field(0.0, description="经营活动现金流入")
    operating_cash_outflow: float = Field(0.0, description="经营活动现金流出")
    net_operating_cash_flow: float = Field(0.0, description="经营活动净现金流")
    
    # 投资活动现金流
    investing_cash_inflow: float = Field(0.0, description="投资活动现金流入")
    investing_cash_outflow: float = Field(0.0, description="投资活动现金流出")
    net_investing_cash_flow: float = Field(0.0, description="投资活动净现金流")
    
    # 筹资活动现金流
    financing_cash_inflow: float = Field(0.0, description="筹资活动现金流入")
    financing_cash_outflow: float = Field(0.0, description="筹资活动现金流出")
    net_financing_cash_flow: float = Field(0.0, description="筹资活动净现金流")
    
    # 总现金流
    net_cash_flow: float = Field(0.0, description="净现金流")
    
    def calculate_net_flows(self):
        """计算净现金流"""
        self.net_operating_cash_flow = self.operating_cash_inflow - self.operating_cash_outflow
        self.net_investing_cash_flow = self.investing_cash_inflow - self.investing_cash_outflow
        self.net_financing_cash_flow = self.financing_cash_inflow - self.financing_cash_outflow
        self.net_cash_flow = self.net_operating_cash_flow + self.net_investing_cash_flow + self.net_financing_cash_flow

# ============================================================================
# 运维相关模型
# ============================================================================

class OperationKnowledge(TimestampMixin):
    """运维知识模型"""
    
    knowledge_id: str = Field(..., description="知识ID")
    title: str = Field(..., description="标题")
    category: str = Field(..., description="分类")
    content: str = Field(..., description="内容")
    tags: List[str] = Field(default_factory=list, description="标签")
    
    # 关联信息
    project_type: Optional[ProjectType] = Field(None, description="项目类型")
    industry_type: Optional[IndustryType] = Field(None, description="行业类型")
    
    # 元数据
    author: str = Field(..., description="作者")
    difficulty_level: int = Field(1, description="难度等级（1-5）")
    view_count: int = Field(0, description="查看次数")
    like_count: int = Field(0, description="点赞次数")
    
    @validator('difficulty_level')
    def validate_difficulty_level(cls, v):
        """验证难度等级"""
        if not 1 <= v <= 5:
            raise ValueError('难度等级必须在1-5之间')
        return v

class OperationIssue(TimestampMixin):
    """运维问题模型"""
    
    issue_id: str = Field(..., description="问题ID")
    title: str = Field(..., description="问题标题")
    description: str = Field(..., description="问题描述")
    
    # 分类信息
    category: str = Field(..., description="问题分类")
    priority: str = Field(..., description="优先级")
    severity: str = Field(..., description="严重程度")
    
    # 状态信息
    status: str = Field("待处理", description="处理状态")
    assigned_to: Optional[str] = Field(None, description="分配给")
    
    # 解决信息
    solution: Optional[str] = Field(None, description="解决方案")
    resolved_at: Optional[datetime] = Field(None, description="解决时间")
    
    # 关联信息
    project_id: Optional[str] = Field(None, description="关联项目")
    knowledge_ids: List[str] = Field(default_factory=list, description="关联知识")

# ============================================================================
# 用户相关模型
# ============================================================================

class UserInfo(TimestampMixin):
    """用户信息模型"""
    
    user_id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    
    # 个人信息
    full_name: str = Field(..., description="姓名")
    department: str = Field(..., description="部门")
    position: str = Field(..., description="职位")
    
    # 权限信息
    role: str = Field("user", description="角色")
    permissions: List[str] = Field(default_factory=list, description="权限列表")
    
    # 状态信息
    is_active: bool = Field(True, description="是否激活")
    last_login: Optional[datetime] = Field(None, description="最后登录时间")

class UserSession(BaseDataModel):
    """用户会话模型"""
    
    session_id: str = Field(..., description="会话ID")
    user_id: str = Field(..., description="用户ID")
    login_time: datetime = Field(default_factory=datetime.now, description="登录时间")
    last_activity: datetime = Field(default_factory=datetime.now, description="最后活动时间")
    ip_address: Optional[str] = Field(None, description="IP地址")
    user_agent: Optional[str] = Field(None, description="用户代理")
    is_active: bool = Field(True, description="是否活跃")

# ============================================================================
# 智能体相关模型
# ============================================================================

class AgentRequest(BaseDataModel):
    """智能体请求模型"""
    
    request_id: str = Field(..., description="请求ID")
    agent_type: AgentType = Field(..., description="智能体类型")
    user_id: str = Field(..., description="用户ID")
    
    # 请求内容
    query: str = Field(..., description="查询内容")
    context: Dict[str, Any] = Field(default_factory=dict, description="上下文信息")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="参数")
    
    # 时间信息
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    
class AgentResponse(BaseDataModel):
    """智能体响应模型"""
    
    response_id: str = Field(..., description="响应ID")
    request_id: str = Field(..., description="请求ID")
    agent_type: AgentType = Field(..., description="智能体类型")
    
    # 响应内容
    result: Dict[str, Any] = Field(..., description="结果")
    confidence: float = Field(0.0, description="置信度")
    processing_time: float = Field(0.0, description="处理时间（秒）")
    
    # 状态信息
    status: str = Field("success", description="状态")
    error_message: Optional[str] = Field(None, description="错误信息")
    
    # 时间信息
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")

# ============================================================================
# 系统配置模型
# ============================================================================

class SystemConfig(BaseDataModel):
    """系统配置模型"""
    
    config_key: str = Field(..., description="配置键")
    config_value: Union[str, int, float, bool, Dict, List] = Field(..., description="配置值")
    config_type: str = Field(..., description="配置类型")
    description: Optional[str] = Field(None, description="描述")
    is_active: bool = Field(True, description="是否激活")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

class DataImportLog(BaseDataModel):
    """数据导入日志模型"""
    
    import_id: str = Field(..., description="导入ID")
    user_id: str = Field(..., description="用户ID")
    file_name: str = Field(..., description="文件名")
    file_size: int = Field(..., description="文件大小")
    
    # 导入信息
    data_type: str = Field(..., description="数据类型")
    total_records: int = Field(0, description="总记录数")
    success_records: int = Field(0, description="成功记录数")
    failed_records: int = Field(0, description="失败记录数")
    
    # 状态信息
    status: str = Field("processing", description="状态")
    error_details: Optional[List[str]] = Field(None, description="错误详情")
    
    # 时间信息
    started_at: datetime = Field(default_factory=datetime.now, description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")

# ============================================================================
# 数据转换工具
# ============================================================================

class DataConverter:
    """数据转换工具类"""
    
    @staticmethod
    def dataframe_to_projects(df: pd.DataFrame) -> List[ProjectInfo]:
        """DataFrame转换为项目信息列表"""
        projects = []
        
        for _, row in df.iterrows():
            try:
                project = ProjectInfo(
                    project_id=str(row.get('项目ID', '')),
                    project_name=str(row.get('项目名称', '')),
                    project_type=ProjectType(row.get('项目类型', ProjectType.OTHER)),
                    project_status=ProjectStatus(row.get('项目状态', ProjectStatus.PLANNING)),
                    client_name=str(row.get('客户名称', '')),
                    client_type=ClientType(row.get('客户类型', ClientType.PRIVATE)),
                    industry_type=IndustryType(row.get('行业类型', IndustryType.OTHER)),
                    start_date=pd.to_datetime(row.get('开始日期')).date(),
                    end_date=pd.to_datetime(row.get('结束日期')).date() if pd.notna(row.get('结束日期')) else None,
                    planned_duration=int(row.get('计划工期', 0)),
                    contract_amount=float(row.get('合同金额', 0)),
                    paid_amount=float(row.get('已付金额', 0)),
                    cost_budget=float(row.get('成本预算', 0)),
                    actual_cost=float(row.get('实际成本', 0)),
                    project_manager=str(row.get('项目经理', '')),
                    team_size=int(row.get('团队规模', 0)),
                    description=str(row.get('项目描述', '')) if pd.notna(row.get('项目描述')) else None,
                    remarks=str(row.get('备注', '')) if pd.notna(row.get('备注')) else None
                )
                projects.append(project)
            except Exception as e:
                print(f"转换项目数据失败: {e}")
                continue
        
        return projects
    
    @staticmethod
    def dataframe_to_financial(df: pd.DataFrame) -> List[FinancialData]:
        """DataFrame转换为财务数据列表"""
        financial_data = []
        
        for _, row in df.iterrows():
            try:
                data = FinancialData(
                    record_id=str(row.get('记录ID', '')),
                    project_id=str(row.get('项目ID', '')) if pd.notna(row.get('项目ID')) else None,
                    period=str(row.get('期间', '')),
                    revenue=float(row.get('营业收入', 0)),
                    other_income=float(row.get('其他收入', 0)),
                    direct_cost=float(row.get('直接成本', 0)),
                    indirect_cost=float(row.get('间接成本', 0)),
                    sales_expense=float(row.get('销售费用', 0)),
                    admin_expense=float(row.get('管理费用', 0)),
                    rd_expense=float(row.get('研发费用', 0)),
                    finance_expense=float(row.get('财务费用', 0)),
                    data_source=DataSource(row.get('数据源', DataSource.EXCEL))
                )
                
                # 计算衍生字段
                data.calculate_derived_fields()
                financial_data.append(data)
                
            except Exception as e:
                print(f"转换财务数据失败: {e}")
                continue
        
        return financial_data
    
    @staticmethod
    def projects_to_dataframe(projects: List[ProjectInfo]) -> pd.DataFrame:
        """项目信息列表转换为DataFrame"""
        data = []
        
        for project in projects:
            data.append({
                '项目ID': project.project_id,
                '项目名称': project.project_name,
                '项目类型': project.project_type,
                '项目状态': project.project_status,
                '客户名称': project.client_name,
                '客户类型': project.client_type,
                '行业类型': project.industry_type,
                '开始日期': project.start_date,
                '结束日期': project.end_date,
                '计划工期': project.planned_duration,
                '合同金额(万元)': project.contract_amount,
                '已付金额(万元)': project.paid_amount,
                '剩余金额(万元)': project.remaining_amount,
                '付款进度(%)': project.payment_progress,
                '成本预算(万元)': project.cost_budget,
                '实际成本(万元)': project.actual_cost,
                '成本进度(%)': project.cost_progress,
                '利润率(%)': project.profit_margin,
                '项目经理': project.project_manager,
                '团队规模': project.team_size,
                '项目描述': project.description,
                '备注': project.remarks,
                '创建时间': project.created_at,
                '更新时间': project.updated_at
            })
        
        return pd.DataFrame(data)
    
    @staticmethod
    def financial_to_dataframe(financial_data: List[FinancialData]) -> pd.DataFrame:
        """财务数据列表转换为DataFrame"""
        data = []
        
        for item in financial_data:
            data.append({
                '记录ID': item.record_id,
                '项目ID': item.project_id,
                '期间': item.period,
                '营业收入(万元)': item.revenue,
                '其他收入(万元)': item.other_income,
                '总收入(万元)': item.total_income,
                '直接成本(万元)': item.direct_cost,
                '间接成本(万元)': item.indirect_cost,
                '总成本(万元)': item.total_cost,
                '销售费用(万元)': item.sales_expense,
                '管理费用(万元)': item.admin_expense,
                '研发费用(万元)': item.rd_expense,
                '财务费用(万元)': item.finance_expense,
                '毛利润(万元)': item.gross_profit,
                '营业利润(万元)': item.operating_profit,
                '净利润(万元)': item.net_profit,
                '毛利率(%)': item.gross_margin,
                '营业利润率(%)': item.operating_margin,
                '净利润率(%)': item.net_margin,
                '数据源': item.data_source,
                '创建时间': item.created_at,
                '更新时间': item.updated_at
            })
        
        return pd.DataFrame(data)

# ============================================================================
# 测试函数
# ============================================================================

def test_models():
    """测试数据模型"""
    print("🧪 开始测试数据模型...")
    
    # 测试项目信息模型
    project = ProjectInfo(
        project_id="P001",
        project_name="智慧电厂监控系统",
        project_type=ProjectType.SMART_POWER,
        project_status=ProjectStatus.IN_PROGRESS,
        client_name="国家电网",
        client_type=ClientType.STATE_OWNED,
        industry_type=IndustryType.POWER,
        start_date=date(2024, 1, 1),
        planned_duration=180,
        contract_amount=500.0,
        paid_amount=200.0,
        cost_budget=400.0,
        actual_cost=150.0,
        project_manager="张三",
        team_size=8
    )
    
    print(f"✅ 项目信息模型测试通过: {project.project_name}")
    print(f"   付款进度: {project.payment_progress:.1f}%")
    print(f"   利润率: {project.profit_margin:.1f}%")
    
    # 测试财务数据模型
    financial = FinancialData(
        record_id="F001",
        period="2024-01",
        revenue=100.0,
        direct_cost=60.0,
        indirect_cost=20.0,
        sales_expense=5.0,
        admin_expense=8.0
    )
    
    financial.calculate_derived_fields()
    print(f"✅ 财务数据模型测试通过: 净利润率 {financial.net_margin:.1f}%")
    
    # 测试数据转换
    test_df = pd.DataFrame({
        '项目ID': ['P001'],
        '项目名称': ['测试项目'],
        '项目类型': ['智慧电厂'],
        '项目状态': ['进行中'],
        '客户名称': ['测试客户'],
        '客户类型': ['国企'],
        '行业类型': ['电力'],
        '开始日期': ['2024-01-01'],
        '计划工期': [180],
        '合同金额': [500.0],
        '已付金额': [200.0],
        '成本预算': [400.0],
        '实际成本': [150.0],
        '项目经理': ['张三'],
        '团队规模': [8]
    })
    
    projects = DataConverter.dataframe_to_projects(test_df)
    print(f"✅ 数据转换测试通过: 转换了 {len(projects)} 个项目")
    
    print("🎉 所有数据模型测试完成！")

if __name__ == "__main__":
    test_models()