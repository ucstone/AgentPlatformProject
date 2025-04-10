from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.llm_config import LLMConfig
from app.schemas.llm_config import LLMConfigCreate, LLMConfigUpdate

def get_config_by_id(db: Session, config_id: int) -> Optional[LLMConfig]:
    """
    通过ID获取LLM配置
    """
    return db.query(LLMConfig).filter(LLMConfig.id == config_id).first()

def get_configs_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[LLMConfig]:
    """
    获取用户的所有LLM配置
    """
    return db.query(LLMConfig).filter(LLMConfig.user_id == user_id).offset(skip).limit(limit).all()

def get_default_config(db: Session, user_id: int) -> Optional[LLMConfig]:
    """
    获取用户的默认LLM配置
    """
    return db.query(LLMConfig).filter(LLMConfig.user_id == user_id, LLMConfig.is_default == True).first()

def create_config(db: Session, config_in: LLMConfigCreate, user_id: int) -> LLMConfig:
    """
    创建新的LLM配置
    """
    # 如果这是默认配置，先将其他配置的默认状态取消
    if config_in.is_default:
        db.query(LLMConfig).filter(
            LLMConfig.user_id == user_id, 
            LLMConfig.is_default == True
        ).update({"is_default": False})
        
    db_config = LLMConfig(
        name=config_in.name,
        provider=config_in.provider,
        model_name=config_in.model_name,
        api_key=config_in.api_key,
        api_base_url=config_in.api_base_url,
        is_default=config_in.is_default,
        user_id=user_id
    )
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

def update_config(db: Session, db_config: LLMConfig, config_in: LLMConfigUpdate) -> LLMConfig:
    """
    更新LLM配置
    """
    update_data = config_in.dict(exclude_unset=True)
    
    # 如果更新为默认配置，需要将其他配置的默认状态取消
    if update_data.get("is_default"):
        db.query(LLMConfig).filter(
            LLMConfig.user_id == db_config.user_id, 
            LLMConfig.is_default == True,
            LLMConfig.id != db_config.id
        ).update({"is_default": False})
    
    for key, value in update_data.items():
        setattr(db_config, key, value)
    
    db.commit()
    db.refresh(db_config)
    return db_config

def delete_config(db: Session, db_config: LLMConfig) -> None:
    """
    删除LLM配置
    """
    # 如果删除的是默认配置，而且还有其他配置，则将第一个配置设为默认
    if db_config.is_default:
        other_config = db.query(LLMConfig).filter(
            LLMConfig.user_id == db_config.user_id,
            LLMConfig.id != db_config.id
        ).first()
        
        if other_config:
            other_config.is_default = True
            db.add(other_config)
    
    db.delete(db_config)
    db.commit()

def get_available_providers() -> Dict[str, Any]:
    """
    获取可用的LLM提供商和模型
    """
    return {
        "providers": {
            "openai": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
            "deepseek": ["deepseek-chat", "deepseek-coder"],
            "ollama": ["llama3", "mistral", "codellama"],
            "anthropic": ["claude-2", "claude-3-opus", "claude-3-sonnet"],
            "gemini": ["gemini-pro", "gemini-ultra"]
        }
    } 