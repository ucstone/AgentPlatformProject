from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.init_db import init_db # 导入 init_db 函数

# --- 移到这里 --- 
app = FastAPI(
    title="智能体综合应用平台",
    description="企业级多智能体应用平台 API",
    version="1.0.0"
)
# --- 移到这里 --- 

# 在应用启动时初始化数据库
@app.on_event("startup")
def on_startup():
    print("FastAPI 应用启动，开始初始化数据库...")
    init_db()
    print("数据库初始化完成。")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "欢迎使用智能体综合应用平台 API"}

# 导入路由
from app.api import (
    auth,
    # chat, # 暂时注释掉，确保启动不报错
    # text2sql,
    # knowledge_base,
    # content_creation
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
# app.include_router(chat.router, prefix="/api/chat", tags=["智能客服"])
# app.include_router(text2sql.router, prefix="/api/text2sql", tags=["Text2SQL"])
# app.include_router(knowledge_base.router, prefix="/api/knowledge", tags=["知识库"])
# app.include_router(content_creation.router, prefix="/api/content", tags=["文案创作"]) 