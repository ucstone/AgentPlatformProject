from sqlalchemy.orm import Session
from app.db import base  # noqa: F401 - 让 SQLAlchemy 能发现模型
from app.db.session import engine, SessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from app.models.llm_config import LLMConfig

# 确保所有继承自 Base 的模型都被导入，SQLAlchemy 才能找到它们。
# 虽然这里没有直接使用 User，但导入 base 会间接导入它。

# 导入聊天相关服务
from app.services.chat import create_session, create_message

def init_db(db: Session) -> None:
    """
    初始化数据库，创建所有表
    """
    # 在这里创建所有表
    # 在生产环境中，你可能更愿意使用 Alembic 进行数据库迁移
    print("正在尝试创建数据库表...")
    try:
        base.Base.metadata.create_all(bind=engine)
        print("数据库表创建（或已存在）成功。")
    except Exception as e:
        print(f"创建数据库表时出错: {e}")
        raise

    # 检查是否存在 LLM 配置
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