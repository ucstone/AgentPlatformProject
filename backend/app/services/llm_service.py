from typing import List, Dict, Any, AsyncGenerator, Union, Optional
import json
import asyncio
import httpx
import os
from enum import Enum
from pydantic import BaseModel
import logging

from app.core.config import settings

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("llm_service")

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
    model: str
    temperature: float = 0.7
    max_tokens: int = 1000
    api_key: Optional[str] = None
    api_base: Optional[str] = None


DEFAULT_SYSTEM_MESSAGE = "你是一个智能客服助手，提供专业、准确、友好的回答。"


class LLMService:
    """大模型服务抽象层，统一不同LLM的API接口"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = None
        logger.info(f"初始化LLM服务: 提供商={config.provider}, 模型={config.model}")
        self.setup_client()
    
    def setup_client(self):
        """根据提供商配置客户端"""
        if self.config.provider == LLMProvider.OPENAI:
            # OpenAI设置
            try:
                from openai import AsyncOpenAI
                api_key = self.config.api_key or settings.OPENAI_API_KEY
                api_base = self.config.api_base
                
                if not api_key:
                    logger.warning("OpenAI API密钥未设置，将使用模拟模式")
                    self.config.provider = LLMProvider.MOCK
                    return
                
                client_kwargs = {"api_key": api_key}
                if api_base:
                    client_kwargs["base_url"] = api_base
                    
                self.client = AsyncOpenAI(**client_kwargs)
                logger.info("OpenAI客户端初始化成功")
            except ImportError as e:
                logger.error(f"导入OpenAI库失败: {str(e)}")
                raise ImportError("未安装OpenAI库，请使用pip install openai安装")
            except Exception as e:
                logger.error(f"初始化OpenAI客户端失败: {str(e)}")
                raise Exception(f"初始化OpenAI客户端失败: {str(e)}")
            
        elif self.config.provider == LLMProvider.DEEPSEEK:
            # DeepSeek设置
            try:
                from openai import AsyncOpenAI
                api_key = self.config.api_key or settings.DEEPSEEK_API_KEY
                api_base = self.config.api_base or "https://api.deepseek.com/v1"
                
                if not api_key:
                    logger.warning("DeepSeek API密钥未设置，将使用模拟模式")
                    self.config.provider = LLMProvider.MOCK
                    return
                
                # 清除可能干扰的环境变量
                http_proxy = os.environ.pop("http_proxy", None)
                https_proxy = os.environ.pop("https_proxy", None)
                HTTP_PROXY = os.environ.pop("HTTP_PROXY", None)
                HTTPS_PROXY = os.environ.pop("HTTPS_PROXY", None)
                
                self.client = AsyncOpenAI(
                    api_key=api_key,
                    base_url=api_base
                )
                
                # 恢复环境变量
                if http_proxy:
                    os.environ["http_proxy"] = http_proxy
                if https_proxy:
                    os.environ["https_proxy"] = https_proxy
                if HTTP_PROXY:
                    os.environ["HTTP_PROXY"] = HTTP_PROXY
                if HTTPS_PROXY:
                    os.environ["HTTPS_PROXY"] = HTTPS_PROXY
                    
                logger.info("DeepSeek客户端初始化成功")
            except ImportError as e:
                logger.error(f"导入OpenAI库失败: {str(e)}")
                raise ImportError("未安装OpenAI库，请使用pip install openai安装")
            except Exception as e:
                logger.error(f"初始化DeepSeek客户端失败: {str(e)}")
                raise Exception(f"初始化DeepSeek客户端失败: {str(e)}")
            
        elif self.config.provider == LLMProvider.OLLAMA:
            # Ollama没有专门的客户端，使用httpx
            try:
                ollama_host = self.config.api_base or settings.OLLAMA_HOST or "http://localhost:11434"
                logger.info(f"正在初始化Ollama客户端，地址: {ollama_host}")
                self.client = httpx.AsyncClient(
                    base_url=ollama_host
                )
                logger.info("Ollama客户端初始化成功")
            except Exception as e:
                logger.error(f"初始化Ollama客户端失败: {str(e)}")
                self.config.provider = LLMProvider.MOCK
                logger.warning("将使用模拟模式作为回退")
    
    async def generate_stream(
        self, 
        messages: List[LLMMessage], 
        system_message: str = DEFAULT_SYSTEM_MESSAGE
    ) -> AsyncGenerator[str, None]:
        """以流式方式生成回复"""
        # 如果是模拟模式，返回模拟响应
        if self.config.provider == LLMProvider.MOCK:
            logger.info("使用模拟模式生成回复")
            async for chunk in self._mock_response(messages):
                yield chunk
            return
            
        if self.config.provider in [LLMProvider.OPENAI, LLMProvider.DEEPSEEK]:
            # OpenAI和DeepSeek格式一致
            try:
                full_messages = [{"role": "system", "content": system_message}]
                full_messages.extend([{"role": m.role, "content": m.content} for m in messages])
                
                logger.info(f"向{self.config.provider}发送请求，模型: {self.config.model}")
                stream = await self.client.chat.completions.create(
                    model=self.config.model,
                    messages=full_messages,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                    stream=True
                )
                
                async for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            except Exception as e:
                logger.error(f"{self.config.provider}生成错误: {str(e)}")
                yield f"错误: {str(e)}"
                # 回退到模拟模式
                async for chunk in self._mock_response(messages):
                    yield chunk
        
        elif self.config.provider == LLMProvider.OLLAMA:
            # Ollama API格式
            try:
                formatted_messages = [{"role": "system", "content": system_message}]
                formatted_messages.extend([{"role": m.role, "content": m.content} for m in messages])
                
                request_data = {
                    "model": self.config.model,
                    "messages": formatted_messages,
                    "stream": True,
                    "options": {
                        "temperature": self.config.temperature,
                    }
                }
                
                logger.info(f"向Ollama发送请求，模型: {self.config.model}")
                async with self.client.stream(
                    "POST", 
                    "/api/chat", 
                    json=request_data,
                    timeout=60.0
                ) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        error_msg = f"Ollama API错误 ({response.status_code}): {error_text.decode('utf-8')}"
                        logger.error(error_msg)
                        yield error_msg
                        # 回退到模拟模式
                        async for chunk in self._mock_response(messages):
                            yield chunk
                        return
                        
                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue
                        try:
                            data = json.loads(line)
                            if "message" in data and "content" in data["message"]:
                                content = data["message"]["content"]
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                logger.error(f"Ollama错误: {str(e)}")
                yield f"Ollama错误: {str(e)}"
                # 回退到模拟模式
                async for chunk in self._mock_response(messages):
                    yield chunk
    
    async def _mock_response(self, messages: List[LLMMessage]) -> AsyncGenerator[str, None]:
        """生成模拟响应，用于API不可用时"""
        logger.info("生成模拟响应")
        
        # 获取最后一条用户消息
        last_user_msg = None
        for msg in reversed(messages):
            if msg.role == "user":
                last_user_msg = msg.content
                break
        
        if not last_user_msg:
            last_user_msg = "你好"
            
        # 生成简单响应
        response = f"[模拟回复] 你说：\"{last_user_msg}\"。我是智能客服助手，但当前我处于模拟模式，实际LLM服务不可用。请确保配置了正确的API密钥，或者检查服务连接是否正常。"
        
        # 模拟流式输出
        words = response.split()
        for i, word in enumerate(words):
            yield word + " "
            if i < len(words) - 1:  # 不是最后一个词
                await asyncio.sleep(0.05)  # 添加延迟模拟打字效果


# 模型配置
DEFAULT_MODEL_CONFIGS = {
    LLMProvider.OPENAI: {
        "default": LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-3.5-turbo",
            api_key=settings.OPENAI_API_KEY
        ),
        "gpt4": LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            api_key=settings.OPENAI_API_KEY
        )
    },
    LLMProvider.DEEPSEEK: {
        "default": LLMConfig(
            provider=LLMProvider.DEEPSEEK,
            model="deepseek-chat",
            api_key=settings.DEEPSEEK_API_KEY,
            api_base="https://api.deepseek.com/v1"
        )
    },
    LLMProvider.OLLAMA: {
        "default": LLMConfig(
            provider=LLMProvider.OLLAMA,
            model="llama3",
            api_base=settings.OLLAMA_HOST
        ),
        "mistral": LLMConfig(
            provider=LLMProvider.OLLAMA,
            model="mistral",
            api_base=settings.OLLAMA_HOST
        )
    },
    LLMProvider.MOCK: {
        "default": LLMConfig(
            provider=LLMProvider.MOCK,
            model="mock",
        )
    }
}


def get_llm_service(provider: LLMProvider, model_key: str = "default") -> LLMService:
    """获取指定提供商和模型的LLM服务实例"""
    logger.info(f"请求LLM服务: provider={provider}, model_key={model_key}")
    
    # 如果提供商不支持，回退到模拟模式
    if provider not in DEFAULT_MODEL_CONFIGS:
        logger.warning(f"不支持的LLM提供商: {provider}，将使用模拟模式")
        return LLMService(DEFAULT_MODEL_CONFIGS[LLMProvider.MOCK]["default"])
        
    # 如果模型不支持，使用默认模型
    if model_key not in DEFAULT_MODEL_CONFIGS[provider]:
        available_models = list(DEFAULT_MODEL_CONFIGS[provider].keys())
        logger.warning(f"提供商 {provider} 不支持模型 {model_key}，可用模型: {available_models}。将使用默认模型。")
        model_key = "default"
    
    config = DEFAULT_MODEL_CONFIGS[provider][model_key]
    return LLMService(config) 