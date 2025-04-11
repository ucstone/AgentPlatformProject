from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import WebSocket
import json
from datetime import datetime
import uuid
from fastapi import HTTPException

from app.models.session import ChatSession as SessionModel
from app.models.message import ChatMessage as MessageModel
from app.schemas.chat import ChatSessionCreate, ChatMessageCreate, ChatMessageResponse, ChatRequest, ChatResponse, ChatMessage
from app.services.agent_service import get_agent_service
from app.services.llm_config_service import llm_config_service
from app.services.chat_service import chat_service
from app.services.llm_service import llm_service, LLMConfig
from app.db.session import get_db

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)

    def disconnect(self, websocket: WebSocket, session_id: str):
        if session_id in self.active_connections:
            self.active_connections[session_id].remove(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

    async def broadcast(self, session_id: str, message: str):
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                await connection.send_text(message)

websocket_manager = WebSocketManager()

def get_sessions_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[SessionModel]:
    """
    获取用户的所有会话
    """
    return db.query(SessionModel).filter(
        SessionModel.user_id == user_id
    ).order_by(
        SessionModel.updated_at.desc()
    ).offset(skip).limit(limit).all()

def get_session_by_id(db: Session, session_id: str) -> Optional[SessionModel]:
    """
    获取特定会话
    """
    return db.query(SessionModel).filter(SessionModel.id == session_id).first()

async def create_session(
    db: Session,
    session_in: ChatSessionCreate,
    user_id: int
) -> SessionModel:
    """创建新的聊天会话"""
    # 获取用户的默认LLM配置
    default_config = llm_config_service.get_default_config(db, user_id)
    
    # 创建会话记录
    db_session = SessionModel(
        title=session_in.title,
        user_id=user_id,
        llm_config_id=default_config.id if default_config else None
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def update_session(db: Session, session: SessionModel, title: str) -> SessionModel:
    """
    更新会话
    """
    session.title = title
    db.commit()
    db.refresh(session)
    return session

def delete_session(db: Session, session: SessionModel) -> None:
    """
    删除会话
    """
    db.delete(session)
    db.commit()

def get_messages_by_session(db: Session, session_id: str, skip: int = 0, limit: int = 100) -> List[MessageModel]:
    """
    获取指定会话的所有消息
    """
    return db.query(MessageModel).filter(
        MessageModel.session_id == session_id
    ).order_by(
        MessageModel.created_at.asc()
    ).offset(skip).limit(limit).all()

def create_message(db: Session, session_id: str, content: str, role: str) -> MessageModel:
    """
    创建新消息
    """
    db_message = MessageModel(
        id=str(uuid.uuid4()),
        session_id=session_id,
        content=content,
        role=role,
        created_at=datetime.utcnow()
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

async def send_message(
    session_id: str,
    content: str,
    user_id: str,
    llm_config: LLMConfig
) -> ChatMessageResponse:
    """发送消息并获取AI回复"""
    try:
        # 创建用户消息
        user_message = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            content=content,
            role="user",
            created_at=datetime.utcnow()
        )
        
        # 保存用户消息
        await chat_service.save_message(user_message)
        
        # 获取AI回复
        assistant_content = await llm_service.generate_response(
            content=content,
            llm_config=llm_config,
            user_id=user_id
        )
        
        # 创建AI回复消息
        assistant_message = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            content=assistant_content,
            role="assistant",
            created_at=datetime.utcnow()
        )
        
        # 保存AI回复
        await chat_service.save_message(assistant_message)
        
        # 返回响应
        return ChatMessageResponse(
            user_message=user_message,
            assistant_message=assistant_message
        )
        
    except Exception as e:
        logger.error(f"发送消息失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"发送消息失败: {str(e)}"
        )

async def handle_websocket_message(db: Session, websocket: WebSocket, session_id: str, data: str, user_id: int) -> None:
    """
    处理 WebSocket 消息
    """
    try:
        message_data = json.loads(data)
        message_in = ChatMessageCreate(content=message_data["content"])
        
        # 发送消息并获取回复
        response = await send_message(session_id, message_in.content, str(user_id), llm_config_service.get_default_config(db, user_id))
        
        # 广播回复
        await websocket_manager.broadcast(
            session_id,
            json.dumps({
                "type": "message",
                "data": {
                    "user_message": response.user_message.dict(),
                    "assistant_message": response.assistant_message.dict()
                }
            })
        )
    except Exception as e:
        # 发送错误消息
        await websocket.send_text(json.dumps({
            "type": "error",
            "data": str(e)
        }))

async def chat_with_ai(db: Session, user_id: int, chat_request: ChatRequest) -> ChatResponse:
    """
    与AI进行聊天
    """
    try:
        # 获取或创建会话
        session_id = chat_request.session_id
        user_message = chat_request.message
        
        if not session_id:
            # 使用消息的前20个字符作为会话标题
            title = user_message[:20] + "..." if len(user_message) > 20 else user_message
            db_session = await create_session(
                db,
                session_in=ChatSessionCreate(title=title),
                user_id=user_id
            )
            session_id = db_session.id
        else:
            # 获取现有会话
            db_session = get_session_by_id(db, session_id)
            if not db_session or db_session.user_id != user_id:
                raise ValueError("无效的会话ID")
            
            # 更新会话时间戳
            update_session(db, db_session, db_session.title)
        
        # 保存用户消息
        user_message_obj = create_message(db, session_id=session_id, content=user_message, role="user")
        
        # 获取会话历史消息
        messages = get_messages_by_session(db, session_id)
        
        # 准备消息历史
        message_history = [
            {"role": msg.role, "content": msg.content}
            for msg in messages[-10:] # 最多获取最近10条消息
        ]
        
        # 获取默认 LLM 配置
        llm_config = llm_config_service.get_default_config(db, user_id)
        if not llm_config:
            raise ValueError("未找到可用的 LLM 配置")
        
        # 获取智能体服务
        agent_service = get_agent_service(
            agent_type="customer_service",
            llm_provider=llm_config.provider,
            model_key=llm_config.model_name
        )
        
        # 调用智能体服务获取回复
        assistant_response = ""
        async for chunk in agent_service.chat_stream(
            messages=message_history,
            user_id=user_id
        ):
            assistant_response += chunk
        
        # 创建助手消息
        assistant_message_obj = create_message(db, session_id=session_id, content=assistant_response, role="assistant")
        
        return ChatResponse(
            message=assistant_response,
            session_id=str(session_id)
        )
        
    except Exception as e:
        raise ValueError(f"聊天过程中发生错误: {str(e)}")

class ChatService:
    def __init__(self):
        self.active_sessions: dict = {}

    async def save_message(self, message: ChatMessage) -> None:
        """
        保存消息到数据库
        """
        db = next(get_db())
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

    async def get_session_messages(self, session_id: str) -> List[ChatMessage]:
        """
        获取会话的所有消息
        """
        db = next(get_db())
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