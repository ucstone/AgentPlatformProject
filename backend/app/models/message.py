from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base

class ChatMessage(Base):
    """聊天消息模型"""
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, index=True)
    session_id = Column(String(36), ForeignKey("chat_sessions.id"), nullable=False)
    content = Column(Text, nullable=False)
    role = Column(String(50), nullable=False)  # user 或 assistant
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    session = relationship("ChatSession", back_populates="messages")

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, role={self.role}, content={self.content[:20]}...)>" 