from datetime import datetime, timedelta
from typing import Optional, Any, Union

from jose import jwt
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.user import TokenPayload


def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建JWT访问令牌
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # 设置JWT声明
    to_encode = {"exp": expire, "sub": str(subject)}
    # 使用密钥进行编码
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenPayload]:
    """
    验证JWT令牌
    """
    try:
        # 解码JWT
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        # 验证令牌格式
        token_data = TokenPayload(**payload)
        
        # 检查令牌是否过期
        if datetime.fromtimestamp(token_data.exp) < datetime.utcnow():
            return None
            
        return token_data
    except (jwt.JWTError, ValidationError):
        return None 