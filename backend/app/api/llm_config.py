from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.db.deps import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.llm_config import LLMConfig, LLMConfigCreate, LLMConfigUpdate
from app.services import llm_config_service

router = APIRouter(tags=["模型配置"])


@router.get("/providers", response_model=Dict[str, Any])
def get_available_providers(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    获取可用的LLM提供商和模型列表
    """
    return llm_config_service.get_available_providers()


@router.get("/", response_model=List[LLMConfig])
def get_configs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[LLMConfig]:
    """
    获取当前用户的所有LLM配置
    """
    return llm_config_service.get_configs_by_user(db, current_user.id, skip, limit)


@router.post("/", response_model=LLMConfig, status_code=status.HTTP_201_CREATED)
def create_config(
    config_in: LLMConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> LLMConfig:
    """
    创建新的LLM配置
    """
    return llm_config_service.create_config(db, config_in, current_user.id)


@router.get("/default", response_model=LLMConfig)
def get_default_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> LLMConfig:
    """
    获取当前用户的默认LLM配置
    """
    config = llm_config_service.get_default_config(db, current_user.id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到默认配置"
        )
    return config


@router.get("/{config_id}", response_model=LLMConfig)
def get_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> LLMConfig:
    """
    获取特定的LLM配置
    """
    config = llm_config_service.get_config_by_id(db, config_id)
    if not config or config.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配置不存在或无权访问"
        )
    return config


@router.put("/{config_id}", response_model=LLMConfig)
def update_config(
    config_id: int,
    config_in: LLMConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> LLMConfig:
    """
    更新LLM配置
    """
    config = llm_config_service.get_config_by_id(db, config_id)
    if not config or config.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配置不存在或无权访问"
        )
    return llm_config_service.update_config(db, config, config_in)


@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """
    删除LLM配置
    """
    config = llm_config_service.get_config_by_id(db, config_id)
    if not config or config.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配置不存在或无权访问"
        )
    llm_config_service.delete_config(db, config) 