from pydantic import BaseModel, Field
from typing import Optional


class LLMConfigBase(BaseModel):
    """LLM配置基础模型"""
    name: str = Field(..., description="配置名称")
    provider: str = Field(..., description="提供商，如openai, deepseek, ollama等")
    model_name: str = Field(..., description="模型名称")
    api_key: Optional[str] = Field(None, description="API密钥")
    api_base_url: Optional[str] = Field(None, description="API基础URL")
    is_default: bool = Field(False, description="是否为默认配置")


class LLMConfigCreate(LLMConfigBase):
    """创建LLM配置的输入模型"""
    pass


class LLMConfigUpdate(BaseModel):
    """更新LLM配置的输入模型"""
    name: Optional[str] = Field(None, description="配置名称")
    provider: Optional[str] = Field(None, description="提供商")
    model_name: Optional[str] = Field(None, description="模型名称")
    api_key: Optional[str] = Field(None, description="API密钥")
    api_base_url: Optional[str] = Field(None, description="API基础URL")
    is_default: Optional[bool] = Field(None, description="是否为默认配置")


class LLMConfigInDBBase(LLMConfigBase):
    """数据库中的LLM配置模型"""
    id: int
    user_id: int

    class Config:
        from_attributes = True


class LLMConfig(LLMConfigInDBBase):
    """API返回的LLM配置模型"""
    pass 