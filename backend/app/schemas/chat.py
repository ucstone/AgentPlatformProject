from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Literal


class MessageBase(BaseModel):
    """消息基础模型"""
    content: str = Field(..., description="消息内容")


class MessageCreate(MessageBase):
    """创建消息请求模型"""
    pass


class Message(MessageBase):
    """消息响应模型"""
    id: str = Field(..., description="消息ID")
    role: Literal["user", "assistant"] = Field(..., description="消息角色：用户或助手")
    session_id: str = Field(..., description="会话ID")
    created_at: datetime = Field(default_factory=datetime.now, description="消息创建时间")

    class Config:
        orm_mode = True


class SessionBase(BaseModel):
    """会话基础模型"""
    title: str = Field(..., description="会话标题")


class SessionCreate(SessionBase):
    """创建会话请求模型"""
    pass


class SessionUpdate(BaseModel):
    """更新会话请求模型"""
    title: Optional[str] = Field(None, description="会话标题")


class Session(SessionBase):
    """会话响应模型"""
    id: str = Field(..., description="会话ID")
    user_id: int = Field(..., description="用户ID")
    created_at: datetime = Field(default_factory=datetime.now, description="会话创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="会话更新时间")
    messages: Optional[List[Message]] = Field(None, description="会话中的消息列表")

    class Config:
        orm_mode = True


class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str = Field(..., description="用户消息内容")
    session_id: Optional[str] = Field(None, description="会话ID，如果为空则创建新会话")


class ChatResponse(BaseModel):
    """聊天响应模型"""
    message: str = Field(..., description="助手回复内容")
    session_id: str = Field(..., description="会话ID")


class ChatSessionBase(BaseModel):
    title: str


class ChatSessionCreate(ChatSessionBase):
    pass


class ChatSessionUpdate(ChatSessionBase):
    pass


class ChatSession(ChatSessionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatMessageBase(BaseModel):
    content: str
    role: str


class ChatMessageCreate(ChatMessageBase):
    session_id: int


class ChatMessage(ChatMessageBase):
    id: int
    session_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ChatMessageResponse(ChatMessageBase):
    id: int
    session_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSessionWithMessages(ChatSession):
    messages: List[ChatMessageResponse] 