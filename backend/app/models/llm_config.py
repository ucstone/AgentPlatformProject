from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class LLMConfig(Base):
    """
    存储LLM配置信息的数据库模型
    """
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True, nullable=False, unique=True)  # 配置名称
    provider = Column(String(50), nullable=False)  # 提供商，如openai, deepseek, ollama
    model_name = Column(String(100), nullable=False)  # 模型名称
    api_key = Column(String(255))  # API密钥
    api_base_url = Column(String(255))  # API基础URL
    is_default = Column(Boolean, default=False)  # 是否为默认配置
    
    # 创建者信息
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="llm_configs") 