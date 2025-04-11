from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.logging import logger

# 创建数据库引擎
# connect_args 用于处理特定数据库的连接参数，例如 SQLite 的 check_same_thread
engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI), 
    pool_pre_ping=True, # 检查连接有效性
    # connect_args={"check_same_thread": False} # 仅在 SQLite 时需要
)

# 创建 SessionLocal 类，用于创建数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    获取数据库会话的生成器函数
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"数据库会话错误: {str(e)}")
        raise
    finally:
        db.close() 