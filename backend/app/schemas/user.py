from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """用户基础信息模型"""
    email: EmailStr = Field(..., description="用户邮箱")


class UserCreate(UserBase):
    """用户创建请求模型"""
    password: str = Field(..., min_length=8, description="用户密码，至少8个字符")


class UserLogin(UserBase):
    """用户登录请求模型"""
    password: str = Field(..., description="用户密码")


class UserInDB(UserBase):
    """数据库中存储的用户模型"""
    id: int
    is_active: bool = True
    hashed_password: str

    class Config:
        orm_mode = True


class User(UserBase):
    """用户响应模型（不包含敏感信息）"""
    id: int
    is_active: bool = True

    class Config:
        orm_mode = True


class Token(BaseModel):
    """Token响应模型"""
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """Token载荷模型"""
    sub: str = None
    exp: int = None 