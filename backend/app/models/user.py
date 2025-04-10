from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean, default=False)
    
    # 关系
    chat_sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    llm_configs = relationship("LLMConfig", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email}>" 