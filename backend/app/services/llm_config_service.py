from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.llm_config import LLMConfig
from app.schemas.llm_config import LLMConfigCreate, LLMConfigUpdate

class LLMConfigService:
    def get_config_by_id(self, db: Session, config_id: int) -> Optional[LLMConfig]:
        """
        通过ID获取LLM配置
        """
        return db.query(LLMConfig).filter(LLMConfig.id == config_id).first()

    def get_configs_by_user(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[LLMConfig]:
        """
        获取用户的所有LLM配置
        """
        print(f"获取用户 {user_id} 的配置，skip={skip}, limit={limit}")
        configs = db.query(LLMConfig).filter(LLMConfig.user_id == user_id).offset(skip).limit(limit).all()
        print(f"找到 {len(configs)} 条配置")
        for config in configs:
            print(f"配置: id={config.id}, name={config.name}, provider={config.provider}, model_name={config.model_name}")
        return configs

    def get_default_config(self, db: Session, user_id: int) -> Optional[LLMConfig]:
        """
        获取用户的默认LLM配置
        """
        try:
            print(f"获取用户 {user_id} 的默认LLM配置")
            
            # 首先尝试获取用户的默认配置
            config = db.query(LLMConfig).filter(
                LLMConfig.user_id == user_id,
                LLMConfig.is_default == True
            ).first()
            
            if config:
                print(f"找到用户的默认配置: {config.__dict__}")
                # 确保所有必要的字段都被正确设置
                config.model = config.model_name
                config.api_base = config.api_base_url
                config.api_key = config.api_key
                config.provider = config.provider
                config.temperature = 0.7  # 默认温度
                config.max_tokens = 2000  # 默认最大token数
                return config
            
            # 如果没有默认配置，获取第一个配置
            config = db.query(LLMConfig).filter(
                LLMConfig.user_id == user_id
            ).first()
            
            if config:
                print(f"找到用户的第一个配置: {config.__dict__}")
                # 设置为默认配置
                config.is_default = True
                db.commit()
                db.refresh(config)
                
                # 确保所有必要的字段都被正确设置
                config.model = config.model_name
                config.api_base = config.api_base_url
                config.api_key = config.api_key
                config.provider = config.provider
                config.temperature = 0.7  # 默认温度
                config.max_tokens = 2000  # 默认最大token数
                return config
            
            print(f"用户 {user_id} 没有任何LLM配置")
            return None
            
        except Exception as e:
            print(f"获取默认配置失败: {str(e)}")
            return None

    def create_config(self, db: Session, config_in: LLMConfigCreate, user_id: int) -> LLMConfig:
        """
        创建新的LLM配置
        """
        # 检查名称是否已存在，如果存在则添加后缀
        base_name = config_in.name
        name = base_name
        counter = 1
        while db.query(LLMConfig).filter(LLMConfig.name == name).first():
            name = f"{base_name}-{counter}"
            counter += 1
        
        # 如果这是默认配置，先将其他配置的默认状态取消
        if config_in.is_default:
            db.query(LLMConfig).filter(
                LLMConfig.user_id == user_id, 
                LLMConfig.is_default == True
            ).update({"is_default": False})
        
        db_config = LLMConfig(
            name=name,  # 使用修改后的名称
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

    def update_config(self, db: Session, db_config: LLMConfig, config_in: LLMConfigUpdate) -> LLMConfig:
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

    def delete_config(self, db: Session, db_config: LLMConfig) -> None:
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

    def get_available_providers(self) -> Dict[str, Any]:
        """
        获取可用的LLM提供商和模型
        """
        return {
            "providers": {
                "openai": [
                    "gpt-3.5-turbo",
                    "gpt-3.5-turbo-16k",
                    "gpt-4",
                    "gpt-4-turbo-preview",
                    "gpt-4-32k"
                ],
                "deepseek": [
                    "deepseek-chat",
                    "deepseek-coder"
                ],
                "ollama": [
                    "llama2",
                    "mistral",
                    "codellama",
                    "vicuna",
                    "wizardcoder"
                ]
            },
            "current": {
                "provider": "openai",
                "model": "gpt-3.5-turbo"
            }
        }

# 创建LLMConfigService的实例
llm_config_service = LLMConfigService()

# 导出服务实例和系统提示
__all__ = ["llm_config_service", "CUSTOMER_SERVICE_SYSTEM_PROMPT"]

CUSTOMER_SERVICE_SYSTEM_PROMPT = """你是一个专业的智能客服助手，需要：
1. 用礼貌、专业的口吻回答用户问题
2. 保持回答简洁、清晰，避免过长的内容
3. 如遇到无法解答的问题，坦诚告知用户并提供可能的解决方向
4. 不泄露任何敏感信息，包括公司内部数据、用户数据等
5. 避免对不确定的内容做出承诺
""" 