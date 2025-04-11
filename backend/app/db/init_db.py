from sqlalchemy.orm import Session
from app.db import base  # noqa: F401 - 让 SQLAlchemy 能发现模型
from app.db.session import engine, SessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from app.models.llm_config import LLMConfig
from app.core.config import settings
from app.models.session import ChatSession
from app.models.message import ChatMessage
from app.services.llm_config_service import llm_config_service
from sqlalchemy import inspect, text
from datetime import datetime

# 确保所有继承自 Base 的模型都被导入，SQLAlchemy 才能找到它们。
# 虽然这里没有直接使用 User，但导入 base 会间接导入它。

# 导入聊天相关服务
from app.services.chat import create_session, create_message

def check_and_add_missing_columns(db: Session) -> None:
    """
    检查并添加缺失的列
    """
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if "users" in tables:
        columns = [col['name'] for col in inspector.get_columns("users")]
        
        # 检查并添加 created_at 列
        if "created_at" not in columns:
            print("添加 created_at 列到 users 表...")
            db.execute(text("ALTER TABLE users ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP"))
        
        # 检查并添加 updated_at 列
        if "updated_at" not in columns:
            print("添加 updated_at 列到 users 表...")
            db.execute(text("ALTER TABLE users ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
        
        db.commit()
        print("列检查完成。")

def init_db(db: Session) -> None:
    """
    初始化数据库，创建所有表
    """
    # 创建所有表
    print("正在创建数据库表...")
    try:
        base.Base.metadata.create_all(bind=engine)
        print("数据库表创建成功。")
    except Exception as e:
        print(f"创建数据库表时出错: {e}")
        raise

    # 检查并添加缺失的列
    check_and_add_missing_columns(db)

    # 检查 LLM 配置
    check_llm_config(db)

def check_llm_config(db: Session) -> None:
    """
    检查数据库中是否存在 LLM 配置
    如果没有配置，则打印提示信息
    """
    llm_config_count = db.query(LLMConfig).count()
    if llm_config_count == 0:
        print("\n" + "="*80)
        print("警告：数据库中没有任何 LLM 配置！")
        print("请先通过 API 添加至少一个 LLM 配置，否则聊天功能将无法使用。")
        print("可以使用以下 API 添加配置：")
        print("POST /api/v1/llm-configs/")
        print("请求体示例：")
        print('''{
    "name": "默认配置",
    "provider": "openai",
    "model_name": "gpt-3.5-turbo",
    "api_key": "your-api-key",
    "api_base_url": "https://api.openai.com/v1",
    "is_default": true
}''')
        print("="*80 + "\n")

# 你可以创建一个单独的脚本来调用这个函数，或者在应用启动时调用它（用于开发）
# 例如，在 main.py 中添加:
# @app.on_event("startup")
# def on_startup():
#     init_db() 