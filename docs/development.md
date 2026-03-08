# 开发指南

## 环境要求

- Python 3.10+
- Node.js 18+
- Git

## 开发环境设置

### 1. 克隆项目

```bash
cd C:\Users\murky\.openclaw\workspace-dev\agent-dashboard
```

### 2. 后端设置

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置 OpenClaw API 配置

# 启动开发服务器
python app/main.py
```

后端运行在：http://localhost:8000
API 文档：http://localhost:8000/docs

### 3. 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端运行在：http://localhost:5173

### 4. 快速启动脚本

Windows:
```bash
scripts\dev.bat
```

## 代码规范

### Python

- 使用 Black 格式化代码
- 使用 Flake8 检查代码风格
- 遵循 PEP 8

```bash
# 格式化
black app/

# 检查
flake8 app/
```

### TypeScript/React

- 使用 ESLint 检查代码
- 遵循 TypeScript 严格模式
- 组件使用函数式 + Hooks

```bash
cd frontend
npm run lint
```

## 测试

### 后端测试

```bash
cd backend
pytest
pytest --cov=app  # 带覆盖率
```

### 前端测试

```bash
cd frontend
npm test
```

## 目录约定

### 后端

- `app/api/` - API 路由（按资源分文件）
- `app/models/` - SQLAlchemy 模型
- `app/schemas/` - Pydantic Schema
- `app/services/` - 业务逻辑
- `app/db/` - 数据库配置

### 前端

- `src/components/ui/` - 通用 UI 组件
- `src/components/dashboard/` - Dashboard 专用组件
- `src/pages/` - 页面组件
- `src/stores/` - Zustand stores
- `src/services/` - API 服务
- `src/types/` - TypeScript 类型定义

## 调试技巧

### 后端调试

1. 启用 DEBUG 模式：`.env` 中设置 `DEBUG=true`
2. 查看日志：控制台输出
3. 使用 Swagger UI 测试 API：http://localhost:8000/docs

### 前端调试

1. React DevTools 检查组件状态
2. 网络面板查看 API 请求
3. 控制台查看错误日志

## 常见问题

### 后端启动失败

1. 检查 Python 版本：`python --version` (需要 3.10+)
2. 检查虚拟环境是否激活
3. 检查端口是否被占用：`netstat -ano | findstr :8000`

### 前端启动失败

1. 检查 Node.js 版本：`node --version` (需要 18+)
2. 删除 `node_modules` 重新安装：`rm -rf node_modules && npm install`
3. 检查端口是否被占用

### API 请求失败

1. 检查后端是否运行
2. 检查 CORS 配置
3. 查看浏览器控制台和网络面板

## 部署

详见 [deployment.md](./deployment.md)
