# Agent Dashboard

OpenClaw Agent 状态和行为可视化监控面板。

## 🎯 功能特性

- ✅ Agent 状态实时展示（在线/离线/忙碌/错误）
- ✅ 当前任务进度 + TODO 列表
- ✅ 会话历史列表 + 详情查看
- ✅ 工具调用日志（时间线展示）
- ✅ 资源消耗统计（Token/成本）

## 🚀 快速开始

### 前置要求

- Python 3.10+
- Node.js 18+
- Docker & Docker Compose（可选）

### 开发环境启动

#### 1. 后端启动

```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 配置 OpenClaw API

python app/main.py
```

后端服务运行在：http://localhost:8000
API 文档：http://localhost:8000/docs

#### 2. 前端启动

```bash
cd frontend
npm install
npm run dev
```

前端服务运行在：http://localhost:5173

### Docker 启动（推荐）

```bash
docker-compose up -d
```

访问：http://localhost:5173

## 📁 项目结构

```
agent-dashboard/
├── backend/           # FastAPI 后端
│   ├── app/
│   │   ├── api/      # API 路由
│   │   ├── services/ # 业务逻辑
│   │   ├── models/   # 数据模型
│   │   ├── db/       # 数据库
│   │   └── schemas/  # Pydantic 模型
│   └── tests/
├── frontend/          # React + Vite 前端
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── stores/
│       └── services/
├── docs/             # 文档
└── scripts/          # 脚本工具
```

## 🛠️ 技术栈

**后端**
- FastAPI + Uvicorn
- SQLAlchemy + SQLite
- WebSocket 实时推送

**前端**
- React 18 + Vite
- TypeScript
- Tailwind CSS
- Zustand 状态管理
- Recharts 图表

## 📖 文档

- [API 文档](./docs/api.md)
- [开发指南](./docs/development.md)
- [架构说明](./docs/architecture.md)
- [部署指南](./docs/deployment.md)

## 📝 开发规范

本项目遵循 Vibe Coding 原则：
- 先规划，后代码
- 小步迭代，每步验证
- 语义化命名
- 单一职责
- 文档先行

## 📄 License

MIT
