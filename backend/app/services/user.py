from typing import Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.models.user import User
from app.schemas.user import UserCreate


# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    对明文密码进行哈希处理
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证明文密码与哈希密码是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    通过邮箱获取用户
    """
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user_in: UserCreate) -> User:
    """
    创建新用户
    """
    # 对密码进行哈希处理
    hashed_password = get_password_hash(user_in.password)
    
    # 创建用户对象
    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        is_active=True
    )
    
    # 添加到数据库并提交
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user 