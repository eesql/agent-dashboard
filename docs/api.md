# API 文档

## 基础信息

- Base URL: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs` (Swagger UI)
- ReDoc: `http://localhost:8000/redoc`

## 认证

当前版本无需认证。后续版本可能支持 API Key 或 OAuth2。

## 端点列表

### Agents

#### GET /api/agents

获取所有 Agent 状态列表。

**响应示例:**
```json
[
  {
    "id": "agent-123",
    "name": "feishu-agent-dev",
    "status": "online",
    "current_task": "Processing user request",
    "last_seen": "2026-03-08T08:00:00Z",
    "created_at": "2026-03-01T00:00:00Z",
    "updated_at": "2026-03-08T08:00:00Z"
  }
]
```

#### GET /api/agents/{agent_id}

获取单个 Agent 详情。

**路径参数:**
- `agent_id` (string): Agent ID

**响应:** Agent 对象

#### POST /api/agents/sync

从 OpenClaw API 同步 Agent 状态。

**响应示例:**
```json
{
  "synced": 3,
  "agents": [...]
}
```

---

### Sessions

#### GET /api/sessions

获取会话列表。

**查询参数:**
- `limit` (integer, default: 50): 返回数量限制
- `agent_id` (string, optional): 按 Agent 过滤

**响应示例:**
```json
{
  "sessions": [...],
  "total": 10
}
```

#### GET /api/sessions/{session_id}

获取会话详情。

---

### Tool Calls

#### GET /api/tool-calls

获取工具调用日志。

**查询参数:**
- `session_id` (string, optional): 按会话过滤
- `limit` (integer, default: 50): 返回数量限制
- `hours` (integer, default: 24): 时间范围（小时）

**响应示例:**
```json
{
  "tool_calls": [...],
  "total": 50
}
```

---

### Metrics

#### GET /api/metrics/summary

获取统计汇总。

**响应示例:**
```json
{
  "today": {
    "token_count": 10000,
    "request_count": 50,
    "estimated_cost": 0.02
  },
  "this_week": {...},
  "this_month": {...},
  "total_agents": 5,
  "active_agents": 3
}
```

#### GET /api/metrics/today

获取今日统计。

---

## 错误响应

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## WebSocket (待实现)

实时推送 Agent 状态变化。

### 连接
```
ws://localhost:8000/ws
```

### 消息格式
```json
{
  "type": "agent:status",
  "data": {
    "id": "agent-123",
    "status": "busy",
    "current_task": "..."
  }
}
```
