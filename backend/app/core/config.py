from pydantic_settings import BaseSettings
from pydantic import validator, AnyUrl
from typing import List, Optional
import os
from dotenv import load_dotenv
import secrets
from urllib.parse import urlparse

load_dotenv()

class Settings(BaseSettings):
    # 基础配置
    PROJECT_NAME: str = "智能体综合应用平台"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")  # 默认为开发环境
    
    # CORS 配置
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # 前端开发服务器
        "http://localhost:8000",  # 后端开发服务器
        "http://localhost:5173",  # Vite 开发服务器
        "http://127.0.0.1:5173",  # Vite 开发服务器 (IP 地址)
        "http://localhost:5174",  # Vite 开发服务器 (备用端口)
        "http://127.0.0.1:5174",  # Vite 开发服务器 (备用端口 IP 地址)
    ]
    
    # 数据库配置
    MYSQL_USER: str = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD")
    MYSQL_HOST: str = os.getenv("MYSQL_HOST")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT"))
    MYSQL_DB: str = os.getenv("MYSQL_DB")
    
    # 构建 SQLAlchemy 数据库连接 URL (DSN)
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        if isinstance(v, str):
            return v
        # 使用 PyMySQL 驱动
        # 将 AnyUrl 对象转换为字符串再返回
        return str(AnyUrl.build(
            scheme="mysql+pymysql",
            username=values.get("MYSQL_USER"),
            password=values.get("MYSQL_PASSWORD"),
            host=values.get("MYSQL_HOST"),
            port=values.get("MYSQL_PORT"),
            path=values.get('MYSQL_DB') or '',
        ))
    
    # Milvus 配置
    MILVUS_HOST: str = os.getenv("MILVUS_HOST", "localhost")
    MILVUS_PORT: int = int(os.getenv("MILVUS_PORT", "19530"))
    
    # MinIO 配置
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_BUCKET_NAME: str = os.getenv("MINIO_BUCKET_NAME", "agent-platform")
    
    # JWT 配置
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    
    # OpenAI 配置
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_API_BASE: str = os.getenv("OPENAI_API_BASE", "")
    
    # DeepSeek 配置
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    
    # Ollama 配置
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    
    # 智能体配置
    DEFAULT_LLM_PROVIDER: str = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
    DEFAULT_LLM_MODEL: str = os.getenv("DEFAULT_LLM_MODEL", "default")
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings() 