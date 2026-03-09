"""Agent 状态监控服务"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.agent import Agent
from app.models.session import Session
from app.models.tool_call import ToolCall
from app.services.openclaw_parser import parse_openclaw_sessions
from app.api.websocket import notify_agent_status
from app.config import settings
from datetime import datetime
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class AgentMonitor:
    """Agent 状态监控器"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self._status_cache: Dict[str, dict] = {}
    
    async def sync_agents(self) -> List[Agent]:
        """从 OpenClaw 同步 Agent 状态"""
        try:
            # 使用 openclaw sessions 命令获取会话列表
            sessions_data = parse_openclaw_sessions()
            agents = []
            total_tokens = 0
            
            for session_data in sessions_data:
                agent_id = session_data.get("id") or session_data.get("key")
                if not agent_id:
                    continue
                
                # 累加 token 数
                tokens = session_data.get("tokens", 0)
                total_tokens += tokens
                
                # 更新或创建 Agent 记录
                agent = await self._upsert_agent(agent_id, session_data)
                agents.append(agent)
                
                # 同步保存 Session 记录
                await self._upsert_session(agent_id, session_data)
            
            # 提交事务（先提交 agent 更新，避免长时间持有锁）
            await self.db.commit()
            
            # 单独更新 metrics（使用新的事务）
            try:
                await self._update_metrics_simple(total_tokens, len(agents))
            except Exception as e:
                logger.error(f"Failed to update metrics: {e}")
            
            # 同步工具调用记录（异步，不阻塞）
            try:
                await self._sync_tool_calls(sessions_data[:5])  # 只同步最近 5 个 session
            except Exception as e:
                logger.error(f"Failed to sync tool calls: {e}")
            
            logger.info(f"Synced {len(agents)} agents from OpenClaw, total tokens: {total_tokens}")
            return agents
            
        except Exception as e:
            logger.error(f"Failed to sync agents: {e}")
            await self.db.rollback()
            return []
    
    async def _update_metrics_simple(self, token_count: int, request_count: int):
        """简单更新统计数据（避免锁竞争）"""
        from app.models.metric import Metric
        from datetime import date
        from sqlalchemy import update
        
        today = date.today()
        
        # 直接使用 execute 更新，不查询
        result = await self.db.execute(
            update(Metric)
            .where(Metric.date == today)
            .values(
                token_count=token_count,
                request_count=request_count,
                estimated_cost=token_count * 0.000002,
            )
        )
        
        # 如果没有更新任何行，插入新记录
        if result.rowcount == 0:
            metric = Metric(
                agent_id=None,
                date=today,
                token_count=token_count,
                request_count=request_count,
                avg_response_time_ms=0,
                estimated_cost=token_count * 0.000002,
            )
            self.db.add(metric)
        
        await self.db.commit()
    
    async def _sync_tool_calls(self, sessions_data: List[Dict[str, Any]]):
        """同步工具调用记录"""
        from app.services.openclaw_parser import parse_session_jsonl
        
        tool_calls_count = 0
        
        for session_data in sessions_data:
            session_key = session_data.get("id") or session_data.get("key")
            session_file = session_data.get("sessionFile")
            
            if not session_key or not session_file:
                continue
            
            try:
                # 解析 session 的 jsonl 文件
                tool_calls = parse_session_jsonl(session_file, session_key)
                
                # 保存工具调用到数据库
                for tc in tool_calls:
                    await self._upsert_tool_call(tc)
                    tool_calls_count += 1
                    
            except Exception as e:
                logger.debug(f"Failed to sync tool calls for session {session_key}: {e}")
        
        logger.info(f"Synced {tool_calls_count} tool calls")
    
    async def _upsert_tool_call(self, tool_call_data: Dict[str, Any]):
        """更新或插入 Tool Call 记录"""
        session_id = tool_call_data.get("session_id")
        tool_name = tool_call_data.get("tool_name")
        timestamp_str = tool_call_data.get("timestamp")
        
        if not session_id or not tool_name:
            return
        
        # 解析时间戳
        timestamp = datetime.now()
        if timestamp_str:
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except:
                pass
        
        # 检查是否已存在（避免重复）
        result = await self.db.execute(
            select(ToolCall).where(
                ToolCall.session_id == session_id,
                ToolCall.tool_name == tool_name,
                ToolCall.timestamp == timestamp
            )
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            # 创建新记录
            tool_call = ToolCall(
                session_id=session_id,
                tool_name=tool_name,
                tool_args=tool_call_data.get("tool_args"),
                result_summary=tool_call_data.get("result_summary"),
                timestamp=timestamp,
                duration_ms=tool_call_data.get("duration_ms"),
            )
            self.db.add(tool_call)
            await self.db.flush()
    
    async def _upsert_agent(self, agent_id: str, data: dict) -> Agent:
        """更新或插入 Agent 记录"""
        # 尝试获取现有记录
        result = await self.db.execute(
            select(Agent).where(Agent.id == agent_id)
        )
        agent = result.scalar_one_or_none()
        
        # 解析状态
        status = self._parse_status(data)
        old_status = agent.status if agent else None
        
        # 获取 token 数据
        token_count = data.get("tokens", 0)
        
        if agent:
            # 更新现有记录
            agent.status = status
            agent.name = data.get("model") or agent.name
            agent.current_task = f"{data.get('age', '')} ago - {token_count} tokens"
            agent.last_seen = datetime.now()
        else:
            # 创建新记录
            agent = Agent(
                id=agent_id,
                name=data.get("model"),
                status=status,
                current_task=f"{data.get('age', '')} ago - {token_count} tokens",
            )
            self.db.add(agent)
        
        await self.db.flush()
        
        # 如果状态变化，发送 WebSocket 通知
        if old_status != status:
            await notify_agent_status({
                "id": agent.id,
                "name": agent.name,
                "status": status,
                "current_task": agent.current_task,
                "last_seen": agent.last_seen.isoformat(),
            })
        
        return agent
    
    async def _upsert_session(self, session_id: str, data: dict):
        """更新或插入 Session 记录"""
        # 尝试获取现有记录
        result = await self.db.execute(
            select(Session).where(Session.id == session_id)
        )
        session = result.scalar_one_or_none()
        
        # 解析 last_activity 时间
        last_seen_str = data.get("last_seen", "")
        last_activity = None
        if last_seen_str:
            try:
                last_activity = datetime.fromisoformat(last_seen_str)
            except:
                last_activity = datetime.now()
        else:
            last_activity = datetime.now()
        
        if session:
            # 更新现有记录
            session.last_activity = last_activity
            session.message_count = data.get("tokens", 0)  # 暂时用 tokens 作为 message_count 的代理
        else:
            # 创建新记录
            session = Session(
                id=session_id,
                agent_id=session_id.split(":")[1] if ":" in session_id else None,  # 提取 agent 部分
                label=data.get("model"),
                kind=data.get("kind", "direct"),
                created_at=last_activity,
                last_activity=last_activity,
                message_count=data.get("tokens", 0),
            )
            self.db.add(session)
        
        await self.db.flush()
    
    def _parse_status(self, data: dict) -> str:
        """解析 Agent 状态"""
        # 根据最后活跃时间判断状态
        age = data.get("age", "")
        last_seen = data.get("last_seen", "")
        
        if age:
            # 5 分钟内活跃 = online
            if "now" in age or "1m" in age or "2m" in age or "3m" in age or "4m" in age or "5m" in age:
                return "online"
            # 1 小时内活跃 = busy（可能还在运行）
            elif "10m" in age or "20m" in age or "30m" in age or "40m" in age or "50m" in age or "1h" in age:
                return "busy"
            # 超过 1 小时 = offline
            else:
                return "offline"
        
        # 如果有 last_seen 时间，计算时间差
        if last_seen:
            try:
                from datetime import datetime, timedelta
                last_seen_dt = datetime.fromisoformat(last_seen)
                now = datetime.now()
                diff = (now - last_seen_dt).total_seconds()
                
                if diff < 300:  # 5 分钟
                    return "online"
                elif diff < 3600:  # 1 小时
                    return "busy"
                else:
                    return "offline"
            except:
                pass
        
        return "offline"
    
    async def get_all_agents(self) -> List[Agent]:
        """获取所有 Agent"""
        result = await self.db.execute(select(Agent).order_by(Agent.last_seen.desc()))
        return result.scalars().all()
    
    async def get_agent(self, agent_id: str) -> Optional[Agent]:
        """获取单个 Agent"""
        result = await self.db.execute(select(Agent).where(Agent.id == agent_id))
        return result.scalar_one_or_none()
    
    async def update_agent_status(
        self,
        agent_id: str,
        status: str,
        current_task: Optional[str] = None,
    ) -> Optional[Agent]:
        """更新 Agent 状态"""
        result = await self.db.execute(select(Agent).where(Agent.id == agent_id))
        agent = result.scalar_one_or_none()
        
        if agent:
            agent.status = status
            agent.current_task = current_task
            agent.last_seen = datetime.now()
            await self.db.flush()
        
        return agent
    
    async def get_status_changes(self, last_check: datetime) -> List[dict]:
        """获取状态变化"""
        result = await self.db.execute(
            select(Agent).where(Agent.updated_at > last_check)
        )
        agents = result.scalars().all()
        
        return [
            {
                "id": agent.id,
                "name": agent.name,
                "status": agent.status,
                "current_task": agent.current_task,
                "last_seen": agent.last_seen,
            }
            for agent in agents
        ]
