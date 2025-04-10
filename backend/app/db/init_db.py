from sqlalchemy.orm import Session
from app.db import base  # noqa: F401 - 让 SQLAlchemy 能发现模型
from app.db.session import engine

# 确保所有继承自 Base 的模型都被导入，SQLAlchemy 才能找到它们。
# 虽然这里没有直接使用 User，但导入 base 会间接导入它。


def init_db() -> None:
    # 在这里创建所有表
    # 在生产环境中，你可能更愿意使用 Alembic 进行数据库迁移
    print("正在尝试创建数据库表...")
    try:
        base.Base.metadata.create_all(bind=engine)
        print("数据库表创建（或已存在）成功。")
    except Exception as e:
        print(f"创建数据库表时出错: {e}")
        raise

# 你可以创建一个单独的脚本来调用这个函数，或者在应用启动时调用它（用于开发）
# 例如，在 main.py 中添加:
# @app.on_event("startup")
# def on_startup():
#     init_db() 