"""AI Orchestrator - Core AI coordination layer"""
import json
import re
from typing import List, Dict, Any, Optional, Union
from openai import OpenAI
from app.config import settings
from loguru import logger


class AIOrchestrator:
    """AI调度中心 - 负责协调所有AI相关操作，支持多种LLM提供商"""

    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.LLM_MAX_TOKENS
        self.client: Any = None  # 可以是OpenAI或Gemini客户端

        # 初始化对应的LLM客户端
        if self.provider == "openai":
            self._init_openai()
        elif self.provider == "gemini":
            self._init_gemini()
        elif self.provider in ["local", "custom"]:
            self._init_local()
        else:
            logger.warning(f"未知的LLM提供商: {self.provider}，默认使用OpenAI")
            self._init_openai()

    def _init_openai(self):
        """初始化OpenAI客户端"""
        api_key = settings.LLM_API_KEY or settings.OPENAI_API_KEY
        api_base = settings.LLM_API_BASE or settings.OPENAI_API_BASE
        self.model = settings.LLM_MODEL or settings.OPENAI_MODEL

        if not api_key:
            logger.warning("OpenAI API Key未配置")

        self.client = OpenAI(
            api_key=api_key,
            base_url=api_base
        )
        logger.info(f"OpenAI客户端初始化完成 - Model: {self.model}, Base: {api_base}")

    def _init_gemini(self):
        """初始化Google Gemini客户端"""
        try:
            # 优先使用新的 google.genai 包
            try:
                from google import genai
                use_new_sdk = True
            except ImportError:
                # 回退到旧的 google.generativeai 包
                import google.generativeai as genai
                use_new_sdk = False
                logger.warning("建议升级到新的 google-genai SDK: pip install google-genai")

            api_key = settings.LLM_API_KEY or settings.GEMINI_API_KEY
            self.model = settings.LLM_MODEL or settings.GEMINI_MODEL

            if not api_key:
                logger.warning("Gemini API Key未配置")

            if use_new_sdk:
                # 新 SDK 用法
                self.client = genai.Client(api_key=api_key)
                self.gemini_model = self.model
            else:
                # 旧 SDK 用法
                genai.configure(api_key=api_key)
                self.client = genai.GenerativeModel(self.model)

            self.use_new_gemini_sdk = use_new_sdk
            logger.info(f"Gemini客户端初始化完成 - Model: {self.model} (SDK: {'new' if use_new_sdk else 'legacy'})")
        except ImportError:
            logger.error("未安装 Gemini SDK，请运行: pip install google-genai 或 pip install google-generativeai")
            raise

    def _init_local(self):
        """初始化本地/自定义LLM客户端（使用OpenAI兼容接口）"""
        api_key = settings.LLM_API_KEY or "local-key"
        api_base = settings.LLM_API_BASE or settings.LOCAL_LLM_API_BASE
        self.model = settings.LLM_MODEL or settings.LOCAL_LLM_MODEL

        self.client = OpenAI(
            api_key=api_key,
            base_url=api_base
        )
        logger.info(f"本地LLM客户端初始化完成 - Model: {self.model}, Base: {api_base}")

    def _call_llm(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        json_mode: bool = False
    ) -> str:
        """调用LLM并返回响应（支持多种提供商）"""
        try:
            if self.provider == "gemini":
                return self._call_gemini(messages, temperature, json_mode)
            else:
                # OpenAI, Local, Custom都使用OpenAI兼容接口
                return self._call_openai_compatible(messages, temperature, json_mode)
        except Exception as e:
            logger.error(f"LLM调用失败 (Provider: {self.provider}): {str(e)}")
            raise

    def _call_openai_compatible(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        json_mode: bool = False
    ) -> str:
        """调用OpenAI兼容的API"""
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

    def _call_gemini(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        json_mode: bool = False
    ) -> str:
        """调用Google Gemini API（支持新旧SDK）"""
        # 将消息格式转换为Gemini格式
        prompt_parts = []
        system_instruction = None

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                system_instruction = content
            elif role == "user":
                prompt_parts.append(f"User: {content}\n")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}\n")

        prompt = "".join(prompt_parts)

        if json_mode:
            # 为 Gemini 添加更强的 JSON 格式要求
            json_instruction = """

CRITICAL INSTRUCTIONS FOR JSON RESPONSE:
1. You MUST respond with ONLY valid JSON format
2. Do NOT include any markdown formatting like ```json or ```
3. Do NOT include any explanatory text before or after the JSON
4. Start directly with { or [ and end with } or ]
5. Ensure all strings are properly quoted
6. Ensure all JSON syntax is correct

Your response should be parseable by json.loads() function directly.
"""
            prompt += json_instruction

        # 配置生成参数
        temp = temperature or self.temperature
        max_tokens = self.max_tokens

        if hasattr(self, 'use_new_gemini_sdk') and self.use_new_gemini_sdk:
            # 新 SDK 用法
            generation_config = {
                "temperature": temp,
                "max_output_tokens": max_tokens,
            }

            # 如果有系统指令，添加到开头
            if system_instruction:
                prompt = f"System Instructions: {system_instruction}\n\n{prompt}"

            response = self.client.models.generate_content(
                model=self.gemini_model,
                contents=prompt,
                config=generation_config
            )
            return response.text
        else:
            # 旧 SDK 用法
            generation_config = {
                "temperature": temp,
                "max_output_tokens": max_tokens,
            }

            # 如果有系统指令，添加到开头
            if system_instruction:
                prompt = f"System Instructions: {system_instruction}\n\n{prompt}"

            response = self.client.generate_content(
                prompt,
                generation_config=generation_config
            )
            return response.text

    def _extract_json_from_response(self, response: str) -> str:
        """从响应中提取 JSON 内容"""
        # 尝试提取 JSON 代码块
        json_match = re.search(r'```json\s*\n(.*?)\n```', response, re.DOTALL)
        if json_match:
            return json_match.group(1).strip()

        # 尝试提取普通代码块
        code_match = re.search(r'```\s*\n(.*?)\n```', response, re.DOTALL)
        if code_match:
            content = code_match.group(1).strip()
            # 检查是否是 JSON
            if content.startswith('{') or content.startswith('['):
                return content

        # 尝试找到第一个 { 或 [ 到最后一个 } 或 ]
        start_idx = -1
        end_idx = -1
        for i, char in enumerate(response):
            if char in '{[' and start_idx == -1:
                start_idx = i
            if char in '}]':
                end_idx = i

        if start_idx != -1 and end_idx != -1:
            return response[start_idx:end_idx+1]

        return response.strip()

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """解析 JSON 响应，带有错误处理"""
        try:
            # 直接尝试解析
            return json.loads(response)
        except json.JSONDecodeError:
            # 尝试提取 JSON
            logger.warning("直接解析 JSON 失败，尝试提取...")
            try:
                cleaned = self._extract_json_from_response(response)
                return json.loads(cleaned)
            except Exception as e:
                logger.error(f"JSON 提取和解析失败: {str(e)}")
                logger.error(f"原始响应: {response[:500]}...")
                raise ValueError(f"无法解析 LLM 响应为 JSON: {str(e)}")

    def analyze_interface(self, interface_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析接口，生成测试点"""
        prompt = self._build_interface_analysis_prompt(interface_data)

        messages = [
            {
                "role": "system",
                "content": "你是一个专业的API测试专家。你需要分析接口信息，生成全面的测试点列表。请确保返回有效的JSON格式。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        response = self._call_llm(messages, json_mode=True)
        return self._parse_json_response(response)

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
                "content": "你是一个专业的测试工程师。你需要根据测试点生成完整的pytest测试用例代码。请确保返回有效的JSON格式。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        response = self._call_llm(messages, json_mode=True)
        return self._parse_json_response(response)

    def analyze_test_report(
        self,
        execution_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """分析测试执行结果，生成智能报告"""
        prompt = self._build_report_analysis_prompt(execution_result)

        messages = [
            {
                "role": "system",
                "content": "你是一个专业的测试分析专家。你需要分析测试执行结果，提供深度洞察和优化建议。请确保返回有效的JSON格式。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        response = self._call_llm(messages, json_mode=True)
        return self._parse_json_response(response)

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

