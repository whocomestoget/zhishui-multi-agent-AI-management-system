#!/usr/bin/env python3
"""
智水信息Multi-Agent智能分析系统 - 知识管理专家
专注于电力水利行业知识检索、文档管理和最佳实践分享

核心能力：
1. 基于FAISS向量搜索的智能知识检索
2. 多格式文档智能导入和处理
3. 知识库生命周期管理和维护

Author: 商海星辰队
Version: 1.0.0
"""

import json
import logging
import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from .business_agent import BusinessAgent, AgentTask, AgentResult

# ================================
# 1. KnowledgeAgent类
# ================================

class KnowledgeAgent(BusinessAgent):
    """知识管理专家Agent"""
    
    def __init__(self):
        """初始化知识管理专家"""
        super().__init__(
            agent_id="knowledge_manager",
            agent_name="知识管理专家",
            mcp_service="knowledge"
        )
        
        # 知识管理专业配置
        self.analysis_types = {
            "knowledge_search": "知识检索查询",
            "document_import": "文档导入管理",
            "knowledge_consultation": "专业知识咨询",
            "best_practices_analysis": "最佳实践分析"
        }
        
        # 知识分类体系
        self.knowledge_categories = {
            "电力系统运维": ["水电站", "火电站", "新能源站", "变电站", "配电系统", "发电机组"],
            "水利系统运维": ["大坝监测", "水库管理", "灌区系统", "水文监测", "闸门控制", "泵站设备"],
            "通信网络运维": ["通信设备", "网络系统", "数据传输", "无线通信", "光纤网络", "网络安全"],
            "安防系统运维": ["视频监控", "门禁系统", "报警系统", "周界防护", "安全检测", "消防系统"],
            "运维标准规范": ["操作流程", "安全规范", "维护标准", "应急预案", "质量管理", "技术标准"]
        }
        
        self.logger.info("知识管理专家初始化完成")

    def get_system_prompt(self) -> str:
        """获取知识管理专家的系统提示词"""
        return """你是智水信息技术有限公司的资深知识管理专家，拥有10年以上电力水利行业信息化运维和知识管理经验。

## 🎯 专业定位与职责
你是企业知识资产的守护者和智能导航员，专精于：
- **智能知识检索**：基于FAISS向量数据库的语义搜索，快速定位相关技术文档和解决方案
- **文档资产管理**：多格式文档智能导入、分类管理和生命周期维护
- **最佳实践萃取**：从海量运维经验中提炼可复制的最佳实践和操作规范
- **专业知识咨询**：提供电力、水利、通信、安防等领域的专业技术答疑服务

## 🏢 行业知识体系深度构建

### 电力系统运维知识域
**水电站运维管理**：
- **发电设备管理**：水轮机、发电机、变压器的运行监控和维护保养
- **水工建筑物维护**：大坝、厂房、引水系统的安全检查和维修
- **自动化系统管理**：监控系统、保护系统、通信系统的运维标准
- **应急管理体系**：洪水调度、设备故障、安全事故的应急处置

**火电站运维管理**：
- **主设备运维**：锅炉、汽轮机、发电机的运行参数监控和维护策略
- **辅助系统管理**：给水、燃料、除灰、脱硫脱硝系统的运维要点
- **环保设施运维**：排放监测、污染治理设施的运行管理
- **燃料管理**：煤炭采购、储存、燃烧优化的管理规范

### 水利系统运维知识域
**水库大坝管理**：
- **安全监测**：坝体变形、渗流、应力应变的监测技术和数据分析
- **调度运行**：防洪调度、发电调度、生态调度的决策规则和操作规程
- **设备维护**：闸门、启闭机、监测设备的维护保养标准
- **应急管理**：超标洪水、大坝险情、设备故障的应急预案

**灌区系统管理**：
- **渠道维护**：渠道清淤、护坡修复、水草清理的技术标准
- **计量监测**：流量计量、水质监测、用水管理的技术方案
- **自动化控制**：闸门自动化、泵站自动化、远程监控系统运维
- **节水技术**：滴灌、喷灌、智能灌溉系统的运行管理

### 通信网络运维知识域
**有线通信系统**：
- **光纤网络**：光缆敷设、熔接技术、OTDR测试、故障定位与修复
- **以太网交换**：交换机配置、VLAN划分、网络优化、故障排除
- **电力载波通信**：载波设备安装调试、信道测试、通信质量优化
- **网络安全**：防火墙配置、入侵检测、安全审计、漏洞管理

**无线通信系统**：
- **微波通信**：微波设备调试、天线对星、信号质量优化
- **卫星通信**：卫星链路建立、信号传输优化、备用链路管理
- **移动通信**：基站维护、信号覆盖优化、干扰排查
- **应急通信**：便携式通信设备、应急通信预案、通信保障

### 安防系统运维知识域
**视频监控系统**：
- **摄像头管理**：设备选型、安装调试、图像质量优化、故障维修
- **存储系统**：录像存储、数据备份、存储容量规划、数据恢复
- **网络传输**：视频编码、网络带宽、传输质量、延时优化
- **智能分析**：行为分析、目标识别、报警联动、误报处理

**门禁控制系统**：
- **读卡设备**：读卡器安装、权限配置、设备维护、故障处理
- **控制器管理**：门禁控制器配置、通信链路、数据同步
- **权限管理**：人员权限、时间权限、区域权限、临时权限
- **安全审计**：出入记录、异常报警、权限变更、系统日志

## 核心知识服务工具箱

### 1. 智能知识检索引擎 (search_knowledge)
**技术特色**：
- **FAISS向量数据库**：基于深度学习的语义相似度搜索，理解查询意图
- **Qwen3嵌入模型**：2560维高精度文本向量化，支持中文语义理解
- **多维度检索**：支持关键词、语义、分类、时间等多维度综合检索
- **智能排序**：基于相关性、权威性、时效性的智能排序算法

**检索策略**：
- **精确匹配**：技术规范、操作步骤、设备型号等需要精确匹配的查询
- **语义检索**：故障现象、问题描述、经验分享等需要语义理解的查询
- **关联推荐**：基于用户查询历史和知识图谱的相关内容推荐
- **实时更新**：知识库内容实时更新，确保信息的时效性和准确性

**应用场景**：
- **故障诊断**：根据故障现象快速查找诊断方法和解决方案
- **技术咨询**：专业技术问题的权威答案和参考资料
- **规范查询**：操作规程、技术标准、安全规范的快速检索
- **经验分享**：最佳实践、经验教训、创新方案的知识发现

### 2. 文档智能管理系统 (import_file_to_knowledge & manage_documents)
**支持格式**：
- **PDF文档**：技术手册、设计图纸、检测报告、研究论文
- **Word文档**：操作规程、管理制度、工作总结、技术方案
- **Excel表格**：设备清单、检测数据、统计报表、参数配置
- **图片文件**：设备照片、现场图像、电路图、结构图

**智能处理能力**：
- **自动分类**：基于内容特征自动识别文档类别和归属领域
- **关键信息提取**：设备型号、技术参数、操作步骤、安全注意事项
- **版本管理**：文档版本控制、变更跟踪、历史版本查询
- **权限控制**：基于角色的访问控制，确保信息安全

**生命周期管理**：
- **导入处理**：文档格式转换、内容解析、质量检查、索引建立
- **存储优化**：分布式存储、数据压缩、备份恢复、性能优化
- **更新维护**：内容更新、失效清理、质量评估、用户反馈
- **统计分析**：使用统计、热点分析、用户行为、知识地图

### 3. 最佳实践知识萃取
**实践来源**：
- **运维经验**：一线运维人员的实际操作经验和故障处理案例
- **技术创新**：新技术应用、工艺改进、设备优化的成功实践
- **管理创新**：管理流程优化、组织架构调整、绩效提升方案
- **安全管理**：安全事故预防、应急处置、风险管控的成功经验

**萃取方法**：
- **案例分析法**：从具体案例中提炼可复制的操作方法和管理经验
- **对比分析法**：通过横向对比发现最优实践和改进机会
- **根因分析法**：深入分析成功要素，建立最佳实践的理论基础
- **专家访谈法**：通过专家知识挖掘，获取隐性知识和经验技巧

## 💼 知识服务方法论

### 知识检索优化策略
1. **查询理解**：分析用户查询意图，识别关键信息和隐含需求
2. **检索策略**：根据查询类型选择最优检索算法和参数配置
3. **结果过滤**：基于权威性、时效性、相关性过滤检索结果
4. **结果排序**：综合多个维度对检索结果进行智能排序
5. **结果展示**：结构化展示检索结果，突出关键信息

### 知识质量保障体系
**内容质量控制**：
- **来源权威性**：确保知识来源的专业性和可靠性
- **内容准确性**：通过专家审核确保技术内容的准确性
- **信息时效性**：定期更新过时信息，保持知识库的时效性
- **结构完整性**：确保知识结构的逻辑性和完整性

**用户反馈机制**：
- **满意度评价**：用户对检索结果的满意度评价和改进建议
- **内容纠错**：用户发现错误信息的反馈和纠正机制
- **需求收集**：收集用户的知识需求，指导知识库建设方向
- **使用分析**：分析用户使用行为，优化知识服务体验

### 知识共享与传承机制
**显性知识管理**：
- **文档标准化**：建立统一的文档格式和编写规范
- **分类体系**：构建科学合理的知识分类和标签体系
- **检索优化**：持续优化检索算法，提升查询效率和准确性
- **版本控制**：建立严格的版本管理制度，确保信息一致性

**隐性知识挖掘**：
- **专家访谈**：定期开展专家访谈，挖掘经验性知识
- **案例收集**：系统收集成功案例和失败教训，形成案例库
- **社区建设**：建立知识分享社区，促进经验交流和传承
- **培训体系**：将最佳实践融入培训体系，实现知识传承

## 🎯 服务输出标准

### 知识检索服务标准
1. **检索响应时间**：平均响应时间<2秒，95%查询<5秒
2. **检索准确率**：前3个结果的相关性>90%，前10个结果>80%
3. **内容覆盖率**：主要技术领域知识覆盖率>95%
4. **用户满意度**：知识检索服务满意度>4.5分（5分制）

### 知识质量评估标准
- **准确性**：技术内容准确率>98%，定期专家审核验证
- **完整性**：核心知识点覆盖率>90%，关键信息完整率>95%
- **时效性**：知识更新周期<30天，过时信息清理率>99%
- **可用性**：知识应用成功率>85%，用户问题解决率>80%

### 文档管理服务标准
- **处理效率**：单个文档导入处理时间<5分钟
- **格式支持**：支持主流文档格式，转换成功率>98%
- **存储安全**：数据备份完整性100%，恢复时间<1小时
- **访问性能**：文档下载速度>10MB/s，并发访问支持>100用户

## 🤝 协作策略与集成

### 与其他专业Agent协作
**财务分析专家协作**：
- 提供行业财务标准、投资政策、成本控制最佳实践
- 支持财务分析模型的理论依据和参数标准查询
- 分享同行业财务管理成功案例和经验教训

**成本预测专家协作**：
- 提供工程造价标准、设备价格信息、技术规范要求
- 支持成本预测模型的技术参数和行业标准查询
- 分享类似项目的成本控制经验和风险防范措施

**效能评估专家协作**：
- 提供人员管理制度、绩效评估标准、组织优化案例
- 支持效能评估指标的理论基础和计算方法查询
- 分享人力资源管理最佳实践和团队建设经验

### 用户服务优化策略
**个性化服务**：
- **用户画像**：基于使用历史建立用户知识需求画像
- **推荐系统**：智能推荐相关知识和潜在感兴趣内容
- **订阅服务**：知识更新提醒、专题知识推送服务
- **学习路径**：为不同用户设计个性化的知识学习路径

**交互体验优化**：
- **自然语言查询**：支持自然语言描述的复杂查询
- **多媒体展示**：图文并茂的知识展示，提升理解效果
- **移动端适配**：支持移动设备的知识查询和浏览
- **语音交互**：支持语音查询和语音播报功能

你现在开始运用以上专业知识和服务能力，为智水信息的客户提供高质量的知识管理服务。始终保持检索的精准性、知识的权威性和服务的便民性，确保每一次知识服务都能为用户解决实际问题，提升工作效率。"""

    def get_required_fields(self) -> List[str]:
        """获取知识管理必需的字段"""
        return ["analysis_type"]  # 基础必需字段，具体字段根据分析类型动态确定

    def validate_input_data(self, task: AgentTask) -> tuple[bool, List[str]]:
        """验证知识管理输入数据"""
        errors = []
        data = task.input_data
        
        # 兼容处理：从input_data字段或直接从data获取业务数据
        business_data = data.get("input_data", data)
        
        # 检查分析类型
        analysis_type = business_data.get("analysis_type")
        if not analysis_type:
            errors.append("缺少分析类型(analysis_type)")
            return False, errors
            
        if analysis_type not in self.analysis_types:
            errors.append(f"不支持的分析类型: {analysis_type}")
            return False, errors
        
        # 根据分析类型检查特定字段
        if analysis_type == "knowledge_search":
            if "query" not in business_data or not business_data["query"]:
                errors.append("知识检索需要查询内容(query)")
        
        elif analysis_type == "document_import":
            if "document_path" not in business_data and "document_content" not in business_data:
                errors.append("文档导入需要文档路径(document_path)或文档内容(document_content)")
        
        elif analysis_type == "knowledge_consultation":
            if "question" not in business_data or not business_data["question"]:
                errors.append("知识咨询需要问题内容(question)")
        
        return len(errors) == 0, errors

    def perform_analysis(self, data: Dict[str, Any], task: AgentTask) -> Dict[str, Any]:
        """执行知识管理分析 - 专注于MCP服务调用"""
        # 数据结构：data包含input_data字段，input_data包含实际的业务数据
        input_data = data.get("input_data", data)  # 兼容处理
        analysis_type = input_data.get("analysis_type")
        
        self.logger.info(f"开始知识管理分析，类型: {analysis_type}")
        self.logger.debug(f"输入数据结构: {list(data.keys())}")
        self.logger.debug(f"业务数据结构: {list(input_data.keys())}")
        
        try:
            # 调用对应的分析方法
            if analysis_type == "knowledge_search":
                result = self._perform_knowledge_search(input_data)
            elif analysis_type == "document_import":
                result = self._perform_document_import(input_data)
            elif analysis_type == "knowledge_consultation":
                result = self._perform_knowledge_consultation(input_data)
            elif analysis_type == "best_practices_analysis":
                result = self._perform_best_practices_analysis(input_data)
            else:
                raise ValueError(f"未实现的分析类型: {analysis_type}")
            
            if "error" in result:
                return result
            
            # 添加通用字段
            result.update({
                "status": "completed",
                "data_quality": "good" if result.get("mcp_result") else "limited"
            })
            
            return result
                
        except Exception as e:
            self.logger.error(f"知识管理分析执行失败: {e}")
            return {"error": f"分析执行失败: {str(e)}"}
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        import time
        return time.strftime('%Y-%m-%d %H:%M:%S')
    
    def _call_mcp_for_search(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """调用MCP服务进行知识检索"""
        query = data["query"]
        category = data.get("category", "")
        top_k = data.get("top_k", 10)
        
        return self.call_mcp_tool(
            "search_knowledge",
            arguments={
                "query": query,
                "category": category,
                "top_k": top_k
            }
        )
    
    def _call_mcp_for_import(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """调用MCP服务进行文档导入"""
        document_path = data.get("document_path", "")
        document_content = data.get("document_content", "")
        document_title = data.get("document_title", "未命名文档")
        category = data.get("category", "")
        
        if document_path:
            return self.call_mcp_tool(
                "import_file_to_knowledge",
                arguments={
                    "file_path": document_path,
                    "title": document_title,
                    "category": category
                }
            )
        else:
            # 知识库MCP服务不支持直接导入文本内容
            # 需要先将文本保存为临时文件再导入
            if not self.mcp_client:
                raise Exception("MCP客户端不可用")
            
            # 创建临时文件
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(document_content)
                temp_file_path = f.name
            
            try:
                result = self.call_mcp_tool(
                    "import_file_to_knowledge",
                    arguments={
                        "file_path": temp_file_path,
                        "title": document_title,
                        "category": category
                    }
                )
                return result
            finally:
                # 清理临时文件
                os.unlink(temp_file_path)
    
    def _call_mcp_for_consultation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """调用MCP服务进行知识咨询"""
        question = data["question"]
        context = data.get("context", "")
        
        return self.call_mcp_tool(
            "search_knowledge",
            arguments={
                "query": question,
                "category": context,
                "top_k": 5
            }
        )
    
    def _call_mcp_for_practices(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """调用MCP服务进行最佳实践分析"""
        topic = data["topic"]
        domain = data.get("domain", "")
        
        return self.call_mcp_tool(
            "search_knowledge",
            arguments={
                "query": f"最佳实践 {topic}",
                "category": domain,
                "top_k": 8
            }
        )
    
    # 已删除复杂的LLM分析方法，专注于MCP服务调用
    
    def _generate_search_recommendations(self, mcp_result: Dict[str, Any], query: str) -> List[str]:
        """基于MCP结果和查询生成搜索建议"""
        recommendations = []
        
        try:
            # 基于查询内容生成建议
            if "故障" in query:
                recommendations.append("建议查看相关设备的历史故障记录")
                recommendations.append("检查设备维护手册中的故障排除章节")
            elif "监测" in query:
                recommendations.append("建议查看监测系统的技术规范")
                recommendations.append("参考相关行业标准和最佳实践")
            elif "安全" in query:
                recommendations.append("建议查看安全管理制度和应急预案")
                recommendations.append("参考相关安全技术标准")
            else:
                recommendations.append("建议扩展搜索关键词")
                recommendations.append("可以尝试搜索相关的技术文档")
            
            # 基于MCP结果添加建议
            if mcp_result and "documents" in mcp_result:
                doc_count = len(mcp_result.get("documents", []))
                if doc_count > 0:
                    recommendations.append(f"找到{doc_count}个相关文档，建议详细阅读")
                else:
                    recommendations.append("未找到直接相关文档，建议调整搜索策略")
            
        except Exception as e:
            self.logger.warning(f"生成搜索建议时出错: {e}")
            recommendations = ["建议联系技术专家获取更多帮助"]
        
        return recommendations[:3]  # 最多返回3个建议

    def _perform_knowledge_search(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """执行知识检索"""
        query = data["query"]
        category = data.get("category", "")
        top_k = data.get("top_k", 10)
        
        # 调用MCP服务进行知识检索
        mcp_result = self.call_mcp_tool(
            "search_knowledge",
            query=query,
            category=category,
            top_k=top_k
        )
        
        if "error" in mcp_result:
            return mcp_result
        
        # 简化的分析结果 - 直接返回MCP结果和基本信息
        enhanced_result = {
            "analysis_type": "知识检索查询",
            "search_params": {
                "query": query,
                "category": category,
                "top_k": top_k
            },
            "mcp_result": mcp_result,
            "recommendations": self._generate_search_recommendations(mcp_result, query),
            "timestamp": self._get_timestamp()
        }
        
        return enhanced_result

    def _perform_document_import(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """执行文档导入"""
        document_path = data.get("document_path", "")
        document_content = data.get("document_content", "")
        document_title = data.get("document_title", "未命名文档")
        category = data.get("category", "")
        
        # 调用MCP服务进行文档导入
        if document_path:
            # 直接使用文件路径
            mcp_result = self.call_mcp_tool(
                "import_file_to_knowledge",
                file_path=document_path,
                title=document_title,
                category=category
            )
        elif document_content:
            # 当只有内容时，创建临时文件
            import tempfile
            import os
            
            try:
                # 创建临时文件
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
                    temp_file.write(document_content)
                    temp_file_path = temp_file.name
                
                # 使用临时文件路径调用MCP工具
                mcp_result = self.call_mcp_tool(
                    "import_file_to_knowledge",
                    file_path=temp_file_path,
                    title=document_title,
                    category=category
                )
                
                # 清理临时文件
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                    
            except Exception as e:
                mcp_result = {"error": f"创建临时文件失败: {str(e)}"}
        else:
            mcp_result = {"error": "必须提供文档路径或文档内容"}
        
        return {
            "analysis_type": "文档导入管理",
            "import_params": {
                "document_title": document_title,
                "category": category,
                "has_file_path": bool(document_path),
                "has_content": bool(document_content)
            },
            "mcp_result": mcp_result,
            "timestamp": self._get_timestamp()
        }

    def _perform_knowledge_consultation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """执行知识咨询"""
        question = data["question"]
        domain = data.get("domain", "")
        
        # 首先进行知识检索
        search_result = self._perform_knowledge_search({
            "query": question,
            "category": domain,
            "top_k": 5
        })
        
        return {
            "analysis_type": "专业知识咨询",
            "consultation_params": {
                "question": question,
                "domain": domain
            },
            "knowledge_search": search_result,
            "timestamp": self._get_timestamp()
        }

    def _perform_best_practices_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """执行最佳实践分析"""
        topic = data.get("topic", "")
        domain = data.get("domain", "")
        
        # 搜索相关最佳实践
        search_result = self._perform_knowledge_search({
            "query": f"{topic} 最佳实践 经验分享",
            "category": domain,
            "top_k": 10
        })
        
        return {
            "analysis_type": "最佳实践分析",
            "analysis_params": {
                "topic": topic,
                "domain": domain
            },
            "practices_search": search_result,
            "timestamp": self._get_timestamp()
        }

    # ================================
    # MCP服务调用方法
    # ================================

    def calculate_confidence_score(self, result: Dict[str, Any]) -> float:
        """基于实际数据计算知识管理置信度"""
        confidence_factors = []
        
        # 检查MCP服务结果质量
        if "mcp_result" in result:
            mcp_result = result["mcp_result"]
            if "error" not in mcp_result:
                confidence_factors.append(0.4)  # MCP服务成功
                
                # 根据检索结果数量调整
                if "results_count" in mcp_result:
                    count = mcp_result.get("results_count", 0)
                    if count > 0:
                        confidence_factors.append(min(count * 0.05, 0.2))  # 最多0.2
                        
                # 根据检索质量调整
                if "search_quality" in mcp_result:
                    quality = mcp_result.get("search_quality", 0)
                    confidence_factors.append(quality * 0.2)
        
        # 检查LLM分析质量
        if "knowledge_insights" in result and "error" not in result["knowledge_insights"]:
            confidence_factors.append(0.2)  # 知识洞察生成成功
            
        if "related_topics" in result and "error" not in result["related_topics"]:
            confidence_factors.append(0.1)  # 主题推荐生成成功
            
        if "llm_analysis" in result and "error" not in result["llm_analysis"]:
            confidence_factors.append(0.1)  # 综合分析生成成功
        
        # 计算最终置信度
        if confidence_factors:
            final_confidence = sum(confidence_factors)
            return min(final_confidence, 1.0)
        else:
            # 如果没有任何有效数据，置信度为0
            return 0.0

    def generate_recommendations(self, result: Dict[str, Any]) -> List[str]:
        """基于LLM分析生成知识管理建议"""
        try:
            # 使用LLM生成专业的知识管理建议
            prompt = f"""
            基于以下知识管理分析结果，请生成3-5条具体的知识管理建议：
            
            分析结果：{json.dumps(result, ensure_ascii=False, indent=2)}
            
            请提供：
            1. 知识检索优化建议
            2. 知识应用指导建议
            3. 知识库建设建议
            4. 知识共享推广建议
            5. 专业能力提升建议
            
            每条建议要具体、可操作，针对智水信息的知识管理需求。
            """
            
            response = self.call_llm(prompt)
            
            # 解析建议列表
            recommendations = []
            for line in response.split('\n'):
                line = line.strip()
                if line and (line.startswith(('1.', '2.', '3.', '4.', '5.', '-', '•')) or len(line) > 10):
                    # 清理编号和符号
                    clean_line = re.sub(r'^[0-9]+\.\s*', '', line)
                    clean_line = re.sub(r'^[-•]\s*', '', clean_line)
                    if clean_line:
                        recommendations.append(clean_line)
            
            return recommendations if recommendations else ["基于当前分析结果，建议优化知识管理策略"]
            
        except Exception as e:
            self.logger.error(f"生成知识管理建议失败: {e}")
            return ["建议基于分析结果制定知识管理策略"]
    
    # 已删除默认分析结果生成方法，专注于MCP服务调用
