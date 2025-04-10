# 这个文件用于方便地导入所有模型，以便 Alembic 或其他工具可以找到它们

from app.db.base_class import Base # 导入 Base
# 导入所有的模型 (目前还没有，后面会创建 User 模型)
from app.models.user import User  # noqa 