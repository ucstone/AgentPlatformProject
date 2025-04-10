from typing import List, Dict, Any, AsyncGenerator, Optional
import json
import asyncio
from pydantic import BaseModel, Field

from app.services.llm_service import LLMService, LLMMessage, LLMProvider, get_llm_service


# 智能体类型枚举
class AgentType(str):
    CUSTOMER_SERVICE = "customer_service"  # 客服智能体
    KNOWLEDGE_BASE = "knowledge_base"      # 知识库问答


# 智能体配置
class AgentConfig(BaseModel):
    agent_type: str = Field(default=AgentType.CUSTOMER_SERVICE)
    llm_provider: str = Field(default="openai")
    model_key: str = Field(default="default")
    system_message: Optional[str] = Field(default=None)


# 客服智能体系统消息
CUSTOMER_SERVICE_SYSTEM_PROMPT = """你是一个专业的智能客服助手，需要：
1. 用礼貌、专业的口吻回答用户问题
2. 保持回答简洁、清晰，避免过长的内容
3. 如遇到无法解答的问题，坦诚告知用户并提供可能的解决方向
4. 不泄露任何敏感信息，包括公司内部数据、用户数据等
5. 避免对不确定的内容做出承诺

在处理问题时，应按照以下流程：
1. 理解用户问题的核心需求
2. 提供直接、有帮助的回答
3. 必要时提供额外的相关信息
4. 询问用户是否解决了问题，是否需要其他帮助
"""


class AgentService:
    """智能体服务"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.setup_agent()
    
    def setup_agent(self):
        """设置智能体"""
        try:
            # 获取LLM服务
            llm_provider = LLMProvider(self.config.llm_provider)
            self.llm_service = get_llm_service(llm_provider, self.config.model_key)
            
            # 设置系统消息
            if self.config.agent_type == AgentType.CUSTOMER_SERVICE:
                self.system_message = self.config.system_message or CUSTOMER_SERVICE_SYSTEM_PROMPT
            else:
                self.system_message = self.config.system_message or "你是一个AI助手。"
                
        except Exception as e:
            raise Exception(f"初始化智能体失败: {str(e)}")
    
    async def chat_stream(self, 
                         messages: List[Dict[str, str]],
                         user_id: Optional[int] = None) -> AsyncGenerator[str, None]:
        """流式聊天接口"""
        try:
            # 转换消息格式
            llm_messages = [
                LLMMessage(role=msg["role"], content=msg["content"])
                for msg in messages
            ]
            
            # 使用LLM服务生成回复
            async for chunk in self.llm_service.generate_stream(
                llm_messages,
                system_message=self.system_message
            ):
                yield chunk
                
        except Exception as e:
            yield f"抱歉，智能助手遇到了问题: {str(e)}"
    
    async def ask(self, query: str, history: List[Dict[str, str]]) -> str:
        """非流式聊天，返回完整回复"""
        # 流式聊天结果拼接为完整字符串
        full_response = ""
        async for chunk in self.chat_stream([*history, {"role": "user", "content": query}]):
            full_response += chunk
        return full_response


# 获取智能体服务的工厂函数
def get_agent_service(
    agent_type: str = AgentType.CUSTOMER_SERVICE,
    llm_provider: str = "openai",
    model_key: str = "default",
    system_message: Optional[str] = None
) -> AgentService:
    """获取指定类型和配置的智能体服务"""
    config = AgentConfig(
        agent_type=agent_type,
        llm_provider=llm_provider,
        model_key=model_key,
        system_message=system_message
    )
    return AgentService(config) 