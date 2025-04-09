from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title="智能体综合应用平台",
    description="企业级多智能体应用平台 API",
    version="1.0.0"
)

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
    chat,
    text2sql,
    knowledge_base,
    content_creation
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(chat.router, prefix="/api/chat", tags=["智能客服"])
app.include_router(text2sql.router, prefix="/api/text2sql", tags=["Text2SQL"])
app.include_router(knowledge_base.router, prefix="/api/knowledge", tags=["知识库"])
app.include_router(content_creation.router, prefix="/api/content", tags=["文案创作"]) 