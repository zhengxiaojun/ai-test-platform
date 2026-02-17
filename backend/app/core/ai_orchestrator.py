"""AI Orchestrator - Core AI coordination layer"""
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from app.config import settings
from loguru import logger


class AIOrchestrator:
    """AI调度中心 - 负责协调所有AI相关操作"""

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_API_BASE
        )
        self.model = settings.OPENAI_MODEL
        self.temperature = settings.OPENAI_TEMPERATURE
        self.max_tokens = settings.OPENAI_MAX_TOKENS

    def _call_llm(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        json_mode: bool = False
    ) -> str:
        """调用LLM并返回响应"""
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature or self.temperature,
                "max_tokens": self.max_tokens
            }

            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}

            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM调用失败: {str(e)}")
            raise

    def analyze_interface(self, interface_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析接口，生成测试点"""
        prompt = self._build_interface_analysis_prompt(interface_data)

        messages = [
            {
                "role": "system",
                "content": "你是一个专业的API测试专家。你需要分析接口信息，生成全面的测试点列表。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        response = self._call_llm(messages, json_mode=True)
        return json.loads(response)

    def generate_test_case(
        self,
        test_point: Dict[str, Any],
        interface_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """根据测试点生成测试用例代码"""
        prompt = self._build_test_case_generation_prompt(test_point, interface_data)

        messages = [
            {
                "role": "system",
                "content": "你是一个专业的测试工程师。你需要根据测试点生成完整的pytest测试用例代码。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        response = self._call_llm(messages, json_mode=True)
        return json.loads(response)

    def analyze_test_report(
        self,
        execution_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """分析测试执行结果，生成智能报告"""
        prompt = self._build_report_analysis_prompt(execution_result)

        messages = [
            {
                "role": "system",
                "content": "你是一个专业的测试分析专家。你需要分析测试执行结果，提供深度洞察和优化建议。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        response = self._call_llm(messages, json_mode=True)
        return json.loads(response)

    def _build_interface_analysis_prompt(self, interface_data: Dict[str, Any]) -> str:
        """构建接口分析Prompt"""
        return f"""
请分析以下API接口信息，生成全面的测试点列表：

接口名称: {interface_data.get('name')}
URL: {interface_data.get('url')}
方法: {interface_data.get('method')}
请求参数: {json.dumps(interface_data.get('params', {}), ensure_ascii=False, indent=2)}
响应示例: {json.dumps(interface_data.get('response_example', {}), ensure_ascii=False, indent=2)}
描述: {interface_data.get('description', '无')}

请按以下JSON格式返回测试点：
{{
    "test_points": [
        {{
            "title": "测试点标题",
            "description": "详细描述",
            "category": "功能性/边界值/异常/安全",
            "risk_level": "low/medium/high/critical",
            "test_scenario": "具体测试场景描述"
        }}
    ],
    "risk_summary": "整体风险评估",
    "suggestions": ["建议1", "建议2"]
}}

要求：
1. 至少包含5种不同类型的测试点
2. 覆盖正常场景、边界值、异常情况、安全测试
3. 标注风险等级
4. 提供具体可执行的测试场景
"""

    def _build_test_case_generation_prompt(
        self,
        test_point: Dict[str, Any],
        interface_data: Dict[str, Any]
    ) -> str:
        """构建测试用例生成Prompt"""
        return f"""
请根据以下测试点生成完整的pytest测试用例代码：

测试点信息:
- 标题: {test_point.get('title')}
- 描述: {test_point.get('description')}
- 分类: {test_point.get('category')}
- 风险等级: {test_point.get('risk_level')}

接口信息:
- URL: {interface_data.get('url')}
- 方法: {interface_data.get('method')}
- 参数: {json.dumps(interface_data.get('params', {}), ensure_ascii=False, indent=2)}

请按以下JSON格式返回：
{{
    "test_case_name": "test_xxx",
    "description": "用例描述",
    "code": "完整的pytest代码",
    "test_data": {{
        "input": {{}},
        "expected": {{}}
    }},
    "dependencies": ["requests", "pytest"],
    "notes": "执行注意事项"
}}

代码要求：
1. 使用pytest框架
2. 包含完整的断言
3. 包含错误处理
4. 代码可直接执行
5. 使用requests库进行HTTP请求
6. 包含详细的注释
"""

    def _build_report_analysis_prompt(self, execution_result: Dict[str, Any]) -> str:
        """构建报告分析Prompt"""
        return f"""
请分析以下测试执行结果，生成深度分析报告：

执行结果:
{json.dumps(execution_result, ensure_ascii=False, indent=2)}

请按以下JSON格式返回分析结果：
{{
    "summary": "执行结果总结（200字内）",
    "key_findings": ["发现1", "发现2"],
    "risk_analysis": {{
        "high_risks": ["高风险问题"],
        "medium_risks": ["中风险问题"],
        "low_risks": ["低风险问题"]
    }},
    "optimization_suggestions": [
        {{
            "title": "优化建议标题",
            "description": "详细建议",
            "priority": "high/medium/low"
        }}
    ],
    "uncovered_scenarios": ["未覆盖的测试场景"],
    "next_steps": ["后续行动建议"]
}}

要求：
1. 分析要深入、专业
2. 风险评估要准确
3. 建议要可执行
4. 突出关键问题
"""


# 全局实例
ai_orchestrator = AIOrchestrator()

