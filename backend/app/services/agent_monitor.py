"""Agent 状态监控服务"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.agent import Agent
from app.models.session import Session
from app.services.openclaw_parser import parse_openclaw_status, get_active_sessions
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
            # 使用 openclaw status 命令获取会话列表
            sessions = parse_openclaw_status()
            agents = []
            
            for session_data in sessions:
                agent_id = session_data.get("id") or session_data.get("key")
                if not agent_id:
                    continue
                
                # 更新或创建 Agent 记录
                agent = await self._upsert_agent(agent_id, session_data)
                agents.append(agent)
            
            logger.info(f"Synced {len(agents)} agents from OpenClaw")
            return agents
            
        except Exception as e:
            logger.error(f"Failed to sync agents: {e}")
            return []
    
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
        
        if agent:
            # 更新现有记录
            agent.status = status
            agent.name = data.get("label") or agent.name
            agent.current_task = data.get("currentTask")
            agent.last_seen = datetime.now()
        else:
            # 创建新记录
            agent = Agent(
                id=agent_id,
                name=data.get("label"),
                status=status,
                current_task=data.get("currentTask"),
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
    
    def _parse_status(self, data: dict) -> str:
        """解析 Agent 状态"""
        # 根据会话数据判断状态
        age = data.get("age", "")
        kind = data.get("kind", "")
        
        # 如果是 subagent 且最近活跃，标记为 busy
        if kind == "subagent" and age and "1m" in age:
            return "busy"
        
        # 根据最后活跃时间判断状态
        if age:
            if "now" in age or "1m" in age or "5m" in age:
                return "online"
            elif "10m" in age or "30m" in age or "1h" in age:
                return "offline"
            else:
                return "offline"
        
        return "online"
    
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
