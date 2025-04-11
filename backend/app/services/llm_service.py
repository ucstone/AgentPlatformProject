from typing import List, Dict, Any, AsyncGenerator, Union, Optional
import json
import asyncio
import os
from enum import Enum
from pydantic import BaseModel
from openai import AsyncOpenAI
import uuid
import logging
from datetime import datetime

from app.core.config import settings
from app.core.logging import logger

class LLMProvider(str, Enum):
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    OLLAMA = "ollama"
    MOCK = "mock"  # 添加模拟模式


class LLMMessage(BaseModel):
    role: str
    content: str


class LLMConfig(BaseModel):
    provider: LLMProvider
    model_name: str
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000


DEFAULT_SYSTEM_MESSAGE = "你是一个智能客服助手，提供专业、准确、友好的回答。"


class LLMService:
    """大模型服务抽象层，统一不同LLM的API接口"""
    
    def __init__(self, provider: LLMProvider = LLMProvider.OPENAI, model_key: str = "gpt-3.5-turbo"):
        self.provider = provider
        self.model_key = model_key
        self.client = None
        self.config = DEFAULT_MODEL_CONFIGS[provider][model_key]
        self.setup_client()
        logger.info(f"[LLMService] 初始化LLM服务: 提供商={provider}, 模型={model_key}")
    
    def setup_client(self):
        """根据提供商设置客户端"""
        if self.provider == LLMProvider.OPENAI:
            self.client = AsyncOpenAI(
                api_key=self.config.api_key,
                base_url=self.config.api_base
            )
        elif self.provider == LLMProvider.DEEPSEEK:
            self.client = AsyncOpenAI(
                api_key=self.config.api_key,
                base_url=self.config.api_base
            )
        elif self.provider == LLMProvider.OLLAMA:
            self.client = AsyncOpenAI(
                base_url=self.config.api_base
            )
        else:  # MOCK
            self.client = None
    
    async def generate_stream(
        self,
        messages: List[LLMMessage],
        config: Optional[LLMConfig] = None
    ) -> AsyncGenerator[str, None]:
        """生成流式响应"""
        if config:
            self.config = config
            self.setup_client()

        if self.provider == LLMProvider.MOCK:
            async for chunk in self._mock_response():
                yield chunk
            return

        try:
            response = await self.client.chat.completions.create(
                model=self.model_key,
                messages=[{"role": msg.role, "content": msg.content} for msg in messages],
                stream=True,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            async for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"生成响应时出错: {str(e)}")
            yield f"生成响应时出错: {str(e)}"
    
    async def _mock_response(self) -> AsyncGenerator[str, None]:
        """模拟响应"""
        mock_responses = [
            "你好！",
            "我是一个AI助手。",
            "很高兴为你服务。",
            "有什么我可以帮助你的吗？"
        ]
        for response in mock_responses:
            yield response
            await asyncio.sleep(0.5)

    async def generate_response(
        self,
        content: str,
        llm_config: LLMConfig,
        user_id: str
    ) -> str:
        """生成完整响应"""
        messages = [LLMMessage(role="user", content=content)]
        response = ""
        async for chunk in self.generate_stream(messages, llm_config):
            response += chunk
        return response


# 模型配置
DEFAULT_MODEL_CONFIGS = {
    LLMProvider.OPENAI: {
        "default": LLMConfig(
            provider=LLMProvider.OPENAI,
            model_name="gpt-3.5-turbo",
            api_key=settings.OPENAI_API_KEY
        ),
        "gpt4": LLMConfig(
            provider=LLMProvider.OPENAI,
            model_name="gpt-4",
            api_key=settings.OPENAI_API_KEY
        )
    },
    LLMProvider.DEEPSEEK: {
        "default": LLMConfig(
            provider=LLMProvider.DEEPSEEK,
            model_name="deepseek-chat",
            api_key=settings.DEEPSEEK_API_KEY,
            api_base="https://api.deepseek.com/v1"
        )
    },
    LLMProvider.OLLAMA: {
        "default": LLMConfig(
            provider=LLMProvider.OLLAMA,
            model_name="llama3",
            api_base=settings.OLLAMA_HOST
        ),
        "mistral": LLMConfig(
            provider=LLMProvider.OLLAMA,
            model_name="mistral",
            api_base=settings.OLLAMA_HOST
        )
    },
    LLMProvider.MOCK: {
        "default": LLMConfig(
            provider=LLMProvider.MOCK,
            model_name="mock",
        )
    }
}


def get_llm_service(provider: LLMProvider = LLMProvider.OPENAI, model_key: str = "gpt-3.5-turbo") -> LLMService:
    """获取 LLM 服务实例"""
    logger.info(f"[LLMService] 请求LLM服务: provider={provider}, model_key={model_key}")
    
    # 如果提供商不支持，回退到模拟模式
    if provider not in DEFAULT_MODEL_CONFIGS:
        logger.warning(f"[LLMService] 不支持的LLM提供商: {provider}，将使用模拟模式")
        return LLMService(provider=LLMProvider.MOCK, model_key="mock")
        
    # 如果模型不支持，使用默认模型
    if model_key not in DEFAULT_MODEL_CONFIGS[provider]:
        available_models = list(DEFAULT_MODEL_CONFIGS[provider].keys())
        logger.warning(f"[LLMService] 提供商 {provider} 不支持模型 {model_key}，可用模型: {available_models}。将使用默认模型。")
        model_key = "default"
    
    config = DEFAULT_MODEL_CONFIGS[provider][model_key]
    return LLMService(provider=provider, model_key=model_key)

# 创建默认的 llm_service 实例
llm_service = get_llm_service(provider=LLMProvider.OPENAI, model_key="gpt-3.5-turbo") 