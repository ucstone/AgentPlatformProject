# 智能体综合应用平台

企业级多智能体应用平台，支持多种智能体服务场景，前后端分离，系统可扩展性强、界面现代、体验流畅。

## 项目结构

```
.
├── frontend/          # 前端项目
├── backend/          # 后端项目
└── README.md         # 项目说明文档
```

## 技术栈

### 前端

- React + Vite
- TailwindCSS
- React Router
- shadcn/ui
- Framer Motion

### 后端

- Python 3.10+
- FastAPI
- Milvus
- MinIO
- MySQL

## 快速开始

### 前端开发

```bash
cd frontend
npm install
npm run dev
```

### 后端开发

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

## 功能模块

1. 智能客服智能体
2. Text2SQL 数据分析智能体
3. 企业知识库问答智能体
4. 企业文案创作智能体
