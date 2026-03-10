# Agent Dashboard 测试指南

## 后端测试 (Python/FastAPI)

### 安装依赖

```bash
cd backend
pip install pytest pytest-asyncio httpx
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_api.py

# 运行特定测试类
pytest tests/test_api.py::TestSessionsAPI

# 运行特定测试函数
pytest tests/test_api.py::TestSessionsAPI::test_list_sessions

# 详细输出
pytest -v

# 带覆盖率报告
pytest --cov=app --cov-report=html
```

### 测试覆盖

- `TestAgentsAPI` - Agent 相关 API 端点
- `TestSessionsAPI` - Session 相关 API 端点
- `TestToolCallsAPI` - ToolCall 相关 API 端点
- `TestMetricsAPI` - Metrics 相关 API 端点
- `TestHealthCheck` - 健康检查端点

---

## 前端测试 (React/Vitest)

### 安装依赖

```bash
cd frontend
npm install
```

### 运行测试

```bash
# 运行所有测试（监视模式）
npm test

# 运行所有测试（单次）
npm run test:run

# 运行特定测试文件
npx vitest run src/tests/api.test.ts

# 运行匹配文件名的测试
npx vitest run --reporter=verbose
```

### 测试覆盖

- `agentApi` - Agent API 调用
- `sessionApi` - Session API 调用
- `toolCallApi` - ToolCall API 调用
- `metricsApi` - Metrics API 调用
- `messageApi` - Message API 调用

---

## CI/CD 集成

### GitHub Actions 示例

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r backend/requirements.txt
      - run: pip install pytest pytest-asyncio httpx
      - run: pytest backend/tests/ -v

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '22'
      - run: cd frontend && npm install
      - run: cd frontend && npm run test:run
```

---

## 开发流程

1. **开发新功能** → 编写对应测试用例
2. **修改代码** → 运行相关测试
3. **提交前** → 运行全部测试确保通过
4. **推送后** → CI 自动运行测试

---

## 常见问题

### 后端测试失败

1. 确保数据库文件存在：`backend/agent_dashboard.db`
2. 确保依赖已安装：`pip install -r requirements.txt`
3. 检查 pytest 配置：`backend/pytest.ini`

### 前端测试失败

1. 确保依赖已安装：`npm install`
2. 检查 vite 配置中的 test 部分
3. 清除缓存：`rm -rf node_modules && npm install`
