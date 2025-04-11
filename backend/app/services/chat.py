from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import WebSocket
import json
from datetime import datetime

from app.models.chat import Session as ChatSession, Message
from app.schemas.chat import ChatSessionCreate, ChatMessageCreate, ChatMessageResponse, ChatRequest, ChatResponse
from app.services.agent_service import get_agent_service
from app.services.llm_config_service import llm_config_service

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

def get_sessions_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[ChatSession]:
    """
    获取用户的所有会话
    """
    return db.query(ChatSession).filter(
        ChatSession.user_id == user_id
    ).order_by(
        ChatSession.updated_at.desc()
    ).offset(skip).limit(limit).all()

def get_session_by_id(db: Session, session_id: str) -> Optional[ChatSession]:
    """
    获取特定会话
    """
    return db.query(ChatSession).filter(ChatSession.id == session_id).first()

async def create_session(
    db: Session,
    session_in: ChatSessionCreate,
    user_id: int
) -> ChatSession:
    """创建新的聊天会话"""
    # 获取用户的默认LLM配置
    default_config = llm_config_service.get_default_config(db, user_id)
    
    # 创建会话记录
    db_session = ChatSession(
        title=session_in.title,
        user_id=user_id,
        llm_config_id=default_config.id if default_config else None
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def update_session(db: Session, session: ChatSession, title: str) -> ChatSession:
    """
    更新会话
    """
    session.title = title
    db.commit()
    db.refresh(session)
    return session

def delete_session(db: Session, session: ChatSession) -> None:
    """
    删除会话
    """
    db.delete(session)
    db.commit()

def get_messages_by_session(db: Session, session_id: str, skip: int = 0, limit: int = 100) -> List[Message]:
    """
    获取会话的所有消息
    """
    return db.query(Message).filter(
        Message.session_id == session_id
    ).order_by(
        Message.created_at.asc()
    ).offset(skip).limit(limit).all()

def create_message(db: Session, session_id: str, content: str, role: str) -> Message:
    """
    创建新消息
    """
    db_message = Message(
        session_id=session_id,
        content=content,
        role=role
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

async def send_message(db: Session, session_id: str, message_in: ChatMessageCreate, user_id: int) -> ChatMessageResponse:
    """
    发送消息并获取回复
    """
    # 创建用户消息
    user_message = create_message(db, session_id, message_in.content, "user")
    
    # 获取默认 LLM 配置
    llm_config = llm_config_service.get_default_config(db, user_id)
    if not llm_config:
        raise ValueError("未找到可用的 LLM 配置")
    
    # 获取会话历史消息
    messages = get_messages_by_session(db, session_id)
    
    # 准备消息历史
    message_history = [
        {"role": msg.role, "content": msg.content}
        for msg in messages[-10:] # 最多获取最近10条消息
    ]
    
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
    assistant_message = create_message(db, session_id, assistant_response, "assistant")
    
    return ChatMessageResponse(
        user_message=user_message,
        assistant_message=assistant_message
    )

async def handle_websocket_message(db: Session, websocket: WebSocket, session_id: str, data: str, user_id: int) -> None:
    """
    处理 WebSocket 消息
    """
    try:
        message_data = json.loads(data)
        message_in = ChatMessageCreate(content=message_data["content"])
        
        # 发送消息并获取回复
        response = await send_message(db, session_id, message_in, user_id)
        
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