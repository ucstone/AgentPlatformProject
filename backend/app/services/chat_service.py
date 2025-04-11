from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from app.models.session import ChatSession as SessionModel
from app.models.message import ChatMessage as MessageModel
from app.schemas.chat import ChatMessage
from app.db.session import get_db

class ChatService:
    def __init__(self):
        self.active_sessions: dict = {}

    async def save_message(self, message: ChatMessage) -> None:
        """保存消息到数据库"""
        db = next(get_db())
        try:
            db_message = MessageModel(
                id=message.id,
                session_id=message.session_id,
                content=message.content,
                role=message.role,
                created_at=message.created_at
            )
            db.add(db_message)
            db.commit()
            db.refresh(db_message)
        finally:
            db.close()

    async def get_session_messages(self, session_id: str) -> List[ChatMessage]:
        """获取会话的所有消息"""
        db = next(get_db())
        try:
            messages = db.query(MessageModel).filter(
                MessageModel.session_id == session_id
            ).order_by(MessageModel.created_at).all()
            return [
                ChatMessage(
                    id=msg.id,
                    session_id=msg.session_id,
                    content=msg.content,
                    role=msg.role,
                    created_at=msg.created_at
                )
                for msg in messages
            ]
        finally:
            db.close()

    async def create_session(self, user_id: str) -> str:
        """创建新的会话"""
        session_id = str(uuid.uuid4())
        db = next(get_db())
        try:
            db_session = SessionModel(
                id=session_id,
                title=f"会话 {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}",
                user_id=int(user_id),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(db_session)
            db.commit()
            db.refresh(db_session)
            
            self.active_sessions[session_id] = {
                "user_id": user_id,
                "created_at": datetime.utcnow(),
                "messages": []
            }
            return session_id
        finally:
            db.close()

    async def get_session(self, session_id: str) -> Optional[dict]:
        """获取会话信息"""
        db = next(get_db())
        try:
            session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
            if session:
                return {
                    "id": session.id,
                    "title": session.title,
                    "user_id": session.user_id,
                    "created_at": session.created_at,
                    "updated_at": session.updated_at
                }
            return None
        finally:
            db.close()

    async def delete_session(self, session_id: str) -> None:
        """删除会话"""
        db = next(get_db())
        try:
            session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
            if session:
                db.delete(session)
                db.commit()
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
        finally:
            db.close()

chat_service = ChatService() 