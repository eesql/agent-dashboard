# Agent Dashboard - Claude 上下文

## 项目概述

OpenClaw Agent 状态和行为可视化监控面板。

## 技术栈

**后端**
- FastAPI + Uvicorn
- SQLAlchemy + SQLite (异步)
- Pydantic v2
- HTTPX (OpenClaw API 客户端)

**前端**
- React 18 + Vite
- TypeScript
- Tailwind CSS
- Zustand (状态管理)
- Recharts (图表)
- Lucide React (图标)
- date-fns (日期处理)

## 项目结构

```
agent-dashboard/
├── backend/
│   ├── app/
│   │   ├── api/          # API 路由
│   │   ├── db/           # 数据库配置
│   │   ├── models/       # SQLAlchemy 模型
│   │   ├── schemas/      # Pydantic Schema
│   │   ├── services/     # 业务逻辑
│   │   ├── config.py     # 配置
│   │   └── main.py       # 应用入口
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/   # React 组件
│       ├── pages/        # 页面
│       ├── stores/       # Zustand stores
│       ├── services/     # API 服务
│       ├── types/        # TypeScript 类型
│       ├── utils/        # 工具函数
│       └── styles/       # 样式
└── docker-compose.yml
```

## 开发规范

### 命名规范
- 变量：camelCase (语义化命名)
- 常量：UPPER_SNAKE_CASE
- 组件：PascalCase
- 文件：kebab-case (组件用 PascalCase)

### 代码风格
- 单一职责原则
- DRY (Don't Repeat Yourself)
- 函数名用动词，变量名用名词
- 使用卫语句，避免深层嵌套

### Git 提交
- feat: 新功能
- fix: 修复 bug
- docs: 文档更新
- style: 代码格式
- refactor: 重构
- test: 测试
- chore: 构建/工具

## 常用命令

### 后端
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python app/main.py
```

### 前端
```bash
cd frontend
npm install
npm run dev
```

## API 端点

- `GET /api/agents` - 获取所有 Agent
- `GET /api/agents/:id` - 获取单个 Agent
- `POST /api/agents/sync` - 同步 Agent 状态
- `GET /api/sessions` - 获取会话列表
- `GET /api/tool-calls` - 获取工具调用日志
- `GET /api/metrics/summary` - 获取统计汇总

## 设计规范

参考 `frontend/src/styles/variables.css` 和 `frontend/tailwind.config.js`

- 主色：靛蓝 (#6366F1)
- 暗色模式优先
- 间距基准：8px
- 圆角：4-6px (工具类应用)

## 注意事项

1. 后端使用异步 SQLAlchemy (aiosqlite)
2. 前端使用 Tailwind CSS，不要写内联样式
3. 状态管理使用 Zustand
4. API 请求统一在 `services/api.ts` 封装
5. 所有组件必须是 TypeScript + React.FC
