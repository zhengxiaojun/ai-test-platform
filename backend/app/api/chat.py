"""
AI 聊天接口
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.core.ai_orchestrator import AIOrchestrator
from loguru import logger

router = APIRouter()

ai_orchestrator = AIOrchestrator()


class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []


class ChatResponse(BaseModel):
    message: str
    timestamp: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    AI 对话接口
    
    支持：
    - 测试咨询
    - 用例生成建议
    - 测试方案讨论
    - 问题解答
    """
    try:
        logger.info(f"收到对话请求: {request.message}")
        
        # 构建对话历史上下文
        context = ""
        for msg in request.history[-5:]:  # 只保留最近5条历史
            if msg.role == "user":
                context += f"用户: {msg.content}\n"
            else:
                context += f"助手: {msg.content}\n"
        
        # 构建 prompt
        system_prompt = """你是一个专业的测试助手，擅长：
1. 分析测试需求
2. 生成测试用例
3. 解答测试问题
4. 提供测试建议
5. 帮助优化测试流程

请用专业、友好的方式回答用户的问题。"""
        
        full_prompt = f"""{system_prompt}

对话历史:
{context}

用户问题: {request.message}

请提供专业、详细的回答："""
        
        # 调用 AI
        response = await ai_orchestrator.client.chat.completions.create(
            model=ai_orchestrator.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.message}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        assistant_message = response.choices[0].message.content
        
        from datetime import datetime
        
        return ChatResponse(
            message=assistant_message,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"AI 对话失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI 对话失败: {str(e)}")

