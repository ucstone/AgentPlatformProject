from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import json
from fastapi import HTTPException, status, WebSocket, WebSocketDisconnect

from app.models.session import ChatSession as SessionModel
from app.models.message import ChatMessage as MessageModel
from app.schemas.chat import ChatMessageCreate, ChatMessageResponse, ChatMessage, ChatRequest, ChatResponse
from app.services.agent_service import get_agent_service
from app.services.llm_config_service import llm_config_service
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

class ChatService:
    def __init__(self):
        self.active_sessions: dict = {}
        self.websocket_manager = WebSocketManager()

    async def save_message(self, message: ChatMessage) -> None:
        """
        保存消息到数据库
        """
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
        """
        获取会话的所有消息
        """
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

    async def create_session(self, db: Session, title: str, user_id: int) -> SessionModel:
        """创建新的会话"""
        try:
            print(f"开始创建会话: title={title}, user_id={user_id}")
            
            # 获取用户的默认LLM配置
            default_config = llm_config_service.get_default_config(db, user_id)
            print(f"获取默认LLM配置: {default_config}")
            
            if not default_config:
                print("未找到默认LLM配置")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="请先配置默认的LLM模型"
                )
            
            # 创建会话记录
            db_session = SessionModel(
                id=str(uuid.uuid4()),
                title=title,
                user_id=user_id,
                llm_config_id=default_config.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            print(f"创建会话记录: {db_session.__dict__}")
            
            db.add(db_session)
            db.commit()
            db.refresh(db_session)
            print(f"会话创建成功: {db_session.__dict__}")
            
            self.active_sessions[db_session.id] = {
                "user_id": user_id,
                "created_at": datetime.utcnow(),
                "messages": []
            }
            return db_session
        except Exception as e:
            print(f"创建会话失败: {str(e)}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"创建会话失败: {str(e)}"
            )

    async def get_session(self, db: Session, session_id: str) -> Optional[SessionModel]:
        """获取会话信息"""
        return db.query(SessionModel).filter(SessionModel.id == session_id).first()

    async def delete_session(self, db: Session, session_id: str) -> None:
        """删除会话"""
        try:
            session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
            if session:
                db.delete(session)
                db.commit()
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"删除会话失败: {str(e)}"
            )

    async def send_message(
        self,
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
            await self.save_message(user_message)
            
            # 获取会话历史消息
            messages = await self.get_session_messages(session_id)
            
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
            assistant_content = ""
            async for chunk in agent_service.chat_stream(
                messages=message_history,
                user_id=user_id
            ):
                assistant_content += chunk
            
            # 创建AI回复消息
            assistant_message = ChatMessage(
                id=str(uuid.uuid4()),
                session_id=session_id,
                content=assistant_content,
                role="assistant",
                created_at=datetime.utcnow()
            )
            
            # 保存AI回复
            await self.save_message(assistant_message)
            
            # 返回响应
            return ChatMessageResponse(
                user_message=user_message,
                assistant_message=assistant_message
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"发送消息失败: {str(e)}"
            )

    async def chat_with_ai(self, db: Session, user_id: int, chat_request: ChatRequest) -> ChatResponse:
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
                db_session = await self.create_session(db, title, user_id)
                session_id = db_session.id
            else:
                # 获取现有会话
                db_session = await self.get_session(db, session_id)
                if not db_session or db_session.user_id != user_id:
                    raise ValueError("无效的会话ID")
            
            # 获取默认 LLM 配置
            llm_config = llm_config_service.get_default_config(db, user_id)
            if not llm_config:
                raise ValueError("未找到可用的 LLM 配置")
            
            # 发送消息并获取回复
            response = await self.send_message(
                session_id=session_id,
                content=user_message,
                user_id=str(user_id),
                llm_config=llm_config
            )
            
            return ChatResponse(
                message=response.assistant_message.content,
                session_id=session_id
            )
            
        except Exception as e:
            raise ValueError(f"聊天过程中发生错误: {str(e)}")

    async def handle_websocket_message(self, db: Session, websocket: WebSocket, session_id: str, data: str, user_id: int) -> None:
        """
        处理 WebSocket 消息
        """
        try:
            message_data = json.loads(data)
            message_in = ChatMessageCreate(content=message_data["content"])
            
            # 发送消息并获取回复
            response = await self.send_message(
                session_id=session_id,
                content=message_in.content,
                user_id=str(user_id),
                llm_config=llm_config_service.get_default_config(db, user_id)
            )
            
            # 广播回复
            await self.websocket_manager.broadcast(
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

    def get_sessions_by_user(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[SessionModel]:
        """
        获取用户的所有会话
        """
        return db.query(SessionModel).filter(
            SessionModel.user_id == user_id
        ).order_by(
            SessionModel.updated_at.desc()
        ).offset(skip).limit(limit).all()

    def get_session_by_id(self, db: Session, session_id: str) -> Optional[SessionModel]:
        """
        获取特定会话
        """
        return db.query(SessionModel).filter(SessionModel.id == session_id).first()

    def update_session(self, db: Session, session: SessionModel, title: str) -> SessionModel:
        """
        更新会话
        """
        session.title = title
        session.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(session)
        return session

    def delete_session(self, db: Session, session: SessionModel) -> None:
        """
        删除会话
        """
        db.delete(session)
        db.commit()

    def get_messages_by_session(self, db: Session, session_id: str, skip: int = 0, limit: int = 100) -> List[MessageModel]:
        """
        获取指定会话的所有消息
        """
        return db.query(MessageModel).filter(
            MessageModel.session_id == session_id
        ).order_by(
            MessageModel.created_at.asc()
        ).offset(skip).limit(limit).all()

# 创建 ChatService 实例
chat_service = ChatService()

# 导出 WebSocket 管理器实例
websocket_manager = chat_service.websocket_manager

# 导出处理函数
handle_websocket_message = chat_service.handle_websocket_message

async def create_session(db: Session, title: str, user_id: int) -> SessionModel:
    """
    创建新的聊天会话
    """
    return await chat_service.create_session(db, title, user_id)

async def create_message(db: Session, session_id: str, content: str, role: str) -> MessageModel:
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