from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import SessionLocal
from app.db.init_db import init_db

# API 版本配置
API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{API_PREFIX}/openapi.json"
)

# 设置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # 初始化数据库
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "欢迎使用智能体综合应用平台 API"}

# 导入并注册路由
from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.llm_config import router as llm_config_router

app.include_router(auth_router, prefix=API_PREFIX, tags=["认证"])
app.include_router(chat_router, prefix=API_PREFIX, tags=["聊天"])
app.include_router(llm_config_router, prefix=f"{API_PREFIX}/llm-config", tags=["LLM配置"])

# 注册路由
# app.include_router(text2sql.router, prefix=f"{settings.API_V1_STR}/text2sql", tags=["Text2SQL"])
# app.include_router(knowledge_base.router, prefix=f"{settings.API_V1_STR}/knowledge", tags=["知识库"])
# app.include_router(content_creation.router, prefix=f"{settings.API_V1_STR}/content", tags=["文案创作"]) 