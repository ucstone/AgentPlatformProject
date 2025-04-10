# 项目交接文档大纲：智能体综合应用平台

**1. 项目概述 (Project Overview)**

- **1.1 项目名称:** 智能体综合应用平台 (Intelligent Agent Comprehensive Application Platform)
- **1.2 项目目标:** 构建一个企业级的多智能体应用平台，旨在集成和支持多种智能服务场景（如智能客服、数据分析、知识问答、内容创作等），提供统一的管理界面和可扩展的智能体能力。
- **1.3 核心价值:** 提高企业运营效率，赋能业务创新，提供智能化解决方案。
- **1.4 整体架构:**
  - 前后端分离架构。
  - 前端：负责用户界面展示、用户交互、API 请求。
  - 后端：负责业务逻辑处理、API 服务、数据存储、智能体核心能力集成与调度。

**2. 技术栈 (Technology Stack)**

- **2.1 前端 (Frontend):**
  - 构建工具: Vite
  - 框架: React (v18.2)
  - 语言: TypeScript
  - 路由: React Router DOM (v6)
  - 状态管理: React Context API (用于主题管理), `useState` (组件级状态), (未来可考虑引入 Zustand 或 Redux 进行复杂状态管理)
  - UI 库/组件: 基于 Shadcn/ui 风格手动构建 (包括 Button, Input, Label, Avatar, DropdownMenu, Toast 等)
  - 样式: Tailwind CSS, PostCSS, `tailwindcss-animate`
  - 代码规范: ESLint, Prettier (配置文件已创建)
- **2.2 后端 (Backend):**
  - 框架: FastAPI (Python)
  - 语言: Python (建议注明版本，如 3.10+)
  - Web 服务器: Uvicorn
  - 数据库: **MySQL 8.0 (通过 Docker Compose 运行)**
  - ORM: **SQLAlchemy**
  - 数据库驱动: **PyMySQL**
  - 密码哈希: **Passlib (with bcrypt)**
  - 环境配置: **python-dotenv, Pydantic-Settings**
  - 认证: (待定 - 计划使用 JWT)
  - 代码规范: Ruff, Black (建议配置)
- **2.3 版本控制:** Git
- **2.4 容器化:** Docker, Docker Compose (用于运行数据库)

**3. 项目设置与启动 (Project Setup & Running)**

- **3.1 环境要求:**
  - Node.js (建议注明版本，如 v18+) 和 npm/yarn/pnpm
  - Python (建议注明版本，如 3.10+) 和 pip (或 uv)
  - Git
  - **Docker 和 Docker Compose (或 OrbStack 等替代品)**
- **3.2 数据库启动 (首次):**
  - 在**项目根目录**下，确保 `docker-compose.yml` 中的密码已修改为强密码。
  - 运行 `docker-compose up -d` 启动 MySQL 容器。
- **3.3 后端设置:**
  - `cd backend`
  - 创建虚拟环境: `python -m venv venv` (或 `python3`)
  - 激活虚拟环境: `source venv/bin/activate` (macOS/Linux) 或 `.\venv\Scripts\activate` (Windows)
  - 安装依赖: `pip install -r requirements.txt` (或 `uv pip install ...`)
  - 配置环境变量:
    - 创建 `.env` 文件 (已忽略)
    - 填入 `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_DB` (确保密码与 `docker-compose.yml` 一致)。
    - 设置一个安全的 `SECRET_KEY`。
  - 启动开发服务器: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` (首次启动会自动创建数据库表)
- **3.4 前端设置:**
  - `cd frontend`
  - 安装依赖: `npm install`
  - 配置环境变量: (如果需要)
  - 启动开发服务器: `npm run dev`
- **3.5 环境变量详解:** (应包含后端 `.env` 中新增的数据库和 JWT 变量)

**4. 项目结构 (Project Structure)**

- **4.1 根目录:** (添加 `docker-compose.yml`)
  - `.git/`: Git 仓库元数据 (已忽略)
  - `.gitignore`: Git 忽略配置
  - `README.md`: 项目说明
  - `backend/`: 后端代码
  - `frontend/`: 前端代码
  - `HANDOVER.md`: 本交接文档
  - `docker-compose.yml`: Docker 服务定义 (数据库)
- **4.2 后端 (`backend/`) 结构:** (更新 `db` 和 `models`)
  - `app/`:
    - `api/`: API 路由模块 (e.g., `auth.py`)
    - `core/`: 配置、核心函数 (e.g., `config.py`)
    - `db/`: **数据库相关 (session.py, base_class.py, base.py, deps.py, init_db.py)**
    - `models/`: **SQLAlchemy 模型 (user.py)**
    - `services/`: (规划) 业务逻辑服务层
    - `schemas/`: (规划) Pydantic 请求/响应模型
    - `utils/`: (规划) 通用工具函数
    - `main.py`: FastAPI 应用实例和全局中间件
  - `tests/`: (规划) 测试代码
  - `venv/`: (已忽略) Python 虚拟环境
  - `requirements.txt`: Python 依赖列表
  - `.env`: (已忽略) **必需**的环境变量文件
- **4.3 前端 (`frontend/`) 结构:**
  - `node_modules/`: (已忽略) Node.js 依赖
  - `public/`: 静态资源
  - `src/`: 源代码
    - `assets/`: 图片、字体等资源
    - `components/`: 可复用组件
      - `layout/`: 页面布局组件 (Header, Sidebar, index.tsx)
      - `ui/`: 基础 UI 组件 (Button, Input, Toast, etc.)
      - `mode-toggle.tsx`: 主题切换按钮
      - `theme-provider.tsx`: 主题上下文提供者
      - `user-nav.tsx`: 用户导航菜单
    - `hooks/`: 自定义 Hooks (e.g., `use-toast.ts`)
    - `lib/`: 工具函数 (e.g., `utils.ts` for `cn`)
    - `pages/`: 页面级组件 (Home, Login, Register, Chat, Text2SQL, etc.)
    - `router/`: (可选) 路由配置 (当前在 `App.tsx`)
    - `services/`: (可选) API 请求服务封装
    - `store/`: (可选) 全局状态管理
    - `types/`: (可选) TypeScript 类型定义
    - `App.tsx`: 应用根组件、路由配置
    - `main.tsx`: 应用入口文件
    - `index.css`: 全局样式、Tailwind 指令
  - `index.html`: HTML 入口文件
  - `package.json`: 项目元数据和依赖
  - `postcss.config.js`: PostCSS 配置
  - `tailwind.config.js`: Tailwind CSS 配置
  - `tsconfig.json`, `tsconfig.node.json`: TypeScript 配置
  - `vite.config.ts`: Vite 配置
  - `.env`: (已忽略) 环境变量

**5. 当前状态与已实现功能 (Current Status & Implemented Features)**

- **5.1 整体进度:** 项目基础框架搭建完成，**后端数据库集成初步完成**。
- **5.2 后端:**
  - FastAPI 应用骨架。
  - **MySQL 数据库通过 Docker Compose 启动并运行。**
  - **SQLAlchemy ORM 集成完成，包含数据库引擎、会话管理、模型基类。**
  - **User 模型 (`models/user.py`) 已定义 (包含 id, email, hashed_password, is_active)。**
  - **通过 `.env` 和 `core/config.py` 配置数据库连接 (DSN)。**
  - **实现应用启动时自动创建数据库表 (`db/init_db.py`)。**
  - 基础配置加载 (`core/config.py`)。
  - 认证 API 路由 (`/login`, `/register` in `api/auth.py`) 已定义，但**具体逻辑未实现**。
  - CORS 中间件已配置。
- **5.3 前端:**
  - Vite + React + TypeScript 项目初始化完成。
  - Tailwind CSS 及 PostCSS 配置完成，基础样式和主题变量 (`index.css`) 已定义。
  - 路径别名 `@` 配置完成 (`vite.config.ts`)。
  - 基础路由结构 (`App.tsx`) 搭建完成，包含公共布局 (`Layout`) 和独立页面 (Login, Register)。
  - `Layout` 组件包含 `Header`, `Sidebar`, 和 `Outlet`。
  - `Header` 组件包含 Logo (占位)、`UserNav`, `ModeToggle`。
  - `Sidebar` 组件包含导航链接 (占位)。
  - `ThemeProvider` 和 `ModeToggle` 实现亮/暗主题切换。
  - 核心 UI 组件 (`components/ui/`) 已创建 (Button, Input, Label, Avatar, DropdownMenu, Toast, Toaster, use-toast)。
  - 主要页面组件 (`pages/`) 已创建骨架 (Home, Login, Register, Chat, Text2SQL, KnowledgeBase, ContentCreation)，包含基础布局，**无实际功能逻辑**。
- **5.4 版本控制:**
  - `.gitignore` 文件已配置，包含 Node.js, Python, macOS 和 IDE 的忽略规则。
  - 代码已进行初步提交。

**6. 后续开发路线图 (Future Development Roadmap)**

- **6.1 后端开发:** (更新数据库部分)
  - **数据库:** **集成完成，可进行后续开发。** (未来可考虑使用 Alembic 进行数据库迁移管理)
  - **认证:** **实现用户注册逻辑 (密码哈希) 和登录逻辑 (密码验证, JWT 生成)。**
- **6.2 前端开发:**
  - **API 集成:** 对接后端 API，实现前后端数据交互。
  - **页面逻辑:** 在 `pages/` 组件中实现具体功能逻辑（状态管理、API 调用、数据显示、用户交互）。
  - **表单处理:** 实现登录、注册表单的验证和提交。
  - **状态管理:** 对于跨组件或复杂的页面状态，考虑引入全局状态管理库 (如 Zustand)。
  - **智能体交互:** 实现各个智能体页面的交互逻辑（如聊天界面消息发送接收、Text2SQL 查询提交与结果展示等）。
  - **UI 完善:** 根据设计稿（如果有）或进一步需求细化 UI 样式和交互体验。
  - **用户体验:** 添加加载状态、错误提示 (使用已有的 Toast 组件)。
  - **测试:** 编写组件测试和端到端测试 (可选)。
- **6.3 整体规划:**
  - **智能体集成:** 明确各个智能体的具体实现方式或第三方服务。
  - **部署策略:** 规划前后端的部署方案 (e.g., Docker, K8s, Serverless)。
  - **CI/CD:** 搭建持续集成与持续部署流水线。
  - **监控与日志:** 集成监控和日志系统。

**7. 开发规范与工作流 (Development Guidelines & Workflow)**

- **7.1 分支策略:** (推荐)
  - `main`: 稳定分支，用于生产部署。
  - `develop`: 开发主分支，集成各功能特性。
  - `feature/xxx`: 功能开发分支，从 `develop` 切出，完成后合并回 `develop`。
  - `fix/xxx`: Bug 修复分支。
- **7.2 Commit 信息规范:** (推荐)
  - 遵循 Conventional Commits 规范 (e.g., `feat: add login api`, `fix: correct button style`, `docs: update README`)。
- **7.3 Code Review:**
  - 所有代码合并到 `develop` 或 `main` 分支前必须经过 Code Review。
  - 通过 GitHub Pull Request 进行。
- **7.4 编码风格:**
  - 前端: 遵循项目已配置的 ESLint 和 Prettier 规则。
  - 后端: (建议) 使用 Ruff 和 Black 进行代码格式化和检查。
- **7.5 测试要求:** (待明确)
  - 核心功能需要有单元测试覆盖。
  - 关键流程需要有集成测试。

**8. 关键模块详解 (Key Module Details)**

- **8.1 数据库 (`backend/app/db`):**
  - 使用 SQLAlchemy Core 和 ORM。
  - `session.py`: 创建 `engine` 和 `SessionLocal`。
  - `base_class.py`: 定义模型基类 `Base`，自动生成表名。
  - `base.py`: 用于导入所有模型。
  - `deps.py`: 提供 `get_db` FastAPI 依赖项用于获取会话。
  - `init_db.py`: 提供 `init_db` 函数，通过 `Base.metadata.create_all()` 创建表。
- **8.2 用户模型 (`backend/app/models/user.py`):**
  - 定义了 `users` 表的结构，包含 email、哈希密码等字段。
- **8.3 认证流程 (预期):** (需要更新，结合数据库操作)
- **8.4 UI 组件库 (`frontend/src/components/ui`):**
  - 基于 Radix UI Primitives 和 Tailwind CSS 构建，遵循 Shadcn/ui 的风格和方法。
  - 可复用、可组合、易于定制。
- **8.5 主题系统 (`frontend/src/components/theme-provider.tsx`):**
  - 使用 React Context API 和 localStorage 实现亮/暗模式切换。
  - 通过在 `<html>` 标签上添加 `dark` 类名，并结合 Tailwind 的 `darkMode: 'class'` 配置和 CSS 变量实现样式切换。
- **8.6 路由 (`frontend/src/App.tsx`):**
  - 使用 React Router DOM v6 定义路由规则。
  - 包含嵌套路由，`Layout` 作为父路由包裹需要公共布局的页面。

**9. 附录 (Appendix)**

- **9.1 相关链接:**
  - 设计稿链接 (如果有)
  - API 文档链接 (后端完成后建议使用 Swagger UI 或类似工具生成)
  - 第三方服务文档链接
- **9.2 联系人:** (如果需要)
  - 项目发起人/产品经理
  - 架构师/技术负责人

---

**给接手同事的建议:**

- 请仔细阅读本文档，理解项目背景、架构和当前状态。
- 按照文档中的步骤设置本地开发环境并成功运行前后端服务。
- 熟悉项目代码结构，特别是前后端的核心目录和文件。
- 确保本地 Docker 环境已启动 MySQL 容器 (`docker-compose up -d`)。
- 在 `backend/.env` 文件中配置正确的数据库密码和 JWT 密钥。
- 熟悉 `backend/app/db` 和 `backend/app/models` 下的 SQLAlchemy 相关代码。
- 优先实现 `backend/app/api/auth.py` 中的注册和登录数据库操作逻辑。
- 在开发新功能前，请遵循开发规范和工作流。
- **重要：在开发过程中，请持续更新本文档，确保其准确反映项目最新状态。**
