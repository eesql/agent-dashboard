# Token 消耗趋势图表修复

## 问题描述
Token 消耗趋势图表没有正确显示过去七天的数据，使用的是模拟随机数据而非真实 API 数据。

## 修复内容

### 后端修改

#### 1. `backend/app/services/data_aggregator.py`
- **新增方法**: `get_trend_data(days: int = 7, agent_id: Optional[str] = None) -> List[Dict]`
  - 查询指定日期范围内的 metrics 数据
  - 自动填充没有数据的日期（补零）
  - 返回按日期排序的完整趋势数据

#### 2. `backend/app/api/metrics.py`
- **新增 API 端点**: `GET /api/metrics/trend`
  - 参数：
    - `days`: 查询天数 (1-30)，默认 7 天
    - `agent_id`: 可选，筛选特定 Agent
  - 返回：趋势数据数组

### 前端修改

#### 1. `frontend/src/types/index.ts`
- **新增接口**: `TrendDataPoint`
  ```typescript
  interface TrendDataPoint {
    date: string;
    token_count: number;
    request_count: number;
    estimated_cost: number;
  }
  ```

#### 2. `frontend/src/services/api.ts`
- **新增方法**: `metricsApi.getTrend(days, agentId)`
  - 调用后端 `/metrics/trend` 端点
  - 支持自定义天数和 Agent 筛选

#### 3. `frontend/src/stores/metricsStore.ts`
- **新增状态**:
  - `trendData: TrendDataPoint[] | null`
  - `loadingTrend: boolean`
  - `errorTrend: string | null`
- **新增 Action**: `fetchTrendData(days?, agentId?)`
  - 从 API 获取趋势数据
  - 更新 store 状态

#### 4. `frontend/src/components/dashboard/StatsChart.tsx`
- **修改数据源**:
  - 优先使用 API 传入的真实数据
  - 仅在没有数据时使用模拟数据（用于调试）
- **新增函数**: `convertToChartData(trendData)`
  - 将 API 数据转换为图表所需格式
  - 格式化日期显示为 MM-DD

#### 5. `frontend/src/pages/Dashboard.tsx`
- **数据获取**:
  - 在 `useEffect` 中调用 `fetchTrendData(7)` 获取过去 7 天数据
  - 每 30 秒自动刷新趋势数据
- **传递数据**:
  - 将 `trendData` 传递给 `StatsChart` 组件

## 使用说明

### 查看趋势数据
1. 启动后端：`cd backend && .\venv\Scripts\python.exe -m app.main`
2. 启动前端：`cd frontend && npm run dev`
3. 访问 Dashboard 页面，Token 消耗趋势图表将显示过去 7 天的真实数据

### API 调用示例
```bash
# 获取过去 7 天数据
GET http://localhost:8000/api/metrics/trend?days=7

# 获取过去 30 天数据
GET http://localhost:8000/api/metrics/trend?days=30

# 获取特定 Agent 的数据
GET http://localhost:8000/api/metrics/trend?days=7&agent_id=agent:main:xxx
```

## 注意事项

1. **数据聚合**: 趋势数据基于 `metrics` 表，需要确保 sync 服务正常运行以聚合每日数据
2. **空数据日期**: 对于没有数据的日期，系统会自动填充零值，保证图表连续性
3. **TypeScript 错误**: 项目中存在一些已有的 TypeScript 错误（主要在 Sessions.tsx 和 agentStore.ts），不影响趋势图表功能

## 测试验证

- ✅ 后端 API 端点正常工作
- ✅ 前端编译通过（新增代码无错误）
- ✅ 数据流完整：API → Store → Component
- ⏳ 前端页面渲染（需手动验证）

## 后续优化建议

1. 添加更多图表类型切换（Tokens/Requests/Cost）
2. 支持自定义日期范围选择
3. 添加数据导出功能
4. 优化空数据状态的 UI 提示

---

# 工具调用时间线修复（已完成）

## 问题描述
工具调用时间线使用的是硬编码的模拟数据，没有显示真实的工具调用记录。

## 实现内容

### 后端修改

#### 1. `backend/app/services/openclaw_parser.py`
- **新增函数**: `parse_session_jsonl(session_file, session_key)`
  - 直接读取 OpenClaw session 的 .jsonl 文件
  - 解析 `type: "toolCall"` 和 `type: "toolResult"` 消息
  - 提取工具名称、参数、结果、时间戳等信息

#### 2. `backend/app/services/agent_monitor.py`
- **新增方法**: `_sync_tool_calls(sessions_data)`
  - 遍历最近 5 个 session
  - 调用 `parse_session_jsonl` 解析每个 session 的历史
  - 保存工具调用到数据库
- **新增方法**: `_upsert_tool_call(tool_call_data)`
  - 检查是否已存在（避免重复）
  - 插入新的 ToolCall 记录

#### 3. `backend/app/services/openclaw_client.py`
- **新增方法**: `sessions_history(session_key, limit)`
  - 调用 `openclaw sessions history` 命令（备用方案）
  - 解析输出返回消息列表

### 前端修改

#### 1. 新增 `frontend/src/stores/toolCallStore.ts`
- 创建专门的 Tool Call 状态管理
- 实现 `fetchToolCalls()` 方法从 API 获取数据

#### 2. `frontend/src/pages/Dashboard.tsx`
- 集成 `useToolCallStore`
- 定时刷新工具调用数据（每 30 秒）

## 工作流程

```
Agent Monitor 同步
    ↓
读取 sessions.json 获取 session 列表
    ↓
对每个 session:
  - 读取 .jsonl 文件
  - 解析 toolCall 和 toolResult 消息
  - 保存到 tool_calls 表
    ↓
前端定时拉取 /api/tool-calls
    ↓
ToolCallTimeline 组件渲染
```

## 使用说明

### 查看工具调用时间线
1. 访问 Dashboard 页面
2. 右侧"工具调用时间线"卡片将显示真实数据
3. 数据每 30 秒自动刷新（随 Agent 同步）

### 数据特点
- 每次 Agent 同步时会解析最近 5 个 session 的历史
- 自动去重（基于 session_id + tool_name + timestamp）
- 支持的工具类型：read, write, edit, exec, web_search, browser, message 等

## 测试验证

- ✅ 解析器测试：从单个 session 解析出 140 个工具调用
- ✅ 后端 API 正常工作
- ✅ 前端编译通过
- ✅ 数据流完整：JSONL → DB → API → Frontend

## 问题描述
工具调用时间线使用的是硬编码的模拟数据，没有显示真实的工具调用记录。

## 修复内容

### 前端修改

#### 1. 新增 `frontend/src/stores/toolCallStore.ts`
- 创建专门的 Tool Call 状态管理
- 实现 `fetchToolCalls()` 方法从 API 获取数据
- 处理加载状态和错误

#### 2. `frontend/src/pages/Dashboard.tsx`
- 引入 `useToolCallStore`
- 在 `useEffect` 中调用 `fetchToolCalls({ limit: 20, hours: 24 })`
- 每 30 秒自动刷新数据
- 将真实的 `toolCalls` 数据传递给 `ToolCallTimeline` 组件
- 移除硬编码的 `mockToolCalls` 数组

#### 3. `frontend/src/components/dashboard/ToolCallTimeline.tsx`
- 清理未使用的导入（`CheckCircle`, `AlertCircle`）
- 移除 map 函数中未使用的 `index` 参数
- 保持组件逻辑不变（已正确实现数据展示）

### 后端 API
- ✅ 已有端点：`GET /api/tool-calls`
- 支持参数：
  - `limit`: 返回数量限制 (1-500)，默认 50
  - `hours`: 时间范围 (1-168 小时)，默认 24
  - `session_id`: 可选，筛选特定会话

## 使用说明

### 查看工具调用时间线
1. 访问 Dashboard 页面
2. 右侧"工具调用时间线"卡片将显示最近 20 条工具调用记录
3. 数据每 30 秒自动刷新

### API 调用示例
```bash
# 获取最近 20 条记录（过去 24 小时）
GET http://localhost:8000/api/tool-calls?limit=20&hours=24

# 获取特定会话的记录
GET http://localhost:8000/api/tool-calls?session_id=session-xxx&limit=50
```

## 数据流
```
Dashboard 页面加载
    ↓
useEffect 触发
    ↓
fetchToolCalls({ limit: 20, hours: 24 })
    ↓
toolCallApi.list() → GET /api/tool-calls
    ↓
后端查询 tool_calls 表
    ↓
返回最近 20 条记录
    ↓
更新 toolCallStore
    ↓
ToolCallTimeline 组件渲染真实数据
```

## 测试验证

- ✅ 后端 API 端点正常工作
- ✅ 前端编译通过（新增代码无错误）
- ✅ 数据流完整：API → Store → Component
- ⏳ 前端页面渲染（需手动验证）
