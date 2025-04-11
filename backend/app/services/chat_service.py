from datetime import datetime
from sqlalchemy.orm import Session
from backend.models.session import Session as SessionModel
from backend.schemas.session import Session as SessionSchema

def create_session(db: Session, title: str, user_id: int) -> SessionSchema:
    """
    创建新的聊天会话
    """
    # 检查标题是否已存在，如果存在则添加后缀
    base_title = title
    final_title = base_title
    counter = 1
    while db.query(SessionModel).filter(SessionModel.title == final_title, SessionModel.user_id == user_id).first():
        final_title = f"{base_title}-{counter}"
        counter += 1
    
    db_session = SessionModel(
        title=final_title,
        user_id=user_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return SessionSchema.from_orm(db_session) 