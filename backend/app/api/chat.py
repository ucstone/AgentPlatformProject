from fastapi import APIRouter, Depends, HTTPException, status, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json
import asyncio
import uuid

from app.db.deps import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.chat import Session as ChatSession, Message
from app.schemas.chat import (
    Session as SessionSchema,
    Message as MessageSchema,
    MessageCreate,
    ChatSessionCreate,
    ChatMessage,
    ChatMessageCreate,
    ChatMessageResponse,
    SessionCreate,
    SessionUpdate,
    ChatRequest,
    ChatResponse
)
from app.services import chat as chat_service
from app.services.agent_service import get_agent_service, AgentType
from app.core.config import settings

router = APIRouter(prefix="/chat", tags=["聊天"])


@router.get("/health")
def health_check():
    """
    API健康检查接口
    """
    return {"status": "ok", "message": "聊天服务正常运行"}


@router.post("/send", response_model=ChatResponse)
async def send_message(
    chat_request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ChatResponse:
    """
    发送消息给AI并获取回复
    """
    try:
        return await chat_service.chat_with_ai(db, current_user.id, chat_request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"聊天服务发生错误: {str(e)}"
        )


@router.get("/sessions", response_model=List[SessionSchema])
def get_sessions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[SessionSchema]:
    """
    获取当前用户的所有聊天会话
    """
    return chat_service.get_sessions_by_user(db, current_user.id, skip, limit)


@router.post("/sessions", response_model=SessionSchema, status_code=status.HTTP_201_CREATED)
def create_session(
    session_in: SessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> SessionSchema:
    """
    创建新的聊天会话
    """
    return chat_service.create_session(db, session_in.title, current_user.id)


@router.get("/sessions/{session_id}", response_model=SessionSchema)
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> SessionSchema:
    """
    获取特定的聊天会话
    """
    session = chat_service.get_session_by_id(db, session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在或无权访问"
        )
    return session


@router.put("/sessions/{session_id}", response_model=SessionSchema)
def update_session(
    session_id: str,
    session_in: SessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> SessionSchema:
    """
    更新聊天会话
    """
    session = chat_service.get_session_by_id(db, session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在或无权访问"
        )
    return chat_service.update_session(db, session, session_in)


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """
    删除聊天会话
    """
    session = chat_service.get_session_by_id(db, session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在或无权访问"
        )
    chat_service.delete_session(db, session)


@router.get("/sessions/{session_id}/messages", response_model=List[MessageSchema])
def get_messages(
    session_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[MessageSchema]:
    """
    获取会话中的消息
    """
    try:
        # 验证session_id是否为有效的UUID
        try:
            uuid.UUID(session_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="无效的会话ID格式"
            )
        
        session = chat_service.get_session_by_id(db, session_id)
        if not session or session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在或无权访问"
            )
        return chat_service.get_messages_by_session(db, session_id, skip, limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取消息失败: {str(e)}"
        )


@router.post("/sessions/{session_id}/messages", response_model=MessageSchema)
def send_message(
    session_id: str,
    message_in: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> MessageSchema:
    """
    在会话中发送消息
    """
    try:
        # 验证session_id是否为有效的UUID
        try:
            uuid.UUID(session_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="无效的会话ID格式"
            )
        
        session = chat_service.get_session_by_id(db, session_id)
        if not session or session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在或无权访问"
            )
        return chat_service.create_message(db, session_id, message_in.content, "user")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"发送消息失败: {str(e)}"
        )


@router.post("/stream", response_class=StreamingResponse)
async def stream_chat(
    chat_request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    以流式方式与AI聊天
    """
    try:
        # 获取或创建会话
        session_id = chat_request.session_id
        user_message = chat_request.message
        
        if not session_id:
            # 使用消息的前20个字符作为会话标题
            title = user_message[:20] + "..." if len(user_message) > 20 else user_message
            db_session = chat_service.create_session(db, title=title, user_id=current_user.id)
            session_id = db_session.id
        else:
            # 获取现有会话
            db_session = chat_service.get_session_by_id(db, session_id)
            if not db_session or db_session.user_id != current_user.id:
                raise ValueError("无效的会话ID")
            
            # 更新会话时间戳
            chat_service.update_session(db, db_session, db_session.title)
        
        # 保存用户消息
        chat_service.create_message(db, session_id=session_id, content=user_message, role="user")
        
        # 获取会话历史消息
        messages = chat_service.get_messages_by_session(db, session_id)
        
        # 准备消息历史
        message_history = [
            {"role": msg.role, "content": msg.content}
            for msg in messages[-10:] # 最多获取最近10条消息
        ]
        
        # 确保已设置默认的LLM提供商和模型
        llm_provider = settings.DEFAULT_LLM_PROVIDER
        llm_model = settings.DEFAULT_LLM_MODEL
        
        # 如果没有配置API密钥，默认使用mock模式
        if not settings.OPENAI_API_KEY and llm_provider == "openai":
            llm_provider = "mock"
            print("未配置OpenAI API密钥，使用模拟模式")
        
        # 流式聊天处理函数
        async def generate_stream():
            # 发送会话ID
            yield f"data: {json.dumps({'session_id': session_id})}\n\n"
            
            # 存储完整回复以便后续保存
            full_response = ""
            
            # 尝试使用智能体服务
            try:
                # 创建智能体服务
                agent_service = get_agent_service(
                    agent_type=AgentType.CUSTOMER_SERVICE,
                    llm_provider=llm_provider,
                    model_key=llm_model
                )
                
                # 流式生成回复
                async for chunk in agent_service.chat_stream(
                    message_history,
                    user_id=current_user.id  # 添加user_id参数
                ):
                    full_response += chunk
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                    await asyncio.sleep(0.01)  # 添加小延迟确保前端接收流畅
            except Exception as e:
                # 智能体服务失败，回退到标准聊天服务
                error_msg = f"智能体服务失败，正在使用标准服务: {str(e)}"
                print(f"[智能体错误] {error_msg}")
                
                # 使用ChatRequest对象
                try:
                    response = await chat_service.chat_with_ai(db, current_user.id, chat_request)
                    full_response = response.message
                    # 模拟流式输出
                    words = full_response.split()
                    for i, word in enumerate(words):
                        yield f"data: {json.dumps({'chunk': word + ' '})}\n\n"
                        if i < len(words) - 1:  # 不是最后一个词
                            await asyncio.sleep(0.05)  # 添加延迟模拟打字效果
                except Exception as inner_e:
                    error_msg = f"标准聊天服务也失败了: {str(inner_e)}"
                    full_response = error_msg
                    yield f"data: {json.dumps({'error': error_msg})}\n\n"
            
            # 保存助手回复（如果尚未保存）
            chat_service.create_message(db, session_id=session_id, content=full_response, role="assistant")
            
            # 发送结束标记
            yield f"data: {json.dumps({'done': True})}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"聊天服务发生错误: {str(e)}"
        )


@router.post("/providers", response_model=Dict[str, Any])
async def get_available_providers(
    current_user: User = Depends(get_current_user)
):
    """
    获取可用的LLM提供商和模型
    """
    # 检查用户权限
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
        
    return {
        "providers": {
            "openai": ["default", "gpt4"],
            "deepseek": ["default"],
            "ollama": ["default", "mistral"]
        },
        "current": {
            "provider": settings.DEFAULT_LLM_PROVIDER,
            "model": settings.DEFAULT_LLM_MODEL
        }
    }


@router.post("/stop", status_code=status.HTTP_200_OK)
async def stop_generation(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    停止消息生成 (目前仅为占位API，实际停止功能需要前端处理)
    """
    # 验证会话存在且属于当前用户
    return {"success": True, "message": "已发送停止信号"}


@router.websocket("/sessions/{session_id}/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    WebSocket 端点，用于实时聊天
    """
    session = chat_service.get_session_by_id(db, session_id)
    if not session or session.user_id != current_user.id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await chat_service.websocket_manager.connect(websocket, session_id)
    try:
        while True:
            data = await websocket.receive_text()
            await chat_service.handle_websocket_message(db, websocket, session_id, data, current_user.id)
    except WebSocketDisconnect:
        chat_service.websocket_manager.disconnect(websocket, session_id) 