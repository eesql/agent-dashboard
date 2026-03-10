"""
API 端点测试用例
"""
import pytest
from httpx import AsyncClient
from app.main import app
from app.db.database import async_session_maker
from app.models.agent import Agent
from app.models.session import Session
from app.models.tool_call import ToolCall
from sqlalchemy import select
from datetime import datetime, timedelta


@pytest.fixture
async def client():
    """创建测试客户端"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def setup_test_data():
    """准备测试数据"""
    async with async_session_maker() as db:
        # 创建测试 Agent
        agent = Agent(
            id="agent:test:001",
            name="test-model",
            status="online",
            current_task="Testing...",
        )
        db.add(agent)
        
        # 创建测试 Session
        session = Session(
            id="agent:test:001",
            agent_id="test",
            label="test-model",
            kind="direct",
            created_at=datetime.now() - timedelta(hours=1),
            last_activity=datetime.now(),
            message_count=100,
        )
        db.add(session)
        
        # 创建测试 ToolCall
        tool_call = ToolCall(
            session_id="agent:test:001",
            tool_name="web_search",
            tool_args={"query": "test"},
            result_summary="Test result",
            timestamp=datetime.now(),
            duration_ms=150,
        )
        db.add(tool_call)
        
        await db.commit()
        
        yield {
            "agent_id": "agent:test:001",
            "session_id": "agent:test:001",
        }
        
        # 清理测试数据
        await db.rollback()


class TestAgentsAPI:
    """Agent API 测试"""
    
    @pytest.mark.asyncio
    async def test_list_agents(self, client, setup_test_data):
        """测试获取 Agent 列表"""
        response = await client.get("/api/agents")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    @pytest.mark.asyncio
    async def test_get_agent(self, client, setup_test_data):
        """测试获取单个 Agent"""
        agent_id = setup_test_data["agent_id"]
        response = await client.get(f"/api/agents/{agent_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == agent_id
    
    @pytest.mark.asyncio
    async def test_get_agent_not_found(self, client):
        """测试获取不存在的 Agent"""
        response = await client.get("/api/agents/nonexistent")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_sync_agents(self, client):
        """测试同步 Agent 状态"""
        response = await client.post("/api/agents/sync")
        assert response.status_code == 200
        data = response.json()
        assert "synced" in data


class TestSessionsAPI:
    """Session API 测试"""
    
    @pytest.mark.asyncio
    async def test_list_sessions(self, client, setup_test_data):
        """测试获取会话列表"""
        response = await client.get("/api/sessions")
        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
        assert "total" in data
        assert isinstance(data["sessions"], list)
    
    @pytest.mark.asyncio
    async def test_list_sessions_with_limit(self, client, setup_test_data):
        """测试带 limit 参数的会话列表"""
        response = await client.get("/api/sessions?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["sessions"]) <= 10
    
    @pytest.mark.asyncio
    async def test_get_session(self, client, setup_test_data):
        """测试获取会话详情"""
        session_id = setup_test_data["session_id"]
        response = await client.get(f"/api/sessions/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == session_id
        assert "label" in data
        assert "kind" in data
    
    @pytest.mark.asyncio
    async def test_get_session_not_found(self, client):
        """测试获取不存在的会话"""
        response = await client.get("/api/sessions/nonexistent")
        assert response.status_code == 404


class TestToolCallsAPI:
    """ToolCall API 测试"""
    
    @pytest.mark.asyncio
    async def test_list_tool_calls(self, client, setup_test_data):
        """测试获取工具调用列表"""
        response = await client.get("/api/tool-calls")
        assert response.status_code == 200
        data = response.json()
        assert "tool_calls" in data
        assert "total" in data
        assert isinstance(data["tool_calls"], list)
    
    @pytest.mark.asyncio
    async def test_list_tool_calls_by_session(self, client, setup_test_data):
        """测试按会话获取工具调用"""
        session_id = setup_test_data["session_id"]
        response = await client.get(f"/api/tool-calls?session_id={session_id}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["tool_calls"], list)


class TestMetricsAPI:
    """Metrics API 测试"""
    
    @pytest.mark.asyncio
    async def test_get_metrics_summary(self, client):
        """测试获取统计汇总"""
        response = await client.get("/api/metrics/summary")
        assert response.status_code == 200
        data = response.json()
        assert "today" in data
        assert "this_week" in data
        assert "this_month" in data
    
    @pytest.mark.asyncio
    async def test_get_today_metrics(self, client):
        """测试获取今日统计"""
        response = await client.get("/api/metrics/today")
        assert response.status_code == 200
        data = response.json()
        assert "date" in data
        assert "token_count" in data
    
    @pytest.mark.asyncio
    async def test_get_trend_data(self, client):
        """测试获取趋势数据"""
        response = await client.get("/api/metrics/trend?days=7")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 7


class TestHealthCheck:
    """健康检查测试"""
    
    @pytest.mark.asyncio
    async def test_root(self, client):
        """测试根端点"""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"
    
    @pytest.mark.asyncio
    async def test_health(self, client):
        """测试健康检查"""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
